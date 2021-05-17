""" Utilities to simplify the tests
"""
import os
from pathlib import Path

import sys
if sys.version_info < (3, 8, 0):
    import aiounittest
    AsyncTestCase = aiounittest.AsyncTestCase

else:
    import unittest
    AsyncTestCase = unittest.IsolatedAsyncioTestCase


CWD = Path(os.path.dirname(__file__))


def get_drawing() -> bytes:
    """ Small helper function to return the bytes of
    an example drawing that can be used for testing

    Returns:
        bytes: Bytes of the Example Drawing
    """
    path = CWD / "assets" / "test_drawing.pdf"
    with open(path, 'rb') as file_handle:
        return file_handle.read()


def get_model() -> bytes:
    """ Small helper function to return the bytes of
    an example model that can be used for testing

    Returns:
        bytes: Bytes of the Example Step File
    """
    path = CWD / "assets" / "test_model.stp"
    with open(path, 'rb') as file_handle:
        return file_handle.read()
