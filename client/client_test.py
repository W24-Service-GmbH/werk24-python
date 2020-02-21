import asyncio
import os

from dotenv import load_dotenv

from models.architecture import W24Architecture
from models.attachment_drawing import W24AttachmentDrawing
from models.drawing_read_request import W24DrawingReadRequest

from .client import W24Client

# load the environment variables
load_dotenv()

# make the client reference
client = W24Client(os.environ.get("W24IO_SERVER"))
client.register(
    os.environ.get("W24IO_COGNITO_REGION"),
    os.environ.get("W24IO_COGNITO_IDENTITY_POOL_ID"),
    os.environ.get("W24IO_COGNITO_CLIENT_ID"),
    os.environ.get("W24IO_COGNITO_CLIENT_SECRET"),
    os.environ.get("W24IO_COGNITO_USERNAME"),
    os.environ.get("W24IO_COGNITO_PASSWORD"))


def test_ping():
    response = asyncio.run(client.ping())
    print(response)


def test_read_drawing():

    read_request = W24DrawingReadRequest(
        drawing=W24AttachmentDrawing(
            content_b64=content_b64,
            attachment_hash=W24AttachmentDrawing.make_attachment_hash(content_b64)),
        architecture=W24Architecture.CPU_V1)


if __name__ == "__main__":
    test_ping()
