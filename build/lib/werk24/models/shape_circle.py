from .measure import W24Measure
from .shape import W24Shape
from .shape_type import W24ShapeType


class W24ShapeCircle(W24Shape):
    """ 2D Shape of a Circle
    """

    diameter: W24Measure
    shape_type = W24ShapeType.CIRCLE

    @property
    def maximal_diameter(self) -> W24Measure:
        return self.diameter
