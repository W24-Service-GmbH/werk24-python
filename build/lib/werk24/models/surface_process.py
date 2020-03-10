from enum import Enum


class W24SurfaceProcess(str, Enum):
    """ Enum that lists all surface proceses
    """

    ANY_PERMITTED = "any_permitted"
    SHALL_BE_REMOVED = "shall_be_removed"
    SHALL_NOT_BE_REMOVED = "shall_not_be_removed"
