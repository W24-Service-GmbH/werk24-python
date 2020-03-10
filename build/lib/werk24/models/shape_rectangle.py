from .measure import W24Measure
from .shape import W24Shape
from .shape_type import W24ShapeType


class W24ShapeRectangle(W24Shape):
    """ 2D Shape of a Rectangle
    """

    width: W24Measure
    height: W24Measure
    shape_type = W24ShapeType.RECTANGLE

    @property
    def maximal_diameter(self) -> W24Measure:
        if self.width.value > self.height.value:
            return self.width

        return self.height
