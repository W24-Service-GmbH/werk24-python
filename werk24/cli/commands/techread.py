import asyncio
import io
from functools import partial
from typing import Optional

import typer
from rich.console import Console

from werk24.models import (
    AskBalloons,
    AskCustom,
    AskDocumentProfile,
    AskFeatures,
    AskInsights,
    AskMetaData,
    AskPageAssessment,
    AskRedaction,
    AskReferencePositions,
    AskSheetImages,
    AskViewImages,
    Hook,
    TechreadMessage,
    TechreadMessageSubtype,
    TechreadMessageType,
)
from werk24.techread import Werk24Client
from werk24.utils.defaults import Settings
from werk24.utils.exceptions import UserInputError
from werk24.utils.logger import get_logger

# Kept so the name keeps working. Output goes through print_message() and
# report_exceptions() instead.
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
    ask_document_profile: bool = typer.Option(
        False,
        help="Ask for the document profile (page count, paper size, "
        "processing-time estimate)",
    ),
    ask_features: bool = typer.Option(False, help="Ask for features"),
    ask_insights: bool = typer.Option(False, help="Ask for insights"),
    ask_meta_data: bool = typer.Option(False, help="Ask for meta data"),
    ask_page_assessment: bool = typer.Option(
        False, help="Ask for the page assessment (page type and welding, per page)"
    ),
    ask_redaction: bool = typer.Option(
        False,
        help="Ask for a redacted copy of the drawing (the JSON carries the "
        "redaction zones and a payload_url for the redacted file)",
    ),
    ask_reference_positions: bool = typer.Option(
        False, help="Ask for reference positions"
    ),
    ask_sheet_images: bool = typer.Option(False, help="Ask for sheet images"),
    ask_view_images: bool = typer.Option(False, help="Ask for view image"),
    pretty: bool = typer.Option(
        False,
        "--pretty",
        help="Indent each JSON object over several lines instead of printing "
        "one object per line",
    ),
):
    """Read a drawing file and extract information.

    Prints one JSON object on stdout for every message that answers an ask:
    the fields of TechreadMessage, without the downloaded payload_bytes.
    Exceptions the server reports are written to stderr. The exit status is 1
    when an ask failed or the read did not complete, and 0 otherwise.
    """
    payload = partial(recv_payload, pretty=pretty)
    thumbnail = partial(recv_thumbnail, pretty=pretty)

    # Register the hooks, in the order of the options above
    hooks = [
        Hook(ask=AskBalloons(), function=payload) if ask_balloons else None,
        (
            Hook(ask=AskCustom(custom_id=ask_custom), function=payload)
            if ask_custom
            else None
        ),
        (
            Hook(ask=AskDocumentProfile(), function=payload)
            if ask_document_profile
            else None
        ),
        Hook(ask=AskFeatures(), function=payload) if ask_features else None,
        Hook(ask=AskInsights(), function=payload) if ask_insights else None,
        Hook(ask=AskMetaData(), function=payload) if ask_meta_data else None,
        (
            Hook(ask=AskPageAssessment(), function=payload)
            if ask_page_assessment
            else None
        ),
        Hook(ask=AskRedaction(), function=payload) if ask_redaction else None,
        (
            Hook(ask=AskReferencePositions(), function=payload)
            if ask_reference_positions
            else None
        ),
        Hook(ask=AskSheetImages(), function=thumbnail) if ask_sheet_images else None,
        Hook(ask=AskViewImages(), function=thumbnail) if ask_view_images else None,
    ]
    hooks = [hook for hook in hooks if hook]
    if not hooks:
        raise UserInputError(
            "No ask selected. Pass at least one --ask-* option, "
            "for example --ask-meta-data."
        )

    with open(file_path, "rb") as fid:
        # A drawing the upload cannot take exits here, through main()'s
        # error panel, before any connection is made.
        Werk24Client.check_drawing_size(fid)
        exit_code = asyncio.run(run(server, fid, hooks, max_pages))
    if exit_code:
        raise typer.Exit(code=exit_code)


async def run(server: str, fh: str, hooks: list[Hook], max_pages: int) -> int:
    """Read the drawing, call the hooks and return the exit status.

    Every message is checked, not only the ones a hook answers: exceptions
    are reported on stderr, and the status is 1 when an ask failed, the
    server sent an ERROR message, or the read ended before the server
    reported it complete. Otherwise it is 0.
    """
    asks = [hook.ask for hook in hooks if hook.ask is not None]
    failed = False
    completed = False
    async with Werk24Client(server) as client:
        async for message in client.read_drawing(fh, asks, max_pages=max_pages):
            report_exceptions(message)
            if (
                not message.is_successful
                or message.message_type == TechreadMessageType.ERROR
            ):
                failed = True
            if (
                message.message_type == TechreadMessageType.PROGRESS
                and message.message_subtype
                == TechreadMessageSubtype.PROGRESS_COMPLETED
            ):
                completed = True
            await client.call_hooks_for_message(message, hooks)
    if not completed and not failed:
        typer.echo(
            "ERROR: the read ended before the server reported it complete; "
            "the results may be incomplete.",
            err=True,
        )
        failed = True
    return 1 if failed else 0


def _name(value) -> str:
    """The plain name of an enum member, or the value itself.

    An exception type this client does not know arrives as a plain string.
    """
    return getattr(value, "value", value)


def report_exceptions(message: TechreadMessage) -> None:
    """Write one line to stderr for each exception on the message.

    A server ERROR message without exceptions gets a line of its own.
    """
    subtype = _name(message.message_subtype)
    for exception in message.exceptions:
        details = f"page {message.page_number}"
        if exception.ask_type:
            details += f", ask {_name(exception.ask_type)}"
        if exception.reason:
            details += f", reason {_name(exception.reason)}"
        typer.echo(
            f"{_name(exception.exception_level)}: "
            f"{_name(exception.exception_type)} on {subtype} ({details})",
            err=True,
        )
    if message.message_type == TechreadMessageType.ERROR and not message.exceptions:
        typer.echo(
            f"ERROR: the server reported {subtype} (page {message.page_number})",
            err=True,
        )


def print_message(message: TechreadMessage, pretty: bool = False) -> None:
    """Print the message as one JSON object on stdout.

    The downloaded payload_bytes are left out: they are binary (an image, a
    PDF) and can be fetched from payload_url. The text is written as UTF-8
    bytes, so a symbol such as a diameter sign cannot fail on a console
    whose code page lacks it.
    """
    text = message.model_dump_json(
        exclude={"payload_bytes"}, indent=2 if pretty else None
    )
    typer.echo(text.encode("utf-8"))


def recv_payload(message: TechreadMessage, pretty: bool = False):
    print_message(message, pretty=pretty)


def recv_thumbnail(message: TechreadMessage, pretty: bool = False):
    """
    Print the message as JSON, then display the image. The function relies
    on the PIL functionality of Image.show(). The actual behavior will thus
    be different across platforms

    Args:
    ----
    - message (TechreadMessage): The message that carries the image in
      its payload_bytes
    - pretty (bool): Indent the JSON object over several lines
    """
    print_message(message, pretty=pretty)

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
        image.show(title=str(message.message_subtype))
    except BaseException as exc:
        raise UserInputError(f"Image cannot be displayed: {exc}") from exc
