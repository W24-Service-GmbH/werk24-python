"""One HTTPS connection per client, and downloads that do not block the loop.

Every HTTPS call - the drawing upload, read-with-callback, and each payload
download - used to build its own `ClientSession` and `TCPConnector`. The SSL
*context* was cached; the *connection* was not, so a three-ask read paid three
separate DNS, TCP and TLS handshakes to S3.

Worse, the download ran inside the receive loop, so each transfer blocked
receipt of the next ASK message. crew-watchdog reads per-ask latency off that
loop, so it was inside the status page numbers too.

Pure unit tests: nothing connects to anything.
"""

import asyncio

import pytest

from werk24 import TechreadMessageSubtype, TechreadMessageType
from werk24.techread import Werk24Client


def _client():
    return Werk24Client(token="t", region="r")


class FakeSession:
    """Stands in for an aiohttp.ClientSession."""

    instances = 0

    def __init__(self):
        FakeSession.instances += 1
        self.closed = False

    async def close(self):
        self.closed = True


class TestTheSessionIsShared:
    def setup_method(self):
        FakeSession.instances = 0

    def test_it_is_built_once_and_reused(self, monkeypatch):
        client = _client()
        monkeypatch.setattr(client, "_make_https_session", lambda *a, **k: FakeSession())

        first = client._https_session()
        for _ in range(10):
            assert client._https_session() is first
        assert FakeSession.instances == 1

    def test_it_is_not_built_until_it_is_needed(self, monkeypatch):
        """A client used only over the WebSocket should not open one."""
        client = _client()
        assert client._shared_https_session is None

    def test_a_closed_session_is_replaced(self, monkeypatch):
        # aiohttp closes a session whose loop went away; asking for one must
        # not hand back something unusable.
        client = _client()
        monkeypatch.setattr(client, "_make_https_session", lambda *a, **k: FakeSession())
        first = client._https_session()
        first.closed = True
        assert client._https_session() is not first

    @pytest.mark.asyncio
    async def test_shutdown_closes_it(self, monkeypatch):
        """Leaving it open leaks the connector and warns on every discard."""
        client = _client()
        monkeypatch.setattr(client, "_make_https_session", lambda *a, **k: FakeSession())
        session = client._https_session()

        await client._graceful_shutdown()

        assert session.closed
        assert client._shared_https_session is None

    @pytest.mark.asyncio
    async def test_shutdown_survives_a_session_that_will_not_close(self, monkeypatch):
        """Shutdown is a teardown path; it must not raise a new failure."""
        client = _client()

        class Stubborn(FakeSession):
            async def close(self):
                raise OSError("no")

        monkeypatch.setattr(client, "_make_https_session", lambda *a, **k: Stubborn())
        client._https_session()
        await client._graceful_shutdown()
        assert client._shared_https_session is None

    def test_no_call_site_opens_its_own(self):
        """The three former `async with self._make_https_session()` sites."""
        import inspect

        source = inspect.getsource(Werk24Client)
        assert "async with self._make_https_session()" not in source
        # The factory itself stays - _https_session() calls it.
        assert source.count("self._make_https_session()") == 1


