from decimal import Decimal
from typing import Optional, Tuple

from pydantic import UUID4, BaseModel

from .base_feature import W24BaseFeatureModel
from .tolerance import W24ToleranceType
from .unit import W24UnitAngle


class W24AngleSize(BaseModel):
    """Size of an Angle including its tolerance

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
    """Label associated with an Angle indicated
    on the Technical Drawing

    Attributes:

        blurb: Blurb for human consumption
        quantity: Number of annotated angles
        angle: Nominal angle size
        angle_tolerance: Tolerated deviations
    """

    blurb: str
    quantity: int
    angle: W24AngleSize
    angle_tolerance: W24ToleranceType


class W24Angle(W24BaseFeatureModel):
    """Tolerated Angle detected on a sectional of the
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
