"""A knowingly incomplete read can say so without failing (werk24-python#586).

core-reader knows when a read is incomplete (a stage timed out, a region had
no text) and records it in its own metrics, but the result reached the
customer through the ordinary success path with nothing to mark it. The
client models had no place to carry a marker, and adding one server-side
would have broken deserialization in every consumer, because
``TechreadException`` accepted only the levels and types it already knew.

So: a WARNING level and a READ_INCOMPLETE type that ride on a COMPLETED
message, ``is_successful`` that counts only ERROR as fatal, and lenient
parsing so the next new type the server adds does not fail the whole
message.
"""

import json
from uuid import uuid4

import pytest
from pydantic import BaseModel, ValidationError

from werk24.models.v2.enums import TechreadExceptionLevel
from werk24.models.v2.internal import (
    TechreadException,
    TechreadExceptionType,
    TechreadMessage,
    TechreadMessageSubtype,
    TechreadMessageType,
)


def _completed(*exceptions: dict) -> TechreadMessage:
    return TechreadMessage.model_validate_json(
        json.dumps(
            {
                "request_id": str(uuid4()),
                "message_type": "PROGRESS",
                "message_subtype": "COMPLETED",
                "exceptions": list(exceptions),
            }
        )
    )


def test_a_completed_read_can_carry_an_incompleteness_warning():
    message = _completed(
        {
            "exception_level": "WARNING",
            "exception_type": "READ_INCOMPLETE",
            "ask_type": "DOCUMENT_PROFILE",
            "reason": "timeout",
        }
    )
    assert message.message_type == TechreadMessageType.PROGRESS
    assert message.message_subtype == TechreadMessageSubtype.PROGRESS_COMPLETED
    (warning,) = message.exceptions
    assert warning.exception_level is TechreadExceptionLevel.WARNING
    assert warning.exception_type is TechreadExceptionType.READ_INCOMPLETE
    assert warning.ask_type == "DOCUMENT_PROFILE"
    assert warning.reason == "timeout"
    # The results that were delivered stand.
    assert message.is_successful


def test_an_error_still_fails_the_message():
    message = _completed(
        {"exception_level": "ERROR", "exception_type": "DRAWING_FILE_SIZE_TOO_LARGE"}
    )
    assert not message.is_successful


def test_an_error_next_to_a_warning_still_fails_the_message():
    message = _completed(
        {"exception_level": "WARNING", "exception_type": "READ_INCOMPLETE"},
        {"exception_level": "ERROR", "exception_type": "DRAWING_RESOLUTION_TOO_LOW"},
    )
    assert not message.is_successful


def test_info_does_not_fail_the_message():
    """The docstring always said only ERROR counts; the code counted any."""
    message = _completed({"exception_level": "INFO", "exception_type": "NOTICE"})
    assert message.is_successful


def test_the_new_fields_are_optional():
    """What servers send today still parses, with the new fields empty."""
    message = _completed(
        {"exception_level": "ERROR", "exception_type": "DRAWING_FILE_SIZE_TOO_LARGE"}
    )
    (exception,) = message.exceptions
    assert exception.ask_type is None
    assert exception.reason is None


def test_an_unknown_type_is_kept_rather_than_failing_the_message():
    message = _completed(
        {"exception_level": "WARNING", "exception_type": "SOMETHING_NEW"}
    )
    (warning,) = message.exceptions
    assert warning.exception_type == "SOMETHING_NEW"
    assert message.is_successful


def test_an_unknown_level_is_still_refused():
    """The level decides ``is_successful``, so it is not guessed at.

    core-reader also relies on this to refuse a request-cache manifest it
    could not replay faithfully.
    """
    with pytest.raises(ValidationError):
        TechreadException.model_validate(
            {"exception_level": "FATAL", "exception_type": "READ_INCOMPLETE"}
        )


def test_known_values_still_come_back_as_enum_members():
    """Leniency must not turn every level and type into a bare string."""
    exception = TechreadException.model_validate(
        {"exception_level": "ERROR", "exception_type": "CONFIGURATION_INCORRECT"}
    )
    assert exception.exception_level is TechreadExceptionLevel.ERROR
    assert exception.exception_type is TechreadExceptionType.CONFIGURATION_INCORRECT


class _ClientBefore586(BaseModel):
    """``TechreadException`` as released clients define it."""

    exception_level: TechreadExceptionLevel
    exception_type: TechreadExceptionType


def test_an_error_serialized_by_this_model_still_parses_in_an_older_client():
    """core-reader serializes with this model and sends to every client.

    The two new fields must be ignorable by a client that predates them, or
    upgrading the server's copy of this package breaks every ERROR message.
    """
    exception = TechreadException(
        exception_level=TechreadExceptionLevel.ERROR,
        exception_type=TechreadExceptionType.DRAWING_FILE_SIZE_TOO_LARGE,
    )
    old = _ClientBefore586.model_validate_json(exception.model_dump_json())
    assert old.exception_type is TechreadExceptionType.DRAWING_FILE_SIZE_TOO_LARGE


def test_the_warning_round_trips():
    exception = TechreadException(
        exception_level=TechreadExceptionLevel.WARNING,
        exception_type=TechreadExceptionType.READ_INCOMPLETE,
        ask_type="BALLOONS",
        reason="stage_failed",
    )
    again = TechreadException.model_validate_json(exception.model_dump_json())
    assert again == exception
    assert again.ask_type == "BALLOONS"


def test_an_exception_without_the_new_fields_dumps_as_it_did_before():
    """Unset ``ask_type`` and ``reason`` stay off the wire and out of dumps.

    core-reader dumps exceptions into its callbacks and its request cache and
    compares the dicts, so two ``None`` keys appearing in every existing
    exception would change what it stores and sends without anyone asking.
    """
    exception = TechreadException(
        exception_level=TechreadExceptionLevel.INFO,
        exception_type=TechreadExceptionType.DRAWING_RESOLUTION_TOO_LOW,
    )
    expected = {
        "exception_level": "INFO",
        "exception_type": "DRAWING_RESOLUTION_TOO_LOW",
    }
    assert exception.model_dump(mode="json") == expected
    assert json.loads(exception.model_dump_json()) == expected


def test_a_set_field_is_dumped():
    exception = TechreadException(
        exception_level=TechreadExceptionLevel.WARNING,
        exception_type=TechreadExceptionType.READ_INCOMPLETE,
        reason="timeout",
    )
    assert exception.model_dump(mode="json") == {
        "exception_level": "WARNING",
        "exception_type": "READ_INCOMPLETE",
        "reason": "timeout",
    }
