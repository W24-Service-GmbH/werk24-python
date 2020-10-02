import os
from pathlib import Path

CWD = Path(os.path.dirname(__file__))


def get_drawing() -> bytes:
    """ Small helper function to return the bytes of
    an example drawing that can be used for testing

    Returns:
        bytes: Bytes of the Example Drawing
    """
    path = CWD / "assets" / "technical_drawing.png"
    with open(path, 'rb') as file_handle:
        return file_handle.read()
