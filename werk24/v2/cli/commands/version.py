import typer

app = typer.Typer()
from werk24._version import __version__


@app.command()
def version():
    """Print the version of the Client."""
    print(__version__)
