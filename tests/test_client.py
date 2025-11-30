import os
import uuid
from unittest.mock import AsyncMock, Mock

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
    async with Werk24Client() as client:
        request_id = await client.read_drawing_with_callback(
            drawing_bytes, [AskMetaData()], callback_url
        )
    assert request_id is not None


@requires_license
@pytest.mark.asyncio
async def test_invalid_token():
    """
    Test that an empty token raises an UnauthorizedException.
    """
    with pytest.raises(UnauthorizedException):
        async with Werk24Client(token="", region="eu-central-1"):
            ...


@pytest.mark.asyncio
async def test_invalid_region():
    """
    Test that an empty region raises an InvalidLicenseException.
    """
    with pytest.raises(InvalidLicenseException):
        async with Werk24Client(token="", region=None):
            ...


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
