import asyncio
import io
from typing import Optional

import typer
from rich.console import Console

from werk24.models import (
    AskBalloons,
    AskCustom,
    AskFeatures,
    AskInsights,
    AskMetaData,
    AskReferencePositions,
    AskSheetImages,
    AskViewImages,
    Hook,
    TechreadMessage,
)
from werk24.techread import Werk24Client
from werk24.utils.defaults import Settings
from werk24.utils.exceptions import UserInputError
from werk24.utils.logger import get_logger

console = Console()
app = typer.Typer()
settings = Settings()
logger = get_logger()


@app.command()
def techread(
    file_path: str = typer.Argument(..., help="The file path to read"),
    server: str = typer.Option(settings.wss_server, help="The server to read from"),
    max_pages: int = typer.Option(
        settings.max_pages, help="The maximum number of pages to read"
    ),
    ask_balloons: bool = typer.Option(False, help="Ask for balloons"),
    ask_custom: Optional[str] = typer.Option(None, help="Ask for custom output"),
    ask_features: bool = typer.Option(False, help="Ask for features"),
    ask_insights: bool = typer.Option(False, help="Ask for insights"),
    ask_meta_data: bool = typer.Option(False, help="Ask for meta data"),
    ask_reference_positions: bool = typer.Option(
        False, help="Ask for reference positions"
    ),
    ask_sheet_images: bool = typer.Option(False, help="Ask for sheet images"),
    ask_view_images: bool = typer.Option(False, help="Ask for view image"),
):
    """Read a drawing file and extract information."""

    # Register the hooks
    hooks = [
        Hook(ask=AskBalloons(), function=recv_payload) if ask_balloons else None,
        (
            Hook(ask=AskCustom(custom_id=ask_custom), function=recv_payload)
            if ask_custom
            else None
        ),
        Hook(ask=AskFeatures(), function=recv_payload) if ask_features else None,
        Hook(ask=AskInsights(), function=recv_payload) if ask_insights else None,
        Hook(ask=AskMetaData(), function=recv_payload) if ask_meta_data else None,
        (
            Hook(ask=AskReferencePositions(), function=recv_payload)
            if ask_reference_positions
            else None
        ),
        (
            Hook(ask=AskSheetImages(), function=recv_thumbnail)
            if ask_sheet_images
            else None
        ),
        Hook(ask=AskViewImages(), function=recv_thumbnail) if ask_view_images else None,
    ]
    hooks = [hook for hook in hooks if hook]
    if not hooks:
        raise UserInputError("No hooks selected. At least one hook must be enabled.")

    with open(file_path, "rb") as fid:
        asyncio.run(run(server, fid, hooks, max_pages))


async def run(server: str, fh: str, hooks: list[Hook], max_pages: int):
    async with Werk24Client(server) as client:
        await client.read_drawing_with_hooks(fh, hooks, max_pages)


def recv_payload(message: TechreadMessage):
    print(f"Received message: {message}")
    print(type(message.payload_dict))
    console.print(message.payload_dict)


def recv_thumbnail(message: TechreadMessage):
    """
    Display a debug image. The function relies on
    the PIL functionality of Image.show(). The
    actual behavior will thus be different across platforms

    Args:
    ----
    - log_text (str): Log Text that we want to write back
      to the command line interface
    - image_bytes (bytes): byte representation of the image
      that is to be displayed
    """

    # Import the PIL at runtime to make sure that
    # you can still use the client without the need
    # to install Pillow
    try:
        from PIL import Image  # pylint: disable=import-outside-toplevel
    except ImportError as e:
        raise UserInputError(
            "Viewing image-like responses requires the installation"
            " of the PIL package: pip install pillow. Image skipped."
        ) from e

    # and show the image
    image = Image.open(io.BytesIO(message.payload_bytes))
    try:
        image.show(title=message.payload_bytes)
    except BaseException as exc:
        raise UserInputError(f"Image cannot be displayed: {exc}") from exc
