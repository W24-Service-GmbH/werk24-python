import os
from typing import List

import aiounittest
from werk24._version import __version__
from werk24.exceptions import UnsupportedMediaType
from werk24.models.ask import W24Ask, W24AskVariantCAD
from werk24.models.techread import W24TechreadRequest
from werk24.techread_client import W24TechreadClient

from .utils import get_drawing, get_model


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

    async def test_client_usernames(self):
        """ Test access username

        User Story: As API user I want to access my own username,
        so that I can verify that the login process worked correctly.
        """
        client = W24TechreadClient.make_from_env(None)
        async with client as session:
            self.assertEqual(type(session.username), str)

    async def test_upload_model(self) -> None:
        """ Test whether we can upload an associaed model.

        User Story: As API user, want to be able to upload an associated
        model file, so that I can support Werk24's training effort
        """
        asks: List[W24Ask] = [W24AskVariantCAD(is_training=True)]
        drawing = get_drawing()
        model = get_model()

        client = W24TechreadClient.make_from_env(None)
        async with client as session:
            async for _ in session.read_drawing(drawing, asks, model):
                pass

    async def test_string_as_drawing_bytes(self) -> None:
        """ Test whether submitting a string as drawing_bytes 
        raises the correct exception. 
        
        See Github Issue #13
        """
        client = W24TechreadClient.make_from_env()

        with self.assertRaises(UnsupportedMediaType):
            async with client as session:
                async for _ in session.read_drawing("", asks=[]): 
                    pass    
