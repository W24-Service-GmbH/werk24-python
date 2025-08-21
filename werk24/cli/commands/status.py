import asyncio

import typer
from rich.console import Console

from werk24.techread import Werk24Client

app = typer.Typer()
console = Console()


@app.command()
def status():
    """Fetch and display the Werk24 system status."""

    system_status = asyncio.run(Werk24Client.get_system_status())
    console.print_json(data=system_status.model_dump())
