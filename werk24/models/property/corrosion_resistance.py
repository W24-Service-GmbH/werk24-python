from typing import Literal

from werk24.models.property.base import W24Property
from werk24.models.value import W24PhysicalQuantity


class W24PropertyCorrosionResistance(W24Property):
    property_type: Literal["CORROSION_RESISTANCE"] = "CORROSION_RESISTANCE"


class W24PropertyCorrosionResistanceBlurb(W24PropertyCorrosionResistance):
    """Corrosion Resistance indicated as text.
    """
    property_subtype: Literal["BLURB"] = "BLURB"


class W24PropertyCorrosionResistanceIso9227(W24PropertyCorrosionResistance):
    """Corrosion Resistance specified as ISO 9227.

    Attributes:
        procedure (str): Specified Corrosion Resistance procedure.
            See ISO 9227 for details.

        test_time (W24PhysicalQuantity): Specified Test time.
            Typically indicated in hours. Note that we are
            using the units of the drawing.
    """
    property_subtype: Literal["ISO_9227"] = "ISO_9227"
    procedure: str
    test_time: W24PhysicalQuantity
