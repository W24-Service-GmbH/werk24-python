from enum import Enum

class W24ProjectionMethod(str, Enum):
    """Projection Method according to ISO 128
    """
    FIRST_ANGLE_PROJECTION = "FIRST_ANGLE_PROJECTION"
    THIRD_ANGLE_PROJECTION = "THIRD_ANGLE_PROJECTION"