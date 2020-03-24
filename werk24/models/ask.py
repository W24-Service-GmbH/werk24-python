from enum import Enum

from pydantic import BaseModel


class W24AskType(str, Enum):
    PAGE_THUMBNAIL = "PAGE_THUMBNAIL"

    SHEET_EXPORT_ONSHAPE = "SHEET_EXPORT_ONSHAPE"
    SHEET_THUMBNAIL = "SHEET_THUMBNAIL"

    PLANE_THUMBNAIL = "PLANE_THUMBNAIL"

    VARIANT_OVERALL_DIMENSIONS = "VARIANT_OVERALL_DIMENSIONS"
    VARIANT_EXPORT_STL = "VARIANT_EXPORT_STL"

    TRAIN = "TRAIN"


class W24Ask(BaseModel):
    """ Base model for all possible demand
    in a W24Demand
    """

    ask_type: W24AskType


class W24AskThumbnail(W24Ask):
    """ Base model for features that request a
    thumbnail.

    maximal_width and maximal_height describe the maximal
    dimensions of the thumbnail (in pixel).

    Beware that the resulting image dimensions depend
    on many factors, such as:
    (i) resolution of the original image,
    (ii) rotation of the sheet on the page,
    (iii) noise level of the image, etc.

    Setting auto_rotate to True will rotate the image for
    "human-consumption" (the human rotation algorithm is
    more complext than you'd expect)
    """

    # maximal_width: int = 512
    # maximal_height: int = 512
    # auto_rotate: bool = False


class W24AskPageThumbnail(W24AskThumbnail):
    """ Requests a thumbnail of
    the complete page including the border area
    """

    ask_type = W24AskType.PAGE_THUMBNAIL


class W24AskSheetThumbnail(W24AskThumbnail):
    """ Requests a thumbnail of
    each sheet in the document.
    """

    ask_type = W24AskType.SHEET_THUMBNAIL


class W24AskSheetExportOnshape(W24Ask):
    """Requests the export of each submitted sheet
    to onshape (onshape.com)
    """
    ask_type = W24AskType.SHEET_EXPORT_ONSHAPE


class W24AskPlaneThumbnail(W24AskThumbnail):
    """ The W24AskPlaneThumbnail requests a thumbnail
    of each plane on each sheet in the document.
    """

    ask_type = W24AskType.PLANE_THUMBNAIL


class W24AskVariantOverallDimensions(W24Ask):
    """ Requesting the W24AskVariantOverallDimensions will
    extract the outer dimensions of the extracted part
    """

    ask_type = W24AskType.VARIANT_OVERALL_DIMENSIONS


class W24AskVariantExportSTL(W24Ask):
    """ Requests an export of the Variant as STL File
    """

    ask_type = W24AskType.VARIANT_EXPORT_STL


class W24AskTrain(BaseModel):
    """ If you submit this Ask, we will use your request
    to train and improve our models. It does not trigger
    a response
    """
    ask_type = W24AskType.TRAIN
