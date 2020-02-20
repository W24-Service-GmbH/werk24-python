import base64
import hashlib

from pydantic import BaseModel


class W24Attachment(BaseModel):
    """ W24Attachment describes the details of an attachment.
    This is currently only used to attach images (e.g. of renderings
    or extracts from the sheet).
    """
    attachment_hash: str
    content_b64: str

    @staticmethod
    def from_bytes(content: bytes) -> 'W24Attachment':
        """ Create a new W24 Image instance directly from the bytes of
        a PNG file
        """
        return W24Attachment(
            attachment_hash=hashlib.sha256(content).hexdigest(),
            content_b64=base64.b64encode(content))


W24Attachment.update_forward_refs()
