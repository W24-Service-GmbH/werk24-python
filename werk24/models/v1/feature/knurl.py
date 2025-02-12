from decimal import Decimal
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel

from .base import W24Feature


class W24FeatureKnurlPattern(BaseModel):
    """BaseModel for the Knurl Patterns.

    This is intended to store the common
    attributes across knur patterns. Specifying
    this, requires at minimum the study of the
    ASTM, ISO, DIN, BS and JS standards.
    """


class W24FeatureKnurlPatternDin82BasePattern(str, Enum):

    A = "A"
    B = "B"
    G = "G"
    K = "K"


class W24FeatureKnurlPatternDin82Direction(str, Enum):

    A = "A"
    L = "L"
    R = "R"
    E = "E"
    V = "V"


class W24FeatureKnurlPatternDin82(W24FeatureKnurlPattern):
    """Specification of the Knurling pattern following DIN 82.

    Attributes:
        base_pattern (W24FeatureKnurlPatternDin82BasePattern):
            base pattern of the knurling structure
        direction  (W24FeatureKnurlPatternDin82Direction):
            direction of the knurling pattern
        angle (Decimal): Optional Rotation of the
            pattern.
        partition (Optional[Decimal]): Distance between the
            knurl patterns. Note that the units might depend
            on the referred standard.
    """

    base_pattern: W24FeatureKnurlPatternDin82BasePattern
    direction: W24FeatureKnurlPatternDin82Direction
    angle: Decimal = Decimal("0")
    partition: Optional[Decimal] = None


class W24FeatureKnurl(W24Feature):
    """Knurl Feature"""

    feature_type: Literal["KNURL"] = "KNURL"


class W24FeatureKnurlDin82(W24FeatureKnurl):
    """Knurl Feature according to DIn 82.

    Attributes:
        knurl_pattern (W24FeatureKnurlPattern): Knurl
            Pattern. Note: this will be specific to the
            referred standard.
    """

    feature_subtype: Literal["DIN_82"] = "DIN_82"
    knurl_pattern: W24FeatureKnurlPattern
