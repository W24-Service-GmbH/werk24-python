import os
import uuid
from unittest.mock import AsyncMock, Mock

import aiohttp
import pytest

from werk24 import (
    AskMetaData,
    Hook,
    TechreadMessage,
    TechreadMessageSubtype,
    TechreadMessageType,
    Werk24Client,
    get_test_drawing,
)
from werk24.utils.exceptions import (
    BadRequestException,
    InsufficientCreditsException,
    InvalidLicenseException,
    RequestTooLargeException,
    ResourceNotFoundException,
    ServerException,
    UnauthorizedException,
    UnsupportedMediaType,
)

requires_license = pytest.mark.skipif(
    not (os.getenv("W24TECHREAD_AUTH_TOKEN") and os.getenv("W24TECHREAD_AUTH_REGION")),
    reason="Werk24 license credentials not provided",
)


@pytest.fixture
def drawing_bytes():
    return get_test_drawing()


@requires_license
@pytest.mark.asyncio
async def test_read_drawing(drawing_bytes):
    asks = [AskMetaData()]
    found_initialized = False
    found_started = False
    found_response = False
    found_completed = False
    async with Werk24Client() as client:
        async for msg in client.read_drawing(drawing_bytes, asks):
            if msg.message_type == TechreadMessageType.PROGRESS:
                if (
                    msg.message_subtype
                    == TechreadMessageSubtype.PROGRESS_INITIALIZATION_SUCCESS
                ):
                    found_initialized = True
                elif msg.message_subtype == TechreadMessageSubtype.PROGRESS_STARTED:
                    found_started = True
                elif msg.message_subtype == TechreadMessageSubtype.PROGRESS_COMPLETED:
                    found_completed = True
            elif msg.message_type == TechreadMessageType.ASK:
                found_response = True

    assert found_initialized  # noqa: B101
    assert found_started  # noqa: B101
    assert found_response  # noqa: B101
    assert found_completed  # noqa: B101


@requires_license
@pytest.mark.asyncio
async def test_read_drawing_with_hooks(drawing_bytes):
    hook = AsyncMock()

    hooks = [Hook(ask=AskMetaData(), function=hook)]
    async with Werk24Client() as client:
        await client.read_drawing_with_hooks(drawing_bytes, hooks)

    hook.assert_called_once()
    assert hook.call_args.args[0].message_type == TechreadMessageType.ASK


@requires_license
@pytest.mark.asyncio
async def test_read_drawing_with_callback(
    drawing_bytes, callback_url: str = "https://werk24.io"
):
    """The submission is accepted and returns a request id.

    That is the whole of it, and the URL is why: ``https://werk24.io`` is on
    the server's ``SUPPRESSED_CALLBACKS`` list, so no callback is ever posted
    to it. This test covers the *request* side of the callback endpoint and
    nothing about delivery -- deliberately, since a test asserting on delivery
    would need somewhere public to receive it.

    Delivery is checked in ``tests/test_callback_e2e.py``, which stands up a
    receiver behind a temporary tunnel and validates what actually arrives.
    """
    async with Werk24Client() as client:
        request_id = await client.read_drawing_with_callback(
            drawing_bytes, [AskMetaData()], callback_url
        )
    assert request_id is not None


@requires_license
@pytest.mark.asyncio
async def test_invalid_token():
    """
    Test that a bogus token raises an UnauthorizedException.
    """
    with pytest.raises(UnauthorizedException):
        async with Werk24Client(token="not-a-valid-token", region="eu-central-1"):
            ...


@pytest.mark.asyncio
async def test_empty_token():
    """
    Test that an empty token raises an InvalidLicenseException.
    """
    with pytest.raises(InvalidLicenseException):
        async with Werk24Client(token="", region=None):
            ...


@pytest.mark.asyncio
async def test_token_only_license():
    """
    Test that a client can be created with a token and no region, as issued
    during registration.
    """
    client = Werk24Client(token="some-token")
    assert client.license.token == "some-token"  # nosec
    assert client.license.region is None  # nosec


def test_run_preflight_checks_invalid_type():
    with pytest.raises(UnsupportedMediaType):
        Werk24Client.run_preflight_checks("not-bytes")


