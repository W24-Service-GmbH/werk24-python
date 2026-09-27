import os
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.text import Text

import werk24.utils.license as license_module
from werk24.utils.defaults import API_KEYS_URL, DEMO_URL, Settings
from werk24.utils.exceptions import InvalidLicenseException
from werk24.utils.license import (
    LicenseLookup,
    locate_license,
    parse_license_text,
    save_license_file,
)

app = typer.Typer()
console = Console()
settings = Settings()


@app.command()
def init():
    """Set up Werk24 with your API key."""
    try:
        lookup: Optional[LicenseLookup] = locate_license()
    except InvalidLicenseException:
        lookup = None  # Continue to ask the user for a key

    if lookup is not None and not confirm_replacing_the_key(lookup):
        console.print("Kept the existing key.")
        return
    ask_user_to_create_license()


def _save_path() -> str:
    """The absolute path ``werk24 init`` saves the key to."""
    return os.path.abspath(license_module.USER_LICENSE_PATH)


def confirm_replacing_the_key(lookup: LicenseLookup) -> bool:
    """Say where the current key is read from and ask whether to save a new one.

    Args:
    ----
    - lookup (LicenseLookup): The key that is set up now, and its source.

    Returns:
    -------
    - bool: True to go on and save a new key. No answer (the end of the
      input) keeps the existing key.
    """
    console.print(
        Panel(
            "[bold green]An API key is already set up. It is read from "
            f"{escape(lookup.describe())}.[/bold green]"
        )
    )
    save_path = _save_path()
    if lookup.source == "environment":
        console.print(
            "[yellow]Key files are read before the environment variable "
            f"W24TECHREAD_AUTH_TOKEN, so a key saved to {escape(save_path)} "
            "would be used instead of the variable's key in every script on "
            "this computer.[/yellow]"
        )
    try:
        return typer.confirm(f"Save a new key to {save_path}?", default=False)
    except typer.Abort:
        return False


def ask_user_to_create_license():
    """Ask for an API key, or point the user to the API signup page."""
    CREATE_A_LICENSE_FILE_TEXT = """
    To use the Werk24 API, you need an API key.
    You create API keys in the Werk24 console after signing up.
    """
    console.print(
        Panel(Text(CREATE_A_LICENSE_FILE_TEXT, style="bold red"), title="API Key Setup")
    )
    console.print("[blue]Choose an option:[/blue]")
    console.print("[yellow]1.[/yellow] Paste an API key")
    console.print("[yellow]2.[/yellow] Sign up for the Werk24 API")

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
        except InvalidLicenseException as exc:
            # Nothing has been written: a refused paste never replaces a key.
            message = f"That key cannot be used: {escape(exc.reason)}."
            if attempt < max_attempts:
                console.print(f"[red]{message} Please try again.[/red]")
                continue
            console.print(f"[red]{message} Maximum number of attempts reached.[/red]")
            raise typer.Exit(code=1)  # noqa: B904

        try:
            path = save_license_file(license)
        except InvalidLicenseException as exc:
            # Pasting again would not help: the key is fine, the file is not.
            console.print(f"[red]The key was not saved: {escape(exc.reason)}.[/red]")
            raise typer.Exit(code=1)  # noqa: B904

        console.print(
            Panel(
                f"[bold green]API key saved to {escape(path)}.[/bold green]\n"
                "Scripts started from any folder on this computer will find it. "
                "To use a different key for one process or a CI job, set the "
                "environment variable W24TECHREAD_AUTH_TOKEN instead."
            )
        )
        _warn_if_shadowed(path)
        return


def _warn_if_shadowed(path: str) -> None:
    """Warn when the key just saved is not the one the client will use here.

    A leftover ``.werk24`` in the current folder is read before the key in the
    home folder. It is the user's file, so it is named, never deleted.

    Args:
    ----
    - path (str): The absolute path the new key was saved to.
    """
    try:
        lookup = locate_license()
    except InvalidLicenseException:
        console.print(
            f"[yellow]The client does not read {escape(path)}, so it will not "
            "find the new key. Set the environment variable "
            "W24TECHREAD_AUTH_TOKEN instead.[/yellow]"
        )
        return
    if lookup.source == "file" and lookup.path == path:
        return
    console.print(
        "[yellow]In this folder the key is still read from "
        f"{escape(lookup.describe())}, which takes precedence over "
        f"{escape(path)}. Remove or update it to use the new key here.[/yellow]"
    )


def sign_up_for_license():
    """Point the user to the API signup page, then accept the key they create."""
    # soft_wrap keeps each URL on one line: Rich would otherwise break a URL
    # longer than the terminal is wide, and the copied URL would not work.
    # Text() prints an overridden URL as it is, never as Rich markup.
    console.print("[blue]Sign up for the Werk24 API (billed pay as you go) at:[/blue]")
    console.print(Text(str(settings.signup_url), style="bold cyan"), soft_wrap=True)
    console.print("[blue]Then create an API key in the Werk24 console:[/blue]")
    console.print(Text(API_KEYS_URL, style="bold cyan"), soft_wrap=True)
    console.print(
        "[blue]To try Werk24 on a drawing before signing up, "
        "the browser demo is free:[/blue]"
    )
    console.print(Text(DEMO_URL, style="bold cyan"), soft_wrap=True)
    console.print("[blue]Once you have your API key, paste it below.[/blue]")
    accept_license_from_terminal()


if __name__ == "__main__":
    app()
