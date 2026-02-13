"""Property-based tests for priority validation.

Feature: priority-override
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from werk24.utils.exceptions import InvalidPriorityError
from werk24.utils.priority import VALID_PRIORITIES, validate_priority


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


class TestPriorityValidationValidValues:
    """Feature: priority-override, Property 1: Priority validation accepts valid values case-insensitively

    *For any* string that is a case-insensitive match to "PRIO1", "PRIO2", or "PRIO3",
    the `validate_priority()` function SHALL return the uppercase normalized version
    without raising an exception.

    **Validates: Requirements 2.1, 2.2**
    """

    @settings(max_examples=100)
    @given(priority=valid_priority_strategy())
    def test_valid_priority_returns_uppercase(self, priority: str):
        """Valid priority values are normalized to uppercase."""
        result = validate_priority(priority)
        assert result == priority.upper()
        assert result in VALID_PRIORITIES

    def test_none_returns_none(self):
        """None input returns None without raising."""
        result = validate_priority(None)
        assert result is None

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
    def test_specific_valid_cases(self, priority: str, expected: str):
        """Specific valid priority values are normalized correctly."""
        assert validate_priority(priority) == expected


# Valid priority strings (case-insensitive) for filtering
VALID_PRIORITY_STRINGS = {"prio1", "prio2", "prio3"}


class TestPriorityValidationInvalidValues:
    """Feature: priority-override, Property 2: Invalid priority raises InvalidPriorityError with the invalid value

    *For any* string that is NOT a case-insensitive match to "PRIO1", "PRIO2", or "PRIO3",
    the `validate_priority()` function SHALL raise an `InvalidPriorityError` exception
    where the `invalid_value` attribute equals the original input string.

    **Validates: Requirements 2.3, 2.4, 4.2**
    """

    @settings(max_examples=100)
    @given(
        invalid_string=st.text(min_size=1).filter(
            lambda s: s.lower() not in VALID_PRIORITY_STRINGS
        )
    )
    def test_invalid_strings_raise_exception_with_value(self, invalid_string: str):
        """Any string not matching a valid priority raises InvalidPriorityError with the invalid value."""
        with pytest.raises(InvalidPriorityError) as exc_info:
            validate_priority(invalid_string)

        # Verify the invalid_value attribute contains the original input
        assert exc_info.value.invalid_value == invalid_string

    def test_empty_string_raises_exception(self):
        """Empty string raises InvalidPriorityError."""
        with pytest.raises(InvalidPriorityError) as exc_info:
            validate_priority("")

        assert exc_info.value.invalid_value == ""

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
            "  PRIO1  ",  # whitespace around valid value
            "PRIO1 ",  # trailing whitespace
            " PRIO1",  # leading whitespace
        ],
    )
    def test_specific_invalid_cases(self, invalid_value: str):
        """Specific invalid priority values raise InvalidPriorityError with the value."""
        with pytest.raises(InvalidPriorityError) as exc_info:
            validate_priority(invalid_value)

        assert exc_info.value.invalid_value == invalid_value
