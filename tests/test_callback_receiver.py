"""Tests for the callback receiver and the tunnel helper.

Offline: the receiver is driven by a local client standing in for the API, so
the whole harness minus the tunnel is exercised on every push. What is left
untested here is Cloudflare's half, which no unit test can stand in for.
"""

from __future__ import annotations

import asyncio
import re
import time
import uuid

import aiohttp
import pytest

from werk24 import (
    AskMetaData,
    TechreadMessage,
    TechreadMessageSubtype,
    TechreadMessageType,
)
from werk24.models.v2.responses import ResponseMetaDataComponentDrawing

from tests.callback_check import (
    CallbackDelivery,
    CallbackReceiver,
    QuickTunnel,
    TunnelUnavailable,
    assert_callback_contract,
    cloudflared_binary,
)
from tests.callback_check.contract import (
    EXPECTED_CONTENT_TYPE,
    EXPECTED_USER_AGENT,
)
from tests.test_callback_e2e import _run_is_complete


async def _post(url: str, body: bytes, headers: dict) -> int:
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, data=body, headers=headers) as response:
            return response.status


class TestTheReceiverRecordsWhatArrives:
    async def test_a_post_is_recorded_with_its_headers_and_body(self):
        async with CallbackReceiver() as receiver:
            url = f"http://127.0.0.1:{receiver.port}{receiver.path}"
            status = await _post(url, b'{"hello": "world"}', {"X-Custom": "value"})

        assert status == 200  # noqa: B101
        assert len(receiver.deliveries) == 1  # noqa: B101
        delivery = receiver.deliveries[0]
        assert delivery.method == "POST"  # noqa: B101
        assert delivery.path == receiver.path  # noqa: B101
        assert delivery.body == b'{"hello": "world"}'  # noqa: B101
        # Header names are lower-cased so the contract checks can look them up
        # without caring how the sender capitalised them.
        assert delivery.headers["x-custom"] == "value"  # noqa: B101

    async def test_the_receiver_answers_200(self):
        """core-reader stops sending after a non-2xx.

        A receiver that answered anything else would truncate the message
        sequence and the check would report a missing COMPLETED that the
        server had been perfectly willing to send.
        """
        async with CallbackReceiver() as receiver:
            url = f"http://127.0.0.1:{receiver.port}{receiver.path}"
            assert await _post(url, b"{}", {}) == 200  # noqa: B101

    async def test_a_post_to_the_wrong_path_is_still_recorded(self):
        """Evidence, not noise: dropping it would report "no callback"."""
        async with CallbackReceiver() as receiver:
            url = f"http://127.0.0.1:{receiver.port}/somewhere-else"
            await _post(url, b"{}", {})

        assert len(receiver.deliveries) == 1  # noqa: B101
        assert receiver.deliveries[0].path == "/somewhere-else"  # noqa: B101

    async def test_the_health_endpoint_is_not_recorded_as_a_delivery(self):
        async with CallbackReceiver() as receiver:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                url = f"http://127.0.0.1:{receiver.port}{receiver.health_path}"
                async with session.get(url) as response:
                    assert response.status == 200  # noqa: B101

        assert receiver.deliveries == ()  # noqa: B101

    async def test_deliveries_survive_the_context_manager(self):
        async with CallbackReceiver() as receiver:
            url = f"http://127.0.0.1:{receiver.port}{receiver.path}"
            await _post(url, b"{}", {})

        # The assertions run after the server is down, which is how the
        # end-to-end check is written.
        assert len(receiver.deliveries) == 1  # noqa: B101

    async def test_the_port_is_released_on_exit(self):
        async with CallbackReceiver() as receiver:
            port = receiver.port
        with pytest.raises(RuntimeError):
            _ = receiver.port

        with pytest.raises(aiohttp.ClientError):
            await _post(f"http://127.0.0.1:{port}/callback", b"{}", {})


