from typing import List
import sys
import subprocess
import unittest


class TestCliAuth(unittest.TestCase):

    @staticmethod
    def _call_cli(command: List[str]) -> str:

        # get the absolute path of the python executable
        # to stay safe
        executable = sys.executable

        # then make the call and return the result

        return subprocess.check_output([
            executable,
            "-m", "werk24.cli.w24cli"
        ] + command
        ).decode()

    def test_ask_jwt_token(self):

        # call!
        result = self._call_cli(["auth", "--ask-jwt-token"])

        # assume that we receive a very simple response
        parts = result.split(":", 1)

        # assert that we have exactly two parts
        assert len(parts) == 2

        # assert that the JWT token is 960 bytes long
        # the 1 is added to account for the \n
        assert len(parts[1].strip()) > 500