class TestDownloadsDoNotBlockTheReceiveLoop:
    """A payload transfer must not hold up the next ASK message."""

    def _message(self, subtype=None, payload_url=None):
        message = type(
            "M",
            (),
            {
                "message_type": (
                    TechreadMessageType.PROGRESS
                    if subtype
                    else TechreadMessageType.ASK
                ),
                "message_subtype": subtype,
                "payload_url": payload_url,
                "payload_bytes": None,
                "request_id": None,
            },
        )()
        return message

    @pytest.mark.asyncio
    async def test_a_download_starts_before_the_next_message_is_received(
        self, monkeypatch
    ):
        """The overlap, stated directly.

        The first message's download is started, then the loop goes back for
        the next message. If the download were awaited inline, the recv would
        not begin until it finished.
        """
        client = _client()
        order = []

        started = asyncio.Event()

        async def slow_download(*_args, **_kwargs):
            order.append("download-start")
            await started.wait()
            order.append("download-end")
            return b"payload"

        messages = [
            self._message(payload_url="https://s3/one"),
            self._message(subtype=TechreadMessageSubtype.PROGRESS_COMPLETED),
        ]

        async def fake_recv():
            if order.count("recv") == 0:
                order.append("recv")
                return "raw-0"
            order.append("recv")
            started.set()
            return "raw-1"

        client._wss_session = type("S", (), {"recv": staticmethod(fake_recv)})()
        monkeypatch.setattr(client, "download_payload", slow_download)
        monkeypatch.setattr(
            client, "_parse_message", lambda raw: messages[int(raw.split("-")[1])]
        )

        async def send(*_a, **_k):
            return None

        monkeypatch.setattr(client, "_send_command", send)

        received = [m async for m in client._send_command_read()]

        assert len(received) == 2
        # The second recv happened while the first download was still running.
        assert order.index("recv") < order.index("download-start")
        assert order.index("download-start") < order.index("download-end")
        assert order[-1] == "download-end" or "recv" in order[order.index("download-start") :]

    @pytest.mark.asyncio
    async def test_messages_still_arrive_in_order_with_their_payloads(
        self, monkeypatch
    ):
        """Only the waiting moved; the contract did not."""
        client = _client()

        async def download(url, *_a, **_k):
            return str(url).encode()

        messages = [
            self._message(payload_url="https://s3/a"),
            self._message(payload_url="https://s3/b"),
            self._message(subtype=TechreadMessageSubtype.PROGRESS_COMPLETED),
        ]
        counter = {"n": 0}

        async def fake_recv():
            raw = f"raw-{counter['n']}"
            counter["n"] += 1
            return raw

        client._wss_session = type("S", (), {"recv": staticmethod(fake_recv)})()
        monkeypatch.setattr(client, "download_payload", download)
        monkeypatch.setattr(
            client, "_parse_message", lambda raw: messages[int(raw.split("-")[1])]
        )

        async def send(*_a, **_k):
            return None

        monkeypatch.setattr(client, "_send_command", send)

        received = [m async for m in client._send_command_read()]

        assert [m.payload_bytes for m in received] == [
            b"https://s3/a",
            b"https://s3/b",
            None,
        ]

    @pytest.mark.asyncio
    async def test_a_failed_download_still_raises(self, monkeypatch):
        client = _client()

        async def boom(*_a, **_k):
            raise OSError("s3 said no")

        messages = [
            self._message(payload_url="https://s3/a"),
            self._message(subtype=TechreadMessageSubtype.PROGRESS_COMPLETED),
        ]
        counter = {"n": 0}

        async def fake_recv():
            raw = f"raw-{counter['n']}"
            counter["n"] += 1
            return raw

        client._wss_session = type("S", (), {"recv": staticmethod(fake_recv)})()
        monkeypatch.setattr(client, "download_payload", boom)
        monkeypatch.setattr(
            client, "_parse_message", lambda raw: messages[int(raw.split("-")[1])]
        )

        async def send(*_a, **_k):
            return None

        monkeypatch.setattr(client, "_send_command", send)

        with pytest.raises(OSError):
            async for _ in client._send_command_read():
                pass

    @pytest.mark.asyncio
    async def test_abandoning_the_stream_cancels_a_download_in_flight(
        self, monkeypatch
    ):
        """A caller that stops consuming must not leave a task running.

        It would be downloading against a session the client is about to
        close, and nothing would ever read its result.

        The first message deliberately carries no payload, so it is yielded
        without awaiting anything while the second message's download is still
        outstanding when the caller walks away. The task is found by
        difference against the tasks alive before the read, because a task
        that has not had a tick yet never enters its coroutine and so cannot
        report its own cancellation.
        """
        client = _client()

        async def never_finishes(*_a, **_k):
            await asyncio.Event().wait()

        messages = [
            self._message(),
            self._message(payload_url="https://s3/never"),
        ]
        counter = {"n": 0}

        async def fake_recv():
            raw = f"raw-{min(counter['n'], 1)}"
            counter["n"] += 1
            return raw

        client._wss_session = type("S", (), {"recv": staticmethod(fake_recv)})()
        monkeypatch.setattr(client, "download_payload", never_finishes)
        monkeypatch.setattr(
            client, "_parse_message", lambda raw: messages[int(raw.split("-")[1])]
        )

        async def send(*_a, **_k):
            return None

        monkeypatch.setattr(client, "_send_command", send)

        before = asyncio.all_tasks()
        generator = client._send_command_read()
        first = await generator.__anext__()
        assert first is messages[0]

        spawned = asyncio.all_tasks() - before
        assert spawned, "no download task was started"

        await generator.aclose()
        await asyncio.sleep(0)

        assert all(task.cancelled() or task.done() for task in spawned)


