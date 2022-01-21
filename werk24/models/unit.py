from enum import Enum


class W24UnitLength(str, Enum):
    """ Enum of the supported length units
    """
    METER = "METER"
    DECIMETER = "DECIMETER"
    CENTIMETER = "CENTIMETER"
    MILLIMETER = "MILLIMETER"
    FOOT = "FOOT"
    INCH = "INCH"
    MICRO_INCH = "MICRO_INCH"


class W24UnitAngle(str, Enum):
    """ Enum of all the supported angle units

    NOTE: currently we are only supporting degrees.
    If you come across a drawing that uses GON, let
    us know, we love the concept!
    """
    DEGREE = "DEGREE"


class W24UnitWeight(str, Enum):
    """ Enum of all the supported weights

    NOTE: This also includes relative weights
    such as kilogram per meter

    """

    # Absolute weights
    GRAM = "GRAM"
    KILOGRAM = "KILOGRAM"
    POUND = "POUND"
    OUNCE = "OUNCE"


class W24UnitSystem(str, Enum):
    """ Unit System that is used for a certain feature
    """
    METRIC = "METRIC"
    IMPERIAL = "IMPERIAL"
