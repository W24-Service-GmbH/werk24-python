"""A drawing over the upload limit is refused before anything is sent.

``read_drawing`` uploads the drawing through a presigned upload that accepts
at most ``DRAWING_UPLOAD_LIMIT_BYTES``. It used to send INITIALIZE for a
drawing over that limit, upload the whole file, and let storage refuse it,
which was then logged at ERROR as a request the server "could not interpret".
Now the drawing is measured first:

- ``Werk24Client.check_drawing_size`` raises ``DrawingTooLargeException``;
- ``read_drawing`` sends nothing, logs one WARNING, and reports
  ``DRAWING_FILE_SIZE_TOO_LARGE`` on each ask, as documented;
- ``_upload_associated_file`` refuses what it would post over the limit
  (after encryption) and types a storage ``EntityTooLarge`` refusal;
- the CLI exits through its error panel before connecting.

Everything here is offline: the socket and the HTTPS session are fakes.
"""

from __future__ import annotations

import asyncio
import io
import json
import logging
import pickle
import uuid
from unittest.mock import AsyncMock, Mock, patch

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from typer.testing import CliRunner

import werk24.cli.commands.techread as techread_cli
from werk24 import (
    TechreadExceptionLevel,
    TechreadExceptionType,
    TechreadMessageSubtype,
    TechreadMessageType,
)
from werk24.models.v2.asks import AskBalloons, AskMetaData
from werk24.models.v2.internal import PresignedPost
from werk24.techread import DRAWING_UPLOAD_LIMIT_BYTES, Werk24Client
from werk24.utils.exceptions import (
    BadRequestException,
    DrawingTooLargeException,
    InvalidPriorityError,
    RequestTooLargeException,
    TechreadException,
)

LIMIT = DRAWING_UPLOAD_LIMIT_BYTES
DOCS = "v2.docs.werk24.io/limitations/file-size"

_CLOSED = object()


def _drawing(size: int) -> bytes:
    header = b"%PDF-1.7\n"
    return header + b"\0" * (size - len(header))


# ---------------------------------------------------------------------------
# A fake WebSocket connection and a client wired to it
# ---------------------------------------------------------------------------


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
    """Answers INITIALIZE with an upload target and READ with COMPLETED."""

    def __init__(self):
        self.sent: list = []
        self.closed = False
        self._outbox: asyncio.Queue = asyncio.Queue()

    async def send(self, raw: str) -> None:
        action = json.loads(raw)["action"]
        self.sent.append(action)
        request_id = uuid.uuid4()
        if action == "INITIALIZE":
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
        elif action == "READ":
            self._outbox.put_nowait(_message(request_id, "PROGRESS", "COMPLETED"))

    async def recv(self) -> str:
        item = await self._outbox.get()
        if item is _CLOSED:
            self._outbox.put_nowait(_CLOSED)
            raise ConnectionError("closed")
        return item

    async def close(self) -> None:
        if not self.closed:
            self.closed = True
            self._outbox.put_nowait(_CLOSED)


class _Harness:
    def __init__(self):
        self.client = Werk24Client(token="t", region="r")
        self.connections: list = []
        self.upload = AsyncMock(return_value=None)

        async def connect():
            connection = _Connection()
            self.connections.append(connection)
            self.client._wss_session = connection

        self.connect = AsyncMock(side_effect=connect)

    def patched(self):
        return patch.multiple(
            self.client,
            _connect_with_retry=self.connect,
            _graceful_shutdown=AsyncMock(),
            _upload_associated_file=self.upload,
        )

    async def read_all(self, drawing, asks=None, **kwargs) -> list:
        asks = asks if asks is not None else [AskBalloons()]
        return [
            message
            async for message in self.client.read_drawing(drawing, asks, **kwargs)
        ]


def _werk24_records(caplog, min_level=logging.WARNING) -> list:
    return [
        r
        for r in caplog.records
        if r.name.startswith("werk24") and r.levelno >= min_level
    ]


def _assert_size_refusal_per_ask(messages, asks) -> None:
    assert [m.message_type for m in messages] == [TechreadMessageType.PROGRESS] + [
        TechreadMessageType.ASK
    ] * len(asks)
    for message, ask in zip(messages[1:], asks):
        assert message.message_subtype == ask.ask_type
        (exception,) = message.exceptions
        assert (
            exception.exception_type
            == TechreadExceptionType.DRAWING_FILE_SIZE_TOO_LARGE
        )
        assert exception.exception_level == TechreadExceptionLevel.ERROR


