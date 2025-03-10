from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from .base_feature import W24BaseFeatureModel
from .bom_table import W24BomTable
from .general_tolerances import W24GeneralTolerances
from .language import W24Language
from .material import W24Material
from .projection_method import W24ProjectionMethod
from .property.color import W24PropertyColor
from .roughness import W24GeneralRoughness, W24RoughnessReference
from .unit import W24UnitSpecification
from .weight import W24Weight


class W24TitleBlockItem(W24BaseFeatureModel):
    """Per-Language caption or value

    Attributes:

        language: Language in accordance with the ISO/639-2B standards

        text: Text of the identification
    """

    language: Optional[W24Language]

    text: str


class W24CaptionValuePair(BaseModel):
    """Caption-Value pair for that were found on the Title Block.

    Attributes:

        blurb: Caption-Value pair for human consumption

        captions: List of captions in different languages.
            This will only return the languages that were detected and
            NOT translate the captions into languages that are not present
            on the drawing. This behavior might however change in the
            future.
    """

    blurb: str
    captions: List[W24TitleBlockItem]
    values: List[W24TitleBlockItem]


class W24IdentifierType(str, Enum):
    """List of Identifier Types supported by Werk24"""

    ASSEMBLY_NAME = "ASSEMBLY_NAME "
    ASSEMBLY_NUMBER = "ASSEMBLY_NUMBER"
    CAGE_CODE = "CAGE_CODE"
    CONTRACT_NUMBER = "CONTRACT_NUMBER"
    CUSTOMER_NAME = "CUSTOMER_NAME"
    CUSTOMER_NUMBER = "CUSTOMER_NUMBER"
    DOCUMENT_NUMBER = "DOCUMENT_NUMBER"
    DRAWING_NUMBER = "DRAWING_NUMBER"
    ERP_NUMBER = "ERP_NUMBER"
    IDENTIFICATION_NUMBER = "IDENTIFICATION_NUMBER"
    ITEM_NUMER = "ITEM_NUMER"
    MANUFACTURER_NAME = "MANUFACTURER_NAME"
    MANUFACTURER_NUMBER = "MANUFACTURER_NUMBER"
    NUMBER = "NUMBER"
    ORDER_NAME = "ORDER_NAME"
    ORDER_NUMBER = "ORDER_NUMBER"
    PART_NUMBER = "PART_NUMBER"
    PRODUCT_GROUP = "PRODUCT_GROUP"
    REPLACED_BY = "REPLACED_BY"
    REPLACEMENT_FOR = "REPLACEMENT_FOR"


class W24IdentifierStakeholder(str, Enum):
    """List of Stakeholders that can be identified by Werk24"""

    SUPPLIER = "SUPPLIER"
    OWNER = "OWNER"
    CUSTOMER = "CUSTOMER"


class W24IdentifierPeriod(str, Enum):
    """List of Period Identifiers that can be identified by Werk24"""

    PREVIOUS = "PREVIOUS"
    CURRENT = "CURRENT"
    FUTURE = "FUTURE"


class W24IdentifierPair(W24CaptionValuePair):
    """Caption-Value Pair for Identifies

    Attributes:
        identifier_type (W24IdentifierType): Type of identifier.
    """

    identifier_type: W24IdentifierType
    stakeholder: Optional[W24IdentifierStakeholder] = None
    period: Optional[W24IdentifierPeriod] = None


class W24FileExtensionType(str, Enum):
    """
    Enum of the extension types.

    For example, pdf and idw extensions will be mapped to
    DRAWING, while step and stl extensions will be mapped
    to MODEL.
    """

    DRAWING = "DRAWING"
    MODEL = "MODEL"
    UNKNOWN = "UNKNOWN"


class W24FilePathType(str, Enum):
    """
    Enum of the file path types, indicating whether a
    POSIX (unix) or WINDOWS path is used. When only a filename
    is indicated, the value will be UNKNOWN
    """

    POSIX = "POSIX"
    WINDOWS = "WINDOWS"
    UNKNOWN = "UNKNOWN"


class W24Filename(W24BaseFeatureModel):
    """
    Object describing all the information that we can
    deduce from a filename that was found on the TitleBlock

    Attributes:

        blurb: Filename and Path as it was found on the drawing.
            Example: /path/to/drawing.pdf

        filename: Filename without the prefix.
            Example drawing.pdf

        extension: Extension of the filename.
            Examples: .pdf, .tar.gz

        extension_type: filetype indicated by the extension. PDF, ...
            extensions are mapped to DRAWING, while STEP, ...
            extensions are mapped to MODEL

        path_type: WINDOWS or POSIX (unix) path types if we have
            found an absolute path. UNKNOWN if we only read
            a filename without prefix.
    """

    blurb: str

    filename: str

    extension: str

    extension_type: W24FileExtensionType

    path_type: W24FilePathType


class W24TitleBlock(BaseModel):
    """
    Information that could be extracted from the Title Block.

    Attributes:

        designation: Designation of the Sheet on the Title Block

        drawing_id: Main Identification Number of the Drawing

        part_ids: List of Part IDs that are located on the drawing.
            Keep in mind that the drawing might define multiple
            variants that each specify their own part id

        reference_ids: List of all the identifiers that we found on the
            drawing. The reference ids will hold all the ids that we found
            on the drawing. These will include both the drawing/part numbers
            as well as all the other ids that we identified in addition,
            such as the Order number, the Item number and so on.

        general_tolerances: General Tolerances quoted on the TitleBlock

        material: Material which is quoted on the TitleBlock

        material_number: Optional Material Number. The material number
            if often present on corporate drawings and typically
            corresponds to a unique material number in the customer's
            material master data. The material number is thus specific
            to the company that maintains the master data and obtaining
            the material specification requires access to that database.

        weight: Weight as read from the TitleBlock. NOTE: this is not
            cross-checked with the material and volume of the part,
            but provided as it was read on the TitleBlock.

        filename_drawing: Filename of the drawing if it is explicitly
            indicated on the title block

        colors: List of colors detected on the TitleBlock or in the
            canvas notes.

        bom_table: Reference to the Bill of Material Table. None
            if you are running on an old client or when no BOM
            table was found.

        general_roughnesses (List[W24GeneralRoughness]): List of the
            detected general roughnesses.

        reference_roughnesses (List[W24RoughnessReference]): List of the
            detected reference roughnesses.

        unit_specifications (List[W24UnitSpecification]): List of the detected
            unit specifications.

        projection_method (W24ProjectionMethod): Projection method indicated on the drawing.
            None if no projection method was detected.
    """

    designation: Optional[W24CaptionValuePair]

    drawing_id: Optional[W24CaptionValuePair]
    part_ids: List[W24CaptionValuePair] = []
    reference_ids: List[W24IdentifierPair] = []

    general_tolerances: Optional[W24GeneralTolerances]

    material: Optional[W24Material]
    material_number: Optional[W24CaptionValuePair] = None

    weight: Optional[W24Weight]

    filename_drawing: Optional[W24Filename] = None

    colors: List[W24PropertyColor] = []

    bom_table: Optional[W24BomTable] = None

    general_roughnesses: List[W24GeneralRoughness] = []

    reference_roughnesses: List[W24RoughnessReference] = []

    unit_specifications: List[W24UnitSpecification] = []

    projection_method: Optional[W24ProjectionMethod] = Field(
        None,
        description="Projection method indicated on the drawing. None if no projection method was detected.",
        examples=[W24ProjectionMethod.FIRST_ANGLE, W24ProjectionMethod.THIRD_ANGLE],
    )
