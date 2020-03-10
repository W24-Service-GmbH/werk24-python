from typing import Union

from .chamfer import W24Chamfer
from .measure import W24Measure
from .radius import W24Radius
from .shape_circle import W24ShapeCircle
from .shape_hexagon import W24ShapeHexagon
from .shape_rectangle import W24ShapeRectangle
from .thread import W24Thread
from .volume import W24Volume


class W24VolumeTurning(W24Volume):
    """ W24VolumeTurning derives from W24Volume and
    describes a 3D Volume in a way that is convenient for
    turning parts.
    """

    left_shape: Union[W24ShapeCircle, W24ShapeHexagon, W24ShapeRectangle]
    left_chamfer: W24Chamfer = None

    shell_width: W24Measure
    shell_radius: W24Radius = None
    shell_thread: W24Thread = None

    right_shape: Union[W24ShapeCircle, W24ShapeHexagon, W24ShapeRectangle]
    right_chamfer: W24Chamfer = None
