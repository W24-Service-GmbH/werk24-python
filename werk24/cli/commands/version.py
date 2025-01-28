import typer

from werk24._version import __version__

app = typer.Typer()


@app.command()
def version():
    """Print the version of the Client."""
    print(__version__)
