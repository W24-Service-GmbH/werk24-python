"""Priority validation utilities for the Werk24 client.

This module provides functions for validating and normalizing priority values
used in drawing requests.
"""

from typing import Optional

from werk24.utils.exceptions import InvalidPriorityError

# Valid priority values (uppercase)
VALID_PRIORITIES = {"PRIO1", "PRIO2", "PRIO3"}


def validate_priority(priority: Optional[str]) -> Optional[str]:
    """Validate and normalize a priority string.

    Args:
        priority: The priority string to validate (case-insensitive).
            Valid values are "PRIO1", "PRIO2", "PRIO3" (case-insensitive).
            None is also accepted and returns None.

    Returns:
        The normalized priority string (uppercase) or None if not provided.

    Raises:
        InvalidPriorityError: If the priority value is not valid.

    Examples:
        >>> validate_priority("prio1")
        'PRIO1'
        >>> validate_priority("PRIO2")
        'PRIO2'
        >>> validate_priority(None)
        None
        >>> validate_priority("invalid")  # Raises InvalidPriorityError
    """
    if priority is None:
        return None

    normalized = priority.upper()

    if normalized not in VALID_PRIORITIES:
        raise InvalidPriorityError(
            details=f"Invalid priority value: {priority}. Valid values are: PRIO1, PRIO2, PRIO3",
            invalid_value=priority,
        )

    return normalized
