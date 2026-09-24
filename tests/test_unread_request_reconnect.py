"""A request that is never READ must not stay open on the reused connection.

crew-api#213 refuses a READ while more than one request on a WebSocket
connection is unread (``MultipleOpenRequests``) and closes the connection.
``Werk24Client`` keeps one connection for every ``read_drawing`` inside
``async with client:``, so any read that INITIALIZEs and then stops short of
READ - an upload S3 refuses, an exception, a cancellation, a caller that stops
iterating - would get the next read on that client refused, and that read's
result stream would end empty.

The fake connection below applies that rule the way crew-api does: a READ with
exactly one unread request on the connection takes it; anything else closes
the connection instead of answering. The socket is otherwise stubbed as in
``test_ask_validation_integration.py``: ``_connect_with_retry`` hands out a
new fake connection, so the tests can see which connection each command went
out on.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from websockets.exceptions import ConnectionClosedOK
from websockets.frames import Close

from werk24 import TechreadMessageSubtype, TechreadMessageType
from werk24.models.v2.asks import AskBalloons
from werk24.techread import Werk24Client
from werk24.utils.exceptions import (
    BadRequestException,
    EncryptionException,
    RequestTooLargeException,
    ServerException,
)

_CLOSED = object()


def _closed() -> ConnectionClosedOK:
    return ConnectionClosedOK(Close(1000, ""), Close(1000, ""), True)


def _message(request_id, message_type, subtype, payload=None) -> str:
    return json.dumps(
        {
            "request_id": str(request_id),
            "message_type": message_type,
            "message_subtype": subtype,
            "payload_dict": payload,
        }
    )


class _Connection:
    """One WebSocket connection to a crew-api that enforces #213."""

    def __init__(self, asks_per_read: int = 0):
        self.sent: list = []
        self.unread: list = []
        self.refused = False
        self.closed = False
        self._asks_per_read = asks_per_read
        self._outbox: asyncio.Queue = asyncio.Queue()

    async def send(self, raw: str) -> None:
        if self.closed:
            raise _closed()
        action = json.loads(raw)["action"]
        self.sent.append(action)

        if action == "INITIALIZE":
            request_id = uuid.uuid4()
            self.unread.append(request_id)
            self._outbox.put_nowait(
                _message(
                    request_id,
                    "PROGRESS",
                    "INITIALIZATION_SUCCESS",
                    {
                        "drawing_presigned_post": {
                            "url": "https://upload.example.com/",
                            "fields": {},
                        }
                    },
                )
            )
            return

        # READ. crew-api answers a refusal by closing the connection; the
        # client sees the close, not the 400 body.
        if len(self.unread) != 1:
            self.refused = True
            await self.close()
            return
        request_id = self.unread.pop()
        for _ in range(self._asks_per_read):
            self._outbox.put_nowait(_message(request_id, "ASK", "BALLOONS"))
        self._outbox.put_nowait(_message(request_id, "PROGRESS", "COMPLETED"))

    async def recv(self) -> str:
        item = await self._outbox.get()
        if item is _CLOSED:
            self._outbox.put_nowait(_CLOSED)
            raise _closed()
        return item

    async def close(self) -> None:
        if not self.closed:
            self.closed = True
            self._outbox.put_nowait(_CLOSED)


class _Harness:
    """A client whose connect hands out fake connections and whose upload
    succeeds unless told otherwise."""

    def __init__(self, asks_per_read: int = 0):
        self.client = Werk24Client(token="t", region="r")
        self.connections: list = []
        self.upload = AsyncMock(return_value=None)
        self._asks_per_read = asks_per_read

        async def connect():
            connection = _Connection(self._asks_per_read)
            self.connections.append(connection)
            self.client._wss_session = connection

        self.connect = AsyncMock(side_effect=connect)

    def patched(self, stub_shutdown: bool = True):
        stubs = {
            "_connect_with_retry": self.connect,
            "_upload_associated_file": self.upload,
        }
        if stub_shutdown:
            stubs["_graceful_shutdown"] = AsyncMock()
        return patch.multiple(self.client, **stubs)

    def read(self):
        return self.client.read_drawing(b"%PDF-1.7 drawing", [AskBalloons()])

    async def read_all(self) -> list:
        return [message async for message in self.read()]


