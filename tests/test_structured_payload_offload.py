"""JSON offloads reach callers just like inline structured responses."""

import json
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from werk24 import (
    TechreadMessage,
    TechreadMessageType,
    TechreadMessageSubtype,
    W24AskType,
)
from werk24.models.v1.ask import W24AskProductPMIExtractResponse
from werk24.models.v2.responses import ResponseMetaDataComponentDrawing
from werk24.techread import Werk24Client


async def receive(
    monkeypatch, payload, encoding="json", subtype=W24AskType.PRODUCT_PMI_EXTRACT
):
    client = Werk24Client(token="t", region="r")
    request_id = uuid4()
    message = TechreadMessage(
        request_id=request_id,
        page_number=2,
        message_type=TechreadMessageType.ASK,
        message_subtype=subtype,
        payload_url="https://example.com/result",
        payload_encoding=encoding,
    )
    completed = TechreadMessage(
        request_id=request_id,
        message_type=TechreadMessageType.PROGRESS,
        message_subtype=TechreadMessageSubtype.PROGRESS_COMPLETED,
    )
    client._wss_session = type(
        "Session",
        (),
        {
            "recv": AsyncMock(
                side_effect=[message.model_dump_json(), completed.model_dump_json()]
            )
        },
    )()
    monkeypatch.setattr(client, "_send_command", AsyncMock())
    monkeypatch.setattr(client, "download_payload", AsyncMock(return_value=payload))
    return [message async for message in client._send_command_read()]


@pytest.mark.asyncio
async def test_large_json_restored_before_sync_http_discards_bytes(monkeypatch):
    payload = {"data": "ä" * (130 * 1024)}
    messages = await receive(monkeypatch, json.dumps(payload).encode())
    result = messages[0]
    assert result.payload_dict == payload
    assert result.payload_bytes is None
    assert result.page_number == 2
    result.payload_bytes = None  # crew-api's synchronous HTTP adapter
    assert result.model_dump(mode="json")["payload_dict"] == payload


@pytest.mark.asyncio
async def test_v2_response_uses_same_deserializer_as_inline(monkeypatch):
    payload = ResponseMetaDataComponentDrawing()
    messages = await receive(
        monkeypatch, payload.model_dump_json().encode(), subtype="META_DATA"
    )
    assert type(messages[0].payload_dict) is type(payload)
    assert messages[0].payload_dict == payload


@pytest.mark.asyncio
async def test_unmarked_json_file_stays_binary(monkeypatch):
    payload = b'{"data": "a downloadable JSON file"}'
    messages = await receive(monkeypatch, payload, encoding=None)
    assert messages[0].payload_bytes == payload
    assert messages[0].payload_dict is None


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [b"not json", b"[]", b"null"])
async def test_corrupt_offload_fails_instead_of_empty_success(monkeypatch, payload):
    with pytest.raises(ValueError):
        await receive(monkeypatch, payload)


@pytest.mark.asyncio
async def test_v1_pmi_response_uses_same_deserializer_as_inline(monkeypatch):
    payload = W24AskProductPMIExtractResponse(
        variant_id=uuid4(),
        material=None,
        general_tolerances=None,
        measures=[],
        gdts=[],
        radii=[],
        roughnesses=[],
    )
    messages = await receive(monkeypatch, payload.model_dump_json().encode())
    assert type(messages[0].payload_dict) is type(payload)
    assert messages[0].payload_dict == payload
