from decimal import Decimal
from pydantic import BaseModel


class W24GeometricShapeCuboid(BaseModel):
    """ Geometric Shape of a cuboid

    Attributes:
        width (Decimal): Width of the cuboid

        height (Decimal): Height of the cuboid

        depth (Decimal): Depth of the cuboid
    """
    width: Decimal
    height: Decimal
    depth: Decimal


class W24GeometricShapeCylinder(BaseModel):
    """ Geometric Shape of a cylinder

    Attributes:
        diameter (Decimal): Diameter of the cylinder

        depths (Decimal): Depth of the cylinder
    """
    diameter: Decimal
    depth: Decimal