class TestNormalTerminationLosesNothing:
    """The message held back for the overlap is a real message.

    Holding one back is what creates the overlap, but every way out of the
    receive loop except an exception is a normal end - and at those ends the
    held-back message still has to be delivered. Cancelling it instead loses
    an answer the customer was already sent, and with a message cap of 1 it
    yields nothing at all.
    """

    def _message(self, subtype=None, payload_url=None):
        return type(
            "M",
            (),
            {
                "message_type": (
                    TechreadMessageType.PROGRESS
                    if subtype
                    else TechreadMessageType.ASK
                ),
                "message_subtype": subtype,
                "payload_url": payload_url,
                "payload_bytes": None,
                "request_id": None,
            },
        )()

    def _wire(self, client, monkeypatch, messages, closes_after=None):
        counter = {"n": 0}

        async def fake_recv():
            index = counter["n"]
            counter["n"] += 1
            if closes_after is not None and index >= closes_after:
                import websockets

                raise websockets.exceptions.ConnectionClosedOK(None, None)
            return f"raw-{index}"

        client._wss_session = type("S", (), {"recv": staticmethod(fake_recv)})()
        monkeypatch.setattr(
            client, "_parse_message", lambda raw: messages[int(raw.split("-")[1])]
        )

        async def send(*_a, **_k):
            return None

        monkeypatch.setattr(client, "_send_command", send)

    @pytest.mark.asyncio
    async def test_a_clean_server_close_still_delivers_the_last_message(
        self, monkeypatch
    ):
        client = _client()
        messages = [self._message(), self._message()]
        self._wire(client, monkeypatch, messages, closes_after=2)

        received = [m async for m in client._send_command_read()]

        assert received == messages

    @pytest.mark.asyncio
    async def test_a_clean_close_delivers_its_payload_too(self, monkeypatch):
        client = _client()
        messages = [
            self._message(),
            self._message(payload_url="https://s3/last"),
        ]
        self._wire(client, monkeypatch, messages, closes_after=2)

        async def download(url, *_a, **_k):
            return str(url).encode()

        monkeypatch.setattr(client, "download_payload", download)

        received = [m async for m in client._send_command_read()]

        assert len(received) == 2
        assert received[-1].payload_bytes == b"https://s3/last"

    @pytest.mark.asyncio
    async def test_the_message_cap_delivers_what_it_received(self, monkeypatch):
        """A cap of 1 used to yield nothing at all."""
        client = _client()
        messages = [self._message()]
        self._wire(client, monkeypatch, messages)

        received = [
            m
            async for m in client._send_command_read(max_messages_per_session=1)
        ]

        assert received == messages

    @pytest.mark.asyncio
    async def test_an_already_failed_download_is_not_left_unretrieved(
        self, monkeypatch
    ):
        """Cancelling a task that already raised never retrieves its error.

        asyncio then prints "Task exception was never retrieved" and the real
        download failure is lost behind it.
        """
        client = _client()

        async def fails_immediately(*_a, **_k):
            raise OSError("s3 said no")

        messages = [
            self._message(),
            self._message(payload_url="https://s3/boom"),
        ]
        self._wire(client, monkeypatch, messages)
        monkeypatch.setattr(client, "download_payload", fails_immediately)

        before = asyncio.all_tasks()
        generator = client._send_command_read()
        await generator.__anext__()
        spawned = asyncio.all_tasks() - before

        await generator.aclose()
        await asyncio.sleep(0)

        for task in spawned:
            assert task.done()
            # Retrieving it here must not raise "never retrieved" later.
            assert task.cancelled() or task.exception() is not None
