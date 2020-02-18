from enum import Enum


class W24MaterialShape(str, Enum):
    """ Enum describing the possible shapes of raw material
    """
    ROD_ROUND = "rod_round"
    ROD_HEXAGON = "rod_hexagon"
    ROD_SQUARE = "rod_square"
    ROD_RECTANGLE = "rod_rectangle"
