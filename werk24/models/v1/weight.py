from typing import Optional

from .base_feature import W24BaseFeatureModel
from .unit import W24UnitLength, W24UnitWeight


class W24Weight(W24BaseFeatureModel):
    """Weight of a Part - for example as indicated
    on the Title Block.

    NOTE: this can also be a relative weight
    (e.g. kg per meter for profiles)

    Attributes:
        blurb: Weight in a human-readable format.

        value: Value of the Weight

        weight_unit: Unit of the Weight (e.g., kg)

        length_unit: Unit of the Length for relative
            weights (e.g., METER for meter weights of profiles)s
    """

    blurb: str

    value: float

    weight_unit: W24UnitWeight
    length_unit: Optional[W24UnitLength]
