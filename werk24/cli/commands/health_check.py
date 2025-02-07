import asyncio
import platform
import sys

import typer
from packaging.version import Version
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from websockets.exceptions import InvalidStatus, InvalidStatusCode

from werk24._version import __version__
from werk24.techread import Werk24Client
from werk24.utils.defaults import Settings
from werk24.utils.license import LicenseInvalid, find_license

# Initialize Typer app and Rich console
app = typer.Typer()
console = Console()
settings = Settings()


@app.command()
def health_check():
    """Run a comprehensive health check for the CLI."""
    console.print(Panel(f"[blue]Werk24 CLI Health Check v{__version__}[/blue]"))
    system_information()
    license_information()
    asyncio.run(network_information())


def system_information():
    """
    Display system information in a formatted panel.
    """
    python_version = Version(sys.version.split(" ")[0])
    python_version_supported = any(
        c_version.major == python_version.major
        and c_version.minor == python_version.minor
        for c_version in settings.supported_python_versions
    )
    python_version_status = (
        "[green]Supported[/green]"
        if python_version_supported
        else "[red]Not Supported[/red]"
    )

    if python_version.is_prerelease:
        python_version_status += " [yellow](Prerelease)[/yellow]"

    system_info = [
        ("Operating System", f"{platform.system()} {platform.release()}"),
        ("Python Version", f"{sys.version.split(' ')[0]} ({python_version_status})"),
    ]
    print_panel("System Information", system_info)


def license_information():
    """
    Display license information in a formatted panel.
    """
    try:
        find_license()
        license_status = "[green]Found[/green]"
    except LicenseInvalid:
        license_status = (
            "[red]Not Found[/red] - Run [bold]werk24 init[/bold] to configure."
        )

    license_info = [("License Status", license_status)]
    print_panel("License Information", license_info)


async def network_information():
    """
    Display network information and test WebSocket connections.
    """
    server_uri = str(settings.wss_server)
    network_info = []

    try:
        async with Werk24Client() as _:
            network_info.append(
                (f"WebSocket Connection ({server_uri})", "[green]Successful[/green]")
            )

    except InvalidStatus as e:  # WebSocket >= 14.0
        if e.response.status_code == 401:
            network_info.append(
                (
                    f"WebSocket Connection ({server_uri})",
                    "[yellow]Unauthorized (401)[/yellow]",
                )
            )
        else:
            network_info.append(
                (
                    f"WebSocket Connection ({server_uri})",
                    f"[red]Error: {e.response.status_code}[/red]",
                )
            )

    except InvalidStatusCode as e:  # WebSocket < 14.0
        if e.status_code == 401:
            network_info.append(
                (
                    f"WebSocket Connection ({server_uri})",
                    "[yellow]Unauthorized (401)[/yellow]",
                )
            )
        else:
            network_info.append(
                (
                    f"WebSocket Connection ({server_uri})",
                    f"[red]Error: {e.status_code}[/red]",
                )
            )

    except Exception as e:
        network_info.append(
            (
                f"WebSocket Connection ({server_uri})",
                f"[red]Error: {type(e).__name__} - {e}[/red]",
            )
        )

    print_panel("Network Information", network_info)


def print_panel(title: str, rows: list[tuple[str, str]]) -> None:
    """
    Print a panel with a title and tabulated rows of information.

    Args:
        title (str): The title of the panel.
        rows (list[tuple[str, str]]): A list of key-value pairs to display.
    """
    table = Table(show_header=False, box=None, pad_edge=False, expand=False)
    for caption, value in rows:
        table.add_row(f"[bold]{caption}[/bold]:", value)
    console.print(Panel(table, title=f"[bold blue]{title}[/bold blue]"))


if __name__ == "__main__":
    app()
