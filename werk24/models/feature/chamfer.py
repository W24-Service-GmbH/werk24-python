from werk24.models.feature.base import W24Feature
from typing import Literal
from werk24.models.size import W24Size
from werk24.models.tolerance import W24Tolerance
from werk24.models.angle import W24AngleLabel


class W24FeatureChamfer(W24Feature):
    type: Literal["CHAMFER"] = "CHAMFER"
    size: W24Size
    size_tolerance: W24Tolerance
    angle: W24AngleLabel
    angle_tolerance: W24Tolerance