class TestWaitingForDeliveries:
    async def test_wait_for_returns_once_the_predicate_holds(self):
        async with CallbackReceiver() as receiver:
            url = f"http://127.0.0.1:{receiver.port}{receiver.path}"

            async def send_later():
                await asyncio.sleep(0.05)
                await _post(url, b"{}", {})

            task = asyncio.create_task(send_later())
            satisfied = await receiver.wait_for(lambda d: len(d) == 1, timeout=5)
            await task

        assert satisfied  # noqa: B101

    async def test_wait_for_returns_immediately_when_already_satisfied(self):
        async with CallbackReceiver() as receiver:
            url = f"http://127.0.0.1:{receiver.port}{receiver.path}"
            await _post(url, b"{}", {})
            assert await receiver.wait_for(lambda d: len(d) == 1, timeout=0)  # noqa: B101

    async def test_a_delivery_landing_in_the_clear_window_is_not_missed(self):
        """The narrow race between evaluating the predicate and clearing.

        A delivery that lands in that window sets the event, the clear throws
        that wake-up away, and the wait then sleeps out its whole timeout
        before noticing a condition that was already true. It returned the
        right answer -- 300 seconds late on the paid run.
        """
        async with CallbackReceiver() as receiver:
            calls = {"n": 0}

            def predicate(deliveries):
                calls["n"] += 1
                if calls["n"] == 1:
                    # Reproduce the window exactly: append and signal after the
                    # predicate has been evaluated but before wait_for clears.
                    receiver._deliveries.append(  # noqa: SLF001
                        CallbackDelivery(
                            method="POST",
                            path="/callback",
                            headers={},
                            body=b"{}",
                            received_at=time.monotonic(),
                        )
                    )
                    receiver._event.set()  # noqa: SLF001
                    return False
                return len(deliveries) >= 1

            started = time.monotonic()
            satisfied = await receiver.wait_for(predicate, timeout=10)
            elapsed = time.monotonic() - started

        assert satisfied  # noqa: B101
        assert elapsed < 1  # noqa: B101

    async def test_wait_for_returns_false_on_timeout(self):
        """False rather than raising.

        The caller holds the deliveries and can say what did and did not
        arrive, which is worth more than "timed out".
        """
        async with CallbackReceiver() as receiver:
            assert not await receiver.wait_for(  # noqa: B101
                lambda d: len(d) == 1, timeout=0.2
            )


class TestTheHarnessEndToEndWithoutATunnel:
    async def test_a_simulated_server_run_satisfies_the_contract(self):
        """Replay what the server sends, through the receiver, into the checks.

        Everything the live check does except cross the internet. It is what
        catches a harness that broke between paid runs.
        """
        request_id = uuid.uuid4()
        asks = [AskMetaData()]
        headers = {
            "Content-Type": EXPECTED_CONTENT_TYPE,
            "User-Agent": EXPECTED_USER_AGENT,
            "X-Werk24-Callback-Check": "token",
        }

        def body(message_type, subtype, payload=None):
            return (
                TechreadMessage(
                    request_id=request_id,
                    message_type=message_type,
                    message_subtype=subtype,
                    payload_dict=payload,
                )
                .model_dump_json()
                .encode("utf-8")
            )

        async with CallbackReceiver() as receiver:
            url = f"http://127.0.0.1:{receiver.port}{receiver.path}"
            await _post(
                url,
                body(
                    TechreadMessageType.PROGRESS,
                    TechreadMessageSubtype.PROGRESS_STARTED,
                ),
                headers,
            )
            await _post(
                url,
                body(
                    TechreadMessageType.ASK,
                    "META_DATA",
                    ResponseMetaDataComponentDrawing().model_dump(mode="json"),
                ),
                headers,
            )
            await _post(
                url,
                body(
                    TechreadMessageType.PROGRESS,
                    TechreadMessageSubtype.PROGRESS_COMPLETED,
                ),
                headers,
            )

        messages = assert_callback_contract(
            receiver.deliveries,
            request_id=request_id,
            asks=asks,
            expected_path=receiver.path,
            expected_headers={"X-Werk24-Callback-Check": "token"},
        )
        assert len(messages) == 3  # noqa: B101


class TestDetectingTheTerminalMessage:
    """`_run_is_complete` decides when the paid end-to-end run stops waiting."""

    @staticmethod
    def _body(message_type, subtype, payload=None):
        return (
            TechreadMessage(
                request_id=uuid.uuid4(),
                message_type=message_type,
                message_subtype=subtype,
                payload_dict=payload,
            )
            .model_dump_json()
            .encode("utf-8")
        )

    def _delivery(self, body):
        return CallbackDelivery(
            method="POST",
            path="/callback",
            headers={},
            body=body,
            received_at=time.monotonic(),
        )

    def test_a_progress_completed_ends_the_wait(self):
        body = self._body(
            TechreadMessageType.PROGRESS,
            TechreadMessageSubtype.PROGRESS_COMPLETED,
        )
        assert _run_is_complete([self._delivery(body)])  # noqa: B101

    def test_an_error_message_ends_the_wait(self):
        body = self._body(
            TechreadMessageType.ERROR, TechreadMessageSubtype.ERROR_INTERNAL
        )
        assert _run_is_complete([self._delivery(body)])  # noqa: B101

    def test_a_started_does_not_end_the_wait(self):
        body = self._body(
            TechreadMessageType.PROGRESS,
            TechreadMessageSubtype.PROGRESS_STARTED,
        )
        assert not _run_is_complete([self._delivery(body)])  # noqa: B101

    def test_an_ask_payload_saying_completed_does_not_end_the_wait(self):
        """A drawing may legitimately carry the word as a field value.

        A raw scan of the body matched it, stopped the wait on the first ASK,
        and the contract then reported a PROGRESS/COMPLETED the server had
        been about to send. A spurious failure on a run that costs a read.
        """
        payload = ResponseMetaDataComponentDrawing().model_dump(mode="json")
        payload["designation"] = [
            {"reference_id": 0, "value": "COMPLETED", "language": None}
        ]
        body = self._body(TechreadMessageType.ASK, "META_DATA", payload)
        assert not _run_is_complete([self._delivery(body)])  # noqa: B101

    def test_a_malformed_terminal_body_still_ends_the_wait(self):
        """Otherwise the run that most needs reporting times out saying nothing."""
        assert _run_is_complete(  # noqa: B101
            [self._delivery(b'{"message_subtype":"COMPLETED", truncated')]
        )


