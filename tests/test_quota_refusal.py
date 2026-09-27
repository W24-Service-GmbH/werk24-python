"""A used-up request quota has to reach the caller as InsufficientCreditsException.

When an account's request quota is used up, the API refuses the request on
the WebSocket in one of two shapes, depending on where the refusal happens:

- At INITIALIZE, it answers with a PROGRESS_COMPLETED message whose payload is
  ``{"message": "Limit Exceeded"}`` instead of an init response.
- At READ, it answers with the error envelope (``code``, ``message``,
  ``details``, ``request_id``), with ``details.error`` set to
  ``QUOTA_EXHAUSTED``.

Before, the first shape surfaced as a raw pydantic ``ValidationError`` about a
missing ``drawing_presigned_post``, which the CLI printed as a traceback. The
second surfaced as the generic ``ServerException`` that says the service team
has been notified and to try again later, and was logged at ERROR twice.

Now both raise ``InsufficientCreditsException``. It is still a
``ServerException``, so existing handlers keep catching it, but it is not a
``RetryableServerError``: waiting does not reset the quota. Its message says
so and how to top up, and the refusal is logged once, at WARNING.
"""

from __future__ import annotations

import importlib
import io
import json
import logging
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError
from rich.console import Console

from werk24 import AskMetaData, TechreadInitResponse
from werk24.techread import Werk24Client
from werk24.utils.exceptions import (
    InsufficientCreditsException,
    RetryableServerError,
    ServerException,
)

_DETAILS_MESSAGE = (
    "Your request quota is exhausted. This does not reset with time; please "
    "check your account balance and top up."
)


def _quota_envelope(limit=3, request_id="req-1") -> dict:
    """The error envelope the API sends at READ when the quota is used up."""
    return {
        "code": "429",
        "message": "Insufficient credits for this request.",
        "details": {
            "error": "QUOTA_EXHAUSTED",
            "message": _DETAILS_MESSAGE,
            "limit": limit,
        },
        "request_id": request_id,
    }


def _werk24_records(caplog, level: int) -> list:
    return [
        r for r in caplog.records if r.name.startswith("werk24") and r.levelno == level
    ]


def _quota_warnings(caplog) -> list:
    return [
        r for r in _werk24_records(caplog, logging.WARNING) if "quota" in r.getMessage()
    ]


class TestTheReadRefusal:
    """The error envelope the API answers READ with."""

    def test_the_envelope_raises_insufficient_credits(self):
        with pytest.raises(InsufficientCreditsException) as excinfo:
            Werk24Client._parse_message(json.dumps(_quota_envelope()))

        exc = excinfo.value
        assert isinstance(exc, ServerException)
        assert not isinstance(exc, RetryableServerError)
        assert exc.cli_message_header == "Insufficient Credits"
        text = str(exc)
        assert _DETAILS_MESSAGE in text
        assert "Request limit: 3" in text
        assert "Request ID: req-1" in text
        assert "has been notified" not in text
        assert "top up" in text

    def test_a_limit_of_zero_is_reported(self):
        with pytest.raises(InsufficientCreditsException) as excinfo:
            Werk24Client._parse_message(json.dumps(_quota_envelope(limit=0)))
        assert "Request limit: 0" in str(excinfo.value)

    def test_an_unlimited_limit_adds_no_limit_line(self):
        with pytest.raises(InsufficientCreditsException) as excinfo:
            Werk24Client._parse_message(json.dumps(_quota_envelope(limit="unlimited")))
        assert "Request limit" not in str(excinfo.value)

    def test_the_older_top_level_form_is_recognised(self):
        body = {"error": "QUOTA_EXHAUSTED", "message": "Quota used up."}
        with pytest.raises(InsufficientCreditsException) as excinfo:
            Werk24Client._parse_message(json.dumps(body))
        assert "Quota used up." in str(excinfo.value)

    def test_a_rate_limit_is_not_a_spent_quota(self):
        body = {
            "code": "429",
            "message": "Rate limit exceeded. Please try again later.",
            "details": {"retry_after": 60},
        }
        with pytest.raises(ServerException) as excinfo:
            Werk24Client._parse_message(json.dumps(body))
        assert not isinstance(excinfo.value, InsufficientCreditsException)

    def test_details_that_are_not_a_mapping_do_not_crash(self):
        body = {"code": "429", "message": "Refused.", "details": "not a dict"}
        with pytest.raises(ServerException) as excinfo:
            Werk24Client._parse_message(json.dumps(body))
        assert not isinstance(excinfo.value, InsufficientCreditsException)

    def test_it_is_logged_once_at_warning_and_never_at_error(self, caplog):
        caplog.set_level(logging.DEBUG, logger="werk24")

        with pytest.raises(InsufficientCreditsException):
            Werk24Client._parse_message(json.dumps(_quota_envelope()))

        assert len(_quota_warnings(caplog)) == 1
        assert _werk24_records(caplog, logging.ERROR) == []


