"""A callback read refuses, by name, a drawing its request cannot carry.

``read_drawing_with_callback`` posts the drawing inside a multipart body that
API Gateway base64-encodes into a synchronous Lambda invoke, and that invoke
takes at most 6 MiB. So the callback path tops out at about 4.6 MB of drawing
while ``read_drawing`` (a presigned upload) allows 10 MiB, and nothing in this
client checked either: a drawing in between failed at the gateway with an
error that named neither the limit nor the drawing (werk24-python#585).
"""

import io
import math
import pickle
import uuid
from unittest import mock

import aiohttp
import pytest

from werk24 import AskMetaData
from werk24.techread import (
    _CALLBACK_EVENT_RESERVE_BYTES,
    CALLBACK_INVOKE_LIMIT_BYTES,
    CALLBACK_MAX_BODY_BYTES,
    Werk24Client,
    _check_callback_body_size,
    _remaining_size,
)
from werk24.utils.exceptions import (
    CallbackDrawingTooLargeException,
    CallbackFieldsTooLargeException,
    RequestTooLargeException,
)

_PDF_HEADER = b"%PDF-1.7\n"


class _Response:
    status = 200

    async def json(self, content_type=None):
        return {"request_id": str(uuid.uuid4())}


class _ResponseContext:
    async def __aenter__(self):
        return _Response()

    async def __aexit__(self, *exc):
        return False


class _Session:
    def __init__(self):
        self.posts = 0
        self.data = None

    def post(self, url, data=None, headers=None):
        self.posts += 1
        self.data = data
        return _ResponseContext()

    async def close(self):
        pass

    @property
    def closed(self):
        return False


def _drawing(size: int) -> bytes:
    return _PDF_HEADER + b"0" * (size - len(_PDF_HEADER))


class _Pipe(io.RawIOBase):
    """A stream that cannot seek, so its size is unknowable up front."""

    def readable(self):
        return True

    def readinto(self, b):
        return 0


async def _submit(drawing, **kwargs):
    client = Werk24Client(token="t", region="r")
    session = _Session()
    with mock.patch.object(client, "_make_https_session", return_value=session):
        await client.read_drawing_with_callback(
            drawing,
            asks=[AskMetaData()],
            callback_url="https://example.com/webhook",
            **kwargs,
        )
    return session.posts


def test_the_limit_leaves_the_invoke_room_for_its_envelope():
    encoded = 4 * math.ceil(CALLBACK_MAX_BODY_BYTES / 3)
    assert encoded + _CALLBACK_EVENT_RESERVE_BYTES <= CALLBACK_INVOKE_LIMIT_BYTES
    # And it is not so tight that it refuses what the endpoint takes: the
    # assessment put the real ceiling at about 4.4 MB of drawing.
    assert CALLBACK_MAX_BODY_BYTES > 4_400_000


