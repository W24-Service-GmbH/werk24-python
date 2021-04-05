from enum import Enum


class W24FileFormatVariantCAD(str, Enum):
    """ List of the supported CAD file formats

    !!! note
        At this stage, the API only supports DXF
        as output format. Additional formats are available
        upon request.
    """
    DXF = "DXF"


class W24FileFormatThumbnail(str, Enum):
    """ List of supported File Formats in which
    the Thumbnail can be supplied.

    !!! note
        At this stage, the API only supports JPEG.
        This prepares the support for additional format
        (e.g. TIFF)
    """
    JPEG = "JPEG"
