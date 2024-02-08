import json
from decimal import Decimal
from test.utils import AsyncTestCase

from werk24.models.radius import W24CurvatureType, W24RadiusLabel
from werk24.models.size import W24Size, W24SizeType


class TestSerialization(AsyncTestCase):

    def test_infinity_serialization(self):
        obj = W24RadiusLabel(
            curvature_type=W24CurvatureType.PLANE,
            size=W24Size(
                blurb="",
                size_type=W24SizeType.NOMINAL,
                nominal_size=Decimal("Infinity"),
            ),
        ).dict()
        des = W24RadiusLabel.parse_obj(obj)
        self.assertEqual(type(des), W24RadiusLabel)
