from enum import Enum
from typing import Literal, Optional

from werk24.models.property.base import W24Property
from werk24.models.value import W24PhysicalQuantityRange


class PropertySurfaceArea(W24Property):
    """Surface Area

    Attributes:
        surface_area (W24PhysicalQuantityRange): Range
            of the surface area. We deliberately chose
            this to be a range - it is possible, that
            that people specify allowed ranges.
    """
    type: Literal["SURFACE_AREA"] = "SURFACE_AREA"
    surface_area: W24PhysicalQuantityRange
