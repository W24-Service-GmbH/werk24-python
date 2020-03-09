from math import cos, pi
from .measure import W24Measure
from .shape import W24Shape
from .shape_type import W24ShapeType


class W24ShapeHexagon(W24Shape):
    """ 2D Shape of a Hexagon
    """
    inner_diameter: W24Measure
    shape_type = W24ShapeType.HEXAGON

    @property
    def maximal_diameter(self) -> W24Measure:
        return W24Measure(value=self.inner_diameter.value / cos(pi / 6))
