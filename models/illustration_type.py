from enum import Enum


class W24IllustrationType(str, Enum):
    """ Enum of supported illustrations
    """
    Z_PLANE_LEFT = "z_plane_left"
    Z_PLANE_INNER = "z_plane_inner"
    Z_PLANE_RIGHT = "z_plane_right"
    Z_PLANE_COMPLEX = "z_plane_complex"
    X_PLANE_OUTER = "x_plane_outer"
    X_PLANE_INNER = "x_plane_inner"
    X_PLANE_COMPLEX = "x_plane_complex"
    Y_PLANE_INNER = "y_plane_inner"
    Y_PLANE_OUTER = "y_plane_outer"
    Y_PLANE_COMPLEX = "y_plane_complex"
    RENDERING = "rendering"
