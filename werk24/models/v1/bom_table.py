from typing import List, Optional

from pydantic import BaseModel

from .material import W24MaterialSet
from .value import W24PhysicalQuantity
from .weight import W24Weight


class W24BomTableRow(BaseModel):
    """Row of a BOM table

    Attributes:
    ----------
        serial (Optional[str]): Serial number or Item Number,
            giving the serial number used in BOM table.

        position (Optional[str]): Position Number of the part
            on the assembly is defined using position bubbles.
            This position number is mentioned on the BOM table.

        quantity (Optional[W24PhysicalQuantity]): Quantity of the part is defined
            as Physical Quantity with a value, unit and tolerance.

        part_number (Optional[str]): Part Number of the parts
            listed in the bill of material.

        designation (Optional[str]): Designation/Title of the part
            listed in the bill of material.

        material_option (list[W24MaterialSet]): Material of the part listed in the
            bill of material. These materials could be optional
            set of material that could be applicable for the part.
            For example: Either (Material_A and Material_B)
                            Or (Material_C and Material_D)
                            Here,
                            (Material_A and Material_B) is a material set
                            (Material_C and Material_D) is another material set

        weight (Optional[W24Weight]): Weight of the parts listed in the bill of
            material.

    """

    serial: Optional[str]

    position: Optional[str]

    quantity: Optional[W24PhysicalQuantity]

    part_number: Optional[str]

    designation: Optional[str]

    material_option: List[W24MaterialSet]

    weight: Optional[W24Weight]


class W24BomTable(BaseModel):
    """BOM Table object that contains all the
    rows

    Attributes:
    ----------
        rows (List[W24bomTableRow]): List of all
            rows in the bom table
    """

    rows: List[W24BomTableRow]
