from decimal import Decimal
from enum import Enum
from typing import List

from pydantic import BaseModel

from .gdt import W24GDTCharacteristic
from .material import W24Material
from .roughness import W24RoughnessGrade
from .tolerance import W24ToleranceGrade


class W24BaseGeometry(str, Enum):
    """
    Material Shape Enum

    Enum for the different shapes of the material.
    There does not seem to be a standard for this, but rather
    a list of conventions that are used in the industry.

    We are trying to keep this list as short as possible and
    the want to ensure clear cuts among classes.

    PLATE: A plate is a flat material that is at most 17mm thick.
    This also includes sheets (typically thinner than 6mm).

    BLOCK: A block is a material that has a rectangular shape
    and is thicker than 17mm. This also includes bars (which are
    typically longer in one dimension).

    ROD: A rod is a cylindrical material. This also includes wires
    (which are typically thin and flexible), and currently includes
    tubes (which are hollow cylinders).

    TUBE: Reserved for future use!
    """

    PLATE = "PLATE"  # or SHEET or SLAB
    BLOCK = "BLOCK"  # or BAR or INGOT or BILLET or BLOOM
    ROD = "ROD"  # or WIRE or TUBE (for now)
    TUBE = "TUBE"  # reserved for future use!


class W24ComplexityToleranceCount(BaseModel):
    tolerance_grade: W24ToleranceGrade
    count: int


class W24ComplexityRoughnessCount(BaseModel):
    roughness_grade: W24RoughnessGrade
    count: int


class W24ComplexityGDTCount(BaseModel):
    characteristic: W24GDTCharacteristic
    value: Decimal
    count: int


class W24Complexity(BaseModel):
    """
    Manufacturing Complexity

    This class describes the complexity of the manufacturing process of the
    part. This can be used to determine the cost of the part, the time it
    takes to manufacture it, and the required expertise.

    Attributes:
    ----------

    stock_shape (W24StockShape): The shape of the stock material that is
        required to manufacture the part. This can be a PLATE, BLOCK, ROD,
        or TUBE.

    number_of_required_axes (int): The number of axes that are required to
        manufacture the part. This can be 2, 3, 4, or 5. Together with the
        stock_shape, the material category and the customer industry, this
        can be used to determien the main manufacturing process.

    materials (List[W24Material]): List of materials that are required to
        manufacture the part. This can be a list of different materials
        that are used in the part.

    tolerance_distribution (List[W24ComplexityToleranceTally]): List of
        tolerance tallies that are required to manufacture the part. This
        can be used to determine the required precision of the part.
    """

    stock_shape: W24BaseGeometry
    number_of_required_axes: int
    materials: List[W24Material]
    tolerance_distribution: List[W24ComplexityToleranceCount]
    roughness_distribution: List[W24ComplexityRoughnessCount]
    gdt_distribution: List[W24ComplexityGDTCount]
