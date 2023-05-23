
""" Defintion of all the W24Radius class its support structures
"""

from typing import Optional

from pydantic import UUID4, BaseModel, validator

from .base_feature import W24BaseFeatureModel
from .size import W24Size
from .tolerance import W24Tolerance, W24ToleranceGeneral
from .unit import W24UnitLength


class W24RadiusLabel(BaseModel):
    """ Radius Label

    Attributes:
        blurb: String representation of the Radius for human consumption

        quantity: Quantity of the annotated radius, e.g., 2 x R4 returns
            quantity=2

        size: Size of the Radius as referred in the drawing.

        size_tolerance: Tolerance details of the Radius. Please keep in
            mind that Radii can carry special tolerances. If none are
            mentioned on the drawing, the general tolerances apply.

        unit: Length units of the size and size_tolerance. In most cases this
            will be be millimeter (METRIC) or inch (IMPERIAL) and be consistent
            for the complete drawing. Exceptions are very rare, but exist.
    """

    @validator('size_tolerance', pre=True)
    def deserialize_size_tolerance(cls, v):
        if isinstance(v, W24Tolerance):
            return v
        return W24Tolerance.parse_obj(v)

    blurb: str

    quality: int = 1

    size: W24Size

    size_tolerance: W24Tolerance = W24ToleranceGeneral()

    unit: Optional[W24UnitLength] = None


class W24Radius(W24BaseFeatureModel):
    """ Radius Feature

    Attributes:
        radius_id: Unique UUID4 identifier. This can be used to provide
            automated feedback about customer changes.

        label: Label of the radius.

        confidence: Werk24 calcualtes an internal confidence score for
            reach radius. Depending on your use-case, you might want
            to consider or discard low-confidence radii. This value
            allows you to do so. The value ranges from 0.0 to 1.0
    """
    radius_id: UUID4

    label: W24RadiusLabel

    confidence: float
