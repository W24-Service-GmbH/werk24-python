import asyncio

import typer
from rich.console import Console

from werk24._version import __version__
from werk24.v2.defaults import Settings
from werk24.v2.logger import LogLevel, get_logger
from werk24.v2.models.techread import (
    AskThumbnail,
    AskTitleBlock,
    Hook,
    TechreadMessage,
    ThumbnailType,
)
from werk24.v2.techread import Werk24Client

console = Console()
app = typer.Typer()
settings = Settings()


@app.command()
def techread(
    file_path: str = typer.Argument(..., help="The file path to read"),
    server: str = typer.Option(settings.wss_server, help="The server to read from"),
    max_pages: int = typer.Option(
        settings.max_pages, help="The maximum number of pages to read"
    ),
    ask_thumbnail: ThumbnailType = typer.Option(None, help="Ask for a thumbnail"),
    # ask_thumbnail: bool = typer.Option(False, help="Ask for sheet thumbnail"),
    # ask_view_thumbnails: bool = typer.Option(False, help="Ask for view thumbnails"),
    # ask_custom_output_format: bool = typer.Option(False, help="Ask for your custom output format"),
    # ask_pmi_extract: bool = typer.Argument(False, help="Ask for PMI extraction"),
):
    """Read a drawing file and extract information."""
    logger = get_logger()

    hooks = [Hook(ask=AskTitleBlock(), function=recv_title_block)]
    if ask_thumbnail:
        hooks.append(AskThumbnail(thumbnail_type=ask_thumbnail))

    if not hooks:
        logger.error("No hooks selected. At least one hook must be enabled.")
        raise typer.Exit(code=1)

    with open(file_path, "rb") as file:
        data = file.read()

    asyncio.run(run(server, data, hooks, max_pages))


async def run(server: str, data: bytes, hooks: list[Hook], max_pages: int):
    async with Werk24Client(server) as client:
        await client.read_drawing_with_hooks(data, hooks, max_pages)


def recv_title_block(message: TechreadMessage):
    console.print(message.payload_dict)
