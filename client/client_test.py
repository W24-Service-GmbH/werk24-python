import asyncio
import os
import base64
from dotenv import load_dotenv

from models.architecture import W24Architecture
from models.attachment_drawing import W24AttachmentDrawing
from models.drawing_read_request import W24DrawingReadRequest

from .client import W24Client, logger
import logging
import io
import mimetypes
# load the environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)


def _get_test_drawing() -> bytes:
    """ Obtain the bytes content of the test drawing
    """
    cwd = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(cwd, "client_test_drawing.png")

    with open(test_file_path, "rb") as filehandle:
        content_bytes = filehandle.read()

    return content_bytes


# make the client reference
client = W24Client(os.environ.get("W24IO_SERVER"))
client.register(
    os.environ.get("W24IO_COGNITO_REGION"),
    os.environ.get("W24IO_COGNITO_IDENTITY_POOL_ID"),
    os.environ.get("W24IO_COGNITO_CLIENT_ID"),
    os.environ.get("W24IO_COGNITO_CLIENT_SECRET"),
    os.environ.get("W24IO_COGNITO_USERNAME"),
    os.environ.get("W24IO_COGNITO_PASSWORD"))


def test_read_drawing():

    async def read_drawing(asks, content_bytes):

        generator = await client.read_drawing(asks, content_bytes)
        async for res in generator:
            print(res)

    content_bytes = _get_test_drawing()
    response = asyncio.run(read_drawing([], content_bytes))


if __name__ == "__main__":
    test_read_drawing()
