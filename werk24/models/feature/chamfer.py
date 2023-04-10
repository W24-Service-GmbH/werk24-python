from werk24.models.feature.base import W24Feature
from typing import Literal
from werk24.models.size import W24Size, W24SizeTolerance
from werk24.models.angle import W24Angle, W24AngleTolerance


class W24FeatureChamfer(W24Feature):
    type: Literal["CHAMFER"] = "CHAMFER"
    size: W24Size
    size_tolerance: W24SizeTolerance
    angle: W24Angle
    angle_tolerance: W24AngleTolerance