class TestTheTunnelFailsLoudly:
    async def test_a_missing_binary_raises_rather_than_hanging(self, monkeypatch):
        """Forced through the env override, not by passing ``binary=None``.

        ``binary=None`` only means "discover it", so on any machine that has
        cloudflared on PATH -- the callback-check runner, or a developer box
        set up to run the live check -- this launched the real binary and
        asserted against the wrong error. Pointing the override at a path that
        does not exist makes discovery come back empty wherever it runs.
        """
        monkeypatch.setenv("W24_CLOUDFLARED_BIN", "/nonexistent/cloudflared")

        tunnel = QuickTunnel(port=1)
        with pytest.raises(TunnelUnavailable, match="cloudflared was not found"):
            async with tunnel:
                ...

    def test_an_override_pointing_nowhere_resolves_to_none(self, monkeypatch):
        monkeypatch.setenv("W24_CLOUDFLARED_BIN", "/nonexistent/cloudflared")
        assert cloudflared_binary() is None  # noqa: B101

    def test_the_override_takes_precedence_over_path(self, monkeypatch, tmp_path):
        binary = tmp_path / "cloudflared"
        binary.write_text("#!/bin/sh\n")
        monkeypatch.setenv("W24_CLOUDFLARED_BIN", str(binary))
        assert cloudflared_binary() == str(binary)  # noqa: B101

    async def test_a_binary_that_announces_nothing_times_out(self, tmp_path):
        """A tunnel that never comes up must fail, not hang the job."""
        binary = tmp_path / "quiet"
        binary.write_text("#!/bin/sh\nexec sleep 30\n")
        binary.chmod(0o755)

        tunnel = QuickTunnel(port=1, startup_timeout=1.0, binary=str(binary))
        with pytest.raises(TunnelUnavailable, match="did not announce"):
            async with tunnel:
                ...

    async def test_an_announced_hostname_that_never_answers_is_rejected(self, tmp_path):
        """The hostname is parsed, then disbelieved until it carries traffic.

        Cloudflare announces a hostname before the route is live, and handing
        that URL to the API inside the window would spend a billable read on a
        callback that could never be delivered. The fake below announces a
        hostname that will never answer, which is the same situation that
        never resolves.
        """
        binary = tmp_path / "announcer"
        binary.write_text(
            "#!/bin/sh\n"
            "echo '|  https://never-live-abcdef.trycloudflare.com   |'\n"
            "exec sleep 30\n"
        )
        binary.chmod(0o755)

        tunnel = QuickTunnel(
            port=1, startup_timeout=5.0, probe_floor=1.0, binary=str(binary)
        )
        with pytest.raises(TunnelUnavailable) as excinfo:
            async with tunnel:
                ...

        message = str(excinfo.value)
        assert "never carried traffic" in message  # noqa: B101

        # The banner is boxed, so the hostname has to be pulled back out of it.
        # Extracted and compared whole rather than asserted as a substring of
        # the message: a substring check passes on a URL that merely contains
        # the expected one, which would hide exactly the parsing bug this
        # asserts against (and is what CodeQL's incomplete-URL-sanitization
        # rule is about).
        announced = re.search(r"Tunnel (\S+) was announced", message)
        assert announced is not None, message  # noqa: B101
        assert (  # noqa: B101
            announced.group(1) == "https://never-live-abcdef.trycloudflare.com"
        )

    async def test_a_failing_binary_reports_its_output(self, tmp_path):
        """A process that dies on startup fails now, not at the timeout."""
        binary = tmp_path / "loud"
        binary.write_text(
            "#!/bin/sh\necho 'failed to connect to Cloudflare' >&2\nexit 1\n"
        )
        binary.chmod(0o755)

        tunnel = QuickTunnel(port=1, startup_timeout=30.0, binary=str(binary))
        started = time.monotonic()
        with pytest.raises(TunnelUnavailable) as excinfo:
            async with tunnel:
                ...
        elapsed = time.monotonic() - started

        assert "failed to connect to Cloudflare" in str(excinfo.value)  # noqa: B101
        assert "exited with code 1" in str(excinfo.value)  # noqa: B101
        assert elapsed < 10  # noqa: B101
