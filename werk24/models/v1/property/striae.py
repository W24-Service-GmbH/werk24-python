from typing import Literal, Union

from pydantic import Field

from .base import W24Property
from .glass_homogeneity import W24Iso10110Grade, W24Iso10110Limits


class W24PropertyStriae(W24Property):
    """Parent for all Striae Properties"""

    property_type: Literal["STRIAE"] = "STRIAE"


class W24PropertyStriaeSchottGrade(W24PropertyStriae):
    """
    Striae Grade following the Schott Grade.

    The previous SCHOTT specification used internally
    adhered to the nomenclature of the MIL specification.
    The specification in the current SCHOTT catalogue,
    in general, excludes striae with grades higher than C.
    (See SCHOTT TIE 25)
    """

    property_subtype: Literal["SCHOTT_GRADE"] = "SCHOTT_GRADE"
    blurb: str = Field(examples=["Striae Class 3"])
    grade: str = Field(examples=["1", "2", "3", "4", "5"])


class W24PropertyStriaeIso10110Grade(W24PropertyStriae):
    """
    Striae Grade following ISO 10110 Part

    ISO 10110 part 4 [7] introduces 5 classes of striae
    grades for finished optical parts. In grades 1-4,
    only striae with intensities greater than 30 nm
    optical path difference are categorized
    (See SCHOTT TIE 25)
    """

    property_subtype: Literal["ISO_10110_GRADE"] = "ISO_10110_GRADE"
    blurb: str = Field(examples=["2/3;1"])
    grade: W24Iso10110Grade


class W24PropertyStriaeIso10110Limits(W24PropertyStriae):
    """
    Striae Limits following ISO 10110 Part
    """

    property_subtype: Literal["ISO_10110_LIMITS"] = "ISO_10110_LIMITS"
    blurb: str = Field(examples=["5* 10^-6; <15nm"])
    grade: W24Iso10110Limits


class W24PropertyStriaeIso12123(W24PropertyStriae):
    """Striae Grade following ISO 12123"""

    property_subtype: Literal["ISO_12123"] = "ISO_12123"
    blurb: str = Field(examples=["SW60", "SW10"])
    grade: str = Field(examples=["SW60", "SW10"])


class W24PropertyStriaeFreeText(W24PropertyStriae):
    """Striae Free Text"""

    free_text: str
    variation_type: Literal["FREETEXT"] = "FREETEXT"


# class W24PropertyStriaeMilG174B(W24PropertyStriae):
#     """
#     Striae Grade following MIL G 174 B.

#     The MIL-G-174 B categorizes striae in a piece of raw
#     glass according to its intensity but without any
#     reference to the striae area and sample thickness.
#     The striae are categorized by four reference samples
#     of cord-like striae into four classes A to D.
#     (See SCHOTT TIE 25)
#     """


#     property_subtype: Literal["MIL_G_1748_B"] = "MIL_G_1748_B"
#     grade: str
W24PropertyStriaeType = Union[
    W24PropertyStriaeSchottGrade,
    W24PropertyStriaeIso10110Grade,
    W24PropertyStriaeIso10110Limits,
    W24PropertyStriaeIso12123,
    W24PropertyStriaeFreeText,
]
