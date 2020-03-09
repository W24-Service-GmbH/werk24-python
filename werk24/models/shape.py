from pydantic import BaseModel
from .measure import W24Measure
from .shape_type import W24ShapeType


class W24Shape(BaseModel):
    """ Base Model for 2D shapes.
    """
    shape_type: W24ShapeType
    center_x: W24Measure = W24Measure(value=0)
    center_y: W24Measure = W24Measure(value=0)

    @property
    def maximal_diameter(self):
        """ return the maximal diameter of the shape.
        This property needs to be overrridden
        """
        raise NotImplementedError()
