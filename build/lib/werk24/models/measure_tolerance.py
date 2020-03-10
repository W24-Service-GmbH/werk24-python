from pydantic import BaseModel

from .measure import W24Measure


class W24MeasureTolerance(BaseModel):
    edge_start: str
    edge_end: str
    measure: W24Measure