def _completed(messages) -> list:
    return [
        m
        for m in messages
        if m.message_type == TechreadMessageType.PROGRESS
        and m.message_subtype == TechreadMessageSubtype.PROGRESS_COMPLETED
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "refusal",
    [
        RequestTooLargeException("EntityTooLarge"),
        BadRequestException("MalformedPOSTRequest"),
    ],
    ids=["too-large", "bad-request"],
)
async def test_a_failed_upload_reconnects_before_the_next_read(refusal):
    h = _Harness()
    h.upload.side_effect = [refusal, None]

    with h.patched():
        async with h.client:
            failed = await h.read_all()
            second = await h.read_all()

    # The failed read reports the refusal per ask, as before.
    assert [m.message_type for m in failed] == [
        TechreadMessageType.PROGRESS,
        TechreadMessageType.ASK,
    ]
    assert failed[1].exceptions

    # The next read is not refused. Without the reconnect crew-api sees two
    # unread requests on the connection, closes it, and the stream ends empty.
    assert not any(c.refused for c in h.connections)
    assert len(_completed(second)) == 1

    # Its request never got a READ; the connection carrying it was closed and
    # the next read went out on a new one, where it was the only request.
    assert h.connect.await_count == 2
    first, fresh = h.connections
    assert first.sent == ["INITIALIZE"]
    assert first.closed
    assert fresh.sent == ["INITIALIZE", "READ"]


@pytest.mark.asyncio
async def test_successful_reads_share_one_connection():
    h = _Harness()

    with h.patched():
        async with h.client:
            reads = [await h.read_all() for _ in range(3)]

    assert h.connect.await_count == 1
    (only,) = h.connections
    assert only.sent == ["INITIALIZE", "READ"] * 3
    assert not only.closed and not only.refused
    assert all(len(_completed(messages)) == 1 for messages in reads)


async def _upload_server_error(h):
    h.upload.side_effect = [ServerException("S3 answered 503 three times"), None]
    with pytest.raises(ServerException):
        await h.read_all()


async def _upload_encryption_error(h):
    h.upload.side_effect = [EncryptionException("bad key"), None]
    with pytest.raises(EncryptionException):
        await h.read_all()


async def _upload_cancelled(h):
    h.upload.side_effect = [asyncio.CancelledError(), None]
    with pytest.raises(asyncio.CancelledError):
        await h.read_all()


async def _caller_stops_after_initialize(h):
    # The generator is left suspended, not closed: its cleanup would run only
    # when the event loop finalizes it, after the next read has started.
    reader = h.read()
    await reader.__anext__()
    h.abandoned = reader


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "interrupt",
    [
        _upload_server_error,
        _upload_encryption_error,
        _upload_cancelled,
        _caller_stops_after_initialize,
    ],
    ids=["server-error", "encryption-error", "cancelled", "caller-stops"],
)
async def test_an_exit_between_initialize_and_read_leaves_the_next_read_on_a_fresh_connection(
    interrupt,
):
    h = _Harness()

    with h.patched():
        async with h.client:
            await interrupt(h)
            second = await h.read_all()

    assert not any(c.refused for c in h.connections)
    assert len(_completed(second)) == 1

    first, fresh = h.connections
    assert first.sent == ["INITIALIZE"]
    assert first.closed
    assert fresh.sent == ["INITIALIZE", "READ"]


@pytest.mark.asyncio
async def test_a_read_abandoned_mid_stream_does_not_hand_its_messages_to_the_next():
    # Two ASKs, so the caller holds the first while the second and the
    # PROGRESS_COMPLETED are still on the socket.
    h = _Harness(asks_per_read=2)

    with h.patched():
        async with h.client:
            async for message in h.read():
                if message.message_type == TechreadMessageType.ASK:
                    break
            second = await h.read_all()

    assert len(_completed(second)) == 1
    assert h.connect.await_count == 2
    assert h.connections[1].sent == ["INITIALIZE", "READ"]


@pytest.mark.asyncio
async def test_stopping_at_progress_completed_keeps_the_connection():
    h = _Harness()

    with h.patched():
        async with h.client:
            async for message in h.read():
                if _completed([message]):
                    break
            second = await h.read_all()

    assert h.connect.await_count == 1
    assert h.connections[0].sent == ["INITIALIZE", "READ"] * 2
    assert len(_completed(second)) == 1


