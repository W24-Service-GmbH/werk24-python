import hashlib

import bson
from pydantic import BaseModel
import base64


class W24Attachment(BaseModel):
    """ W24Attachment describes the details of an attachment.
    This is currently only used to attach images (e.g. of renderings
    or extracts from the sheet).
    """
    attachment_hash: str
    content: bytes

    class Config:
        json_encoders = {
            bytes: lambda v: ""  # base64.b64encode(v).decode()
        }

    @classmethod
    def from_bytes(cls, content: bytes) -> 'W24Attachment':
        """ Create a new W24 Image instance directly from the bytes of
        a PNG file
        """
        # content_b64 = base64.b64encode(content).decode("utf-8")
        attachment_hash = cls.make_attachment_hash(content)
        return W24Attachment(
            attachment_hash=attachment_hash,
            content=content)

    @staticmethod
    def make_attachment_hash(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()


W24Attachment.update_forward_refs()
