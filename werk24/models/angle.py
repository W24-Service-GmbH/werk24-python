import abc
from enum import Enum
from typing import Optional, Tuple

from pydantic import UUID4, BaseModel

from .unit import W24UnitAngle


class W24AngleTolerationType(str, Enum):
    """ Enum listing all supported AngleToleration Type

    NOTE: currently we are only supporting the general
    tolerances. If you need access to more types, e.g.,
    MINIMUM, MAXIMUM, OFF_SIZE, APPROXIMATION, please
    reach out to us.
    """
    GENERAL_TOLERANCES = "GENERAL_TOLERANCES"


class W24AngleToleration(BaseModel, abc.ABC):
    """ Abstract BaseClass to cover all Angle Tolerations
    """

    toleration_type: W24AngleTolerationType
    """ Toleration Type  of the Angle Size
    """

    blurb: str
    """ String representation for human consummption
    """


class W24AngleSize(BaseModel):

    blurb: str
    """ blurb for human consumpation
    """

    angle: float
    """ Angle size
    """

    unit: W24UnitAngle = W24UnitAngle.DEGREE
    """ Angle Unit
    """


class W24AngleLabel(BaseModel):

    blurb: str
    """ blurb for human consumpation
    """

    size: W24AngleSize
    """ Angle Size
    """

    size_toleration: W24AngleToleration
    """ Angle Toleration
    """


class W24Angle(BaseModel):
    """ Tolerated angle
    """

    angle_id: Optional[UUID4]
    """ Unique id of the Angle
    """

    vertex: Tuple[float, float]
    """ X,Y coordiantes of the angle's vertex normalized
    by the sectional's width / height.
    """

    ray1: Tuple[float, float]
    """ Unit-vector that points from the vertex towards the
    angle's start ray.
    """

    ray2: Tuple[float, float]
    """ Unit-vector that points from the vertex towards the
    angle's end ray.
    """

    label: W24AngleLabel
    """ Angle Label associated with teh Angle
    """

    confidence: float
    """ Werk24 calculates an internal confidence score for
    each angle. The score ranges from 0.0 to 1.0 and can
    be used to accpect the reading as-is or queuing it for
    a manual verification
    """
