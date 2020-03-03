"""
Small Integration test module to check whether the Techread Client
communicates properly with the server
"""
import asyncio
import logging
import os
from typing import List

from models.ask import W24Ask
from models.ask_thumbnail_page import W24AskThumbnailPage
from models.ask_thumbnail_sheet import W24AskThumbnailSheet
from models.ask_thumbnail_drawing import W24AskThumbnailDrawing
from models.techread import W24TechreadMessage, W24TechreadMessageType

from .techread_client import W24TechreadClient

# set the log level to info for the test setting
# We recommend using logging.WARNING for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


def _get_test_drawing() -> bytes:
    """ Obtain the bytes content of the test drawing
    """
    # get the path
    cwd = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(cwd, "techread_client_test_drawing.png")

    # get the content
    with open(test_file_path, "rb") as filehandle:
        return filehandle.read()


def _debug_show_image(log_text, image_bytes):
    from PIL import Image
    import io
    logging.info(log_text)
    image = Image.open(io.BytesIO(image_bytes))
    image.show(title=log_text)


async def process_techread_message(message: W24TechreadMessage):
    """ Your custom code, that is triggered every time the
    server serves a new message
    """

    # small dictionary that maps the message types to funcitons
    TYPE = W24TechreadMessageType
    messsage_type_map = {
        TYPE.TECHREAD_STARTED: lambda msg: logging.info("Techread started"),
        TYPE.ASK_THUMBNAIL_PAGE: lambda msg: _debug_show_image(
            "Thumbnail_page received",
            msg.payload_bytes),
        TYPE.ASK_THUMBNAIL_SHEET: lambda msg: _debug_show_image(
            "Thumbnail_sheet received",
            msg.payload_bytes), }

    # get the function and execute the code
    func = messsage_type_map.get(message.message_type)
    if func is not None:
        func(message)

    # if the message_type does not contain a handler for the message type,
    # raise a runtime warning
    else:
        raise RuntimeWarning(
            f"Received unhandled message of type {message.message_type}")


async def test_read_drawing(drawing_bytes: bytes, asks: List[W24Ask]):

    # make the client. This will automatically
    # fetch the authentication information
    # from the environment variables. We will
    # provide you with separate .env files for
    # the development and production environments
    client = W24TechreadClient.make_from_dotenv()

    # Create a new client session with the server.
    # Each techread request requires its own session
    async with client as session:

        # send out the request and make a generator
        # that triggers when the result of an ask
        # becomes available
        generator = session.read_drawing(
            asks,
            drawing_bytes)

        # wait for the asks
        async for message in generator:
            await process_techread_message(message)


if __name__ == "__main__":

    # make the request and run
    asks = [
        W24AskThumbnailPage(),
        W24AskThumbnailSheet(),
        W24AskThumbnailDrawing()]
    drawing_bytes = _get_test_drawing()
    async_request = test_read_drawing(drawing_bytes, asks)
    asyncio.run(async_request)
