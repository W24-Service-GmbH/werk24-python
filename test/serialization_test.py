import json
from decimal import Decimal
from test.utils import AsyncTestCase

from werk24.models.ask import W24AskVariantProcesses, deserialize_ask
from werk24.models.radius import W24CurvatureType, W24Radius, W24RadiusLabel
from werk24.models.size import W24Size
from werk24.models.tolerance import W24Tolerance, W24ToleranceGeneral


class TestSerialization(AsyncTestCase):

    def test_infinity_serialization(self):
        obj = W24RadiusLabel(
            curvature_type=W24CurvatureType.PLANE,
            size=W24Size(nominal_size=Decimal("Infinity")),
        ).dict()
        des = W24RadiusLabel.parse_obj(obj)
        self.assertEqual(type(des), W24RadiusLabel)