def test_get_hook_function_for_message_ask():
    ask = AskMetaData()
    hook_func = Mock()
    hook = Hook(ask=ask, function=hook_func)
    message = TechreadMessage(
        request_id=uuid.uuid4(),
        message_type=TechreadMessageType.ASK,
        message_subtype=ask.ask_type,
    )
    result = Werk24Client._get_hook_function_for_message(message, [hook])
    assert result is hook_func


def test_get_hook_function_for_message_no_match():
    hook = Hook(
        message_type=TechreadMessageType.PROGRESS,
        message_subtype=TechreadMessageSubtype.PROGRESS_COMPLETED,
        function=Mock(),
    )
    message = TechreadMessage(
        request_id=uuid.uuid4(),
        message_type=TechreadMessageType.PROGRESS,
        message_subtype=TechreadMessageSubtype.PROGRESS_STARTED,
    )
    assert Werk24Client._get_hook_function_for_message(message, [hook]) is None


@pytest.mark.asyncio
async def test_call_hooks_for_message_async():
    client = Werk24Client(token="t", region="r")
    message = TechreadMessage(
        request_id=uuid.uuid4(),
        message_type=TechreadMessageType.PROGRESS,
        message_subtype=TechreadMessageSubtype.PROGRESS_STARTED,
    )
    hook = Hook(
        message_type=TechreadMessageType.PROGRESS,
        message_subtype=TechreadMessageSubtype.PROGRESS_STARTED,
        function=AsyncMock(),
    )
    await client.call_hooks_for_message(message, [hook])
    hook.function.assert_awaited_once_with(message)


@pytest.mark.asyncio
async def test_call_hooks_for_message_sync():
    client = Werk24Client(token="t", region="r")
    message = TechreadMessage(
        request_id=uuid.uuid4(),
        message_type=TechreadMessageType.PROGRESS,
        message_subtype=TechreadMessageSubtype.PROGRESS_STARTED,
    )
    func = Mock()
    hook = Hook(
        message_type=TechreadMessageType.PROGRESS,
        message_subtype=TechreadMessageSubtype.PROGRESS_STARTED,
        function=func,
    )
    await client.call_hooks_for_message(message, [hook])
    func.assert_called_once_with(message)


def test_raise_for_status_ok():
    Werk24Client._raise_for_status("https://example.com", 200)


@pytest.mark.parametrize(
    "code,exc",
    [
        (400, BadRequestException),
        (401, UnauthorizedException),
        (404, ResourceNotFoundException),
        (413, RequestTooLargeException),
        (415, UnsupportedMediaType),
        (429, InsufficientCreditsException),
        (300, ServerException),
        (500, ServerException),
    ],
)
def test_raise_for_status_raises(code, exc):
    with pytest.raises(exc):
        Werk24Client._raise_for_status("https://example.com", code)


class _FakeS3Stream:
    """The ``content`` half of a response: a reader with a byte limit.

    ``read(n)`` answers at most ``n`` bytes, like aiohttp's ``StreamReader``,
    and records what it was asked for so a test can assert the read was
    bounded rather than trusting a slice applied afterwards.
    """

    def __init__(self, body: bytes, raises: bool = False):
        self._body = body
        self._raises = raises
        self.requested: list[int] = []

    async def read(self, n: int = -1) -> bytes:
        self.requested.append(n)
        if self._raises:
            raise aiohttp.ClientError("connection went away")
        return self._body if n < 0 else self._body[:n]


class _FakeS3Response:
    """An aiohttp-shaped response over a bounded stream."""

    def __init__(self, status: int, body: str = "", raises: bool = False):
        self.status = status
        self.content = _FakeS3Stream(body.encode("utf-8"), raises=raises)

    @property
    def reads(self) -> int:
        return len(self.content.requested)


_ENTITY_TOO_LARGE = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    "<Error><Code>EntityTooLarge</Code>"
    "<Message>Your proposed upload exceeds the maximum allowed size</Message>"
    "<ProposedSize>92160000</ProposedSize><MaxSizeAllowed>62914560</MaxSizeAllowed>"
    "</Error>"
)


