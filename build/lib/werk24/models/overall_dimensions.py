from enum import Enum

from pydantic import BaseModel

from .measure import W24Measure


class W24OverallDimensionsShape(str, Enum):
    ROD_ROUND = "ROD_ROUND"
    ROD_HEXAGON = "ROD_HEXAGON"
    ROD_SQUARE = "ROD_SQUARE"


class W24OverallDimensions(BaseModel):
    shape: W24OverallDimensionsShape
    x_measure: W24Measure
    y_measure: W24Measure
    z_measure: W24Measure
