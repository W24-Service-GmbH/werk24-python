from datetime import date
from typing import List, Optional

from pydantic import BaseModel

from werk24.models.revision_table import W24GridSquare


class BomQuantity(BaseModel):
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
        serial (Optional[str]): Serial number or Item Number of the part.

        quantity (Optional[str]): Quantity of the part. 

        position (Optional[str]): Position of the part on the 
            assembly. 

        part_number (Optional[str]): Part Number of 
            the part listed in the bill of material.

        designation Optional[str]: Designation/Title of the part

        bom_material (str): Material of the part given in the 
            bill of material.

        weight (str): Weight of the part given in the bill of 
            material.

        grid_squares: (List[W24GridSquare]): List of the grid squares
            that are affected by the bom.
    """
    serial: Optional[str]

    quantity: BomQuantity

    position: Optional[str]

    part_number: Optional[str]

    designation: str

    bom_material: Optional[str]

    weight: Optional[str]

    grid_squares: List[W24GridSquare]


class W24BomTable(BaseModel):
    """ BOM Table object that contains all the
    rows

    Attributes:
        rows (List[W24bomTableRow]): List of all
            rows in the bom table
    """
    rows: List[W24BomTableRow]
