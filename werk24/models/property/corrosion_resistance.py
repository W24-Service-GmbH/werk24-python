from typing import Literal

from werk24.models.physical_quantity import W24PhysicalQuantityRange
from werk24.models.property.base import W24Property


class W24PropertyCorrosionResistanceIso9227(W24Property):
    type: Literal["CORROSION_RESISTANCE"] = "CORROSION_RESISTANCE"
    procedure: str
    test_time: W24PhysicalQuantityRange
