""" Module containing all W24x dataclasses that are used in its
external API.
"""

import base64
import hashlib
from enum import Enum
from math import cos, degrees, pi, radians
from typing import Dict, List, Union

from pydantic import BaseModel


class W24UnitPositionQuantity(str, Enum):
    """ Unit definition used to describe
    the quantities in positions
    """
    UNITS = "units"
    KILOGRAMM = "kilogramm"


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


class W24Measure(BaseModel):
    """ Tolerated measure with positve and negative tolerances.
    All measures are in Millimeter

    NOTE: Fit measures are translated into positive and
    negative tolerances.
    """
    value: float
    positive_tolerance: float = None
    negative_tolerance: float = None


class W24Position(BaseModel):
    """ Position as listed on the title pages.
    See W24PositionGroup for more details
    """
    position: str
    quantity: float
    quantity_unit: str = W24UnitPositionQuantity.UNITS


class W24SheetId(BaseModel):
    """ The W24SheetId object contains the information
    that is frequently used to refer to a specific sheet

    1. The drawing id as quoted on the sheet or on the
        title page
    2. The respective revision id
    3. The date of the drawing
    """
    drawing_id: str = None
    drawing_revision: str = None
    drawing_date: str = None


class W24MaterialShape(str, Enum):
    """ Enum describing the possible shapes of raw material
    """
    ROD_ROUND = "rod_round"
    ROD_HEXAGON = "rod_hexagon"


class W24MaterialStandard(str, Enum):
    """ Enum of supported material standards
    """
    EN10025 = "EN10025"
    DIN17100 = "DIN17100"
    SAE = "SAE"


class W24StandardMaterial(BaseModel):
    """ W24StandardMaterial describes a material as defined
    by a standardization body.

    NOTE: Werk24 makes an effort to map material names from
    deprecated norms to the most recent standard in each
    geography.
    """
    standard: W24MaterialStandard = W24MaterialStandard.EN10025
    material_name: str


class W24Material(BaseModel):
    """ W24Material describes the shape and type of material
    from which a part is to be produced.

    NOTE: The material_name variable holds the material_name
    as quoted in the document. Werk24 makes an effort to translate
    the information into the most recent standard without changing
    geographies.
    """
    material_name: str
    material_shape: W24MaterialShape = None
    associated_standard_materials: List[W24StandardMaterial] = []


class W24PositionGroup(BaseModel):
    """ A W24PositionGroup contains all position information
    for a given part
    """
    positions: List[W24Position]
    article_number: str
    description: str


class W24ThreadStandard(str, Enum):
    """ Enum of supported thread standards
    """
    ISO1502 = "ISO1502"
    UNIFIED_THREAD_STANDARD = "UNIFIED_THREAD_STANDARD"


class W24ThreadDirection(str, Enum):
    """ Enum of thread directions
    """
    RIGHT = "RIGHT"
    LEFT = "LEFT"


class W24Thread(BaseModel):
    """ A W24Thread contains all information about a thread.
    As the W24Thread object is always associated to a W24Volume,
    it does not contain any information about the diameter
    """
    direction: W24ThreadDirection = W24ThreadDirection.RIGHT
    standard: W24ThreadStandard
    designation: str
    angle: W24Angle = None
    pitch: float = None


class W24GeometryType(str, Enum):
    """ Enum of all the supported GeometryTypes
    """
    TURN_MILL = "TURN_MILL"


class W24Geometry(BaseModel):
    """ The W24Geometry describes the complete geometry
    of a part. It contains a list of W24GeometryVolume
    """
    geometry_type: W24GeometryType
    overall_x_measure: W24Measure
    overall_y_measure: W24Measure
    overall_z_measure: W24Measure


class W24RadiusType(str, Enum):
    """ Enum of the radius types
    """
    CONCAVE = "concave"
    CONVEX = "convex"


class W24Radius(BaseModel):
    """ W24Radius describes a radius (e.g. for the curvature)
    of a volume shell

    The value is  measured in millimeter
    """
    value: float
    radius_type: W24RadiusType


class W24Chamfer(BaseModel):
    """ W24Chamfer describes a chamfer that is associated
    with a side of a W24GeometryTurnMill.

    The information of its diameter is contained in the
    W24GeometryTrunMill object.
    """
    width: W24Measure
    angle: W24Angle


class W24SurfaceProcess(str, Enum):
    """ Enum that lists all surface proceses
    """
    ANY_PERMITTED = "any_permitted"
    SHALL_BE_REMOVED = "shall_be_removed"
    SHALL_NOT_BE_REMOVED = "shall_not_be_removed"


class W24SurfaceMethod(str, Enum):
    """ Enum that lists all surface modificatino methods
    """
    TURNED = "turned"
    GROUND = "ground"
    PLATED = "plated"


class W24SurfaceLay(str, Enum):
    """ Enum that lists all surface lays
    """
    PARALLEL = "parallel"
    PERPENDICULAR = "perpendicular"
    CROSSED = "crossed"
    MULTI_DIRECTIONAL = "multi_directional"
    CIRCULAR = "circular"
    RADIAL = "radial"
    PARTICULATE = "particulate"


