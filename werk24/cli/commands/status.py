import asyncio

import typer
from rich.console import Console

from werk24.techread import Werk24Client

app = typer.Typer()
console = Console()


@app.command()
def status(
    custom_cafile: str = typer.Option(
        None, help="Path to an additional CA bundle for TLS verification"
    )
):
    """Fetch and display the Werk24 system status."""

    if custom_cafile:
        system_status = asyncio.run(
            Werk24Client.get_system_status(custom_cafile=custom_cafile)
        )
    else:
        system_status = asyncio.run(Werk24Client.get_system_status())
    console.print_json(data=system_status.model_dump(mode="json"))
