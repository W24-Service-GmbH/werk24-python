""" Defintion of all W24Ask types that are understood by the Werk24 API.
"""
from enum import Enum
from typing import List

from pydantic import UUID4, BaseModel

from .gdt import W24GDT
from .measure import W24Measure


class W24AskType(str, Enum):
    """ List of all Ask Type supported by the current
    API version.

    """
    PAGE_THUMBNAIL = "PAGE_THUMBNAIL"
    """ Thumbnail of the overall page - rotated and with
    surrounding white space removed """

    SHEET_THUMBNAIL = "SHEET_THUMBNAIL"
    """ Thumbnail of the sheet (i.e., the part of the
    page that is described by the surrounding frame) """

    CANVAS_THUMBNAIL = "CANVAS_THUMBNAIL"
    """ Thumbnail of the canvas (i.e., the part of the
    sheet that contains the geometry)
    """

    SECTIONAL_THUMBNAIL = "SECTIONAL_THUMBNAIL"
    """ Thumbnail of a sectional on the canvas.
    Here the sectional describes both cuts and perspectives
    """

    VARIANT_MEASURES = "VARIANT_MEASURES"
    """ List of Measures that were found on the Sectionals
    associated with the variant
    """

    VARIANT_GDTS = "VARIANT_GDTS"
    """ List of Geometric Dimensions and Tolerations detected
    on the Sectionals associated with the variant
    """

    TRAIN = "TRAIN"
    """ Supplying the request for training only without
    expecting a response.
    """


class W24Ask(BaseModel):
    """ Base model from wich all Asks inherit
    """
    ask_type: W24AskType


class W24AskThumbnailFileFormat(str, Enum):
    """ List of supported File Formats in which
    the Thumbnail can be supplied.

    NOTE: At this stage, the API only supports JPEG.
    This prepares the support for additional format
    (e.g. TIFF)
    """
    JPEG = "JPEG"


class W24AskThumbnail(W24Ask):
    """ Base model for features that request a thumbnail.

    NOTE: At this stage, the API will return a high-resolution
    image. Future releases will allow the defintion of the
    maximal dimensions.
    """
    file_format: W24AskThumbnailFileFormat = W24AskThumbnailFileFormat.JPEG


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
    ask_type = W24AskType.PAGE_THUMBNAIL


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


class W24AskVariantMeasuresResponse(BaseModel):
    """ Response object corresponding to the
    W24AskVariantMeasures ask.

    NOTE: Be aware that requesting the measures will
    yield one responds for each variant and sectional
    """
    variant_id: UUID4
    sectional_id: UUID4
    measures: List[W24Measure]


class W24AskVariantGDTs(W24Ask):
    """ This Ask requests the complete
    list of all Geometric Dimensions and Tolerations
    that were detected on the variant.
    """
    ask_type = W24AskType.VARIANT_GDTS


class W24AskVariantGDTsResponse(BaseModel):
    """ Response object corresponding ot hte
    W24AskVariantGDTs.

    NOTE: Be aware that requesting the measures will
    yield one responds for each variant and sectional
    """
    variant_id: UUID4
    sectional_id: UUID4
    gdts: List[W24GDT]


class W24AskTrain(BaseModel):
    """ If you submit this Ask, we will use your request
    to train and improve our models.
    It does not trigger a response
    """
    ask_type = W24AskType.TRAIN
