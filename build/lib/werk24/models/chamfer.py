from pydantic import BaseModel

from .angle import W24Angle
from .measure import W24Measure


class W24Chamfer(BaseModel):
    """ W24Chamfer describes a chamfer that is associated
    with a side of a W24GeometryTurnMill.

    The information of its diameter is contained in the
    W24GeometryTrunMill object.
    """

    width: W24Measure
    angle: W24Angle
