import sys
from enum import Enum

import typer
from rich.console import Console
from rich.panel import Panel

from ..utils.defaults import Settings
from ..utils.exceptions import TechreadException
from ..utils.logger import get_logger
from .commands.health_check import app as health_check_app
from .commands.init import app as init_app
from .commands.status import app as status_app
from .commands.techread import app as techread_app
from .commands.version import app as version_app

settings = Settings()


console = Console()
logger = get_logger()

app = typer.Typer(pretty_exceptions_show_locals=False, no_args_is_help=True)
app.add_typer(init_app)
app.add_typer(health_check_app)
app.add_typer(techread_app)
app.add_typer(version_app)
app.add_typer(status_app)


class PromptType(str, Enum):
    """Type of prompt to display"""

    YES = "y"
    NO = "n"


# Callback function for global options
def common_options(log_level: str = typer.Option("WARNING", help="Set the log level")):
    level = log_level.upper()
    if level not in Settings.VALID_LOG_LEVELS:
        raise typer.BadParameter(
            f"Invalid log level '{log_level}'. Valid values are: "
            f"{', '.join(sorted(Settings.VALID_LOG_LEVELS))}"
        )
    logger.setLevel(level)
    logger.info(f"Log level set to {level}")


# Add the callback to the Typer app
app.callback()(common_options)


def main() -> None:
    """Entry point for the ``werk24`` CLI.

    This wraps the Typer app so that ``TechreadException`` errors are rendered as
    a friendly panel regardless of how the CLI is launched (the installed
    ``werk24`` console script, ``python -m werk24``, or ``python werk24.py``).
    """
    try:
        app()
    except TechreadException as exception:
        console.print(
            Panel(
                f"[red]{exception.cli_message_header}: {exception.cli_message_body}[/red]",
                expand=True,
                border_style="red",
                title="Error",
            )
        )
        # Exit with a non-zero status without emitting a traceback. typer.Exit is
        # only meaningful inside a Click command context, so use sys.exit here.
        sys.exit(1)


if __name__ == "__main__":
    main()
