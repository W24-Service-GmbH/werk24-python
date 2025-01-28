from typing import Literal

from ..property.base import W24Property
from ..value import W24PhysicalQuantity


class W24PropertyWeight(W24Property):
    """Weight of the Part.

    NOTE: this might in the future be extended by another
    attribute that indicates whether the weight was measured
    or calculated.

    Attributes:
        value: weight in the units indicated on the drawing.
    """

    property_type: Literal["WEIGHT"] = "WEIGHT"
    property_subtype: Literal["WEIGHT"] = "WEIGHT"
    weight: W24PhysicalQuantity
