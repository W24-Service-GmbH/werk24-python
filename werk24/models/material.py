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

    EN573 = "EN573"
    """ Material name of materail number following
    the EN573-3 standard for aluminums
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
    """ List of equivalent materials in one of the
    European standards. Either EN10027-1 for steels
    or EN573-3 for aluminums.

    Attributes:
        material_standard: Material standard used for the
            equivalents.
        material_codes: List of equivalent material codes
            in the chosen material_standard
    """
    material_standard: W24MaterialStandard

    material_codes: List[str]


class W24Material(BaseModel):
    """ Parsed Material object that can either be
    associated to the TitleBlock or derived from
    all the available information (including the
    text on the canvas

    Attributes:
        blurb: Material Name for human consumption

        material_standard: Material Standard indicated
            on the technical drawing

        material_code: Name of the material in accordance
            with the material standard

        reference_materials: Optional translation of the
            Material into a list of equivalent materials
    """

    blurb: str

    material_standard: W24MaterialStandard

    material_code: str

    reference_material: Optional[W24MaterialReference] = None
