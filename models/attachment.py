import hashlib

import bson
from pydantic import BaseModel


class W24Attachment(BaseModel):
    """ W24Attachment describes the details of an attachment.
    This is currently only used to attach images (e.g. of renderings
    or extracts from the sheet).
    """
    attachment_hash: str
    content: bytes

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

    def dumps(self) -> bytes:
        return bson.encode(self.dict())


W24Attachment.update_forward_refs()
