""" Data Model for measures according to ISO 10110
    or DIN 3140 or similar standards. Mainly used 
    in optics industry.

Author: Jochen Mattes
"""

from werk24.models.base_feature import W24BaseFeatureModel


class W24MeasureIso10110(W24BaseFeatureModel):
    """Object for measures following ISO 10110
        or DIN 3140.For example: 
        ISO 10110 : 6/4/4/6 2
        DIN 3140 : 3/ 2(1) according to DIN 3140
    Attributes:
        blurb (str): Raw text that was read.
    """
    blurb: str
