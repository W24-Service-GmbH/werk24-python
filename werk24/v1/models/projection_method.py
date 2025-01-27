from enum import Enum


class W24ProjectionMethod(str, Enum):
    """Projection Method according to ISO 128"""

    FIRST_ANGLE = "FIRST_ANGLE"
    THIRD_ANGLE = "THIRD_ANGLE"
