"""A read that never finishes, and a blip that should not fail one.

Two reliability gaps, same file.

**No bounded wait.** The WebSocket keepalive detects a *dead* socket. It cannot
detect a live socket that will never deliver `PROGRESS_COMPLETED`, and nothing
else bounded `_send_command_read`, so a stalled server held the caller until
`wss_close_timeout` (600s) — or, for an SDK user driving it directly,
indefinitely. crew-watchdog is one of those callers: a stalled read pins its
Lambda to the Lambda's own timeout and delays the status page exactly when it
matters.

**Retries that did not exist.** `max_https_retries` was configured and read
nowhere. The upload and the payload download each did one request and re-raised,
and `_raise_for_status` turns any 5xx into a terminal `ServerException`, so a
transient S3 blip failed a request whose quota crew-api had already spent.

Pure unit tests: nothing connects, and every wait is a stand-in.
"""

import asyncio

import pytest

from werk24 import TechreadMessageSubtype, TechreadMessageType
from werk24.techread import Werk24Client, settings
from werk24.utils.exceptions import (
    BadRequestException,
    InsufficientCreditsException,
    ReadTimeoutError,
    ServerException,
)


def _client():
    return Werk24Client(token="t", region="r")


def _no_backoff(monkeypatch):
    """Skip the backoff wait without recursing through the patched sleep."""
    real_sleep = asyncio.sleep

    async def instant(*_args, **_kwargs):
        await real_sleep(0)

    monkeypatch.setattr(asyncio, "sleep", instant)


def _message(subtype=None):
    return type(
        "M",
        (),
        {
            "message_type": (
                TechreadMessageType.PROGRESS if subtype else TechreadMessageType.ASK
            ),
            "message_subtype": subtype,
            "payload_url": None,
            "payload_bytes": None,
            "request_id": None,
        },
    )()


def _wire(client, monkeypatch, recv, messages):
    client._wss_session = type("S", (), {"recv": staticmethod(recv)})()
    monkeypatch.setattr(
        client, "_parse_message", lambda raw: messages[int(raw.split("-")[1])]
    )

    async def send(*_a, **_k):
        return None

    monkeypatch.setattr(client, "_send_command", send)


class TestTheReadIsBounded:
    @pytest.mark.asyncio
    async def test_a_silent_server_raises_rather_than_hanging(self, monkeypatch):
        client = _client()

        async def never():
            await asyncio.Event().wait()

        _wire(client, monkeypatch, never, [])

        with pytest.raises(ReadTimeoutError):
            async for _ in client._send_command_read(total_timeout=0.05):
                pass

    @pytest.mark.asyncio
    async def test_the_timeout_is_typed_not_a_bare_asyncio_error(self, monkeypatch):
        """Callers need to tell a stalled server from a broken transport."""
        client = _client()

        async def never():
            await asyncio.Event().wait()

        _wire(client, monkeypatch, never, [])

        with pytest.raises(ReadTimeoutError) as excinfo:
            async for _ in client._send_command_read(total_timeout=0.05):
                pass
        assert not isinstance(excinfo.value, asyncio.TimeoutError)

    @pytest.mark.asyncio
    async def test_a_read_that_finishes_in_time_is_untouched(self, monkeypatch):
        client = _client()
        counter = {"n": 0}

        async def recv():
            raw = f"raw-{counter['n']}"
            counter["n"] += 1
            return raw

        _wire(
            client,
            monkeypatch,
            recv,
            [
                _message(),
                _message(subtype=TechreadMessageSubtype.PROGRESS_COMPLETED),
            ],
        )

        received = [m async for m in client._send_command_read(total_timeout=30)]
        assert len(received) == 2

    def test_the_default_comes_from_settings(self):
        assert settings.read_total_timeout > 0
        # The idle bound has to be the shorter of the two, or it never fires.
        assert settings.read_idle_timeout <= settings.read_total_timeout


class TestHttpsRetries:
    """Which failures are retried, and which are emphatically not."""

    @pytest.mark.asyncio
    async def test_a_transient_5xx_is_retried_and_then_succeeds(self, monkeypatch):
        client = _client()
        _no_backoff(monkeypatch)
        calls = {"n": 0}

        async def flaky():
            calls["n"] += 1
            if calls["n"] < 3:
                raise ServerException(details="500")
            return "ok"

        assert await client._with_https_retries("upload", flaky) == "ok"
        assert calls["n"] == 3

    @pytest.mark.asyncio
    async def test_it_gives_up_after_the_configured_number(self, monkeypatch):
        client = _client()
        _no_backoff(monkeypatch)
        calls = {"n": 0}

        async def always_fails():
            calls["n"] += 1
            raise ServerException(details="500")

        with pytest.raises(ServerException):
            await client._with_https_retries("upload", always_fails)
        assert calls["n"] == settings.max_https_retries + 1

    @pytest.mark.asyncio
    async def test_a_4xx_is_not_retried(self, monkeypatch):
        """Resending a request that was wrong will not make it right."""
        client = _client()
        calls = {"n": 0}

        async def bad_request():
            calls["n"] += 1
            raise BadRequestException(details="400")

        with pytest.raises(BadRequestException):
            await client._with_https_retries("upload", bad_request)
        assert calls["n"] == 1

    @pytest.mark.asyncio
    async def test_a_quota_refusal_is_not_retried(self, monkeypatch):
        """429 subclasses ServerException, so this is the one that could slip.

        Retrying it would turn a quota refusal into a retry storm against an
        account that has already run out.
        """
        client = _client()
        calls = {"n": 0}

        async def out_of_credits():
            calls["n"] += 1
            raise InsufficientCreditsException(details="429")

        with pytest.raises(InsufficientCreditsException):
            await client._with_https_retries("upload", out_of_credits)
        assert calls["n"] == 1

    @pytest.mark.asyncio
    async def test_a_success_costs_no_retries(self, monkeypatch):
        client = _client()
        calls = {"n": 0}

        async def fine():
            calls["n"] += 1
            return 42

        assert await client._with_https_retries("download", fine) == 42
        assert calls["n"] == 1

    def test_the_upload_and_the_download_both_go_through_it(self):
        import inspect

        for name in ("_upload_associated_file", "download_payload"):
            source = inspect.getsource(getattr(Werk24Client, name))
            assert "_with_https_retries(" in source, name
