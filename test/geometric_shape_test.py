from werk24.models.geometric_shape import W24GeometricShapeCuboid
from test.utils import AsyncTestCase


class TestGeometricShape(AsyncTestCase):

    def test_geometric_shape_encloses_parallel_positive_limit(
        self
    )-> None:
        """ Machine its into itself?
        """
        machine = W24GeometricShapeCuboid(width=100, height=200, depth=300)
        self.assertTrue(machine.encloses(machine, allow_width_depth_rotation=False))

    def test_geometric_shape_encloses_parallel_negative(
        self
    )-> None:
        """ Too large cuboids are rejected?
        """
        machine = W24GeometricShapeCuboid(width=100, height=200, depth=300)
        part = W24GeometricShapeCuboid(width=101, height=200, depth=300)
        self.assertFalse(machine.encloses(part, allow_width_depth_rotation=False))
    
    def test_geometric_shape_encloses_diagonal_positive(
        self
    )-> None:
        """ Diagonal shapes are accepted?
        """
        machine = W24GeometricShapeCuboid(width=300, height=200, depth=100)
        part = W24GeometricShapeCuboid(width=310, height=1, depth=1)
        self.assertTrue(machine.encloses(part, allow_width_depth_rotation=True))

    def test_geometric_shape_encloses_diagonal_positive_limit(
        self
    )-> None:
        """ Diagonal shapes at the limit are accepted?
        """
        machine = W24GeometricShapeCuboid(width=300, height=200, depth=100)
        part = W24GeometricShapeCuboid(width=310, height=1, depth=1.969)
        self.assertTrue(machine.encloses(part, allow_width_depth_rotation=True))

    def test_geometric_shape_encloses_diagonal_positive_limit(
        self
    )-> None:
        """ Diagonal shapes beyond limit are rejected?
        """
        machine = W24GeometricShapeCuboid(width=300, height=1, depth=100)
        part = W24GeometricShapeCuboid(width=310, height=1, depth=2)
        self.assertTrue(machine.encloses(part, allow_width_depth_rotation=True))

    def test_geometric_shape_encloses_diagonal_negative_height(
        self
    )-> None:
        """ Are high parts rejected?
        """
        machine = W24GeometricShapeCuboid(width=300, height=200, depth=100)
        part = W24GeometricShapeCuboid(width=310, height=201, depth=1.969)
        self.assertFalse(machine.encloses(part, allow_width_depth_rotation=True))
