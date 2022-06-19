from typing import Tuple
import abc
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import UUID4, BaseModel

from .feature import W24FeatureModel
from .unit import W24UnitAngle


class W24AngleTolerationType(str, Enum):
    """ Enum listing all supported AngleToleration Type

    !!! note
        Currently we are only supporting the General
        Tolerances indicated on the drawing's Title Block.
        If you need access to more types, e.g.,
        MINIMUM, MAXIMUM, OFF_SIZE, APPROXIMATION, please
        reach out to us.
    """
    GENERAL_TOLERANCES = "GENERAL_TOLERANCES"


class W24AngleToleration(BaseModel, abc.ABC):
    """ Base Class that describes Angle Tolerances

    Attributes:
        toleration_type: Toleration Type  of the
            `W24AngleSize`

        blurb: String representation for human consumption

    !!! caution
        This model will soon be extended to contain the
        toleration information derived from the TitleBlock.
        Be aware that you will need to request the TitleBlock
        to obtain this information.
    """

    toleration_type: W24AngleTolerationType

    blurb: str


class W24AngleSize(BaseModel):
    """ Size of an Angle including its toleration

    Attributes:
        blurb: Blurb for human consumption

        angle: Nominal angle size in [units]

        unit: Angle Unit. Currently only degrees are
            supported.
    """

    blurb: str

    angle: Decimal

    unit: W24UnitAngle = W24UnitAngle.DEGREE


class W24AngleLabel(BaseModel):
    """ Label associated with an Angle indicated
    on the Technical Drawing

    Attributes:
        blurb: Blurb for human consumption

        size: Nominal angle size

        size_toleration: Tolerated deviations
    """

    blurb: str

    size: W24AngleSize

    size_toleration: W24AngleToleration


class W24Angle(W24FeatureModel):
    """ Tolerated Angle detected on a sectional of the
    Technical Drawing

    Attributes:
        angle_id: Unique identifier of the Angle. This
            allows the reference of the angle from another
            object (e.g., a leader)

        vertex: X and y coordinates of the angle's vertex
            normalized by the sectional's width and height.

        ray1: Unit-vector attached to the vertex that indicates
            the angle's start ray

        ray2: Unit-vector attached to the vertex that indicates
            the angle's end ray

        label: AngleLabel associated with the Angle

        confidence: Werk24 calculates an internal confidence
            score for each angle. The score ranges from 0.0
            to 1.0 and can be used to accept the reading
            as-is or queuing it for a manual verification.
    """

    # !!! DEPRECATED
    vertex: Tuple[float, float]

    # !!! DEPRECATED
    ray1: Tuple[float, float]

    # !!! DEPRECATED
    ray2: Tuple[float, float]

    angle_id: Optional[UUID4]

    label: W24AngleLabel

    confidence: float
