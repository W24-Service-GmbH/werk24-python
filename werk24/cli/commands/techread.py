import asyncio
import io
from typing import Any, Optional

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.tree import Tree
from rich.pretty import Pretty
from pydantic import BaseModel

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
    """Interactively explore the message payload.

    The payload can be a :class:`pydantic.BaseModel`, a ``dict`` or ``list``
    structure, or ``None``.  This helper collapses the payload to the first
    child level and lets the user drill down into nested structures on demand.
    """
    payload = getattr(message, "payload_dict", None)
    if payload is None:
        console.print("[yellow]No payload available for this message[/yellow]")
        return

    explore(payload)


def explore(data: Any, name: str | int | None = None) -> None:
    """Recursively explore a nested payload structure.

    Parameters
    ----------
    data:
        The object to explore. Typically the ``payload`` from a
        :class:`TechreadMessage`.
    name:
        Optional label for the current level. Used when navigating through
        lists to display the index that was selected.
    """

    stack: list[tuple[str | int | None, Any]] = [(name, data)]
    while stack:
        current_name, current = stack[-1]
        console.clear()
        display_tree(current, current_name)

        if isinstance(current, dict):
            keys = list(current.keys())
            choice = Prompt.ask(
                "Enter key to expand, '..' to go back or leave empty to quit",
                default="",
            )
            if choice == "":
                break
            if choice == "..":
                stack.pop()
                continue
            if choice in current:
                stack.append((choice, current[choice]))
            else:
                console.print(f"[red]Key '{choice}' not found[/red]")
                Prompt.ask("Press enter to continue")
        elif isinstance(current, list):
            choice = Prompt.ask(
                "Enter index to expand, '..' to go back or leave empty to quit",
                default="",
            )
            if choice == "":
                break
            if choice == "..":
                stack.pop()
                continue
            try:
                index = int(choice)
                stack.append((index, current[index]))
            except (ValueError, IndexError):
                console.print("[red]Invalid index[/red]")
                Prompt.ask("Press enter to continue")
        elif isinstance(current, BaseModel):
            keys = list(current.model_fields.keys())
            choice = Prompt.ask(
                "Enter field to expand, '..' to go back or leave empty to quit",
                default="",
            )
            if choice == "":
                break
            if choice == "..":
                stack.pop()
                continue
            if choice in keys:
                stack.append((choice, getattr(current, choice)))
            else:
                console.print(f"[red]Field '{choice}' not found[/red]")
                Prompt.ask("Press enter to continue")
        else:
            Prompt.ask("Value displayed. Press enter to go back")
            stack.pop()


def display_tree(data: object, name: str | int | None) -> None:
    """Display a single level of the given data structure as a tree."""

    label = str(name) if name is not None else "payload"
    tree = Tree(label)

    if isinstance(data, dict):
        for key, value in data.items():
            branch = tree.add(str(key))
            if isinstance(value, (dict, list, BaseModel)):
                branch.add("...")
            else:
                branch.add(Pretty(value))
    elif isinstance(data, list):
        for idx, value in enumerate(data):
            branch = tree.add(str(idx))
            if isinstance(value, (dict, list, BaseModel)):
                branch.add("...")
            else:
                branch.add(Pretty(value))
    elif isinstance(data, BaseModel):
        for key in data.model_fields.keys():
            value = getattr(data, key)
            branch = tree.add(str(key))
            if isinstance(value, (dict, list, BaseModel)):
                branch.add("...")
            else:
                branch.add(Pretty(value))
    else:
        tree.add(Pretty(data))

    console.print(tree)


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
