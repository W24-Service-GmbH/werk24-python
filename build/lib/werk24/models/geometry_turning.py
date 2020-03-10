from typing import List

from .geometry import W24Geometry
from .geometry_type import W24GeometryType
from .volume_turning import W24VolumeTurning


class W24GeometryTurning(W24Geometry):
    """ W24GeometryTurnMill derives from W24Geometry
    and describes the part's geometry in a way that
    is convenient for Turned/Milled parts.
    """

    geometry_type = W24GeometryType.TURN_MILL
    outer_contour: List[W24VolumeTurning] = []
    inner_contours: List[W24VolumeTurning] = []
