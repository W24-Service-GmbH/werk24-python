import io
from importlib.resources import files
from unittest.mock import patch

import pytest

from werk24 import (
    AskMetaData,
    Hook,
    TechreadMessageSubtype,
    TechreadMessageType,
    Werk24Client,
    get_test_drawing,
)

FILE_PATH = files("werk24") / "assets/DRAWING_SUCCESS.png"


@pytest.fixture
def drawing_bytes():
    return get_test_drawing()


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
                match msg.message_subtype:
                    case TechreadMessageSubtype.PROGRESS_INITIALIZATION_SUCCESS:
                        found_initialized = True
                    case TechreadMessageSubtype.PROGRESS_STARTED:
                        found_started = True
                    case TechreadMessageSubtype.PROGRESS_COMPLETED:
                        found_completed = True
            elif msg.message_type == TechreadMessageType.ASK:
                found_response = True

    assert found_initialized
    assert found_started
    assert found_response
    assert found_completed


@pytest.mark.asyncio
async def test_read_drawing_with_hooks(drawing_bytes):
    received = False

    def recv(msg):
        nonlocal received
        received = True

    hooks = [Hook(ask=AskMetaData(), function=recv)]
    async with Werk24Client() as client:
        await client.read_drawing_with_hooks(drawing_bytes, hooks)

    assert received


@pytest.mark.asyncio
async def test_read_drawing_with_callback(
    drawing_bytes, callback_url: str = "https://werk24.io"
):
    async with Werk24Client() as client:
        request_id = await client.read_drawing_with_callback(
            drawing_bytes, [AskMetaData()], callback_url
        )
    assert request_id is not None
