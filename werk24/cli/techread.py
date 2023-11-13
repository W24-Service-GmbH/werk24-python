""" Command Line Interface for W24 Techread
"""
import argparse
import io
import json
import logging
import os
from collections import namedtuple
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from pydantic import UUID4

from werk24.cli import utils
from werk24.exceptions import RequestTooLargeException
from werk24.models.ask import (
    W24AskCanvasThumbnail,
    W24AskPageThumbnail,
    W24AskPartFamilyCharacterization,
    W24AskSectionalThumbnail,
    W24AskSheetAnonymization,
    W24AskSheetThumbnail,
    W24AskTitleBlock,
    W24AskVariantCAD,
    W24AskVariantExternalDimensions,
    W24AskVariantGDTs,
    W24AskVariantMeasures,
    W24AskVariantRadii,
    W24AskDebug,
    W24AskVariantRoughnesses,
    W24AskVariantThreadElements,
)
from werk24.models.techread import (
    W24TechreadException,
    W24TechreadMessageSubtypeError,
    W24TechreadMessageSubtypeProgress,
    W24TechreadMessageType,
)
from werk24.techread_client import LICENSE_LOCATIONS, Hook

# load the environment variables
for c_location in LICENSE_LOCATIONS:
    if os.path.exists(c_location):
        load_dotenv(c_location)
        break

# set the log level to info for the test setting
# We recommend using logging.WARNING for production
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",  # noqa
    datefmt="%Y-%m-%d %H:%M:%S",
)

# get the local logger
logger = logging.getLogger(__name__)  # pylint:disable = invalid-name


def _open_in_webbrowser(url: str) -> None:
    """Open a URL in the Webbrowser"""
    import webbrowser

    webbrowser.open(str(url), new=2)


# make the configuration of what hooks we want to handle and how
HookConfig = namedtuple("HookConfig", "arg ask function")
hook_config = [
    HookConfig(
        "ask_page_thumbnail",
        W24AskPageThumbnail,
        lambda m: _show_image("Page Thumbnail", m.payload_bytes),
    ),
    HookConfig(
        "ask_sheet_thumbnail",
        W24AskSheetThumbnail,
        lambda m: _show_image("Sheet Thumbnail", m.payload_bytes),
    ),
    HookConfig(
        "ask_sheet_anonymization",
        W24AskSheetAnonymization,
        lambda m: _show_image("Sheet Anonymization", m.payload_bytes),
    ),
    HookConfig(
        "ask_canvas_thumbnail",
        W24AskCanvasThumbnail,
        lambda m: _show_image("Canvas Thumbnail", m.payload_bytes),
    ),
    HookConfig(
        "ask_sectional_thumbnail",
        W24AskSectionalThumbnail,
        lambda m: _show_image("Sectional Thumbnail", m.payload_bytes),
    ),
    # HookConfig(
    #     'ask_variant_angles',
    #     W24AskVariantAngles,
    #     lambda m: _print_payload("Ask Variant Angles", m.payload_dict)),
    HookConfig(
        "ask_variant_external_dimensions",
        W24AskVariantExternalDimensions,
        lambda m: _print_payload("Ask Variant Ext. Dimensions", m.payload_dict),
    ),
    HookConfig(
        "ask_variant_gdts",
        W24AskVariantGDTs,
        lambda m: _print_payload("Ask Variant GDTs", m.payload_dict),
    ),
    HookConfig(
        "ask_variant_measures",
        W24AskVariantMeasures,
        lambda m: _print_payload("Ask Variant Measures", m.payload_dict),
    ),
    HookConfig(
        "ask_variant_radii",
        W24AskVariantRadii,
        lambda m: _print_payload("Ask Variant Radii", m.payload_dict),
    ),
    HookConfig(
        "ask_variant_roughnesses",
        W24AskVariantRoughnesses,
        lambda m: _print_payload("Ask Variant Roughnesses", m.payload_dict),
    ),
    HookConfig(
        "ask_variant_cad",
        W24AskVariantCAD,
        lambda m: _store_variant_cad(m.payload_dict, m.payload_bytes, m.exceptions),
    ),
    HookConfig(
        "ask_titleblock",
        W24AskTitleBlock,
        lambda m: _print_payload("Ask TitleBlock", m.payload_dict),
    ),
    HookConfig(
        "ask_variant_thread_elements",
        W24AskVariantThreadElements,
        lambda m: _print_payload("Ask Variant Thread Elements", m.payload_dict),
    ),
]


def _store_variant_cad(
    payload_dict: Dict[str, Any],
    payload_bytes: Optional[bytes],
    exceptions: List[W24TechreadException],
) -> None:
    """Store the CAD file the current directory

    Args:
        payload_dict (Dict[str, Any]): Payload Dictionary
        payload_bytes (bytes): CAD that we received as response
    """
    logger.info(f"Ask Variant CAD\n{payload_dict}")

    # print potential exceptions
    if exceptions:
        _log_exceptions(exceptions)

    # store the payload
    if payload_bytes is not None:
        _store_variant_cad_payload(payload_dict, payload_bytes)


