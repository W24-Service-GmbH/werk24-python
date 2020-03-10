from enum import Enum


class W24SurfaceLay(str, Enum):
    """ Enum that lists all surface lays
    """

    PARALLEL = "parallel"
    PERPENDICULAR = "perpendicular"
    CROSSED = "crossed"
    MULTI_DIRECTIONAL = "multi_directional"
    CIRCULAR = "circular"
    RADIAL = "radial"
    PARTICULATE = "particulate"
