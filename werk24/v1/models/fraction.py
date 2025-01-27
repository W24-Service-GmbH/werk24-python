from pydantic import BaseModel


class W24Fraction(BaseModel):
    """Fractions with 32-bit signed integer numerator and denominator.

    Attributes:
    ----------
    numerator: int
        The numerator of the fraction, an integer.
    denominator: int
        The denominator of the fraction, an integer.

    """

    numerator: int
    denominator: int
