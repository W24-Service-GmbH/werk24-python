from pydantic import BaseModel
from .measure import W24Measure
from .angle import W24Angle


class W24Chamfer(BaseModel):
    """ W24Chamfer describes a chamfer that is associated
    with a side of a W24GeometryTurnMill.

    The information of its diameter is contained in the
    W24GeometryTrunMill object.
    """
    width: W24Measure
    angle: W24Angle
