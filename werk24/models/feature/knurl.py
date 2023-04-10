from decimal import Decimal
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel

from werk24.models.feature.base import W24Feature


class W24FeatureKnurlPattern(BaseModel):
    """BaseModel for the Knurl Patterns.
    This is intended to store the common
    attributes across knur patterns. Specifying
    this, requires at minimum the study of the
    ASTM, ISO, DIN, BS and JS standards.
    NOTE: there are also Swiss knurling patterns
    that seem to follow a different pattern.
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
    base_pattern: W24FeatureKnurlPatternDin82BasePattern
    direction: W24FeatureKnurlPatternDin82Direction
    angle: Optional[Decimal]


class W24FeatureKnurl(W24Feature):
    type: Literal["KNURL"] = "KNURL"
    knurl_pattern: W24FeatureKnurlPattern
    partition: Optional[Decimal]


class W24PropertyHardnessRockwellScale(str, Enum):
    A = "A"
    B = "BW"
    C = "C"
    D = "D"
    E = "EW"
    F = "FW"
    G = "GW"
    H = "HW"
    K = "KW"
    _15N = "15N"
    _30N = "30N"
    _45N = "45N"
    _15T = "15TW"
    _30T = "30TW"
    _45T = "45TW"
