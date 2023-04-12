from typing import Literal

from werk24.models.property.base import W24Property
from werk24.models.value import W24PhysicalQuantity


class W24PropertySurfaceArea(W24Property):
    """Surface Area

    Attributes:
        surface_area (W24PhysicalQuantityRange): Range
            of the surface area. We deliberately chose
            this to be a range - it is possible, that
            that people specify allowed ranges.
    """
    property_type: Literal["SURFACE_AREA"] = "SURFACE_AREA"
    property_subtype: Literal["SURFACE_AREA"] = "SURFACE_AREA"
    surface_area: W24PhysicalQuantity
