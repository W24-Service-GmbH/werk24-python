from enum import Enum

from pydantic import BaseModel


class W24AskType(str, Enum):
    THUMBNAIL_PAGE = "THUMBNAIL_PAGE"
    THUMBNAIL_SHEET = "THUMBNAIL_SHEET"
    THUMBNAIL_DRAWING = "THUMBNAIL_DRAWING"
    PART_OVERALL_DIMENSIONS = "PART_OVERALL_DIMENSIONSs"
    TRAIN_SILENTLY = "TRAIN_SILENTLY"


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


class W24AskThumbnailPage(W24AskThumbnail):
    """ Requesting the W24DrawingReadFeatureThumbnailPage will add
    a thumbnail of the complete page including the border area
    to the result.
    """

    ask_type = W24AskType.THUMBNAIL_PAGE


class W24AskThumbnailSheet(W24AskThumbnail):
    """ Requesting the W24DrawingReadFeatureThumbnailPage will add
    a thumbnail of the complete page including the border area
    to the result.
    """

    ask_type = W24AskType.THUMBNAIL_SHEET


class W24AskThumbnailDrawing(W24AskThumbnail):
    """ Requesting the W24DrawingReadFeatureThumbnailPage will add
    a thumbnail of the complete page including the border area
    to the result.
    """

    ask_type = W24AskType.THUMBNAIL_DRAWING


class W24AskPartOverallDimensions(W24Ask):
    """ Requesting the W24AskPartOverallDimensions will
    extract the outer dimensions of the extracted part
    """

    ask_type = W24AskType.PART_OVERALL_DIMENSIONS
