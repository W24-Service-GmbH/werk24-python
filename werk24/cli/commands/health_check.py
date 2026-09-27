import asyncio
import platform
import sys
from dataclasses import dataclass
from typing import Optional

import typer
from packaging.version import Version
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from werk24._version import __version__
from werk24.techread import Werk24Client
from werk24.utils.defaults import Settings
from werk24.utils.exceptions import ApiKeyRejectedException, InvalidLicenseException
from werk24.utils.license import LicenseLookup, locate_license, token_suffix

# Initialize Typer app and Rich console
app = typer.Typer()
console = Console()
settings = Settings()


@dataclass
class ConnectionCheck:
    """The outcome of opening a WebSocket connection with the configured key.

    Attributes:
    ----------
    - outcome (str): "connected", "key_rejected", "failed" or "skipped"
      (no key was found, so no connection was attempted).
    - error (Optional[BaseException]): The exception, when there was one.
    """

    outcome: str
    error: Optional[BaseException] = None


@app.command()
def health_check():
    """Run a comprehensive health check for the CLI."""
    console.print(Panel(f"[blue]Werk24 CLI Health Check v{__version__}[/blue]"))
    system_information()

    try:
        lookup: Optional[LicenseLookup] = locate_license()
    except InvalidLicenseException:
        lookup = None

    check = (
        asyncio.run(check_connection())
        if lookup is not None
        else ConnectionCheck("skipped")
    )

    license_information(lookup, check)
    network_information(check)

    # Informational only: the status page says how the service is doing, not
    # whether this machine can use it.
    asyncio.run(status_information())

    if check.outcome == "key_rejected":
        e = check.error
        console.print(
            Panel(
                f"[red]{e.cli_message_header}: {escape(e.cli_message_body)}[/red]",
                expand=True,
                border_style="red",
                title="Error",
            )
        )

    if lookup is None or check.outcome != "connected":
        raise typer.Exit(code=1)


async def check_connection() -> ConnectionCheck:
    """Open a WebSocket connection with the configured key and report how it went."""
    try:
        async with Werk24Client():
            return ConnectionCheck("connected")
    except ApiKeyRejectedException as e:
        return ConnectionCheck("key_rejected", e)
    except Exception as e:
        return ConnectionCheck("failed", e)


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


def license_information(
    lookup: Optional[LicenseLookup], check: ConnectionCheck
) -> None:
    """
    Display license information in a formatted panel.

    Args:
    ----
    - lookup (Optional[LicenseLookup]): The key that was found and where, or
      None when no key was found.
    - check (ConnectionCheck): Whether the API accepted the key.
    """
    if lookup is None:
        license_status = (
            "[red]Not Found[/red] - Run [bold]werk24 init[/bold] to configure."
        )
        print_panel("License Information", [("License Status", license_status)])
        return

    suffix = token_suffix(lookup.license.token)
    license_info = [
        ("License Status", "[green]Found[/green]"),
        ("Key", f"ending in {escape(suffix)}" if suffix else "(too short to show)"),
        ("Source", escape(lookup.describe())),
    ]
    if lookup.env_shadowed:
        license_info.append(
            (
                "Note",
                "[yellow]W24TECHREAD_AUTH_TOKEN is also set, to a different key, "
                "and is ignored because this file is read first.[/yellow]",
            )
        )

    key_check = {
        "connected": "[green]Accepted[/green]",
        "key_rejected": "[red]Rejected by the Werk24 API[/red]",
        "failed": "[yellow]Not checked (no connection)[/yellow]",
    }.get(check.outcome)
    if key_check is not None:
        license_info.append(("Key Check", key_check))

    print_panel("License Information", license_info)


def network_information(check: ConnectionCheck) -> None:
    """
    Display the outcome of the WebSocket connection test.

    Args:
    ----
    - check (ConnectionCheck): The outcome of the connection attempt.
    """
    server_uri = str(settings.wss_server)
    if check.outcome == "connected":
        status = "[green]Successful[/green]"
    elif check.outcome == "key_rejected":
        status = "[red]Refused: API key rejected[/red]"
    elif check.outcome == "failed":
        e = check.error
        status = f"[red]Error: {type(e).__name__} - {escape(str(e))}[/red]"
    else:
        status = "[yellow]Skipped: no API key found[/yellow]"

    print_panel(
        "Network Information", [(f"WebSocket Connection ({server_uri})", status)]
    )


async def status_information():
    """Display the system status information."""
    status_info = []
    try:
        status = await Werk24Client.get_system_status()
        status_info.append(("Indicator", status.status_indicator))
        if status.status_description:
            status_info.append(("Description", status.status_description))
    except Exception as e:
        status_info.append(("Error", f"[red]{type(e).__name__} - {e}[/red]"))

    print_panel("System Status", status_info)


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