def _client_answering_initialize(payload, subtype="COMPLETED", request_id=None):
    """A client whose socket answers INITIALIZE with one PROGRESS message."""
    request_id = request_id or str(uuid.uuid4())
    client = Werk24Client(token="t", region="r")
    client._wss_session = SimpleNamespace(
        send=AsyncMock(),
        recv=AsyncMock(
            return_value=json.dumps(
                {
                    "request_id": request_id,
                    "message_type": "PROGRESS",
                    "message_subtype": subtype,
                    "payload_dict": payload,
                }
            )
        ),
    )
    return client, request_id


class TestTheInitializeRefusal:
    """The PROGRESS_COMPLETED message the API answers INITIALIZE with."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "text", ["Limit Exceeded", "  limit exceeded "], ids=["as-sent", "padded"]
    )
    async def test_limit_exceeded_raises_insufficient_credits(self, text):
        client, request_id = _client_answering_initialize({"message": text})

        with pytest.raises(InsufficientCreditsException) as excinfo:
            await client.init_request([AskMetaData()], 1)

        assert not isinstance(excinfo.value, ValidationError)
        message = str(excinfo.value)
        assert text.strip() in message
        assert request_id in message
        # The request stays marked open, so the next read reconnects first.
        assert client._exchange_open is True

    @pytest.mark.asyncio
    async def test_the_quota_slug_is_recognised_at_initialize(self):
        client, request_id = _client_answering_initialize(
            {"error": "QUOTA_EXHAUSTED", "message": "x"}
        )

        with pytest.raises(InsufficientCreditsException) as excinfo:
            await client.init_request([AskMetaData()], 1)

        assert f"Request ID: {request_id}" in str(excinfo.value)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("empty", [None, ""], ids=["null", "empty-string"])
    async def test_an_empty_payload_request_id_keeps_the_messages(self, empty):
        client, request_id = _client_answering_initialize(
            {"error": "QUOTA_EXHAUSTED", "message": "x", "request_id": empty}
        )

        with pytest.raises(InsufficientCreditsException) as excinfo:
            await client.init_request([AskMetaData()], 1)

        assert f"Request ID: {request_id}" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_the_payloads_own_request_id_wins(self):
        client, request_id = _client_answering_initialize(
            {"error": "QUOTA_EXHAUSTED", "message": "x", "request_id": "req-9"}
        )

        with pytest.raises(InsufficientCreditsException) as excinfo:
            await client.init_request([AskMetaData()], 1)

        assert "Request ID: req-9" in str(excinfo.value)
        assert request_id not in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_it_is_logged_once_at_warning_and_never_at_error(self, caplog):
        caplog.set_level(logging.DEBUG, logger="werk24")
        client, _ = _client_answering_initialize({"message": "Limit Exceeded"})

        with pytest.raises(InsufficientCreditsException):
            await client.init_request([AskMetaData()], 1)

        assert len(_quota_warnings(caplog)) == 1
        assert _werk24_records(caplog, logging.ERROR) == []

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "payload",
        [None, {"message": "something else"}],
        ids=["no-payload", "other-message"],
    )
    async def test_any_other_answer_is_a_server_exception(self, payload):
        client, _ = _client_answering_initialize(payload)

        with pytest.raises(ServerException, match="INITIALIZE") as excinfo:
            await client.init_request([AskMetaData()], 1)

        assert not isinstance(excinfo.value, InsufficientCreditsException)
        assert not isinstance(excinfo.value, ValidationError)

    @pytest.mark.asyncio
    async def test_a_normal_answer_still_returns_the_init_response(self):
        client, request_id = _client_answering_initialize(
            {
                "drawing_presigned_post": {
                    "url": "https://upload.example.com/",
                    "fields": {},
                }
            },
            subtype="INITIALIZATION_SUCCESS",
        )

        message, init_response = await client.init_request([AskMetaData()], 1)

        assert str(message.request_id) == request_id
        assert isinstance(init_response, TechreadInitResponse)
        assert str(init_response.drawing_presigned_post.url) == (
            "https://upload.example.com/"
        )


def test_the_cli_shows_one_panel_and_no_traceback(monkeypatch):
    cli = importlib.import_module("werk24.cli.werk24")
    output = io.StringIO()

    def app():
        raise InsufficientCreditsException("x")

    monkeypatch.setattr(cli, "app", app)
    monkeypatch.setattr(cli, "console", Console(file=output, width=200))

    with pytest.raises(SystemExit) as excinfo:
        cli.main()

    assert excinfo.value.code == 1
    text = output.getvalue()
    assert "Insufficient Credits" in text
    assert "top up" in text
    assert "Traceback" not in text
    assert "has been notified" not in text
