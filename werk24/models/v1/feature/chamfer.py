from typing import Literal

from ..angle import W24AngleLabel
from ..feature.base import W24Feature
from ..size import W24Size
from ..tolerance import W24ToleranceType


class W24FeatureChamfer(W24Feature):
    type: Literal["CHAMFER"] = "CHAMFER"
    size: W24Size
    size_tolerance: W24ToleranceType
    angle: W24AngleLabel
    angle_tolerance: W24ToleranceType
