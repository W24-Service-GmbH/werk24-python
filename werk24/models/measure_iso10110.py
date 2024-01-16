""" Data Model for measures according to ISO 10110
    Mainly used in optics industry.

Author: Jochen Mattes
"""

from werk24.models.base_feature import W24BaseFeatureModel


class W24MeasureIso10110(W24BaseFeatureModel):
    """Object for measures following ISO 10110.

    Attributes:
        blurb (str): Raw text that was read.
    """
    blurb: str
