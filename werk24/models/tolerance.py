from decimal import Decimal
from typing import Optional

from .feature import W24FeatureModel
from .gender import W24Gender
from .size import W24SizeTolerance

class W24ToleranceFeature(W24FeatureModel):
    """Characterization of a Tolerance Feature.

    Attributes:
        gender: Gender (male or female) of the tolerance feature.
            This is determined by checking whether the tolerance feature is
            located on the outer contour of the part or inside the part.
            When the outer contour is unavailable (e.g., in detail drawings),
            the gender is set to None.

        length: Length of the slug corresponding to the tolerance feature.

    """
    gender: Optional[W24Gender]

    length: Optional[Decimal]

    tolerance: W24SizeTolerance