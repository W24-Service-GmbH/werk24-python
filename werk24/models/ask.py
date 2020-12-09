""" Defintion of all W24Ask types that are understood by the Werk24 API.
"""
from enum import Enum
from typing import List, Optional, Union

from pydantic import UUID4, BaseModel

from .file_format import W24FileFormatThumbnail, W24FileFormatVariantCAD
from .gdt import W24GDT
from .leader import W24Leader
from .measure import W24Measure


class W24AskType(str, Enum):
    """ List of all Ask Type supported by the current
    API version.

    """
    CANVAS_THUMBNAIL = "CANVAS_THUMBNAIL"
    """ Thumbnail of the canvas (i.e., the part of the
    sheet that contains the geometry)
    """

    PAGE_THUMBNAIL = "PAGE_THUMBNAIL"
    """ Thumbnail of the overall page - rotated and with
    surrounding white space removed
    """

    SECTIONAL_THUMBNAIL = "SECTIONAL_THUMBNAIL"
    """ Thumbnail of a sectional on the canvas.
    Here the sectional describes both cuts and perspectives
    """

    SHEET_THUMBNAIL = "SHEET_THUMBNAIL"
    """ Thumbnail of the sheet (i.e., the part of the
    page that is described by the surrounding frame)
    """

    TRAIN = "TRAIN"
    """ Supplying the request for training only without
    expecting a response.
    """

    VARIANT_CAD = "VARIANT_CAD"
    """ Requests the generation of a CAD file
    """

    VARIANT_GDTS = "VARIANT_GDTS"
    """ List of Geometric Dimensions and Tolerations detected
    on the Sectionals associated with the variant
    """

    VARIANT_LEADERS = "VARIANT_LEADERS"
    """ List of Leaders that were detected on the Sectional
    """

    VARIANT_MATERIAL = "VARIANT_MATERIAL"
    """ Material that was detected on the data fields of the
    drawing or within a variant table
    """

    VARIANT_MEASURES = "VARIANT_MEASURES"
    """ List of Measures that were found on the Sectionals
    associated with the variant
    """


class W24Ask(BaseModel):
    """ Base model from wich all Asks inherit
    """
    ask_type: W24AskType

    is_training: bool = False
    """ Flag that indicates that your request is a pure
    training request and that you are not expecting to
    obtain a response.
    """


class W24AskThumbnail(W24Ask):
    """ Base model for features that request a thumbnail.

    NOTE: At this stage, the API will return a high-resolution
    image. Future releases will allow the defintion of the
    maximal dimensions.
    """
    file_format: W24FileFormatThumbnail = W24FileFormatThumbnail.JPEG


class W24AskPageThumbnail(W24AskThumbnail):
    """ Requests a thumbnail for each page in the document;
    rotated, and with the surrounding white-space removed.

    NOTE: when you supply a white-on-black document, the thumbnail
    will be black-on-white.
    """
    ask_type = W24AskType.PAGE_THUMBNAIL


class W24AskSheetThumbnail(W24AskThumbnail):
    """ Requests a thumbnail of each sheet on each page in
    the document. The sheet will only contain the pixels within
    the main frame that surrounds the canvas and header fields.
    """
    ask_type = W24AskType.SHEET_THUMBNAIL


class W24AskCanvasThumbnail(W24AskThumbnail):
    """ Requests a thumbnail of each canvas in each sheet.
    The canvas describes the "drawing area" of the sheet.
    """
    ask_type = W24AskType.CANVAS_THUMBNAIL


class W24AskSectionalThumbnail(W24AskThumbnail):
    """ The W24AskPlaneThumbnail requests a thumbnail
    of each sectional on each sheet in the document.

    NOTE: we have chosen the term sectional to describe
    both cuts and perspectives
    """
    ask_type = W24AskType.SECTIONAL_THUMBNAIL


class W24AskVariantMeasures(W24Ask):
    """ With this Ask you are requesting the complete
    list of all measures that were detected for the
    variant
    """
    ask_type = W24AskType.VARIANT_MEASURES

    confidence_min: float = 0.2
    """ Werk24 calculates internal confidence scores
    for each measure. Depending on your use-case you
    might want to consider or discard low-confidence
    results. This parameter allows you to filter the
    results. The resulting W24Measure objects also
    contain a confidence score that allows you to filter
    even further.
    """


class W24AskVariantMeasuresResponse(BaseModel):
    """ Response object corresponding to the
    W24AskVariantMeasures ask.

    NOTE: Be aware that requesting the measures will
    yield one responds for each variant and sectional
    """
    variant_id: UUID4
    sectional_id: UUID4
    measures: List[W24Measure]


class W24AskVariantLeaders(W24Ask):
    """ With this Ask you are requesting the complete
    list of all leaders that were detected on the
    variant
    """
    ask_type = W24AskType.VARIANT_LEADERS


class W24AskVariantLeadersResponse(BaseModel):
    """ Response object corresponding to the
    W24AskVariantLeaders.

    """
    variant_id: UUID4
    sectional_id: UUID4
    leaders: List[W24Leader]


class W24AskVariantMaterial(W24Ask):
    """ This ask requests the material of the
    individual variant.

    !!! This Ask will not be answered by
    !!! the API at this stage. Stay tuned
    !!! for updates
    """
    ask_type = W24AskType.VARIANT_MATERIAL

    material_hint: Optional[str] = None
    """ If your user is already asked about the
    meterial, or if you have any additional
    informationa about the material, you
    can submit it here. This will make the
    reading more stable.
    """


class W24AskVariantGDTs(W24Ask):
    """ This Ask requests the complete
    list of all Geometric Dimensions and Tolerations
    that were detected on the variant.
    """
    ask_type = W24AskType.VARIANT_GDTS


class W24AskVariantGDTsResponse(BaseModel):
    """ Response object corresponding ot the
    W24AskVariantGDTs.

    NOTE: Be aware that requesting the measures will
    yield one response for each variant and sectional
    """
    variant_id: UUID4
    sectional_id: UUID4
    gdts: List[W24GDT]


class W24AskTrain(W24Ask):
    """ If you submit this Ask, we will use your request
    to train and improve our models.
    It does not trigger a response
    """
    ask_type = W24AskType.TRAIN


class W24AskVariantCAD(W24Ask):
    """ By sending this ASk, you are requesting
    an associated CAD model
    """
    ask_type = W24AskType.VARIANT_CAD

    output_format: W24FileFormatVariantCAD = W24FileFormatVariantCAD.DXF
    """ Output format in which to generate
    the CAD file
    """


class W24AskVariantCADResponse(BaseModel):
    """ Response object corresponding ot the
    W24AskVariantCad.

    NOTE: Be aware that requesting the measures will
    yield one response for each variant

    NOTE: the cad file will be returned as part of
    the payload_bytes and needs to be accessed directly
    """
    variant_id: UUID4


W24AskUnion = Union[
    W24AskCanvasThumbnail,
    W24AskPageThumbnail,
    W24AskSectionalThumbnail,
    W24AskSheetThumbnail,
    W24AskTrain,
    W24AskVariantGDTs,
    W24AskVariantLeaders,
    W24AskVariantMaterial,
    W24AskVariantMeasures,
    W24AskVariantCAD,
]
""" Union of all W24Asks to ensure proper deserialization """