def _log_exceptions(exceptions: List[W24TechreadException]) -> None:
    """Log the encountered exceptions as warnings

    Args:
        exceptions (List[W24TechreadException]): List of
            encountered exceptions. Can be an empty list.
    """
    for cur_exception in exceptions:
        logger.warn(cur_exception)


def _store_variant_cad_payload(
    payload_dict: Dict[str, Any], payload_bytes: bytes
) -> None:
    """Store the CAD file with the knowledge that
    the payload exists

    Args:
        payload_dict (Dict[str, Any]): Payload Dictionary
        payload_bytes (bytes): CAD response
    """
    # make the filename
    variant_id = payload_dict.get("variant_id")
    filename = f"./w24_ask_variant_cad_{variant_id}.dxf"

    # and write the content
    with open(filename, "wb+") as file_handle:
        file_handle.write(payload_bytes)

    # tell the user
    logger.info(f"CAD response stored in {filename}")


def _get_drawing(file_path: str) -> Optional[bytes]:
    """Get the bytes of the file that shall be
    read.

    Args:
        file_path (str): path to the input file

    Returns:
        bytes: content of the fiel
    """
    try:
        with open(file_path, "rb") as filehandle:
            return filehandle.read()
    except FileNotFoundError:
        print(f"File {file_path} not found")
        return None


def _print_payload(log_text: str, payload_dict: Dict[str, Any]) -> None:
    """Display the payload dictionary in a format that
    is easy for humans to read

    Args:
        log_text (str): Headline info
        payload_dict (Dict[str, Any]): Payload dictionary
    """
    print(log_text)
    payload_json = json.dumps(payload_dict, indent=4)
    print(payload_json)


def _show_image(log_text: str, image_bytes: bytes) -> None:
    """Display a debug image. The function relies on
    the PIL functionality of Image.show(). The
    actual behavior will thus be different across platforms

    Args:
        log_text (str): Log Text that we want to write back
            to the command line interface
        image_bytes (bytes): byte representation of the image
            that is to be displayed
    """

    # Import the PIL at runtime to make sure that
    # you can still use the client without the need
    # to install Pillow
    try:
        from PIL import Image  # pylint: disable=import-outside-toplevel
    except ImportError:
        logger.warning(
            "Viewing image-like responses requires the installation"
            " of the PIL package: pip install pillow. Image skipped."
        )
        return

    # otherwise print the text
    logger.info(log_text)

    # and show the image
    image = Image.open(io.BytesIO(image_bytes))
    try:
        image.show(title=log_text)
    except BaseException:
        logger.warning(
            "Image cannot be displayed. " "Please check your local security settings."
        )
        return


async def main(args: argparse.Namespace) -> None:
    """
    Run the Techread command with the CLI arguments

    Args:
        args(argparse.Namespace): CLI args generated by
        argparse
    """

    # interpret the sub-account as UUID4 and stop if that
    # does not conform to the correct pattern.
    try:
        if args.sub_account is not None:
            sub_account = UUID4(args.sub_account)
        else:
            sub_account = None

    except ValueError:
        logger.error("Sub-Account ID does not conform to UUID4-pattern")
        return

    # make the hooks from the arguments
    hooks = _make_hooks_from_args(args)

    # get the client instance and handle
    # potential errors
    client = utils.make_client()

    async with client as session:
        # get the drawing
        drawing_bytes = _get_drawing(args.input_file)
        if drawing_bytes is None:
            return

        # and make the request
        try:
            await session.read_drawing_with_hooks(
                drawing_bytes, hooks, sub_account=sub_account
            )

        except RequestTooLargeException:
            message = (
                "Request was too large to be processed. "
                + "Please check the documentation for current limits."
            )
            logger.error(message)


def _make_hooks_from_args(args: argparse.Namespace) -> List[Hook]:
    # add a general hook to deal with internal errors
    hook_error_internal = Hook(
        message_type=W24TechreadMessageType.ERROR,
        message_subtype=W24TechreadMessageSubtypeError.INTERNAL,
        function=lambda msg: logger.error("Internal Error %s", msg.payload_dict),
    )

    # add a general hook to deal with PROGRESS messages
    hook_progress_started = Hook(
        message_type=W24TechreadMessageType.PROGRESS,
        message_subtype=W24TechreadMessageSubtypeProgress.STARTED,
        function=lambda msg: logger.info("Techread process started"),
    )

    # tell the api what asks you are interested in,
    # and define what to do when you receive the result
    hooks = [
        Hook(ask=c.ask(), function=c.function)
        for c in hook_config
        if getattr(args, c.arg)
    ] + [hook_error_internal, hook_progress_started]

    # take special care of teh W24AskPartFamilyCharacterization
    if args.part_family_id is not None:
        c_hook = Hook(
            ask=W24AskPartFamilyCharacterization(part_family_id=args.part_family_id),
            function=lambda m: _print_payload(
                "Part Family Characterization", m.payload_dict
            ),
        )
        hooks.append(c_hook)
    if args.debug_key is not None:
        c_hook = Hook(
            ask=W24AskDebug(debug_key=args.debug_key),
            # function=lambda m: _print_payload("Ask Debug", m.payload_dict),
            function=lambda m: _open_in_webbrowser(m.payload_url),
        )
        hooks.append(c_hook)

    return hooks
