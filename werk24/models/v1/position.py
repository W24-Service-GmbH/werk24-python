from typing import Literal, Union

from pydantic import BaseModel


class W24Coordinate(BaseModel):
    x: int
    y: int


class W24GeometryEllipse(BaseModel):
    """
    Representation of an Ellipse with center coordinates,
    major and minor radius, and an initial angle of rotation.

    Attributes
    ----------
    center (W24Coordinate): The center coordinates of the ellipse (x, y)
    major_radius (float): Major Radius of the Ellipse
    minor_radius (float): Minor Radius of the Ellipse
    angle (float): Angle of Rotation for the Ellipse (default is 0.0)
    """

    geometry_type: Literal["ELLIPSE"] = "ELLIPSE"

    center: W24Coordinate
    major_radius: float
    minor_radius: float
    angle: float = 0.0


class W24GeometryLine(BaseModel):
    """
    Representation of a Line with start and end coordinates.

    Attributes
    ----------
    start (W24Coordinate): Start coordinates of the Line (x, y)
    end (W24Coordinate): End coordinates of the Line (x, y)
    """

    geometry_type: Literal["LINE"] = "LINE"

    start: W24Coordinate
    end: W24Coordinate


W24GeometryFeature = Union[W24GeometryEllipse, W24GeometryLine]


class W24PositionedFeature(BaseModel):
    """
    Representation of the Ellipse placement on the different thumbnails.

    Attributes:
    ----------
    sheet (W24Ellipse): Position of the Geometrz Feature on he Sheet Thumbnail
    """

    sheet: W24GeometryFeature
