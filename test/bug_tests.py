from werk24.models.ask import W24AskVariantProcesses, deserialize_ask
from werk24.models.tolerance import W24Tolerance, W24ToleranceGeneral
from test.utils import AsyncTestCase
import json


class TestGeometricShape(AsyncTestCase):
    def test_w24askprocesses(self):
        """Bug: Deserialization of W24AskVariantProcesses

        This caused an exception and we simply want
        it to pass.
        """
        obj = W24AskVariantProcesses()
        serialized = json.loads(obj.json())
        deserialize_ask(serialized)

    def test_typed_serialization(self):
        obj = W24ToleranceGeneral().dict()
        a = W24Tolerance.parse_obj(obj)
        print(type(a))
