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

        Each recv is labelled, because the claim is about the SECOND one. An
        implementation that received both messages and only then started the
        download would satisfy an assertion that names "recv" alone.
        """
        client = _client()
        order = []

        # Released by the second recv. The download cannot finish until then,
        # so "download-end" after "recv-1" is the overlap. Bounded, so an
        # inline implementation fails the assertions rather than hanging the
        # suite waiting for an event nothing will set.
        second_recv = asyncio.Event()

        async def slow_download(*_args, **_kwargs):
            order.append("download-start")
            try:
                await asyncio.wait_for(second_recv.wait(), timeout=2.0)
            except asyncio.TimeoutError:
                order.append("download-gave-up")
            order.append("download-end")
            return b"payload"

        messages = [
            self._message(payload_url="https://s3/one"),
            self._message(subtype=TechreadMessageSubtype.PROGRESS_COMPLETED),
        ]

        recvs = {"n": 0}

        async def fake_recv():
            index = recvs["n"]
            recvs["n"] += 1
            if index == 0:
                order.append("recv-0")
                return "raw-0"
            # Give the download task a chance to be scheduled before this
            # recv is recorded, so "download-start" precedes "recv-1" and the
            # ordering below is about the overlap rather than about which
            # coroutine the loop happened to run first.
            await asyncio.sleep(0)
            order.append("recv-1")
            second_recv.set()
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
        # The download never gave up waiting, so the second recv did happen
        # while it was still running.
        assert "download-gave-up" not in order
        # And in order: message 1 arrives, its download starts, message 2
        # arrives while that download is still in flight, then it finishes.
        assert (
            order.index("recv-0")
            < order.index("download-start")
            < order.index("recv-1")
            < order.index("download-end")
        )

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


class TestTheSessionIsClosedOnEveryPath:
    """A pooled session needs someone to close it.

    Pooling it for the client's lifetime is right inside `async with`, where
    `__aexit__` closes it. But `read_drawing_with_callback` and
    `download_payload` are documented as usable on a bare client, and that
    caller never reaches `__aexit__`. Before pooling, each of those calls
    built and closed its own session; after pooling, nothing would close it
    and aiohttp warns about it when the client is collected.
    """

    @pytest.mark.asyncio
    async def test_a_standalone_call_closes_the_session(self, monkeypatch):
        client = _client()
        session = FakeSession()
        monkeypatch.setattr(client, "_make_https_session", lambda: session)

        assert client._entered is False
        client._https_session()
        await client._release_https_if_standalone()

        assert session.closed is True
        assert client._shared_https_session is None

    @pytest.mark.asyncio
    async def test_inside_the_context_the_session_survives_a_call(self, monkeypatch):
        client = _client()
        session = FakeSession()
        monkeypatch.setattr(client, "_make_https_session", lambda: session)
        client._entered = True

        client._https_session()
        await client._release_https_if_standalone()

        # Still pooled: closing it per call is exactly what this change was
        # about not doing.
        assert session.closed is False
        assert client._shared_https_session is session

    @pytest.mark.asyncio
    async def test_the_standalone_methods_carry_the_release(self):
        # The decorator, not a hand-written try/finally at each site.
        for name in ("read_drawing_with_callback", "download_payload"):
            method = getattr(Werk24Client, name)
            assert getattr(method, "__wrapped__", None) is not None, name

    @pytest.mark.asyncio
    async def test_close_is_public_and_idempotent(self, monkeypatch):
        client = _client()
        session = FakeSession()
        monkeypatch.setattr(client, "_make_https_session", lambda: session)
        client._https_session()

        await client.close()
        assert session.closed is True

        # Again, on a client that now holds nothing.
        await client.close()

    @pytest.mark.asyncio
    async def test_a_close_that_raises_does_not_fail_the_call(self, monkeypatch):
        """Releasing a connection must never be why a read fails."""
        client = _client()

        class _Angry(FakeSession):
            async def close(self):
                raise RuntimeError("connector already gone")

        monkeypatch.setattr(client, "_make_https_session", lambda: _Angry())
        client._https_session()

        await client._release_https_if_standalone()
        assert client._shared_https_session is None

    @pytest.mark.asyncio
    async def test_entering_and_leaving_tracks_the_flag(self, monkeypatch):
        client = _client()

        async def _noop(*_a, **_k):
            return None

        monkeypatch.setattr(client, "_connect_with_retry", _noop)
        monkeypatch.setattr(client, "_graceful_shutdown", _noop)

        async with client:
            assert client._entered is True
        assert client._entered is False
