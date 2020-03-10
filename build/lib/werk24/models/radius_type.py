from enum import Enum


class W24RadiusType(str, Enum):
    """ Enum of the radius types
    """

    CONCAVE = "concave"
    CONVEX = "convex"