@pytest.mark.asyncio
class TestReadDrawingWithCallback:
    async def test_a_drawing_too_large_is_refused_before_anything_is_sent(self):
        size = CALLBACK_MAX_BODY_BYTES + 1
        client = Werk24Client(token="t", region="r")
        session = _Session()
        with mock.patch.object(client, "_make_https_session", return_value=session):
            with pytest.raises(CallbackDrawingTooLargeException) as caught:
                await client.read_drawing_with_callback(
                    _drawing(size),
                    asks=[AskMetaData()],
                    callback_url="https://example.com/webhook",
                )
        assert session.posts == 0
        assert caught.value.drawing_bytes == size
        assert 0 < caught.value.max_drawing_bytes < CALLBACK_MAX_BODY_BYTES
        # The message names the sizes and the way out.
        assert str(size) in str(caught.value)
        assert "read_drawing" in str(caught.value)

    async def test_it_is_still_a_request_too_large_exception(self):
        """Existing ``except RequestTooLargeException`` handlers keep working."""
        with pytest.raises(RequestTooLargeException):
            await _submit(_drawing(8 * 1024 * 1024))

    async def test_a_drawing_that_fits_is_sent(self):
        assert await _submit(_drawing(4_400_000)) == 1

    async def test_the_other_form_fields_count_against_the_same_body(self):
        size = 4_600_000
        assert await _submit(_drawing(size)) == 1
        big_headers = {f"X-Blob-{i}": "a" * 4000 for i in range(25)}
        with pytest.raises(CallbackDrawingTooLargeException):
            await _submit(_drawing(size), callback_headers=big_headers)

    async def test_a_file_is_measured_and_left_where_it_was(self, tmp_path):
        path = tmp_path / "large.pdf"
        path.write_bytes(_drawing(CALLBACK_MAX_BODY_BYTES + 1))
        with open(path, "rb") as fh:
            with pytest.raises(CallbackDrawingTooLargeException):
                await _submit(fh)
            assert fh.tell() == 0

    async def test_a_stream_that_cannot_seek_is_left_to_the_server(self):
        stream = io.BufferedReader(_Pipe())
        assert _remaining_size(stream) is None
        assert await _submit(stream) == 1

    @pytest.mark.parametrize(
        "make_drawing",
        [
            pytest.param(lambda: _drawing(1000), id="small"),
            pytest.param(lambda: b"", id="empty"),
            pytest.param(lambda: io.BufferedReader(_Pipe()), id="unseekable"),
        ],
    )
    async def test_fields_that_fill_the_body_are_named_not_the_drawing(
        self, make_drawing
    ):
        """With no room left for any drawing, the drawing is not what to fix.

        That holds for a drawing of any size, including one whose size is
        unknowable, so none of them may be sent or blamed for it.
        """
        headers = {f"X-Blob-{i}": "a" * 4000 for i in range(1200)}
        client = Werk24Client(token="t", region="r")
        session = _Session()
        with mock.patch.object(client, "_make_https_session", return_value=session):
            with pytest.raises(CallbackFieldsTooLargeException) as caught:
                await client.read_drawing_with_callback(
                    make_drawing(),
                    asks=[AskMetaData()],
                    callback_url="https://example.com/webhook",
                    callback_headers=headers,
                )
        assert session.posts == 0
        assert caught.value.fields_bytes >= CALLBACK_MAX_BODY_BYTES
        assert isinstance(caught.value, RequestTooLargeException)
        assert "callback_headers" in str(caught.value)


def test_a_file_counts_only_what_is_left_to_read():
    buffer = io.BytesIO(b"x" * 1000)
    buffer.seek(400)
    assert _remaining_size(buffer) == 600
    assert buffer.tell() == 400


def test_bytes_like_drawings_are_measured():
    assert _remaining_size(b"abc") == 3
    assert _remaining_size(bytearray(5)) == 5
    assert _remaining_size(memoryview(b"abcd")) == 4


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "drawing_filename",
    [
        "Zeichnung-\u00fc.pdf",
        # aiohttp percent-encodes the filename, so each of these 2000 UTF-8
        # bytes takes three on the wire.
        "\u00fc" * 1000 + ".pdf",
    ],
    ids=["short-non-ascii", "long-non-ascii"],
)
async def test_the_estimate_is_not_below_what_aiohttp_actually_sends(
    drawing_filename,
):
    """The check estimates the multipart framing; aiohttp must not exceed it.

    If it did, a body the check accepted could still be refused at the
    gateway. Find the largest drawing the method accepts, let the method
    build and post its form, and measure what aiohttp would put on the wire.
    """
    kwargs = dict(
        callback_headers={"Authorization": "Bearer x"},
        drawing_filename=drawing_filename,
    )
    with pytest.raises(CallbackDrawingTooLargeException) as caught:
        await _submit(_drawing(CALLBACK_MAX_BODY_BYTES), **kwargs)
    largest = caught.value.max_drawing_bytes

    client = Werk24Client(token="t", region="r")
    session = _Session()
    with mock.patch.object(client, "_make_https_session", return_value=session):
        await client.read_drawing_with_callback(
            _drawing(largest),
            asks=[AskMetaData()],
            callback_url="https://example.com/webhook",
            **kwargs,
        )
    assert session.posts == 1

    class _Collect:
        def __init__(self):
            self.size = 0

        async def write(self, chunk):
            self.size += len(chunk)

    sink = _Collect()
    await session.data().write(sink)
    assert sink.size <= CALLBACK_MAX_BODY_BYTES


def test_the_exception_survives_pickling():
    """So it can cross a process pool, as the other exceptions here can."""
    again = pickle.loads(pickle.dumps(CallbackDrawingTooLargeException(10, 5)))
    assert (again.drawing_bytes, again.max_drawing_bytes) == (10, 5)
    assert str(again) == str(CallbackDrawingTooLargeException(10, 5))

    again = pickle.loads(pickle.dumps(CallbackFieldsTooLargeException(10, 5)))
    assert (again.fields_bytes, again.max_body_bytes) == (10, 5)
    assert str(again) == str(CallbackFieldsTooLargeException(10, 5))
