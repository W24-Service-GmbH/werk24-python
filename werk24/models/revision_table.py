from datetime import date
from typing import List, Optional

from pydantic import BaseModel

from .date import W24Date


class W24GridSquare(BaseModel):
    """ Grid Square

    Attributes:
        column (str): Column of the Grid Square

        row (str): Row of the Grid Square

    """
    column: str

    row: str


class W24RevisionTableRow(BaseModel):
    """ Row of a revision table

    Attributes:
        serial (Optional[str]): Serial number,
            also referred to as Index or Position of
            the row in the revision table. The serial number
            is typicall used to identify the revision on
            each individual sheet (e.g., A, B, C or 01, 02, 03)

        ecn_number (Optional[str]): Identifier of the Engineering
            Change Note to uniquely identify the change across multiple
            documents. This is typically a long number and sometimes
            identifies a revision process that affect multiple parts.

        description (str): Description of the change

        revision_date (Optional[date]): Date of the revision

        grid_squares: (List[W24GridSquare]): List of the grid squares
            that are affected by the revision.
    """
    serial: Optional[str]

    ecn_number: Optional[str]

    description: str

    revision_date: Optional[W24Date]

    grid_squares: List[W24GridSquare]


class W24RevisionTable(BaseModel):
    """ Revision Table object that contains all the
    rows

    Attributes:
        rows (List[W24RevisionTableRow]): List of all
            rows in the revision table
    """
    rows: List[W24RevisionTableRow]