@pytest.mark.asyncio
async def test_a_client_entered_again_still_reconnects():
    # The first exit runs the real shutdown, which sets _is_shutting_down;
    # _reconnect() is a no-op while that is set.
    h = _Harness()
    h.upload.side_effect = [None, RequestTooLargeException("EntityTooLarge"), None]

    with h.patched(stub_shutdown=False):
        async with h.client:
            await h.read_all()
        async with h.client:
            await h.read_all()
            second = await h.read_all()

    assert not any(c.refused for c in h.connections)
    assert len(_completed(second)) == 1
    assert [c.sent for c in h.connections] == [
        ["INITIALIZE", "READ"],
        ["INITIALIZE"],
        ["INITIALIZE", "READ"],
    ]


@pytest.mark.asyncio
async def test_an_overlapping_read_does_not_take_the_other_reads_request():
    """Two reads on one client, the second INITIALIZEd before the first READ.

    The second finds the first's request open and reconnects. The first must
    not then send its READ on the new connection: the only unread request
    there is the second's, and crew-api would hand it over.
    """
    h = _Harness()

    with h.patched():
        async with h.client:
            first = h.read()
            await first.__anext__()
            second = h.read()
            second_init = await second.__anext__()

            with pytest.raises(RuntimeError, match="must not overlap"):
                await first.__anext__()

            rest = [message async for message in second]

    fresh = h.connections[1]
    assert fresh.sent == ["INITIALIZE", "READ"]
    (completed,) = _completed(rest)
    assert completed.request_id == second_init.request_id


@pytest.mark.asyncio
async def test_a_client_that_was_never_entered_does_not_start_connecting():
    # Outside ``async with`` a read fails before INITIALIZE goes out. The flag
    # it leaves set must not make the next call open a socket nobody closes.
    h = _Harness()

    with h.patched():
        for _ in range(2):
            with pytest.raises(RuntimeError, match="Profile entry is required"):
                await h.read_all()

    h.connect.assert_not_awaited()
    assert h.connections == []


def _after_initialize(h, then):
    """Run *then* on the first connection right after it takes an INITIALIZE."""
    first = h.connections[0]
    original = first.send

    async def send(raw: str) -> None:
        await original(raw)
        if json.loads(raw)["action"] == "INITIALIZE":
            await then(first)

    first.send = send


async def _init_answer_lost(h):
    # The server took the request and the connection went before it answered.
    async def drop_answer_and_close(connection):
        connection._outbox.get_nowait()
        await connection.close()

    _after_initialize(h, drop_answer_and_close)
    with pytest.raises(ServerException):
        await h.read_all()


async def _init_answer_invalid(h):
    # The server took the request and answered with something that is not an
    # init response. The connection stays up with the request unread on it.
    async def replace_answer(connection):
        connection._outbox.get_nowait()
        connection._outbox.put_nowait(
            _message(connection.unread[-1], "PROGRESS", "INITIALIZATION_SUCCESS", {})
        )

    _after_initialize(h, replace_answer)
    with pytest.raises(ServerException, match="Unexpected server response"):
        await h.read_all()


async def _init_send_fails(h):
    # INITIALIZE never got out whole, so the client cannot know whether the
    # server holds the request.
    first = h.connections[0]
    original = first.send
    calls = []

    async def send(raw: str) -> None:
        calls.append(raw)
        if len(calls) == 1:
            raise OSError("network unreachable")
        await original(raw)

    first.send = send
    with pytest.raises(OSError):
        await h.read_all()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "fail_initialize",
    [_init_answer_lost, _init_answer_invalid, _init_send_fails],
    ids=["answer-lost", "answer-invalid", "send-fails"],
)
async def test_a_failed_initialize_leaves_the_next_read_on_a_fresh_connection(
    fail_initialize,
):
    """init_request() marks the request open before INITIALIZE goes out, so
    every failure inside it leaves the flag set and the next read reconnects
    first. The invalid answer is the case that matters most: the connection
    is still up and still carries the unread request, so reusing it would get
    the next READ refused."""
    h = _Harness()

    with h.patched():
        async with h.client:
            await fail_initialize(h)
            second = await h.read_all()

    assert not any(c.refused for c in h.connections)
    assert len(_completed(second)) == 1
    assert h.connect.await_count == 2
    first, fresh = h.connections
    assert first.closed
    assert fresh.sent == ["INITIALIZE", "READ"]
