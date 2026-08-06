import sys

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from werk24.utils.defaults import Settings
from werk24.utils.exceptions import InvalidLicenseException
from werk24.utils.license import (
    find_license,
    parse_license_text,
    save_license_file,
)

app = typer.Typer()
console = Console()
settings = Settings()


@app.command()
def init():
    """Initialize Werk24 by providing or creating a license token."""
    try:
        find_license()
        console.print(
            Panel(
                "[bold green]Werk24 is already initialized. Run 'werk24 --help' for options.[/bold green]"
            )
        )
        return
    except InvalidLicenseException:
        pass  # Continue to ask user to provide a token
    ask_user_to_create_license()


def ask_user_to_create_license():
    """Guide the user to provide or create a license token."""
    CREATE_A_LICENSE_FILE_TEXT = """
    To use Werk24, you need a valid token.
    If you don't have one, you can sign up to get a license.
    """
    console.print(
        Panel(Text(CREATE_A_LICENSE_FILE_TEXT, style="bold red"), title="License Setup")
    )
    console.print("[blue]Choose an option:[/blue]")
    console.print("[yellow]1.[/yellow] Provide a token")
    console.print("[yellow]2.[/yellow] Sign up to get a license")

    while True:
        try:
            choice = typer.prompt("Enter your choice (1 or 2)", type=int)
            if choice == 1:
                accept_license_from_terminal()
                break
            elif choice == 2:
                sign_up_for_license()
                break
            else:
                raise ValueError("Invalid choice")
        except ValueError:
            console.print("[red]Invalid input. Please enter 1 or 2.[/red]")


def accept_license_from_terminal():
    """Accept a token from the user.

    The token you receive during registration can be pasted directly. For
    backwards compatibility, a legacy license block (``W24TECHREAD_AUTH_TOKEN=...``)
    is also accepted.
    """
    console.print(
        "[blue]Please paste your token below and press [bold]Enter[/bold] twice when done:[/blue]"
    )

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        license_text = ""
        while True:
            try:
                raw_line = sys.stdin.readline()
            except KeyboardInterrupt:
                console.print("[red]Input cancelled. Exiting...[/red]")
                raise typer.Exit()  # noqa: B904

            # readline() returns "" only at EOF (e.g. Ctrl-D or a closed/piped
            # stdin), which is distinct from a blank line ("\n"). Detect EOF
            # explicitly so we do not loop or recurse forever on empty input.
            if raw_line == "":
                break

            line = raw_line.strip()
            if not line:  # a blank line terminates the paste
                break
            license_text += line + "\n"

        if not license_text.strip():
            console.print("[red]No token provided. Aborting.[/red]")
            raise typer.Exit(code=1)

        try:
            license = parse_license_text(license_text)
            save_license_file(license)
            console.print(Panel("[bold green]Token successfully saved![/bold green]"))
            return
        except InvalidLicenseException:
            if attempt < max_attempts:
                console.print("[red]Invalid token. Please try again.[/red]")
            else:
                console.print(
                    "[red]Invalid token. Maximum number of attempts reached.[/red]"
                )
                raise typer.Exit(code=1)  # noqa: B904


def sign_up_for_license():
    """Guide the user to sign up for a license and obtain a token."""
    console.print("[blue]To sign up for a license, visit the following URL:[/blue]")
    console.print(f"[bold cyan]{settings.signup_url}[/bold cyan]")
    console.print("[blue]Once you have your token, paste it below.[/blue]")
    accept_license_from_terminal()


if __name__ == "__main__":
    app()
