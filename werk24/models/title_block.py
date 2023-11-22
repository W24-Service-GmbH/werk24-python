from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, validator

from werk24.models.bom_table import W24BomTable
from werk24.models.property.color import W24PropertyColor

from .base_feature import W24BaseFeatureModel
from .general_tolerances import W24GeneralTolerances
from .language import W24Language
from .material import W24Material
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

    CUSTOMER_NUMBER = "CUSTOMER_NUMBER"
    DRAWING_NUMBER = "DRAWING_NUMBER"
    DOCUMENT_NUMBER = "DOCUMENT_NUMBER"
    ERP_NUMBER = "ERP_NUMBER"
    IDENTIFICATION_NUMBER = "IDENTIFICATION_NUMBER"
    ITEM_NUMBER = "ITEM_NUMBER"
    MANUFACTURER_NUMBER = "MANUFACTURER_NUMBER"
    ORDER_NUMBER = "ORDER_NUMBER"
    PART_NUMBER = "PART_NUMBER"
    PROJECT_NUMBER = "PROJECT_NUMBER"
    SUPPLIER_NUMBER = "SUPPLIER_NUMBER"


class W24IdentifierPair(W24CaptionValuePair):
    """Caption-Value Pair for Identifies

    Attributes:
        identifier_type (W24IdentifierType) Type of identifier.
    """

    identifier_type: W24IdentifierType


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

    @validator("designation", pre=True)
    def designation_validator(
        cls, raw: Dict[str, Any]
    ) -> Optional[W24CaptionValuePair]:
        """
        Workaround to deal with the transition period
        while we move from the single-value to the multi-value
        pairs.

        This code can be removed after we complete the
        transition.

        Args:

            raw (Dict[str, Any]): Unparsed value returned
                from the API

        Returns:

            W24CaptionValuePair: Parse value-caption pair
        """
        return cls._parse_caption_value_pair(raw)

    @validator("drawing_id", pre=True)
    def drawing_id_validator(cls, raw: Dict[str, Any]) -> Optional[W24CaptionValuePair]:
        """
        Workaround to deal with the transition period
        while we move from the single-value to the multi-value
        pairs.

        This code can be removed after we complete the
        transition.

        Args:

            raw (Dict[str, Any]): Unparsed value returned
                from the API

        Returns:

            W24CaptionValuePair: Parse value-caption pair
        """
        return cls._parse_caption_value_pair(raw)

    @validator("reference_ids", pre=True)
    def reference_ids_validator(
        cls, raw: List[Dict[str, Any]]
    ) -> List[W24CaptionValuePair]:
        """
        Workaround to deal with the transition period
        while we move from the single-value to the multi-value
        pairs.

        This code can be removed after we complete the
        transition.

        Args:

            raw (List[Dict[str, Any]]): Unparsed value returned
                from the API

        Returns:

            List[W24CaptionValuePair]: Parse value-caption pair
        """
        result = [cls._parse_caption_value_pair(e) for e in raw]
        return [r for r in result if r is not None]

    @staticmethod
    def _parse_caption_value_pair(
        raw: Optional[Dict[str, Any]]
    ) -> Optional[W24CaptionValuePair]:
        """
        Workaround to deal with the transition period
        while we move from the single-value to the multi-value
        pairs.

        This code can be removed after we complete the
        transition.

        Args:

            raw (Dict[str, Any]): Unparsed value returned
                from the API

        Returns:

            W24CaptionValuePair: Parse value-caption pair
        """
        if isinstance(raw, W24CaptionValuePair):
            return raw

        if raw is None:
            return None

        if "value" in raw.keys():
            raw["values"] = [{"language": None, "text": raw.get("value")}]
            del raw["value"]

        return W24CaptionValuePair.parse_obj(raw)
