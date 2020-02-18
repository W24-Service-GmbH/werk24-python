from typing import List

from pydantic import BaseModel

from .geometry_type import W24GeometryType
from .measure import W24Measure
from .measure_tolerance import W24MeasureTolerance


class W24Geometry(BaseModel):
    """ The W24Geometry describes the complete geometry
    of a part. It contains a list of W24GeometryVolume
    """
    geometry_type: W24GeometryType
    overall_x_measure: W24Measure
    overall_y_measure: W24Measure
    overall_z_measure: W24Measure
    measure_tolerances: List[W24MeasureTolerance] = []
