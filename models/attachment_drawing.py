from base64 import b64decode
from io import BytesIO

import magic
from pydantic import validator

from .attachment import W24Attachment

# number of bytes that are read from the IO Buffer
# and passed ot the magic byte reader
MAGIC_BYTE_LENGTH = 2048

# list of accepted mime types
ACCEPTED_MIME_TYPES = ['application/pdf', 'image/png', 'image/jpeg']


class W24AttachmentDrawing(W24Attachment):
    """ Object for passing Technical Drawings.
    It inherits from the W24Attachment and implements
    a mime-validator
    """

    @validator('base64_content')
    def mime_type_must_be_image_or_pdf(cls, v):
        """ Check the mime type of the drawing
        on the client-side
        """

        # obtain the mime type
        bytes_io = BytesIO(b64decode(v))
        mime_type = magic.from_buffer(
            bytes_io.read(MAGIC_BYTE_LENGTH),
            mime=True)

        # compare with the list of accepted mime types
        if mime_type not in ACCEPTED_MIME_TYPES:
            raise ValueError(f'Drawing not of accepted mime type')

        # return unchanged
        return v
