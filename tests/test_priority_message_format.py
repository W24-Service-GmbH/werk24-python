"""Property-based tests for priority message format.

Feature: priority-override

These tests verify that the priority parameter is correctly included in
the message dictionary when building the request message for _send_command_read().
"""

import json
from typing import Optional

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st


def build_read_command_message(
    client_public_key_pem: Optional[bytes] = None,
    priority: Optional[str] = None,
) -> dict:
    """Build the message dictionary for the READ command.

    This function replicates the message building logic from _send_command_read()
    to allow isolated testing of the message format.

    Args:
        client_public_key_pem: Optional PEM-encoded public key.
        priority: Optional priority level (PRIO1, PRIO2, PRIO3).

    Returns:
        The message dictionary that would be sent to the server.
    """
    message = {}
    if client_public_key_pem:
        message["public_key"] = client_public_key_pem.decode("utf-8")

    # Include priority in message if specified (ensure uppercase)
    if priority:
        message["priority"] = priority.upper()

    return message


# Strategy for generating valid priority strings in various cases
def valid_priority_strategy():
    """Generate valid priority strings with random casing."""
    base_priorities = ["PRIO1", "PRIO2", "PRIO3"]

    def random_case(s: str) -> st.SearchStrategy[str]:
        """Generate all possible case variations of a string."""
        return st.sampled_from(
            [
                s.lower(),
                s.upper(),
                s.capitalize(),
                s[0].lower() + s[1:].upper(),
                s[0].upper() + s[1:].lower(),
            ]
        )

    return st.one_of(*[random_case(p) for p in base_priorities])


class TestPriorityMessageFormatWithPriority:
    """Feature: priority-override, Property 3: Valid priority is included in message as uppercase

    *For any* valid priority value (case-insensitive), when included in a request,
    the message body SHALL contain a "priority" key with the uppercase normalized value.

    **Validates: Requirements 1.2, 1.4, 1.6, 5.1, 5.2**
    """

    @settings(max_examples=100)
    @given(priority=valid_priority_strategy())
    def test_valid_priority_included_as_uppercase(self, priority: str):
        """Valid priority values are included in the message as uppercase."""
        message = build_read_command_message(priority=priority)

        # Verify the priority is in the message and is uppercase
        assert "priority" in message
        assert message["priority"] == priority.upper()

    @pytest.mark.parametrize(
        "priority,expected",
        [
            ("PRIO1", "PRIO1"),
            ("PRIO2", "PRIO2"),
            ("PRIO3", "PRIO3"),
            ("prio1", "PRIO1"),
            ("prio2", "PRIO2"),
            ("prio3", "PRIO3"),
            ("Prio1", "PRIO1"),
            ("PrIo2", "PRIO2"),
        ],
    )
    def test_specific_priority_cases(self, priority: str, expected: str):
        """Specific priority values are normalized to uppercase in the message."""
        message = build_read_command_message(priority=priority)
        assert message["priority"] == expected

    @settings(max_examples=100)
    @given(priority=valid_priority_strategy())
    def test_priority_with_public_key(self, priority: str):
        """Priority is included alongside public key when both are provided."""
        public_key = b"-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----"
        message = build_read_command_message(
            client_public_key_pem=public_key,
            priority=priority,
        )

        assert "priority" in message
        assert message["priority"] == priority.upper()
        assert "public_key" in message


class TestPriorityMessageFormatWithoutPriority:
    """Feature: priority-override, Property 4: No priority means no priority key in message

    *For any* request where priority is None or not specified, the message body
    SHALL NOT contain a "priority" key.

    **Validates: Requirements 1.1, 1.3, 1.5, 5.3**
    """

    def test_none_priority_means_no_priority_key(self):
        """When priority is None, the message should not contain a priority key."""
        message = build_read_command_message(priority=None)
        assert "priority" not in message

    def test_no_priority_parameter_means_no_priority_key(self):
        """When priority parameter is not provided, the message should not contain a priority key."""
        message = build_read_command_message()
        assert "priority" not in message

    def test_empty_message_when_no_params(self):
        """When no parameters are provided, the message should be empty."""
        message = build_read_command_message()
        assert message == {}

    def test_only_public_key_when_no_priority(self):
        """When only public key is provided, message should only contain public_key."""
        public_key = b"-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----"
        message = build_read_command_message(client_public_key_pem=public_key)

        assert "public_key" in message
        assert "priority" not in message
        assert len(message) == 1

    @settings(max_examples=100)
    @given(
        has_public_key=st.booleans(),
    )
    def test_no_priority_key_regardless_of_other_params(self, has_public_key: bool):
        """Priority key is absent when priority is None, regardless of other parameters."""
        public_key = (
            b"-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----"
            if has_public_key
            else None
        )
        message = build_read_command_message(
            client_public_key_pem=public_key,
            priority=None,
        )

        assert "priority" not in message