# ---------------------------------------------------------------------------
# The constant and check_drawing_size
# ---------------------------------------------------------------------------


def test_the_limit_is_ten_mebibytes():
    assert DRAWING_UPLOAD_LIMIT_BYTES == 10 * 1024 * 1024 == 10_485_760


def test_one_byte_over_the_limit_is_refused_and_the_limit_itself_is_not():
    with pytest.raises(DrawingTooLargeException) as raised:
        Werk24Client.check_drawing_size(_drawing(LIMIT + 1))
    assert raised.value.drawing_bytes == LIMIT + 1
    assert raised.value.max_drawing_bytes == LIMIT

    # The signed policy's range is inclusive.
    assert Werk24Client.check_drawing_size(_drawing(LIMIT)) == LIMIT


def test_the_limit_is_read_when_the_check_runs(monkeypatch):
    """The limit follows the module constant rather than being frozen into
    a default argument when the class was defined."""
    import werk24.techread as techread

    monkeypatch.setattr(techread, "DRAWING_UPLOAD_LIMIT_BYTES", 100)
    with pytest.raises(DrawingTooLargeException) as raised:
        Werk24Client.check_drawing_size(_drawing(101))
    assert raised.value.max_drawing_bytes == 100
    assert Werk24Client.check_drawing_size(_drawing(100)) == 100


def test_a_file_is_measured_from_its_position_which_is_restored(tmp_path):
    stream = io.BytesIO(_drawing(1000))
    stream.seek(5)
    assert Werk24Client.check_drawing_size(stream) == 995
    assert stream.tell() == 5

    path = tmp_path / "drawing.pdf"
    path.write_bytes(_drawing(1000))
    with open(path, "rb") as fid:
        fid.seek(5)
        assert Werk24Client.check_drawing_size(fid) == 995
        assert fid.tell() == 5


class _Pipe(io.RawIOBase):
    """A raw stream that cannot seek, like a pipe or a socket."""

    def __init__(self, data: bytes):
        self._data = data
        self.position = 0

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return False

    def readinto(self, buffer) -> int:
        chunk = self._data[self.position : self.position + len(buffer)]
        buffer[: len(chunk)] = chunk
        self.position += len(chunk)
        return len(chunk)


def test_a_stream_that_cannot_seek_is_not_measured_or_consumed():
    pipe = _Pipe(_drawing(LIMIT + 1))
    reader = io.BufferedReader(pipe)

    assert Werk24Client.check_drawing_size(reader) is None
    assert pipe.position == 0


# ---------------------------------------------------------------------------
# The exception
# ---------------------------------------------------------------------------


def test_the_exception_is_caught_by_the_existing_handlers():
    refusal = DrawingTooLargeException(LIMIT + 1, LIMIT)
    assert isinstance(refusal, RequestTooLargeException)
    assert isinstance(refusal, TechreadException)


def test_the_exception_is_exported_from_the_package():
    from werk24 import DrawingTooLargeException as exported

    assert exported is DrawingTooLargeException


def test_the_exception_survives_pickling():
    refusal = DrawingTooLargeException(LIMIT + 1, LIMIT)
    restored = pickle.loads(pickle.dumps(refusal))

    assert type(restored) is DrawingTooLargeException
    assert restored.drawing_bytes == refusal.drawing_bytes
    assert restored.max_drawing_bytes == refusal.max_drawing_bytes
    assert str(restored) == str(refusal)


def test_the_message_names_both_sizes_and_the_docs():
    text = str(DrawingTooLargeException(LIMIT + 1, LIMIT))
    assert str(LIMIT + 1) in text
    assert str(LIMIT) in text
    assert "limitations/file-size" in text


def test_the_cli_header():
    assert DrawingTooLargeException.cli_message_header == "Drawing Too Large"


