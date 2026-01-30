"""Property-based tests for priority error handling.

Feature: priority-override

These tests verify that the _parse_message() method correctly handles
priority-related error responses from the server.
"""

import json

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from werk24.techread import Werk24Client
from werk24.utils.exceptions import (
    InvalidPriorityError,
    PriorityTooHighError,
    ServerException,
)


# Strategy for generating valid priority tier strings
def priority_tier_strategy():
    """Generate valid priority tier strings."""
    return st.sampled_from(["PRIO1", "PRIO2", "PRIO3"])


class TestPriorityTooHighErrorParsing:
    """Feature: priority-override, Property 5: PriorityTooHighError contains account_tier and requested_priority

    *For any* server response with error type "PRIORITY_TOO_HIGH" containing
    account_tier and requested_priority in details, the raised `PriorityTooHighError`
    exception SHALL have `account_tier` and `requested_priority` attributes
    matching the response values.

    **Validates: Requirements 3.2, 3.3**
    """

    @settings(max_examples=100)
    @given(
        account_tier=priority_tier_strategy(),
        requested_priority=priority_tier_strategy(),
    )
    def test_priority_too_high_error_contains_attributes(
        self, account_tier: str, requested_priority: str
    ):
        """PriorityTooHighError contains account_tier and requested_priority from response."""
        # Build a PRIORITY_TOO_HIGH error response
        error_response = {
            "error": "PRIORITY_TOO_HIGH",
            "message": f"Requested priority {requested_priority} exceeds account tier {account_tier}",
            "details": {
                "account_tier": account_tier,
                "requested_priority": requested_priority,
            },
        }
        message_raw = json.dumps(error_response)

        # Parse the message and verify the exception
        with pytest.raises(PriorityTooHighError) as exc_info:
            Werk24Client._parse_message(message_raw)

        # Verify the exception attributes match the response values
        assert exc_info.value.account_tier == account_tier
        assert exc_info.value.requested_priority == requested_priority

    @pytest.mark.parametrize(
        "account_tier,requested_priority",
        [
            ("PRIO2", "PRIO1"),
            ("PRIO3", "PRIO1"),
            ("PRIO3", "PRIO2"),
        ],
    )
    def test_specific_priority_too_high_cases(
        self, account_tier: str, requested_priority: str
    ):
        """Specific PRIORITY_TOO_HIGH cases are handled correctly."""
        error_response = {
            "error": "PRIORITY_TOO_HIGH",
            "message": f"Requested priority {requested_priority} exceeds account tier {account_tier}",
            "details": {
                "account_tier": account_tier,
                "requested_priority": requested_priority,
            },
        }
        message_raw = json.dumps(error_response)

        with pytest.raises(PriorityTooHighError) as exc_info:
            Werk24Client._parse_message(message_raw)

        assert exc_info.value.account_tier == account_tier
        assert exc_info.value.requested_priority == requested_priority


class TestInvalidPriorityErrorParsing:
    """Tests for INVALID_PRIORITY error response handling.

    **Validates: Requirements 4.1, 4.2**
    """

    @settings(max_examples=100)
    @given(
        invalid_value=st.text(min_size=1).filter(
            lambda s: s.upper() not in {"PRIO1", "PRIO2", "PRIO3"}
        )
    )
    def test_invalid_priority_error_contains_invalid_value(self, invalid_value: str):
        """InvalidPriorityError contains the invalid priority value from response."""
        # Build an INVALID_PRIORITY error response
        error_response = {
            "error": "INVALID_PRIORITY",
            "message": f"Invalid priority value: {invalid_value}",
            "details": {
                "priority": invalid_value,
                "valid_values": ["PRIO1", "PRIO2", "PRIO3"],
            },
        }
        message_raw = json.dumps(error_response)

        # Parse the message and verify the exception
        with pytest.raises(InvalidPriorityError) as exc_info:
            Werk24Client._parse_message(message_raw)

        # Verify the exception attribute matches the response value
        assert exc_info.value.invalid_value == invalid_value

    @pytest.mark.parametrize(
        "invalid_value",
        [
            "PRIO4",
            "prio0",
            "priority1",
            "P1",
            "high",
            "low",
            "normal",
            "",
        ],
    )
    def test_specific_invalid_priority_cases(self, invalid_value: str):
        """Specific INVALID_PRIORITY cases are handled correctly."""
        error_response = {
            "error": "INVALID_PRIORITY",
            "message": f"Invalid priority value: {invalid_value}",
            "details": {
                "priority": invalid_value,
                "valid_values": ["PRIO1", "PRIO2", "PRIO3"],
            },
        }
        message_raw = json.dumps(error_response)

        with pytest.raises(InvalidPriorityError) as exc_info:
            Werk24Client._parse_message(message_raw)

        assert exc_info.value.invalid_value == invalid_value


class TestOtherErrorResponseHandling:
    """Tests for other error response handling to ensure no regressions."""

    def test_forbidden_error_raises_unauthorized(self):
        """Forbidden error message raises UnauthorizedException."""
        from werk24.utils.exceptions import UnauthorizedException

        error_response = {"message": "Forbidden"}
        message_raw = json.dumps(error_response)

        with pytest.raises(UnauthorizedException):
            Werk24Client._parse_message(message_raw)

    def test_unknown_error_raises_server_exception(self):
        """Unknown error responses raise ServerException."""
        error_response = {
            "error": "UNKNOWN_ERROR",
            "message": "Something went wrong",
        }
        message_raw = json.dumps(error_response)

        with pytest.raises(ServerException):
            Werk24Client._parse_message(message_raw)

    def test_invalid_json_raises_server_exception(self):
        """Invalid JSON raises ServerException."""
        message_raw = "not valid json"

        with pytest.raises(ServerException):
            Werk24Client._parse_message(message_raw)
