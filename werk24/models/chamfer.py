""" Defintion of the W24Chamfer class and its support structures


Author: Jochen Mattes - Werk24
"""
from pydantic import BaseModel


class W24Chamfer(BaseModel):
    """ Chamfer in degree.

    NOTE: The chamfers can be tolerated.
    Future implementations wil take this into account.
    """

    blurb: str
    """ String representation for human consumption
    """

    angle: float
    """ Chamfer angle in degrees

    NOTE: If you are dealing with GON, let us know.
    Happy to do exend the API for the pleasure of
    dealing with the concept.
    """
