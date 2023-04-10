from typing import Literal

from werk24.models.property.base import W24Property
from werk24.models.value import W24PhysicalQuantityRange


class W24PropertyCorrosionResistanceIso9227(W24Property):
    type: Literal["CORROSION_RESISTANCE"] = "CORROSION_RESISTANCE"
    procedure: str
    test_time: W24PhysicalQuantityRange
