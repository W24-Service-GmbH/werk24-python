import sys

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from werk24.utils.defaults import Settings
from werk24.utils.license import (
    LicenseInvalid,
    find_license,
    parse_license_text,
    save_license_file,
)

app = typer.Typer()
console = Console()
settings = Settings()


@app.command()
def init():
    """Initialize Werk24 by providing or creating a license."""
    try:
        find_license()
        console.print(
            Panel(
                "[bold green]Werk24 is already initialized. Run 'werk24 --help' for options.[/bold green]"
            )
        )
        return
    except LicenseInvalid:
        pass  # Continue to ask user to create a license file
    ask_user_to_create_license()


def ask_user_to_create_license():
    """Guide the user to provide or create a license."""
    CREATE_A_LICENSE_FILE_TEXT = """
    To use Werk24, you need a valid license file. 
    If you don't have one, you can create a trial license to get started.
    """
    console.print(
        Panel(Text(CREATE_A_LICENSE_FILE_TEXT, style="bold red"), title="License Setup")
    )
    console.print("[blue]Choose an option:[/blue]")
    console.print("[yellow]1.[/yellow] Provide a license file")
    console.print("[yellow]2.[/yellow] Create a trial license")

    while True:
        try:
            choice = typer.prompt("Enter your choice (1 or 2)", type=int)
            if choice == 1:
                accept_license_from_terminal()
                break
            elif choice == 2:
                create_trial_license()
                break
            else:
                raise ValueError("Invalid choice")
        except ValueError:
            console.print("[red]Invalid input. Please enter 1 or 2.[/red]")


def accept_license_from_terminal():
    """Accept license text from the user."""
    console.print(
        "[blue]Please paste your license text below and press [bold]Enter[/bold] twice when done:[/blue]"
    )

    license_text = ""
    while True:
        try:
            line = sys.stdin.readline().strip()
            if not line:  # Stop on an empty line
                break
            license_text += line + "\n"
        except KeyboardInterrupt:
            console.print("[red]Input cancelled. Exiting...[/red]")
            raise typer.Exit()  # noqa: B904

    try:
        license = parse_license_text(license_text)
        save_license_file(license)
        console.print(Panel("[bold green]License successfully saved![/bold green]"))
    except LicenseInvalid:
        console.print("[red]Invalid license text. Please try again.[/red]")
        accept_license_from_terminal()  # Retry on failure


def create_trial_license():
    """Guide the user to create a trial license."""
    console.print("[blue]To create a trial license, visit the following URL:[/blue]")
    console.print(f"[bold cyan]{settings.trial_license_url}[/bold cyan]")
    console.print("[blue]Once you have the license text, paste it below.[/blue]")
    accept_license_from_terminal()


if __name__ == "__main__":
    app()
