import subprocess
import unittest

class TestCliAuth(unittest.TestCase):

    def test_ask_jwt_token(self):

        result = subprocess.check_output([
            "python",
            "-m",
            "werk24.cli.w24cli",
            "auth",
            "--ask-jwt-token"]).decode()
        
        # assume that we receive a very simple response
        parts = result.split(":", 1)

        # assert that we have exactly two parts
        assert len(parts) == 2

        # assert that the JWT token is 960 bytes long
        # the 1 is added to account for the \n
        assert len(parts[1]) == 960 +1