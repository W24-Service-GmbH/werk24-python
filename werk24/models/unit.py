from enum import Enum


class W24UnitLength(str, Enum):
    """ Enum of the supported length units
    """
    MILLIMETER = "MILLIMETER"
    INCH = "INCH"


class W24UnitAngle(str, Enum):
    """ Enum of all the supported angle units

    NOTE: currently we are only supporting degrees.
    If you come across a drawing that uses GON, let
    us know, we love the concept!
    """

    DEGREE = "DEGREE"
