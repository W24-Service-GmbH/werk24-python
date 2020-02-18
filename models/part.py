from typing import List, Union

from pydantic import BaseModel

from .geometry_turning import W24GeometryTurning
from .illustration import W24Illustration
from .material import W24Material
from .position_group import W24PositionGroup
from .sheet_id import W24SheetId


class W24Part(BaseModel):
    """ The W24Part object describes a part
    extracted from the supplied file.

    NOTE: Keep in mind that a sheet might be
    describing several different parts (e.g., when
    it specifies the dimensions of a part on a table).
    In such cases, Werk24 will return all possible parts,
    even if they are not refered to by a position group.
    """
    sheet_id: W24SheetId = None
    designation: str = None

    geometry: Union[W24GeometryTurning] = None

    material: W24Material = None

    """ When a Cover Page is supplied, Werk24
    extracts the positions and associates them
    with the part
    """
    position_group: W24PositionGroup = None

    illustrations: List[W24Illustration]
