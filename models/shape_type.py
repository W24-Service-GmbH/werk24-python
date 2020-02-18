from enum import Enum


class W24ShapeType(str, Enum):
    """Enum of 2D base shapes
    """
    CIRCLE = "CIRCLE"
    SQUARE = "SQUARE"
    HEXAGON = "HEXAGON"
    RECTANGLE = "RECTANGLE"
