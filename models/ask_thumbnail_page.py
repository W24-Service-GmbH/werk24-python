from .ask_thumbnail import W24AskThumbnail
from .ask_type import W24AskType


class W24AskThumbnailPage(W24AskThumbnail):
    """ Requesting the W24DrawingReadFeatureThumbnailPage will add
    a thumbnail of the complete page including the border area
    to the result.
    """
    ask_type = W24AskType.THUMBNAIL_PAGE
