from pydantic import BaseModel

from .angle import W24Angle
from .thread_direction import W24ThreadDirection
from .thread_norm import W24ThreadNorm


class W24Thread(BaseModel):
    """ A W24Thread contains all information about a thread.
    As the W24Thread object is always associated to a W24Volume,
    it does not contain any information about the diameter
    """
    designation: str
    direction: W24ThreadDirection = W24ThreadDirection.RIGHT
    norm: W24ThreadNorm
    angle: W24Angle = None
    pitch: float = None
