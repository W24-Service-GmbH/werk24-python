from unittest import mock

from werk24.models.ask import W24AskPageThumbnail
from werk24.models.techread import (W24AskType,
                                    W24TechreadMessageSubtypeProgress,
                                    W24TechreadMessageType)
from werk24.techread_client import Hook, W24TechreadClient

from .base import TestBase
from .utils import CWD, get_drawing

LICENSE_PATH_INVALID_CREDS = CWD / "assets" / "invalid_creds.werk24"
""" Path to the license file with invalid credentials """

DRAWING = get_drawing()
""" Example Drawing in bytes """


class TestPage(TestBase):
    async def test_read_drawing(self):
        """ Test basic read_drawing functionality

        User Story: As API user, I want to initiate a basic
        read request to verify that the basic functionality
        works
        """

        client = W24TechreadClient.make_from_env(None)
        async with client as session:
            request = session.read_drawing(DRAWING, [W24AskPageThumbnail()])

            # check whether the first message give us the state information
            message_first = await request.__anext__()
            self._assert_message_is_progress_started(message_first)

            # check whether the second message gives us the information
            # about the requested thumbnail
            message_second = await request.__anext__()
            self.assertEqual(
                message_second.message_type,
                W24TechreadMessageType.ASK)
            self.assertEqual(
                message_second.message_subtype,
                W24AskType.PAGE_THUMBNAIL)
            self.assertGreater(len(message_second.payload_bytes), 0)

            # check whether we close the iteration correctly
            completed = await request.__anext__()
            self.assertEqual(completed.message_subtype, W24TechreadMessageSubtypeProgress.COMPLETED)

    async def test_read_drawing_with_hooks(self):
        """ Test basic read drawing with hooks functionality

        User Story: As API user, I want to initiate a basic
        read request and receive the responses on the hooks
        so that I can implement asyncronous feedback loops
        with my user
        """
        callback = mock.Mock()
        hooks = [Hook(
            ask=W24AskPageThumbnail(),
            function=callback
        )]

        client = W24TechreadClient.make_from_env(None)
        async with client as session:
            await session.read_drawing_with_hooks(
                DRAWING,
                hooks=hooks)

        self.assertTrue(callback.called)
