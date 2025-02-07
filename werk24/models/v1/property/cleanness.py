from enum import Enum
from typing import Literal

from ..property.base import W24Property


class W24PropertyCleanness(W24Property):
    """Cleanness Property."""

    property_type: Literal["CLEANNESS"] = "CLEANNESS"


class W24PropertyCleannessTypeDin8592(str, Enum):
    CLEANED = "CLEANED"
    SCALE_REMOVED = "SCALE_REMOVED"
    RUST_REMOVED = "RUST_REMOVED"
    COATING_REMOVED = "COATING_REMOVED"
    GREASE_REMOVED = "GREASE_REMOVED"
    DUST_REMOVED = "DUST_REMOVED"
    SHOOT_REMOVED = "SHOOT_REMOVED"
    STERILIZED = "STERILIZED"
    DISINFECTED = "DISINFECTED"
    DECONTAMINATED = "DECONTAMINATED"


class W24PropertyCleannessDin8592(W24PropertyCleanness):
    """DIN 8592 Cleanness Specification.

    DIN 8592 specifies a whole range of
    cleanness targets. These cleanness
    targets are specific to the type
    of impurity that shall be removed.

    Free of Rust for example does not
    mean that the part is sterilized.

    NOTE: Future implementation will likely
    include the cleanness level as well. Be
    aware that they are measured differently
    in different industries / countries.

    Attributes:
        cleanness_type (W24PropertyCleannessTypeDin8592):
            Cleanness Type for which the cleanness
            level should be achieved.
    """

    property_subtype: Literal["DIN_8592"] = "DIN_8592"
    cleanness_type: W24PropertyCleannessTypeDin8592
