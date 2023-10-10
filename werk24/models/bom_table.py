from typing import List, Optional

from pydantic import BaseModel

from werk24.models.material import W24MaterialOption
from werk24.models.weight import W24Weight
from werk24.models.value import W24PhysicalQuantity


class W24BomQuantity(BaseModel):
    """Quantity of parts listed in BOM

    Args:
        quantity (str): Quantity of the part. 
        unit (Optional[str]): Unit of the quantity. 
    """
    quantity: str
    unit: Optional[str]


class W24BomTableRow(BaseModel):
    """ Row of a BOM table

    Attributes:
    ----------
        serial (Optional[str]): Serial number or Item Number, 
            giving the serial number used in BOM table.

        position (Optional[str]): Position Number of the part 
            on the assembly is defined using position bubbles. 
            This position number is mentioned on the BOM table. 

        quantity (W24PhysicalQuantity): Quantity of the part is defined
            as Physical Quantity with a value, unit and tolerance.

        part_number (Optional[str]): Part Number of the parts 
            listed in the bill of material.

        designation Optional[str]: Designation/Title of the part
            listed in the bill of material.

        material_option (str): Material of the part listed in the 
            bill of material. These materials could be optional 
            set of material that could be applicable for the part. 
            For example: Either (Material_A and Material_B)
                            Or (Material_C and Material_D)

        weight (str): Weight of the parts listed in the bill of 
            material.

    """
    serial: Optional[str]

    position: Optional[str]

    quantity: Optional[W24PhysicalQuantity]

    part_number: Optional[str]

    designation: Optional[str]

    material_option: Optional[W24MaterialOption]

    weight: Optional[W24Weight]


class W24BomTable(BaseModel):
    """ BOM Table object that contains all the
    rows

    Attributes:
    ----------
        rows (List[W24bomTableRow]): List of all
            rows in the bom table
    """
    rows: List[W24BomTableRow]
