from .placement import W24PlacementEllipse
from pydantic import BaseModel


class W24Balloon(BaseModel):
    """Balloon used for marking a feature on a drawing.

    Attributes:
    ----------
    placement (W24PlacementEllipse): Placement of the Balloon on the different thumbnails
    label (str): Label of the Balloon. Typically an ascending number.
    """

    placement: W24PlacementEllipse
    label: str
