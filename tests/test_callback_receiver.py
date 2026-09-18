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


class TestTheTunnelFailsLoudly:
    async def test_a_missing_binary_raises_rather_than_hanging(self):
        tunnel = QuickTunnel(port=1, binary=None)
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
