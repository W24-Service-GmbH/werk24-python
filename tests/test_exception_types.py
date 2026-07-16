from uuid import uuid4

from werk24.models.v1.techread import W24TechreadExceptionType
from werk24.models.v2.internal import (
    TechreadExceptionType,
    TechreadMessage,
    TechreadMessageType,
)


def test_configuration_incorrect_enum_present():
    assert (
        TechreadExceptionType.CONFIGURATION_INCORRECT.value == "CONFIGURATION_INCORRECT"
    )
    assert (
        W24TechreadExceptionType.CONFIGURATION_INCORRECT.value
        == "CONFIGURATION_INCORRECT"
    )


def test_drawing_page_count_too_large_enum_present():
    assert (
        TechreadExceptionType.DRAWING_PAGE_COUNT_TOO_LARGE.value
        == "DRAWING_PAGE_COUNT_TOO_LARGE"
    )
    assert (
        W24TechreadExceptionType.DRAWING_PAGE_COUNT_TOO_LARGE.value
        == "DRAWING_PAGE_COUNT_TOO_LARGE"
    )


def test_message_parses_drawing_page_count_too_large():
    """A TechreadMessage carrying the new exception_type must parse
    without raising a pydantic ValidationError.
    """
    message = TechreadMessage.model_validate_json(
        f"""{{
            "request_id": "{uuid4()}",
            "message_type": "ERROR",
            "message_subtype": "COMPLETED",
            "exceptions": [
                {{
                    "exception_level": "ERROR",
                    "exception_type": "DRAWING_PAGE_COUNT_TOO_LARGE"
                }}
            ]
        }}"""
    )
    assert message.message_type == TechreadMessageType.ERROR
    assert len(message.exceptions) == 1
    assert (
        message.exceptions[0].exception_type
        == TechreadExceptionType.DRAWING_PAGE_COUNT_TOO_LARGE
    )
