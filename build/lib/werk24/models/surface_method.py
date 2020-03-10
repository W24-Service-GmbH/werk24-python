from enum import Enum


class W24SurfaceMethod(str, Enum):
    """ Enum that lists all surface modificatino methods
    """

    TURNED = "turned"
    GROUND = "ground"
    PLATED = "plated"
