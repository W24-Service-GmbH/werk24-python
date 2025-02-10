from enum import Enum

import typer
from rich.console import Console
from rich.panel import Panel

from ..utils.defaults import Settings
from ..utils.exceptions import TechreadException
from ..utils.logger import get_logger
from .commands.health_check import app as health_check_app
from .commands.init import app as init_app
from .commands.techread import app as techread_app
from .commands.version import app as version_app

settings = Settings()


console = Console()
logger = get_logger(__name__)

app = typer.Typer(pretty_exceptions_show_locals=False, no_args_is_help=True)
app.add_typer(init_app)
app.add_typer(health_check_app)
app.add_typer(techread_app)
app.add_typer(version_app)


class PromptType(str, Enum):
    """Type of prompt to display"""

    YES = "y"
    NO = "n"


# Callback function for global options
def common_options(log_level: str = typer.Option("WARNING", help="Set the log level")):
    logger.setLevel(level=log_level.upper())
    logger.info(f"Log level set to {log_level}")


# Add the callback to the Typer app
app.callback()(common_options)


if __name__ == "__main__":
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
    except Exception as e:
        raise e
