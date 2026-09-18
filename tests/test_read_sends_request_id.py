"""READ sends back the request id INITIALIZE answered with.

The server has to find the request row again when READ arrives. Without the id
it queries `connection_id-index`, which is a GSI and so cannot be read
consistently: when the drawing upload finishes before the index has propagated
the row INITIALIZE wrote, the lookup comes back empty and the server sleeps
0.5s, then 1s, waiting for it.

`request_id` is that row's primary key, so sending it turns the lookup into one
strongly consistent read. See W24-Service-GmbH/crew-api#136 for the server half.

Pure unit tests: the websocket is a stand-in, nothing is sent anywhere.
"""

import uuid

import pytest

from werk24.techread import Werk24Client

REQUEST_ID = uuid.UUID("9f1d4d02-9f5f-4a4a-9c53-2a7e1f9b0c11")


class RecordingClient(Werk24Client):
    """Captures the READ payload instead of sending it."""

    def __init__(self):
        super().__init__(token="t", region="r")
        self.commands = []

    async def _send_command(self, action, message="{}"):
        self.commands.append((action, message))

    async def _recv_message(self):
        raise AssertionError("these tests stop at the send")


async def _read_payload(**kwargs):
    import json

    client = RecordingClient()
    generator = client._send_command_read(max_messages_per_session=0, **kwargs)
    try:
        async for _ in generator:
            break
    except AssertionError:
        pass
    finally:
        await generator.aclose()

    assert client.commands, "no command was sent"
    _, message = client.commands[-1]
    return json.loads(message)


@pytest.mark.asyncio
async def test_the_request_id_is_sent():
    payload = await _read_payload(request_id=REQUEST_ID)
    assert payload["request_id"] == str(REQUEST_ID)


@pytest.mark.asyncio
async def test_it_is_sent_as_a_string():
    """It travels as JSON; a UUID object is not serialisable."""
    payload = await _read_payload(request_id=REQUEST_ID)
    assert isinstance(payload["request_id"], str)
    assert uuid.UUID(payload["request_id"]) == REQUEST_ID


@pytest.mark.asyncio
async def test_no_id_sends_no_key():
    """The server falls back to its index, so an absent id must stay absent
    rather than arriving as a null it would have to special-case."""
    payload = await _read_payload()
    assert "request_id" not in payload


@pytest.mark.asyncio
async def test_it_does_not_displace_the_other_fields():
    payload = await _read_payload(request_id=REQUEST_ID, priority="prio3")
    assert payload["request_id"] == str(REQUEST_ID)
    assert payload["priority"] == "PRIO3"


def test_read_drawing_passes_the_id_it_was_answered_with():
    """The id sent must be the one from INITIALIZE, not a fresh one."""
    import inspect

    source = inspect.getsource(Werk24Client.read_drawing)
    assert "request_id=init_message.request_id" in source
