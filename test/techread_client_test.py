import os
from test.utils import AsyncTestCase
from typing import List

from werk24._version import __version__
from werk24.exceptions import UnsupportedMediaType
from werk24.models.ask import W24Ask, W24AskPageThumbnail, W24AskVariantCAD
from werk24.models.techread import (
    W24TechreadExceptionType,
    W24TechreadMessageType,
    W24TechreadRequest,
)
from werk24.techread_client import W24TechreadClient

from .utils import get_drawing, get_model


class TestTechreadClient(AsyncTestCase):
    """Test case for the basic Techread functionality"""

    def test_client_version(self) -> None:
        """Test whether Client sends version

        User Story: As Werk24 API developer I want to
        know which client versions are still being used,
        so that I can decide whether it is safe to deprecate
        an old feature

        Github Issue #1
        """
        request = W24TechreadRequest(asks=[])
        self.assertEqual(__version__, request.client_version)

    async def test_client_without_session(self) -> None:
        """Test whether Client without started session throws RuntimeError

        User Story: As API user I want to obtain a clear error message if
        I make a request to the client without entering a session, so that
        I can change my code swiftly.
        """
        client = W24TechreadClient(None, None)
        with self.assertRaises(RuntimeError):
            async with client:
                pass

    async def test_upload_model(self) -> None:
        """Test whether we can upload an associated model.

        User Story: As API user, want to be able to upload an associated
        model file, so that I can support Werk24's training effort
        """
        asks: List[W24Ask] = [W24AskPageThumbnail(is_training=True)]
        drawing = get_drawing()
        model = get_model()

        client = W24TechreadClient.make_from_env(None)
        async with client as session:
            async for _ in session.read_drawing(drawing, asks, model):
                pass

    async def test_string_as_drawing_bytes(self) -> None:
        """Test whether submitting a string as drawing_bytes
        raises the correct exception.

        See Github Issue #13
        """
        client = W24TechreadClient.make_from_env()

        with self.assertRaises(UnsupportedMediaType):
            async with client as session:
                await session.read_drawing("", asks=[]).__anext__()

    async def test_uploading_huge_file(self) -> None:
        """Huge file produces DRAWING_FILE_SIZE_TOO_LARGE?"""
        client = W24TechreadClient.make_from_env()
        asks: List[W24Ask] = [W24AskVariantCAD(is_training=True)]

        # create a new file that is larger than the limit of 5 MB
        file_size = 10 * 1024 * 1024 + 10
        file = b"0" * file_size

        # perform the call
        async with client as session:
            async for msg in session.read_drawing(file, asks=asks):
                if msg.message_type == W24TechreadMessageType.PROGRESS:
                    continue
                self.assertEqual(
                    msg.exceptions[0].exception_type,
                    W24TechreadExceptionType.DRAWING_FILE_SIZE_TOO_LARGE,
                )
                return

    async def test_unsupported_file_format(self) -> None:
        """Unsupported file format triggers DRAWING_FILE_FORMAT_UNSUPPORTED?"""

        client = W24TechreadClient.make_from_env()
        asks: List[W24Ask] = [W24AskPageThumbnail()]

        async with client as session:
            async for message in session.read_drawing(b"", asks=asks):
                if message.message_type == W24TechreadMessageType.ASK:
                    self.assertEqual(
                        message.exceptions[0].exception_type,
                        W24TechreadExceptionType.DRAWING_FILE_FORMAT_UNSUPPORTED,
                    )

    async def test_read_with_callback(self) -> None:
        """Test whether we can read with callback"""
        client = W24TechreadClient.make_from_env()
        asks: List[W24Ask] = [W24AskPageThumbnail()]
        drawing_bytes = b""
        await client.read_drawing_with_callback(
            drawing_bytes,
            asks,
            "https://werk24.io",
            5,
        )


    async def test_read_with_callback_invalid_headers(self) -> None:
        """Test whether invalid headers raise an error."""
        client = W24TechreadClient.make_from_env()
        asks: List[W24Ask] = [W24AskPageThumbnail()]
        drawing_bytes = b""
        with self.assertRaises(ValueError):
            await client.read_drawing_with_callback(
                drawing_bytes,
                asks,
                "https://werk24.io",
                5,
                callback_headers={"Evil Header": "Bearer token"},
            )

    async def test_read_with_callback_encypted(self) -> None:
        """Test whether we can read with callback and encryption."""
        client = W24TechreadClient.make_from_env()
        asks: List[W24Ask] = [W24AskPageThumbnail()]
        drawing_bytes = b""
        passphrase = os.urandom(32)
        public_key, _ = client.generate_encryption_keys(passphrase)

        await client.read_drawing_with_callback(
            drawing_bytes,
            asks,
            "https://werk24.io",
            5,
            public_key=public_key,
        )

    async def test_read_with_callback_insufficient_credit(self) -> None:
        """Test whether invalid headers raise an error."""
        from werk24.exceptions import InsufficientCreditsException
        from werk24.techread_client import TechreadClientHttps
        
        # Using assertRaises as a context manager
        with self.assertRaises(InsufficientCreditsException):
            TechreadClientHttps._raise_for_status("", 429)