from werk24.models.property.base import W24Property
from typing import Literal
from pydantic import Field, BaseModel
from decimal import Decimal
from werk24.models.value import W24PhysicalQuantity, ureg


class W24Iso10110Grade(BaseModel):
    """ISO 10110 Grade.

    This model contains information about both, the
    homogeneity and the striae and is thus used by
    both models.
    """

    blurb: str = Field(examples=["2/3;1"])
    homogeneity_grade: str = Field(examples=["3"])
    striae_grade: str = Field(examples=["1"])


class W24Iso10110Limits(BaseModel):
    """ISO 10110 Limits for Homogeneity and Wavefront"""

    blurb: str = Field(examples=["5* 10^-6; <15nm"])
    tolerance_limit: Decimal = Field(examples=[Decimal(str("50e-6"))])
    striae_wavefront_deviation_tolerance_limit: W24PhysicalQuantity = Field(
        examples=[W24PhysicalQuantity(blurb="15nm", value=15 * ureg.nm)]
    )


class W24PropertyGlasHomogeneity(W24Property):
    """Parent for all Glas Homogeneity Properties"""

    property_type: Literal["GLAS_HOMOGENEITY"] = "GLAS_HOMOGENEITY"


class W24PropertyGlasHomogeneitySchottGrade(W24PropertyGlasHomogeneity):
    """Schott Homogeneity Grade"""

    property_type: Literal["SCHOTT_GRADE"] = "SCHOTT_GRADE"
    blurb: str = Field(examples=["H1", "H2", "H3"])
    grade: str = Field(examples=["H1", "H2", "H3"])


class W24PropertyGlasHomogeneityIso10110Grade(W24PropertyGlasHomogeneity):
    """ISO 10110 Homogeneity Grade"""

    property_type: Literal["ISO_10110_GRADE"] = "ISO_10110_GRADE"
    blurb: str = Field(examples=["2/3;1"])
    grade: W24Iso10110Grade


class W24PropertyGlasHomogeneityIso10110ToleranceLimit(W24PropertyGlasHomogeneity):
    """ISO 10110 Homogeneity Tolerance Limit"""

    property_type: Literal["ISO_10110_TOLERANCE_LIMIT"] = "ISO_10110_TOLERANCE_LIMIT"
    blurb: str = Field(examples=["5* 10^-6; <15nm"])
    limits: W24Iso10110Limits


class W24PropertyGlasHomogeneityIso10110NhGrade(W24PropertyGlasHomogeneity):
    """ISO 10110 Homogeneity NH Grade"""

    property_type: Literal["ISO_10110_NH_GRADE"] = "ISO_10110_NH_GRADE"
    blurb: str = Field(examples=["NH040"])
    grade: str = Field(examples=["NH040"])
    tolerance_limit: Decimal = Field(examples=[Decimal(str("40e-6"))])
