""" Just your basic unit defintions

Author: Jochen Mattes - Werk24
"""
from enum import Enum


class W24UnitLength(str, Enum):
    """ Enum of the supported length units
    """
    MILLIMETER = "MILLIMETER"
    INCH = "INCH"
