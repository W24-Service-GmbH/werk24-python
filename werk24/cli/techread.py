""" Command Line Interface for W24 Techread
"""
import os, tempfile
import subprocess
import platform
import traceback
from datetime import datetime
import argparse
from termcolor import colored
from colorama import just_fix_windows_console
import io
import json
import logging
from werk24.exceptions import TechreadException
import os
from collections import namedtuple
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
import random
import string
from werk24.cli import utils
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
    W24AskVariantProcesses,
)

from werk24.models.techread import (
    W24TechreadException,
    W24TechreadMessageSubtypeError,
    W24TechreadMessageSubtypeProgress,
    W24TechreadMessageType,
    W24TechreadMessage,
)
from werk24.techread_client import LICENSE_LOCATIONS, Hook

# fix the windows console color issue
just_fix_windows_console()

def random_string(length: int) -> str:
    """
    Generate a random string of a given length

    Args:
    ----
    - length (int): Length of the random string

    Returns:
    -------
    - str: Random string of the given length
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

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


def _save_and_open_debug(payload_bytes:bytes, extension:str) -> None:
    """
    Save the debug payload to a temporary file and open it
    with the default application for the file type

    This function is required because we need to support
    E2E encryption. So opening the file directly is not
    possible.
    
    Args:
    ----
    payload_bytes (bytes): The payload
    """
    # Create a temporary file that will be deleted after the block exits
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extension}") as tmp:
        tmp.write(payload_bytes)
        tmp.flush()  # Ensure all data is written to disk
        tmp_name = tmp.name

    # Determine the command based on the operating system
    system_name = platform.system()
    if system_name == "Windows":
        os.startfile(tmp_name)
    elif system_name == "Darwin":  # macOS
        subprocess.run(["open", tmp_name], check=True)
    elif system_name == "Linux":
        subprocess.run(["xdg-open", tmp_name], check=True)
    else:
        raise OSError(f"Unsupported OS: {system_name}")
    input("Press Enter to delete temporary file...")

    # Ensure the temporary file is deleted
    if os.path.exists(tmp_name):
        try:
            os.remove(tmp_name)
        except Exception as cleanup_error:
            print(f"Failed to delete temporary file: {cleanup_error}")



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
    HookConfig(
        "ask_variant_external_dimensions",
        W24AskVariantExternalDimensions,
        lambda m: _print_payload("Ask Variant Ext. Dimensions", m),
    ),
    HookConfig(
        "ask_variant_gdts",
        W24AskVariantGDTs,
        lambda m: _print_payload("Ask Variant GDTs", m),
    ),
    HookConfig(
        "ask_variant_measures",
        W24AskVariantMeasures,
        lambda m: _print_payload("Ask Variant Measures", m),
    ),
    HookConfig(
        "ask_variant_radii",
        W24AskVariantRadii,
        lambda m: _print_payload("Ask Variant Radii", m),
    ),
    HookConfig(
        "ask_variant_roughnesses",
        W24AskVariantRoughnesses,
        lambda m: _print_payload("Ask Variant Roughnesses", m),
    ),
    HookConfig(
        "ask_variant_processes",
        W24AskVariantProcesses,
        lambda m: _print_payload("Ask Variant Processes", m),
    ),
    HookConfig(
        "ask_variant_cad",
        W24AskVariantCAD,
        lambda m: _store_variant_cad(m.payload_dict, m.payload_bytes, m.exceptions),
    ),
    HookConfig(
        "ask_titleblock",
        W24AskTitleBlock,
        lambda m: _print_payload("Ask TitleBlock", m),
    ),
    HookConfig(
        "ask_variant_thread_elements",
        W24AskVariantThreadElements,
        lambda m: _print_payload("Ask Variant Thread Elements", m),
    ),
]


def _store_variant_cad(
    payload_dict: Dict[str, Any],
    payload_bytes: Optional[bytes],
    exceptions: List[W24TechreadException],
) -> None:
    """Store the CAD file the current directory

    Args:
    ----
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
    ----
    exceptions (List[W24TechreadException]): List of
        encountered exceptions. Can be an empty list.
    """

    for cur_exception in exceptions:
        level = str(cur_exception.exception_level.value)
        exception_type = cur_exception.exception_type.value
        message = f"{level}: {exception_type}"
        logger.warn(message)


def _store_variant_cad_payload(
    payload_dict: Dict[str, Any], payload_bytes: bytes
) -> None:
    """Store the CAD file with the knowledge that
    the payload exists

    Args:
    ----
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


