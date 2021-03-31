from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class W24MaterialStandard(str, Enum):
    """ Enum all the supported
    Material Standards
    """

    AUSTENTIC = "AUSTENTIC"
    """ Steel name conventions,
    e.g,. V2A
    """

    BLOB = "BLOB"
    """ Blob material names,
    e.g., steel
    """

    EN10027 = "EN10027"
    """ Material name or material number following
    the EN 10027-1 and EN 10027-2 standard
    """

    EN10210 = "EN10210"
    """ Material make following the EN10210 standard
    for steel tubes
    """

    EN10263 = "EN10263"
    """ Material number following the EN 10264
    standard
    """

    ISO898 = "ISO898"
    """ Material name following the ISO 909
    for metric fasterns.
    """


class W24MaterialReference(BaseModel):
    material_standard: W24MaterialStandard
    material_names: List[str]


class W24Material(BaseModel):
    """ Parsed Material object
    """

    blurb: str
    """ Material Name for human consumption
    """

    material_standard: W24MaterialStandard
    """ Material Standard the designer used
    """

    material_name: str
    """ Nam eof the material in accordance with the
    material standard
    """

    reference_materials: Optional[W24MaterialReference] = None
