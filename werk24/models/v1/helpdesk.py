from enum import Enum
from typing import Optional

from pydantic import UUID4, BaseModel

from .base_feature import W24BaseFeaturePosition


class W24HelpdeskImportance(str, Enum):
    """List of possible importance levels for a helpdesk ticket."""

    MUST_HAVE = "MUST_HAVE"
    SHOULD_HAVE = "SHOULD_HAVE"
    COULD_HAVE = "COULD_HAVE"


class W24HelpdeskTask(BaseModel):
    """
    Minimalistic HelpDesk Ticket Model.

    Attributes:
    ----------
    task_id (Optional[str]): Unique identifier of the task (if already created).
    request_id (UUID4): Unique identifier of the request.
    observed_outcome (str): Observed outcome that the user wants to report.
    expected_outcome (str): Expected outcome that the user considers correct.
    comment (str): Additional comment for explaining the issue.
    position (W24BaseFeaturePosition): Position of the issue in the document.
        When the position of the feature is known, it can be provided here.
        Leaving it empty is also accepted.
    importance (W24HelpdeskImportance): Importance of the issue.
    """

    task_id: Optional[str] = None
    request_id: UUID4
    observed_outcome: str
    expected_outcome: str
    comment: str
    position: Optional[W24BaseFeaturePosition] = None
    importance: W24HelpdeskImportance
