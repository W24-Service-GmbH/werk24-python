from pydantic import BaseModel


class W24Coordinate(BaseModel):
    x: int
    y: int


class W24Ellipse(BaseModel):
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

    center: W24Coordinate
    major_radius: float
    minor_radius: float
    angle: float = 0.0


class W24PlacementEllipse(BaseModel):
    """
    Representation of the Ellipse placement on the different thumbnails.

    Attributes:
    ----------
    sheet (W24Ellipse): Placement of the Ellipse on the Sheet thumbnail
    canvas (W24Ellipse): Placement of the Ellipse on the Canvas thumbnail
    sectional (W24Ellipse): Placement of the Ellipse on the Sectional thumbnail
    """

    sheet: W24Ellipse
    canvas: W24Ellipse
    sectional: W24Ellipse
