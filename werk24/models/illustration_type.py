from enum import Enum


class W24IllustrationType(str, Enum):
    """ Enum of supported illustrations
    """

    Z_SECTIONAL_LEFT = "z_sectional_left"
    Z_SECTIONAL_INNER = "z_sectional_inner"
    Z_SECTIONAL_RIGHT = "z_sectional_right"
    Z_SECTIONAL_COMPLEX = "z_sectional_complex"
    X_SECTIONAL_OUTER = "x_sectional_outer"
    X_SECTIONAL_INNER = "x_sectional_inner"
    X_SECTIONAL_COMPLEX = "x_sectional_complex"
    Y_SECTIONAL_INNER = "y_sectional_inner"
    Y_SECTIONAL_OUTER = "y_sectional_outer"
    Y_SECTIONAL_COMPLEX = "y_sectional_complex"
    RENDERING = "rendering"
