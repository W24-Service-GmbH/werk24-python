from enum import Enum


class W24AttachmentMimeType(str, Enum):
    """ W24AttachmentMimeType lists the supported mime types
    for attachments. Currently only PNG images can be attached.
    """

    IMAGE_PNG = "image/png"