# ---------------------------------------------------------------------------
# read_drawing: the preflight
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_an_oversized_drawing_is_not_sent_and_each_ask_reports_it(caplog):
    caplog.set_level(logging.DEBUG, logger="werk24")
    h = _Harness()
    asks = [AskBalloons(), AskMetaData()]

    with h.patched():
        async with h.client:
            messages = await h.read_all(_drawing(LIMIT + 1), asks)

    assert [m.message_type for m in messages] == [
        TechreadMessageType.PROGRESS,
        TechreadMessageType.ASK,
        TechreadMessageType.ASK,
    ]
    opening = messages[0]
    assert (
        opening.message_subtype
        == TechreadMessageSubtype.PROGRESS_INITIALIZATION_SUCCESS
    )
    assert opening.payload_dict is None
    assert opening.exceptions == []
    _assert_size_refusal_per_ask(messages, asks)

    # Nothing reached the server: no INITIALIZE, no upload.
    (connection,) = h.connections
    assert connection.sent == []
    h.upload.assert_not_awaited()

    # One WARNING that says what happened and where to read about it.
    (record,) = _werk24_records(caplog)
    assert record.levelno == logging.WARNING
    text = record.getMessage()
    assert str(LIMIT + 1) in text
    assert str(LIMIT) in text
    assert DOCS in text
    assert not _werk24_records(caplog, logging.ERROR)


@pytest.mark.asyncio
async def test_a_drawing_of_exactly_the_limit_is_sent():
    h = _Harness()

    with h.patched():
        async with h.client:
            await h.read_all(_drawing(LIMIT))

    (connection,) = h.connections
    assert connection.sent == ["INITIALIZE", "READ"]
    h.upload.assert_awaited_once()


@pytest.mark.asyncio
async def test_the_next_read_reuses_the_connection_after_a_preflight_refusal():
    """No INITIALIZE went out, so no request is left unread, and the next
    read has no reason to reconnect."""
    h = _Harness()

    with h.patched():
        async with h.client:
            await h.read_all(_drawing(LIMIT + 1))
            second = await h.read_all(_drawing(1000))

    assert second[-1].message_subtype == TechreadMessageSubtype.PROGRESS_COMPLETED
    assert h.connect.await_count == 1
    (connection,) = h.connections
    assert connection.sent == ["INITIALIZE", "READ"]


@pytest.mark.asyncio
async def test_an_invalid_priority_still_raises_before_the_size_check():
    h = _Harness()

    with h.patched():
        async with h.client:
            with pytest.raises(InvalidPriorityError):
                await h.read_all(_drawing(LIMIT + 1), priority="PRIO9")

    (connection,) = h.connections
    assert connection.sent == []


# ---------------------------------------------------------------------------
# read_drawing: a refusal from the upload itself
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_an_upload_refused_for_its_size_is_one_warning(caplog):
    caplog.set_level(logging.DEBUG, logger="werk24")
    h = _Harness()
    h.upload.side_effect = DrawingTooLargeException(LIMIT + 60, LIMIT)
    asks = [AskBalloons(), AskMetaData()]

    with h.patched():
        async with h.client:
            messages = await h.read_all(_drawing(1000), asks)

    _assert_size_refusal_per_ask(messages, asks)
    (record,) = _werk24_records(caplog)
    assert record.levelno == logging.WARNING
    assert record.getMessage().startswith("Drawing upload refused")
    assert str(LIMIT + 60) in record.getMessage()
    assert not _werk24_records(caplog, logging.ERROR)


@pytest.mark.asyncio
async def test_any_other_upload_refusal_is_still_an_error(caplog):
    caplog.set_level(logging.DEBUG, logger="werk24")
    h = _Harness()
    h.upload.side_effect = BadRequestException("x")

    with h.patched():
        async with h.client:
            messages = await h.read_all(_drawing(1000))

    _assert_size_refusal_per_ask(messages, [AskBalloons()])
    errors = _werk24_records(caplog, logging.ERROR)
    assert any(
        r.getMessage().startswith("Error during drawing upload") for r in errors
    )


# ---------------------------------------------------------------------------
# _upload_associated_file
# ---------------------------------------------------------------------------

_POST = PresignedPost(url="https://upload.example.com/", fields={})

_ENTITY_TOO_LARGE = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    "<Error><Code>EntityTooLarge</Code>"
    "<Message>Your proposed upload exceeds the maximum allowed size</Message>"
    "<ProposedSize>6291456</ProposedSize>"
    "{max_size}"
    "</Error>"
)


class _Body:
    def __init__(self, body: bytes):
        self._body = body
        self.reads = 0

    async def read(self, n: int = -1) -> bytes:
        self.reads += 1
        return self._body if n < 0 else self._body[:n]


class _Response:
    def __init__(self, status: int, body: str = ""):
        self.status = status
        self.content = _Body(body.encode("utf-8"))


class _Posting:
    def __init__(self, response: _Response):
        self._response = response

    async def __aenter__(self) -> _Response:
        return self._response

    async def __aexit__(self, *exc_info) -> bool:
        return False


