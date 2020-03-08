"""
Small Integration test module to check whether the Techread Client
communicates properly with the server
"""
import asyncio
import logging
import os
from typing import List
import argparse

from ..models.ask import (W24AskThumbnailDrawing, W24AskThumbnailPage,
                          W24AskThumbnailSheet, W24AskPartOverallDimensions)
from ..models.techread import W24TechreadMessageType

from .techread_client import W24TechreadClient, CallbackRequest

# set the log level to info for the test setting
# We recommend using logging.WARNING for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


def _get_drawing(file_path) -> bytes:
    """ Obtain the bytes content of the test drawing
    """
    # get the path
    # cwd = os.path.dirname(os.path.abspath(__file__))
    # test_file_path = os.path.join(cwd, "techread_client_test_drawing.png")
    # test_file_path = "../api-reader/assets/test/e2e/3764012-2.pdf"

    # get the content
    with open(file_path, "rb") as filehandle:
        return filehandle.read()


def _debug_show_image(log_text, image_bytes):
    from PIL import Image
    import io
    logging.info(log_text)
    image = Image.open(io.BytesIO(image_bytes))
    image.show(title=log_text)


async def test_read_drawing(
        drawing_bytes: bytes,
        callback_requests: List[CallbackRequest]):

    # make the client. This will automatically
    # fetch the authentication information
    # from the environment variables. We will
    # provide you with separate .env files for
    # the development and production environments
    client = W24TechreadClient.make_from_dotenv()
    await client.read_drawing_with_callback_requests(drawing_bytes, callback_requests)


if __name__ == "__main__":

    # parse the args
    parser = argparse.ArgumentParser(description="Talk to the TechRead API ")
    parser.add_argument(
        "input_file",
        help="path to the file that is to be analyzed")

    args = parser.parse_args()

    # tell the api what asks you are interested in,
    # and define what to do when you receive the result
    callback_requests = [
        CallbackRequest(
            message_type=W24TechreadMessageType.TECHREAD_STARTED,
            callback=lambda msg: logging.info("Techread started")),
        CallbackRequest(
            ask=W24AskThumbnailPage(),
            callback=lambda msg: _debug_show_image(
                "Thumbnail page received",
                msg.payload_bytes)),
        CallbackRequest(
            ask=W24AskThumbnailSheet(),
            callback=lambda msg: _debug_show_image(
                "Thumbnail sheet received",
                msg.payload_bytes)),
        CallbackRequest(
            ask=W24AskThumbnailDrawing(),
            callback=lambda msg: _debug_show_image(
                "Thumbnail drawing received",
                msg.payload_bytes)),
        CallbackRequest(
            ask=W24AskPartOverallDimensions(),
            callback=lambda msg: logging.info(
                "Outer dimensions: %s",
                msg.payload_dict))]

    drawing_bytes = _get_drawing(args.input_file)
    async_request = test_read_drawing(drawing_bytes, callback_requests)
    asyncio.run(async_request)
