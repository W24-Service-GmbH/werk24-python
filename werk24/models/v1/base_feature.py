from typing import List, Optional

from pydantic import BaseModel

from .balloon import W24Balloon


class W24BaseFeatureCoordinate(BaseModel):
    """Coordinate point

    Attributes:
        x: x position normalized by the thumbnail's width

        y: y position normalized by the thumbnail's height
    """

    x: float
    y: float


class W24BaseFeaturePosition(BaseModel):
    """Position of the Feature on the individual thumbnails normalized
    by the width and height of each thumbnail.

    Each features position is indicated as a list of coordinates. If the
        list only has two elements, you are dealing with a line. If it
        has four or more, you are looking at a polygon

    Attributes:
        page: Position of the Feature on the Page thumbnail

        sheet: Position of the Feature on the Sheet thumbnail

        sectional: Position of the Feature on the Sectional thumbnail

    """

    sheet: List[W24BaseFeatureCoordinate]
    canvas: List[W24BaseFeatureCoordinate]
    sectional: List[W24BaseFeatureCoordinate]


class W24BaseFeatureModel(BaseModel):
    """Base Model for all the features that we might
    extract from the Drawing

    Attributes:
        position: Position of the features on the individual
            thumbnails
    """

    # NOTE: position is optional for the transition period
    position: Optional[W24BaseFeaturePosition] = None
    balloon: Optional[W24Balloon] = None
