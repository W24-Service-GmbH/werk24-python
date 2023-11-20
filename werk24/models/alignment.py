from enum import Enum


class W24AlignmentHorizontal(str, Enum):
    """Horizontal Alignment options"""

    LEFT = "LEFT"
    CENTER = "CENTER"
    RIGHT = "RIGHT"


class W24AlignmentVertical(str, Enum):
    """Vertical Alignment options"""

    TOP = "TOP"
    CENTER = "CENTER"
    BOTTOM = "BOTTOM"
