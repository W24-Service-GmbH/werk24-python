from pydantic import BaseModel

from .position import W24PositionedFeature


class W24Balloon(BaseModel):
    """Balloon used for marking a feature on a drawing.

    Attributes:
    ----------
    placement (W24PlacementEllipse): Placement of the Balloon on the different thumbnails
    label (str): Label of the Balloon. Typically an ascending number.
    """

    position: W24PositionedFeature
    label: str