class W24SurfaceRequirement(BaseModel):
    """ W24SurfaceRequirement contains the information
    on specific requirements on material surfaces.

    NOTE: As these requirements come in a very wide range,
    they are currently only available as blob.
    """
    blob: str


class W24Surface(BaseModel):
    """ W24Surface describes the surface attributes that
    are generally specified with a surface symbol (see
    for example DIN EN ISO 1302)
    """
    process: W24SurfaceProcess
    requirements: List[W24SurfaceRequirement] = []
    method: W24SurfaceMethod = None
    lay: W24SurfaceLay = None


class W24Volume(BaseModel):
    """ W24Volume is the base model for volumes.
    Each GeometryType derives a volume from it.
    """


class W24ShapeType(str, Enum):
    """Enum of 2D base shapes
    """
    CIRCLE = "CIRCLE"
    SQUARE = "SQUARE"
    HEXAGON = "HEXAGON"


class W24Shape(BaseModel):
    """ Base Model for 2D shapes.
    """
    shape_type: W24ShapeType
    center_x: W24Measure = W24Measure(value=0)
    center_y: W24Measure = W24Measure(value=0)

    @property
    def maximal_diameter(self):
        """ return the maximal diameter of the shape.
        This property needs to be overrridden
        """
        raise NotImplementedError()


class W24ShapeCircle(W24Shape):
    """ 2D Shape of a Circle
    """
    diameter: W24Measure
    shape_type = W24ShapeType.CIRCLE

    @property
    def maximal_diameter(self) -> W24Measure:
        return self.diameter


class W24ShapeHexagon(W24Shape):
    """ 2D Shape of a Hexagon
    """
    inner_diameter: W24Measure
    shape_type = W24ShapeType.HEXAGON

    @property
    def maximal_diameter(self) -> W24Measure:
        return W24Measure(value=self.inner_diameter.value / cos(pi / 6))


class W24VolumeTurnMill(W24Volume):
    """ W24VolumeTurnMill derives from W24Volume and
    describes a 3D Volume in a way that is convenient for
    Turned/Milled parts.
    """
    left_shape: Union[W24ShapeCircle, W24ShapeHexagon]
    left_chamfer: W24Chamfer = None
    left_surface: W24Surface = None

    shell_width: W24Measure
    shell_radius: W24Radius = None
    shell_surface: W24Surface = None
    shell_thread: W24Thread = None

    right_shape: Union[W24ShapeCircle, W24ShapeHexagon]
    right_chamfer: W24Chamfer = None
    right_surface: W24Surface = None


class W24GeometryTurnMill(W24Geometry):
    """ W24GeometryTurnMill derives from W24Geometry
    and describes the part's geometry in a way that
    is convenient for Turned/Milled parts.
    """
    geometry_type = W24GeometryType.TURN_MILL
    outer_contour: List[W24VolumeTurnMill] = []
    left_inner_contour: List[W24VolumeTurnMill] = []
    right_inner_contour: List[W24VolumeTurnMill] = []


class W24AttachmentMimeType(str, Enum):
    """ W24AttachmentMimeType lists the supported mime types
    for attachments. Currently only PNG images can be attached.
    """
    PNG = "image/png"


class W24Attachment(BaseModel):
    """ W24Attachment describes the details of an attachment.
    This is currently only used to attach images (e.g. of renderings
    or extracts from the sheet).
    """
    mime_type: W24AttachmentMimeType = W24AttachmentMimeType.PNG
    attachment_hash: str
    base64_content: str

    @staticmethod
    def from_png(png_content: bytes) -> 'W24Attachment':
        """ Create a new W24 Image instance directly from the bytes of
        a PNG file
        """
        return W24Attachment(
            attachment_hash=hashlib.sha256(png_content).hexdigest(),
            mime_type="image/png",
            base64_content=base64.b64encode(png_content))


W24Attachment.update_forward_refs()


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


class W24Illustration(BaseModel):
    """ W24Illustration associates an attachment by its
    attachment_hash to a W24Part
    """
    attachment_hash: str
    illustration_type: W24IllustrationType


class W24Part(BaseModel):
    """ The W24Part object describes a part
    extracted from the supplied file.

    NOTE: Keep in mind that a sheet might be
    describing several different parts (e.g., when
    it specifies the dimensions of a part on a table).
    In such cases, Werk24 will return all possible parts,
    even if they are not refered to by a position group.
    """
    drawing_id: W24SheetId = None
    drawing_designation: str = None

    geometry: Union[W24GeometryTurnMill] = None

    material: W24Material = None

    """ When a Cover Page is supplied, Werk24
    extracts the positions and assocates them
    with the part
    """
    position_group: W24PositionGroup = None

    illustrations: List[W24Illustration]


class W24Document(BaseModel):
    """ The W24Document is the main response document
    and acts as container for all parts
    """

    schema_version: str = "0.02alpha"
    parts: List[W24Part] = []
    attachments: Dict[str, W24Attachment] = {}
    request_id: str

    unassociated_position_groups: List[W24PositionGroup] = []
