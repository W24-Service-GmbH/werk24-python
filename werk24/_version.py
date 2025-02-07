import importlib.metadata
from contextlib import suppress
from pathlib import Path


def extract_version() -> str:
    """Returns either the version of installed package or the one
    found in nearby pyproject.toml"""
    with suppress(FileNotFoundError, StopIteration):
        root_dir = Path(__file__).parent.parent
        with open(root_dir / "pyproject.toml", encoding="utf-8") as pyproject_toml:
            version = (
                next(line for line in pyproject_toml if line.startswith("version"))
                .split("=")[1]
                .strip("'\"\n ")
            )
            return f"{version}"
    return importlib.metadata.version(__package__ or __name__.split(".", maxsplit=1)[0])


__version__ = extract_version()
