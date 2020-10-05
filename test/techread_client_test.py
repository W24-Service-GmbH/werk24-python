import os

import aiounittest
from werk24._version import __version__
from werk24.models.techread import W24TechreadRequest
from werk24.techread_client import W24TechreadClient


class TestTechreadClient(aiounittest.AsyncTestCase):
    """ Test case for the basic Techread functionality
    """

    def test_client_version(self) -> None:
        """ Test whether Client sends version

        User Story: As Werk24 API developer I want to
        know which client versionns are still being used,
        so that I can decide whether it is safe to deprecate
        an old feature

        Github Issue #1
        """
        request = W24TechreadRequest(asks=[])
        self.assertEqual(__version__, request.client_version)

    async def test_client_without_session(self) -> None:
        """ Test whether Client without started session throws RuntimeError

        User Story: As API user I want to obtail a clear error message if
        I make a request to the client without entering a session, so that
        I can change my code swiftly.
        """
        environs = os.environ
        client = W24TechreadClient(
            environs['W24TECHREAD_SERVER_HTTPS'],
            environs['W24TECHREAD_SERVER_WSS'],
            environs['W24TECHREAD_VERSION'])

        with self.assertRaises(RuntimeError):
            async with client:
                pass
