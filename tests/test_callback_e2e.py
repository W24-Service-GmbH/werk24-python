"""End-to-end check that Werk24 callbacks are delivered, and are correct.

This is the check the repository did not have. ``test_client.py`` submits a
callback request to ``https://werk24.io`` and asserts a request id came back,
which proves the submission was accepted and nothing else -- that URL is on the
server's suppression list, so no callback is ever sent to it. Everything after
the submission has been unobserved.

What runs here instead: a receiver on loopback, a temporary public hostname in
front of it, a real drawing submitted against that hostname, and then every
callback the platform posts is held against the contract in
``tests.callback_check.contract``.

It costs one billable read per run and needs an outbound tunnel, so it is
marked ``callback_e2e`` and skips unless both credentials and ``cloudflared``
are present. The rules it enforces are themselves covered offline in
``test_callback_contract.py``; this module is only the part that needs the real
platform.
"""

from __future__ import annotations

import os
import uuid
from typing import Sequence

import pytest

from werk24 import (
    AskMetaData,
    TechreadMessageSubtype,
    Werk24Client,
    get_test_drawing,
)

from tests.callback_check import (
    CallbackDelivery,
    CallbackReceiver,
    QuickTunnel,
    assert_callback_contract,
    cloudflared_binary,
)


def _unavailable() -> str | None:
    """Why this check cannot run here, or None if it can.

    Separate from the skip mark so ``W24_CALLBACK_CHECK_REQUIRED`` can turn
    the same conditions into a failure. In CI a silent skip is the worst
    outcome available: a missing secret or a missing binary would otherwise
    produce a green check over a check that never ran, which is the exact
    shape of the problem this file exists to fix.
    """
    if not (
        os.getenv("W24TECHREAD_AUTH_TOKEN") and os.getenv("W24TECHREAD_AUTH_REGION")
    ):
        return (
            "Werk24 license credentials not provided "
            "(W24TECHREAD_AUTH_TOKEN, W24TECHREAD_AUTH_REGION)"
        )

    if cloudflared_binary() is None:
        return (
            "cloudflared not found; a callback needs a public URL. Install "
            "it or set W24_CLOUDFLARED_BIN"
        )

    return None


UNAVAILABLE = _unavailable()

REQUIRED = os.getenv("W24_CALLBACK_CHECK_REQUIRED") == "1"
"""Set by the workflow: refuse to skip, fail instead."""

pytestmark = [
    pytest.mark.callback_e2e,
    pytest.mark.integration,
    pytest.mark.requires_api,
    pytest.mark.slow,
    pytest.mark.skipif(
        UNAVAILABLE is not None and not REQUIRED,
        reason=UNAVAILABLE or "",
    ),
]

CALLBACK_TIMEOUT = float(os.getenv("W24_CALLBACK_TIMEOUT", "300"))
"""Seconds to wait for the read to finish and its last callback to land.

Generous on purpose. The wait ends as soon as PROGRESS/COMPLETED arrives, so
the only thing a large value costs is the time a genuinely broken run takes to
be declared broken.
"""

TUNNEL_TIMEOUT = float(os.getenv("W24_TUNNEL_TIMEOUT", "90"))


def _run_is_complete(deliveries: Sequence[CallbackDelivery]) -> bool:
    """True once a terminal message has arrived.

    Matched on the raw body rather than on a parsed message: whether the
    payload is well-formed is the contract's question, and a malformed
    terminal message must still end the wait -- otherwise the run that most
    needs reporting is the one that times out with nothing to say.
    """
    terminal = (
        f'"{TechreadMessageSubtype.PROGRESS_COMPLETED.value}"'.encode("utf-8"),
        b'"message_type":"ERROR"',
    )
    return any(
        any(token in delivery.body for token in terminal) for delivery in deliveries
    )


def _describe(deliveries: Sequence[CallbackDelivery]) -> str:
    """A readable account of what arrived, for a failure message."""
    if not deliveries:
        return "nothing was delivered"
    lines = []
    for index, delivery in enumerate(deliveries):
        preview = delivery.body[:200].decode("utf-8", "replace")
        lines.append(f"  [{index}] {delivery.method} {delivery.path} {preview}")
    return "\n".join(lines)


async def test_callbacks_are_delivered_and_valid():
    """Submit one drawing and hold every callback against the contract."""
    if UNAVAILABLE is not None:
        # Only reachable with W24_CALLBACK_CHECK_REQUIRED set; the skip mark
        # handles every other case.
        pytest.fail(f"The callback check was required but cannot run: {UNAVAILABLE}")

    asks = [AskMetaData()]

    # Echoed back by the server on every delivery. A fresh value per run, so a
    # callback from some other run -- a retry of a previous submission, say --
    # cannot be mistaken for this one's.
    correlation = uuid.uuid4().hex
    callback_headers = {"X-Werk24-Callback-Check": correlation}

    async with CallbackReceiver() as receiver:
        async with QuickTunnel(
            receiver.port,
            health_path=receiver.health_path,
            startup_timeout=TUNNEL_TIMEOUT,
        ) as tunnel:
            callback_url = f"{tunnel.url}{receiver.path}"

            async with Werk24Client() as client:
                request_id = await client.read_drawing_with_callback(
                    get_test_drawing(),
                    asks,
                    callback_url,
                    callback_headers=callback_headers,
                )

            delivered = await receiver.wait_for(
                _run_is_complete, timeout=CALLBACK_TIMEOUT
            )

    if not delivered:
        pytest.fail(
            f"Request {request_id} was accepted, but no terminal callback "
            f"reached {callback_url} within {CALLBACK_TIMEOUT:.0f}s.\n"
            f"What did arrive:\n{_describe(receiver.deliveries)}"
        )

    messages = assert_callback_contract(
        receiver.deliveries,
        request_id=request_id,
        asks=asks,
        expected_path=receiver.path,
        expected_headers=callback_headers,
    )

    # Reported on a pass as well as a failure: the run costs a read, and the
    # message count is the cheapest signal that the shape of a healthy run has
    # changed.
    print(  # noqa: T201
        f"\nRequest {request_id}: {len(messages)} callback(s) delivered "
        f"({', '.join(str(m.message_subtype.value) for m in messages)})"
    )
