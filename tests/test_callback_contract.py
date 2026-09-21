"""Tests for the callback contract checks themselves.

These run everywhere, with no credentials and no network. They exist because
the end-to-end check in ``test_callback_e2e.py`` costs a billable read and
needs a tunnel, so it cannot be the thing that proves the rules are right: a
checker that quietly accepts everything would pass that test just as happily
as a correct one. Each test here breaks exactly one rule and asserts it is
reported.
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Any, Dict, List, Sequence

import pytest

from werk24 import (
    AskMetaData,
    TechreadMessage,
    TechreadMessageSubtype,
    TechreadMessageType,
)
from werk24.models.v2.enums import TechreadExceptionLevel
from werk24.models.v2.internal import (
    TechreadException,
    TechreadExceptionType,
)
from werk24.models.v2.responses import ResponseMetaDataComponentDrawing

from tests.callback_check import (
    CallbackContractError,
    CallbackDelivery,
    assert_callback_contract,
)
from tests.callback_check.contract import (
    EXPECTED_CONTENT_TYPE,
    EXPECTED_USER_AGENT,
)

PATH = "/callback"
HEADERS = {"X-Werk24-Callback-Check": "correlation-token"}

REQUEST_ID = uuid.UUID("11111111-2222-4333-8444-555555555555")


def _delivery(
    body: bytes,
    *,
    path: str = PATH,
    method: str = "POST",
    headers: Dict[str, str] | None = None,
) -> CallbackDelivery:
    """A recorded delivery carrying ``body``, correct in every other respect."""
    wire = {
        "content-type": EXPECTED_CONTENT_TYPE,
        "user-agent": EXPECTED_USER_AGENT,
        **{k.lower(): v for k, v in HEADERS.items()},
    }
    wire.update(headers or {})
    return CallbackDelivery(
        method=method,
        path=path,
        headers=wire,
        body=body,
        received_at=time.monotonic(),
    )


def _message(
    message_type: TechreadMessageType,
    message_subtype: Any,
    payload_dict: Any = None,
    exceptions: Sequence[TechreadException] = (),
    request_id: uuid.UUID = REQUEST_ID,
) -> bytes:
    """Serialise a message exactly the way the server puts it on the wire."""
    return (
        TechreadMessage(
            request_id=request_id,
            message_type=message_type,
            message_subtype=message_subtype,
            payload_dict=payload_dict,
            exceptions=list(exceptions),
        )
        .model_dump_json()
        .encode("utf-8")
    )


def _started() -> CallbackDelivery:
    return _delivery(
        _message(
            TechreadMessageType.PROGRESS,
            TechreadMessageSubtype.PROGRESS_STARTED,
        )
    )


def _ask(payload: Any = None) -> CallbackDelivery:
    if payload is None:
        payload = ResponseMetaDataComponentDrawing().model_dump(mode="json")
    return _delivery(
        _message(TechreadMessageType.ASK, "META_DATA", payload_dict=payload)
    )


def _completed() -> CallbackDelivery:
    return _delivery(
        _message(
            TechreadMessageType.PROGRESS,
            TechreadMessageSubtype.PROGRESS_COMPLETED,
        )
    )


def _good_run() -> List[CallbackDelivery]:
    """The delivery sequence a healthy read produces."""
    return [_started(), _ask(), _completed()]


def _check(deliveries: Sequence[CallbackDelivery]) -> List[TechreadMessage]:
    return assert_callback_contract(
        deliveries,
        request_id=REQUEST_ID,
        asks=[AskMetaData()],
        expected_path=PATH,
        expected_headers=HEADERS,
    )


def _problems(deliveries: Sequence[CallbackDelivery]) -> List[str]:
    with pytest.raises(CallbackContractError) as excinfo:
        _check(deliveries)
    return excinfo.value.problems


class TestAHealthyRunPasses:
    def test_a_complete_sequence_is_accepted(self):
        messages = _check(_good_run())
        assert len(messages) == 3  # noqa: B101

    def test_the_parsed_messages_are_returned_in_arrival_order(self):
        messages = _check(_good_run())
        assert [m.message_type for m in messages] == [  # noqa: B101
            TechreadMessageType.PROGRESS,
            TechreadMessageType.ASK,
            TechreadMessageType.PROGRESS,
        ]

    def test_an_ask_that_only_carries_a_payload_url_is_accepted(self):
        body = json.loads(
            _message(TechreadMessageType.ASK, "META_DATA").decode("utf-8")
        )
        body["payload_url"] = "https://example.com/payload.png"
        deliveries = [
            _started(),
            _delivery(json.dumps(body).encode("utf-8")),
            _completed(),
        ]
        _check(deliveries)


class TestTheTransportIsChecked:
    def test_nothing_delivered_is_reported_as_such(self):
        problems = _problems([])
        assert len(problems) == 1  # noqa: B101
        assert "no callback was delivered at all" in problems[0]  # noqa: B101

    def test_a_wrong_content_type_is_reported(self):
        deliveries = _good_run()
        deliveries[1] = _ask()
        deliveries[1] = _delivery(
            deliveries[1].body, headers={"content-type": "text/plain"}
        )
        assert any("Content-Type" in p for p in _problems(deliveries))  # noqa: B101

    def test_a_content_type_with_a_charset_is_accepted(self):
        deliveries = _good_run()
        deliveries[1] = _delivery(
            deliveries[1].body,
            headers={"content-type": "application/json; charset=utf-8"},
        )
        _check(deliveries)

    def test_a_wrong_user_agent_is_reported(self):
        deliveries = _good_run()
        deliveries[1] = _delivery(
            deliveries[1].body, headers={"user-agent": "curl/8.0"}
        )
        assert any("User-Agent" in p for p in _problems(deliveries))  # noqa: B101

    def test_a_dropped_callback_header_is_reported(self):
        deliveries = _good_run()
        stripped = {
            k: v
            for k, v in deliveries[1].headers.items()
            if k != "x-werk24-callback-check"
        }
        deliveries[1] = CallbackDelivery(
            method="POST",
            path=PATH,
            headers=stripped,
            body=deliveries[1].body,
            received_at=time.monotonic(),
        )
        problems = _problems(deliveries)
        assert any(  # noqa: B101
            "X-Werk24-Callback-Check" in p and "None" in p for p in problems
        )

    def test_a_callback_header_delivered_with_a_different_value_is_reported(self):
        deliveries = _good_run()
        deliveries[1] = _delivery(
            deliveries[1].body, headers={"x-werk24-callback-check": "wrong"}
        )
        assert any(  # noqa: B101
            "X-Werk24-Callback-Check" in p for p in _problems(deliveries)
        )

    def test_a_post_to_the_wrong_path_is_reported(self):
        deliveries = _good_run()
        deliveries[1] = _delivery(deliveries[1].body, path="/elsewhere")
        assert any("/elsewhere" in p for p in _problems(deliveries))  # noqa: B101

    def test_a_non_post_method_is_reported(self):
        deliveries = _good_run()
        deliveries[1] = _delivery(deliveries[1].body, method="PUT")
        assert any("expected POST" in p for p in _problems(deliveries))  # noqa: B101


class TestTheBodyIsChecked:
    def test_a_body_that_is_not_json_is_reported(self):
        deliveries = [_started(), _delivery(b"<html>502</html>"), _completed()]
        assert any(  # noqa: B101
            "delivery 1" in p for p in _problems(deliveries)
        )

    def test_a_body_that_is_not_utf8_is_reported(self):
        deliveries = [_started(), _delivery(b"\xff\xfe{}"), _completed()]
        assert any("not valid UTF-8" in p for p in _problems(deliveries))  # noqa: B101

    def test_a_body_that_is_not_a_techread_message_is_reported(self):
        deliveries = [_started(), _delivery(b'{"hello": "world"}'), _completed()]
        assert any(  # noqa: B101
            "does not validate as TechreadMessage" in p for p in _problems(deliveries)
        )

    @pytest.mark.parametrize("token", ["NaN", "Infinity", "-Infinity"])
    def test_a_non_finite_json_constant_is_reported(self, token):
        """The sender serialises with pydantic so these cannot appear.

        pydantic's own JSON parser accepts them, so this would pass unnoticed
        if the body were only ever handed to ``model_validate_json``.
        """
        body = json.loads(_ask().body.decode("utf-8"))
        body["payload_dict"]["general_roughness"] = "__PLACEHOLDER__"
        text = json.dumps(body).replace('"__PLACEHOLDER__"', token)
        deliveries = [_started(), _delivery(text.encode("utf-8")), _completed()]
        assert any(  # noqa: B101
            f"non-JSON constant '{token}'" in p for p in _problems(deliveries)
        )

    def test_a_json_string_infinity_is_accepted(self):
        """ "R PLANE" is a radius of infinity and travels as a JSON string.

        Rejecting it would be rejecting a value the API means.
        """
        body = json.loads(_ask().body.decode("utf-8"))
        body["payload_dict"]["weight"] = {
            "reference_id": 0,
            "value": "Infinity",
            "unit": "kg",
        }
        deliveries = [
            _started(),
            _delivery(json.dumps(body).encode("utf-8")),
            _completed(),
        ]
        messages = _check(deliveries)
        assert str(messages[1].payload_dict.weight.value) == "Infinity"  # noqa: B101

    def test_the_sequence_is_not_judged_when_a_body_failed_to_parse(self):
        """A parse failure must not also be reported as a missing message.

        The COMPLETED below is unreadable, and saying "no PROGRESS/COMPLETED
        was delivered" on top of that points at the wrong thing.
        """
        deliveries = [_started(), _ask(), _delivery(b"not json")]
        problems = _problems(deliveries)
        assert not any(  # noqa: B101
            "PROGRESS/COMPLETED" in p for p in problems
        )


class TestTheSequenceIsChecked:
    def test_a_missing_started_is_reported(self):
        assert any(  # noqa: B101
            "no PROGRESS/STARTED" in p for p in _problems([_ask(), _completed()])
        )

    def test_a_missing_completed_is_reported(self):
        assert any(  # noqa: B101
            "no PROGRESS/COMPLETED" in p for p in _problems([_started(), _ask()])
        )

    def test_a_started_that_is_not_first_is_reported(self):
        """Presence is not enough: an ASK must not overtake STARTED.

        core-reader joins the STARTED task at the top of every
        schedule_callback precisely so nothing can, and a customer keying off
        STARTED to open a record would miss an ASK that arrived ahead of it.
        """
        deliveries = [_ask(), _started(), _completed()]
        assert any(  # noqa: B101
            "was not the first message" in p for p in _problems(deliveries)
        )

    def test_a_completed_that_is_not_last_is_reported(self):
        deliveries = [_started(), _completed(), _ask()]
        assert any(  # noqa: B101
            "was not the last message" in p for p in _problems(deliveries)
        )

    def test_a_message_for_another_request_is_reported(self):
        other = uuid.uuid4()
        deliveries = [
            _started(),
            _delivery(
                _message(
                    TechreadMessageType.ASK,
                    "META_DATA",
                    payload_dict=ResponseMetaDataComponentDrawing().model_dump(
                        mode="json"
                    ),
                    request_id=other,
                )
            ),
            _completed(),
        ]
        assert any(str(other) in p for p in _problems(deliveries))  # noqa: B101

    def test_an_error_message_is_reported(self):
        deliveries = [
            _started(),
            _delivery(
                _message(
                    TechreadMessageType.ERROR,
                    TechreadMessageSubtype.ERROR_INTERNAL,
                )
            ),
            _ask(),
            _completed(),
        ]
        assert any("is an ERROR" in p for p in _problems(deliveries))  # noqa: B101

    def test_a_missing_ask_is_reported(self):
        deliveries = [_started(), _completed()]
        assert any(  # noqa: B101
            "no ASK message was delivered" in p for p in _problems(deliveries)
        )

    def test_a_duplicated_ask_is_reported(self):
        deliveries = [_started(), _ask(), _ask(), _completed()]
        assert any(  # noqa: B101
            "2 ASK messages were delivered" in p for p in _problems(deliveries)
        )

    def test_an_ask_that_was_never_requested_is_reported(self):
        deliveries = [
            _started(),
            _ask(),
            _delivery(_message(TechreadMessageType.ASK, "FEATURES")),
            _completed(),
        ]
        assert any(  # noqa: B101
            "never requested" in p for p in _problems(deliveries)
        )


class TestTheAskPayloadIsChecked:
    def test_a_payload_the_client_cannot_model_is_reported(self):
        """The check the whole exercise exists for.

        The envelope is a valid ``TechreadMessage`` either way. What separates
        a working integration from a broken one is whether ``payload_dict``
        deserialized into a response model, and a customer reading
        ``payload_dict.designation`` on the plain dict below gets an
        AttributeError in production.
        """
        deliveries = [
            _started(),
            _ask(payload={"ask_version": "v2", "ask_type": "FUTURE_ASK"}),
            _completed(),
        ]
        problems = _problems(deliveries)
        assert any(  # noqa: B101
            "did not deserialize into a response model" in p for p in problems
        )

    def test_an_ask_carrying_exceptions_is_reported(self):
        deliveries = [
            _started(),
            _delivery(
                _message(
                    TechreadMessageType.ASK,
                    "META_DATA",
                    payload_dict=ResponseMetaDataComponentDrawing().model_dump(
                        mode="json"
                    ),
                    exceptions=[
                        TechreadException(
                            exception_level=TechreadExceptionLevel.ERROR,
                            exception_type=(
                                TechreadExceptionType.DRAWING_CONTENT_NOT_UNDERSTOOD
                            ),
                        )
                    ],
                )
            ),
            _completed(),
        ]
        assert any(  # noqa: B101
            "carries exceptions" in p for p in _problems(deliveries)
        )

    def test_an_ask_with_neither_payload_nor_url_is_reported(self):
        deliveries = [
            _started(),
            _delivery(_message(TechreadMessageType.ASK, "META_DATA")),
            _completed(),
        ]
        assert any(  # noqa: B101
            "neither payload_dict nor payload_url" in p for p in _problems(deliveries)
        )


class TestEverythingIsReportedAtOnce:
    def test_several_violations_are_all_listed(self):
        """A run that costs a billable read reports everything it found."""
        deliveries = [
            _delivery(
                _ask().body,
                headers={"user-agent": "curl/8.0", "content-type": "text/plain"},
            )
        ]
        problems = _problems(deliveries)
        assert len(problems) >= 4  # noqa: B101
        assert any("User-Agent" in p for p in problems)  # noqa: B101
        assert any("Content-Type" in p for p in problems)  # noqa: B101
        assert any("no PROGRESS/STARTED" in p for p in problems)  # noqa: B101
        assert any("no PROGRESS/COMPLETED" in p for p in problems)  # noqa: B101