class _Session:
    def __init__(self, response: _Response):
        self.response = response
        self.posts = 0

    def post(self, url, data=None):
        self.posts += 1
        return _Posting(self.response)


async def _upload(client, session, content, **kwargs):
    with patch.object(client, "_https_session", return_value=session):
        await client._upload_associated_file(_POST, content, **kwargs)


def _x25519_public_pem() -> bytes:
    return (
        x25519.X25519PrivateKey.generate()
        .public_key()
        .public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


@pytest.mark.asyncio
async def test_encryption_that_pushes_a_drawing_over_the_limit_is_caught():
    """X25519 adds 60 bytes (ephemeral key, IV and tag), so a drawing ten
    bytes under the limit is fifty over it by the time it would be posted."""
    client = Werk24Client(token="t", region="r")
    session = _Session(_Response(204))

    with pytest.raises(DrawingTooLargeException) as raised:
        await _upload(
            client,
            session,
            _drawing(LIMIT - 10),
            public_server_key=_x25519_public_pem(),
        )

    assert raised.value.drawing_bytes == LIMIT + 50
    assert raised.value.max_drawing_bytes == LIMIT
    assert session.posts == 0


@pytest.mark.asyncio
async def test_a_stream_that_could_not_be_measured_is_caught_before_posting():
    client = Werk24Client(token="t", region="r")
    session = _Session(_Response(204))
    reader = io.BufferedReader(_Pipe(_drawing(LIMIT + 1)))

    with pytest.raises(DrawingTooLargeException) as raised:
        await _upload(client, session, reader)

    assert raised.value.drawing_bytes == LIMIT + 1
    assert session.posts == 0


@pytest.mark.asyncio
async def test_a_storage_size_refusal_is_typed_with_the_limit_it_names(caplog):
    caplog.set_level(logging.DEBUG, logger="werk24")
    client = Werk24Client(token="t", region="r")
    body = _ENTITY_TOO_LARGE.format(
        max_size="<MaxSizeAllowed>5242880</MaxSizeAllowed>"
    )
    session = _Session(_Response(400, body))
    payload = _drawing(6 * 1024 * 1024)

    with pytest.raises(DrawingTooLargeException) as raised:
        await _upload(client, session, payload)

    assert raised.value.max_drawing_bytes == 5242880
    assert raised.value.drawing_bytes == len(payload)
    # Not retried, and not logged as a failed upload.
    assert session.posts == 1
    assert not any(
        "File upload failed" in r.getMessage()
        for r in _werk24_records(caplog, logging.ERROR)
    )


@pytest.mark.asyncio
async def test_a_storage_size_refusal_without_a_limit_falls_back_to_ours():
    client = Werk24Client(token="t", region="r")
    session = _Session(_Response(400, _ENTITY_TOO_LARGE.format(max_size="")))

    with pytest.raises(DrawingTooLargeException) as raised:
        await _upload(client, session, _drawing(1000))

    assert raised.value.max_drawing_bytes == DRAWING_UPLOAD_LIMIT_BYTES
    assert raised.value.drawing_bytes == 1000


@pytest.mark.asyncio
async def test_any_other_storage_refusal_is_still_a_bad_request():
    client = Werk24Client(token="t", region="r")
    body = (
        "<Error><Code>MalformedPOSTRequest</Code>"
        "<Message>The body of your POST request is not well-formed</Message>"
        "</Error>"
    )
    session = _Session(_Response(400, body))

    with pytest.raises(BadRequestException) as raised:
        await _upload(client, session, _drawing(1000))

    assert not isinstance(raised.value, DrawingTooLargeException)
    assert "MalformedPOSTRequest" in str(raised.value)


@pytest.mark.asyncio
async def test_an_accepted_upload_succeeds_without_reading_the_body():
    client = Werk24Client(token="t", region="r")
    session = _Session(_Response(204))

    await _upload(client, session, _drawing(1000))

    assert session.posts == 1
    assert session.response.content.reads == 0


# ---------------------------------------------------------------------------
# The CLI
# ---------------------------------------------------------------------------


def test_the_cli_refuses_an_oversized_drawing_before_connecting(
    tmp_path, monkeypatch
):
    path = tmp_path / "drawing.pdf"
    with open(path, "wb") as fid:
        fid.truncate(LIMIT + 1)
    run = Mock()
    monkeypatch.setattr(techread_cli, "run", run)

    result = CliRunner().invoke(techread_cli.app, [str(path), "--ask-meta-data"])

    assert isinstance(result.exception, DrawingTooLargeException)
    run.assert_not_called()