def _get_drawing(file_path: str) -> Optional[io.BufferedReader]:
    """Get the bytes of the file that shall be read.

    Args:
    ----
    file_path (str): path to the input file

    Returns:
    -------
    io.BufferedReader: file handle to the input file
    """
    try:
        return open(file_path, "rb")
    except FileNotFoundError:
        print(f"File {file_path} not found")
        return None


def _print_payload(log_text: str, message: W24TechreadMessage) -> None:
    """Display the payload dictionary in a format that
    is easy for humans to read

    Args:
    ----
    log_text (str): Headline info
    payload_dict (Dict[str, Any]): Payload dictionary
    """
    print(log_text)
    if message.exceptions:
        _log_exceptions(message.exceptions)
    payload_json = json.dumps(message.payload_dict, indent=4)
    print(payload_json)


def _show_image(log_text: str, image_bytes: bytes) -> None:
    """Display a debug image. The function relies on
    the PIL functionality of Image.show(). The
    actual behavior will thus be different across platforms

    Args:
    ----
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
    ----
    args(argparse.Namespace): CLI args generated by
        argparse
    """
    try:
        # make the hooks from the arguments
        hooks = _make_hooks_from_args(args)

        # get the client instance and handle
        # potential errors
        client = utils.make_client(args.server)

        # get the drawing
        drawing = _get_drawing(args.input_file)
        if drawing is None:
            return

        # make a key pair
        passphrase = random_string(16)
        public_key_pem, private_key_pem = client.generate_encryption_keys(
            passphrase=passphrase
        )

        async with client as session:
            await session.read_drawing_with_hooks(
                drawing,
                hooks,
                sub_account=None,
                client_public_key_pem=public_key_pem,
                client_private_key_pem=private_key_pem,
                client_private_key_passphrase=passphrase,
            )
            drawing.close()

    except TechreadException as exception:
        print()
        print(colored("=" * 3 + "[Techread Error]" + "=" * 61, "red"))

        print(colored(exception.cli_message_header, "red"))
        print("-" * 80)

        print(colored(exception.cli_message_body, "yellow"))
        print(colored("=" * 80, "red"))
        raise

    except BaseException as exception:
        catch_crash(exception)


def catch_crash(exception: BaseException) -> None:
    """
    Catch crashes during program execution and log them in a file.

    Args:
    ----
    exception (BaseException): The exception instance captured during crash.

    Returns:
    -------
    None
    """
    filename = write_crash_log()
    print_crash_message(filename)


def write_crash_log() -> str:
    """
    Create a log entry of an internal error that occurred during program execution.

    Returns:
    -------
    filename (str): The name of the log file where the error details are written.
    """

    timestamp = str(datetime.now().isoformat()).replace(":", "-")
    filename = f"werk24-crash-{timestamp}.log"
    content = f"=== [Internal Error] ===\n\nCALLSTACK:\n{traceback.format_exc()}"

    with open(filename, "w") as crash_log:
        crash_log.write(content)

    return filename


def print_crash_message(filename: str) -> None:
    """
    Print an error message regarding an internal crash.

    Args:
    ----
    filename (str): The name of the log file containing the error details.

    Returns:
    -------
    None
    """
    separator_line = colored("=" * 80, "red")

    crash_message = [
        separator_line,
        "",
        "=== [Internal Error] ===",
        "An internal error occurred.",
        "To report the error, please send the file called:",
        "",
        f"  --> {filename} <-- ",
        "",
        "to info@werk24.io",
        "We apologize for the inconvenience.",
        "",
        separator_line,
    ]
    print("\n".join(colored(li, "red") for li in crash_message))


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
                "Part Family Characterization", m
            ),
        )
        hooks.append(c_hook)

    if args.debug_key is not None:
        c_hook = Hook(
            ask=W24AskDebug(debug_key=args.debug_key),
            function=lambda m: _save_and_open_debug(m.payload_bytes, "zip"),
        )
        hooks.append(c_hook)

    return hooks
