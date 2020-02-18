import base64
import hashlib

from pydantic import BaseModel

from .attachment_mime_type import W24AttachmentMimeType


class W24Attachment(BaseModel):
    """ W24Attachment describes the details of an attachment.
    This is currently only used to attach images (e.g. of renderings
    or extracts from the sheet).
    """
    mime_type: W24AttachmentMimeType = W24AttachmentMimeType.IMAGE_PNG
    attachment_hash: str
    base64_content: str

    @staticmethod
    def from_png(png_content: bytes) -> 'W24Attachment':
        """ Create a new W24 Image instance directly from the bytes of
        a PNG file
        """
        return W24Attachment(
            attachment_hash=hashlib.sha256(png_content).hexdigest(),
            mime_type=W24AttachmentMimeType.IMAGE_PNG,
            base64_content=base64.b64encode(png_content))


W24Attachment.update_forward_refs()
