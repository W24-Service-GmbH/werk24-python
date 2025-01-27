from decimal import Decimal
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field

from ..value import W24PhysicalQuantity, ureg
from .base import W24Property


class W24Iso10110Grade(BaseModel):
    """ISO 10110 Grade.

    This model contains information about both, the
    homogeneity and the striae and is thus used by
    both models.
    """

    blurb: str = Field(examples=["2/3;1"])
    homogeneity_grade: Optional[str] = Field(examples=["3"], default=None)
    striae_grade: Optional[str] = Field(examples=["1"], default=None)


class W24Iso10110Limits(BaseModel):
    """ISO 10110 Limits for Homogeneity and Wavefront"""

    blurb: str = Field(examples=["5* 10^-6; <15nm"])
    tolerance_limit: Decimal = Field(examples=[Decimal(str("50e-6"))])
    striae_wavefront_deviation_tolerance_limit: Optional[W24PhysicalQuantity] = Field(
        examples=[W24PhysicalQuantity(blurb="15nm", value=15 * ureg.nm)], default=None
    )


class W24PropertyGlasHomogeneity(W24Property):
    # WORKAROUND FOR TYPO
    pass


class W24PropertyGlassHomogeneity(W24Property):
    """Parent for all Glass Homogeneity Properties"""

    property_type: Literal["GLASS_HOMOGENEITY"] = "GLASS_HOMOGENEITY"


class W24PropertyGlassHomogeneitySchottGrade(W24PropertyGlassHomogeneity):
    """Schott Homogeneity Grade"""

    property_subtype: Literal["SCHOTT_GRADE"] = "SCHOTT_GRADE"
    blurb: str = Field(examples=["H1", "H2", "H3"])
    grade: str = Field(examples=["H1", "H2", "H3"])


class W24PropertyGlassHomogeneityIso10110Grade(W24PropertyGlassHomogeneity):
    """ISO 10110 Homogeneity Grade"""

    property_subtype: Literal["ISO_10110_GRADE"] = "ISO_10110_GRADE"
    blurb: str = Field(examples=["2/3;1"])
    grade: W24Iso10110Grade


class W24PropertyGlassHomogeneityIso10110ToleranceLimit(W24PropertyGlassHomogeneity):
    """ISO 10110 Homogeneity Tolerance Limit"""

    property_subtype: Literal["ISO_10110_TOLERANCE_LIMIT"] = "ISO_10110_TOLERANCE_LIMIT"
    blurb: str = Field(examples=["5* 10^-6; <15nm"])
    limits: W24Iso10110Limits


class W24PropertyGlassHomogeneityIso10110NhGrade(W24PropertyGlassHomogeneity):
    """ISO 10110 Homogeneity NH Grade"""

    property_subtype: Literal["ISO_10110_NH_GRADE"] = "ISO_10110_NH_GRADE"
    blurb: str = Field(examples=["NH040"])
    grade: str = Field(examples=["NH040"])
    tolerance_limit: Decimal = Field(examples=[Decimal(str("40e-6"))])


class W24PropertyGlassHomogeneityFreeText(W24PropertyGlassHomogeneity):
    """Homogeneity Free Text"""

    free_text: str
    variation_type: Literal["FREETEXT"] = "FREETEXT"


W24PropertyGlassHomogeneityType = Union[
    W24PropertyGlassHomogeneitySchottGrade,
    W24PropertyGlassHomogeneityIso10110Grade,
    W24PropertyGlassHomogeneityIso10110ToleranceLimit,
    W24PropertyGlassHomogeneityIso10110NhGrade,
    W24PropertyGlassHomogeneityFreeText,
]
