import asyncio
import io
import sys
from typing import Any, Optional

import typer
from pydantic import BaseModel
from rich.console import Console
from rich.pretty import Pretty
from rich.tree import Tree
from rich.text import Text
import termios
import tty

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
    """Recursively explore a nested payload structure using arrow keys.

    Navigation
    ----------
    • ``↑`` / ``↓`` – move between siblings
    • ``→`` / ``Enter`` – expand selected child
    • ``←`` – return to the parent level
    • ``q`` – quit the explorer
    """

    if not sys.stdin.isatty():
        console.print(Pretty(data))
        return

    stack: list[tuple[str | int | None, Any, int]] = [(name, data, 0)]
    while stack:
        current_name, current, selected = stack[-1]
        children = get_children(current)
        console.clear()
        display_stack(stack)

        key = read_key()
        if key == "up" and children:
            selected = (selected - 1) % len(children)
            stack[-1] = (current_name, current, selected)
        elif key == "down" and children:
            selected = (selected + 1) % len(children)
            stack[-1] = (current_name, current, selected)
        elif key in {"right", "enter"} and children:
            child_name, child_value = children[selected]
            if is_container(child_value):
                stack.append((child_name, child_value, 0))
        elif key == "left":
            if len(stack) > 1:
                stack.pop()
        elif key in {"quit", "escape"}:
            break


def display_stack(stack: list[tuple[str | int | None, Any, int]]) -> None:
    """Render the current navigation stack as a tree with context."""

    root_name, root_value, _ = stack[0]
    label = str(root_name) if root_name is not None else "payload"
    path = format_path(stack)
    console.print(Text(path, style="bold cyan"))
    tree = Tree(label, guide_style="bright_blue")

    def build(node: Tree, level: int, value: Any) -> None:
        children = get_children(value)
        if not children:
            node.add(Pretty(value))
            return

        selected_idx = stack[level][2]
        for idx, (child_name, child_value) in enumerate(children):
            is_current = level == len(stack) - 1 and idx == selected_idx
            icon = "▼" if is_container(child_value) and level + 1 < len(stack) and idx == selected_idx else (
                "▶" if is_container(child_value) else "•"
            )
            style = "reverse" if is_current else ""
            branch = node.add(f"{icon} {child_name}", style=style)
            if is_container(child_value) and level + 1 < len(stack) and idx == selected_idx:
                build(branch, level + 1, stack[level + 1][1])
            elif is_container(child_value):
                branch.add("…", style="dim")
            else:
                branch.add(Pretty(child_value))

    build(tree, 0, root_value)
    console.print(tree)
    console.print(
        Text(
            "↑/↓ move  ← parent  →/Enter expand  q quit",
            style="dim",
        )
    )


def format_path(stack: list[tuple[str | int | None, Any, int]]) -> str:
    """Return a breadcrumb-like path of the current selection."""

    parts: list[str] = []
    for name, _, _ in stack:
        parts.append(str(name) if name is not None else "payload")
    return " > ".join(parts)


def get_children(data: Any) -> list[tuple[str | int, Any]]:
    """Return the child items of a container object."""

    if isinstance(data, dict):
        return list(data.items())
    if isinstance(data, list):
        return list(enumerate(data))
    if isinstance(data, BaseModel):
        return [(key, getattr(data, key)) for key in data.model_fields.keys()]
    return []


def is_container(value: Any) -> bool:
    """Return ``True`` if *value* can have nested children."""

    return isinstance(value, (dict, list, BaseModel))


def read_key() -> str:
    """Read a single key from stdin and map arrow keys."""

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        first = sys.stdin.read(1)
        if first == "\x1b":
            second = sys.stdin.read(1)
            if second in "[O":
                third = sys.stdin.read(1)
                return {
                    "A": "up",
                    "B": "down",
                    "C": "right",
                    "D": "left",
                }.get(third, "escape")
            return "escape"
        if first in {"\r", "\n"}:
            return "enter"
        if first == "q":
            return "quit"
        return first
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


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