@pytest.mark.asyncio
async def test_the_reason_s3_gives_reaches_the_exception():
    """"Could not interpret the request" is the same sentence for every
    refusal S3 answers with a 400. The body is what tells them apart."""
    response = _FakeS3Response(400, _ENTITY_TOO_LARGE)

    detail = await Werk24Client._s3_error_detail(response)
    assert detail == (
        "EntityTooLarge: Your proposed upload exceeds the maximum allowed size"
    )

    with pytest.raises(BadRequestException) as raised:
        Werk24Client._raise_for_status("https://example.com", 400, details=detail)
    assert "EntityTooLarge" in str(raised.value)
    assert "maximum allowed size" in str(raised.value)


@pytest.mark.asyncio
async def test_the_read_itself_is_bounded():
    """The limit has to bound the read, not just what is searched.

    Reading the whole body and slicing afterwards would leave an endpoint
    that answers with a large or never-ending 4xx body -- a proxy or an
    S3-compatible gateway in front of S3, not S3 itself -- allocating all of
    it or waiting for EOF, on the path that is already failing.
    """
    from werk24.techread import _S3_ERROR_BODY_LIMIT

    padding = "<Padding>" + ("x" * 10 * _S3_ERROR_BODY_LIMIT) + "</Padding>"
    response = _FakeS3Response(400, padding + _ENTITY_TOO_LARGE)

    await Werk24Client._s3_error_detail(response)

    assert response.content.requested == [_S3_ERROR_BODY_LIMIT]


@pytest.mark.asyncio
async def test_a_reason_past_the_limit_is_simply_not_found():
    """The other side of the bound, stated rather than left implied: a
    reason that sits past the limit is lost, and losing it costs the detail
    and nothing else. Only a body that is not an S3 error document in the
    first place can push the reason that far out."""
    from werk24.techread import _S3_ERROR_BODY_LIMIT

    padding = "<Padding>" + ("x" * 2 * _S3_ERROR_BODY_LIMIT) + "</Padding>"
    response = _FakeS3Response(400, padding + _ENTITY_TOO_LARGE)

    assert await Werk24Client._s3_error_detail(response) is None


@pytest.mark.asyncio
async def test_undecodable_bytes_do_not_cost_the_reason_or_raise():
    """A bounded read can end mid-character and a gateway can answer with
    bytes that are not UTF-8 at all. Decoding must not raise on this path,
    and the reason must survive whatever sat around it."""
    response = _FakeS3Response(400)
    response.content = _FakeS3Stream(
        b"\xff\xfe<Error><Code>EntityTooLarge</Code></Error>"
    )

    assert await Werk24Client._s3_error_detail(response) == "EntityTooLarge"


@pytest.mark.asyncio
async def test_a_tag_cut_in_half_by_the_limit_is_not_a_reason():
    """The bound can land inside the element it was looking for. A half-read
    tag names nothing, and guessing at the rest would put an invented reason
    in front of whoever reads the log line."""
    response = _FakeS3Response(400, "<Error><Code>EntityTooLar")

    assert await Werk24Client._s3_error_detail(response) is None


@pytest.mark.asyncio
async def test_a_successful_upload_does_not_read_the_body():
    """The happy path pays nothing: there is no reason to fetch, and S3
    answers a successful POST with an empty body anyway."""
    response = _FakeS3Response(204, "")
    assert await Werk24Client._s3_error_detail(response) is None
    assert response.reads == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "response",
    [
        _FakeS3Response(400, "", raises=True),
        _FakeS3Response(400, ""),
        _FakeS3Response(400, "<html><body>502 Bad Gateway</body></html>"),
        _FakeS3Response(400, "<Error><Code></Code></Error>"),
    ],
)
async def test_an_unreadable_refusal_leaves_the_old_message_alone(response):
    """This runs on a path that is already failing. A body that cannot be
    read, is not XML, or names nothing must cost the caller the detail and
    nothing else -- never replace the failure being reported with a new one."""
    assert await Werk24Client._s3_error_detail(response) is None

    with pytest.raises(BadRequestException) as raised:
        Werk24Client._raise_for_status("https://example.com", 400, details=None)
    # The exception's own prose wraps the detail line; what matters is that
    # the detail line is the one the caller had before, with nothing
    # half-read appended to it.
    assert str(raised.value).endswith(
        "Request failed 'https://example.com' with code 400"
    )
