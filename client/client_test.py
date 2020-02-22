import asyncio
import os
import base64
from dotenv import load_dotenv

from models.architecture import W24Architecture
from models.attachment_drawing import W24AttachmentDrawing
from models.drawing_read_request import W24DrawingReadRequest

from .client import W24Client, logger
import logging

# load the environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)


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

    content_b64: str = "iVBORw0KGgoAAAANSUhEUgAAARAAAADoCAIAAACo3iyCAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAAJdSURBVHhe7dMxAQAwEAOh+jedWvjbwQNvwJkwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTAQCAOBMBAIA4EwEAgDgTBwtn2cN8eh0bbmOQAAAABJRU5ErkJggg=="
    content_bytes: bytes = base64.b64decode(content_b64)
    response = asyncio.run(client.read_drawing(content_bytes))


if __name__ == "__main__":
    # test_ping()
    test_read_drawing()
