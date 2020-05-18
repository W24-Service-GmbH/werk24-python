""" Command Line Interface for W24 Techread
"""
import argparse
import logging
from typing import List
from dotenv import load_dotenv

from werk24.models.ask import (
    W24AskSectionalThumbnail,
    W24AskPageThumbnail,
    W24AskSheetThumbnail,
    W24AskVariantMeasures)
from werk24.exceptions import RequestTooLargeException
from werk24.models.techread import (
    W24TechreadMessageType,
    W24TechreadMessageSubtypeError,
    W24TechreadMessageSubtypeProgress)
from werk24.techread_client import Hook, W24TechreadClient

# load the environment variables
load_dotenv(".werk24")

# set the log level to info for the test setting
# We recommend using logging.WARNING for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',  # noqa
    datefmt='%Y-%m-%d %H:%M:%S')

# get the local logger
logger = logging.getLogger(__name__)


def _get_drawing(file_path: str) -> bytes:
    """ Obtain the bytes content of the test drawing
    """
    # get the content
    with open(file_path, "rb") as filehandle:
        return filehandle.read()


def _debug_show_image(log_text: str, image_bytes: bytes) -> None:
    from PIL import Image
    import io
    logger.info(log_text)
    image = Image.open(io.BytesIO(image_bytes))
    image.show(title=log_text)


async def main(
        args: argparse.Namespace
) -> None:

    # make the hooks from the arguments
    hooks = _make_hooks_from_args(args)

    # make the client. This will automatically
    # fetch the authentication information
    # from the environment variables. We will
    # provide you with separate .env files for
    # the development and production environments
    client = W24TechreadClient.make_from_env()

    async with client as session:

        # get the drawing
        drawing_bytes = _get_drawing(args.input_file)

        # and make the request
        try:
            await session.read_drawing_with_hooks(
                drawing_bytes,
                hooks)

        except RequestTooLargeException:
            message = "Request was too large to be processed. " \
                + "Please check the documentation for current limits."
            logger.error(message)


def _make_hooks_from_args(
        args: argparse.Namespace
) -> List[Hook]:

    # tell the api what asks you are interested in,
    # and define what to do when you receive the result
    hooks = []

    # add the hook to get the information that the techread
    # process was started
    if args.ask_techread_started:
        hooks += [Hook(
            message_type=W24TechreadMessageType.PROGRESS,
            message_subtype=W24TechreadMessageSubtypeProgress.STARTED,
            function=print)]

    # add the hook for the page thumbnail
    if args.ask_page_thumbnail:
        hooks += [Hook(
            ask=W24AskPageThumbnail(),
            function=lambda msg: _debug_show_image(
                "Page Thumbnail received",
                msg.payload_bytes))]

    # add the hook for the sheet thumbnail
    if args.ask_sheet_thumbnail:
        hooks += [Hook(
            ask=W24AskSheetThumbnail(),
            function=lambda msg: _debug_show_image(
                "Sheet Thumbnail received",
                msg.payload_bytes))]

    # add the hook for the drawing thumbnail
    if args.ask_sectional_thumbnail:
        hooks += [Hook(
            ask=W24AskSectionalThumbnail(),
            function=lambda msg: _debug_show_image(
                "Drawing thumbnail received",
                msg.payload_bytes))]

    # add the hook for the variant measures
    if args.ask_variant_measures:
        hooks += [Hook(
            ask=W24AskVariantMeasures(),
            function=lambda msg: print(
                "Received Ask Variant Measures\n",
                msg.payload_dict
            ))]

    # add a general hook to deal with internal errors
    hooks += [Hook(message_type=W24TechreadMessageType.ERROR,
                   message_subtype=W24TechreadMessageSubtypeError.INTERNAL,
                   function=lambda msg:
                   logging.error("Internal Error %s", msg.payload_dict))]
    return hooks
