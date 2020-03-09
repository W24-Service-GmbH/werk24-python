from pydantic import BaseModel
from math import degrees, radians


class W24Angle(BaseModel):
    """ W24Angle always in radians
    """
    radians: float

    @staticmethod
    def from_degree(angle_in_degree):
        """ Create a new W24Angle object from a degree measure
        """
        return W24Angle(radians=radians(angle_in_degree))

    @property
    def degrees(self):
        """ obtain the angle in degrees
        """
        return degrees(self.radians)
