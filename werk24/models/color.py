"""Color Models.
"""
from pydantic import BaseModel
from enum import Enum


class W24ColorSystem(str, Enum):
    """Color Systems.

    Multiple color systems exist. Ranging from pure
    textual descriptions to highly-standardized systems.

    In the current implementation we do not make these
    colors comparable - their appearance might even
    vary across materials.

    Rather, we start with the simple implementation of
    the RAL system. At later stages, other color system
    could follow.
    """
    BLURB = "BLURB"
    RAL = "RAL"
    # FED_STD_595 = "FED_STD_595"
    # CIE = "CIE"
    # PANTONE = "PANTONE"
    # HKS = "HKS"
    # NCS = "NCS"


class W24Color(BaseModel):
    """W24 Model for Colors.

    Attributes:
        blurb (str): String representation for human consumption

        system: Color system used to specify
            the color.

        designation: Color designation in the corresponding
            system.
    """
    blurb: str
    system: W24ColorSystem
    designation: str
