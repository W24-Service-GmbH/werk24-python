
from werk24.models.ask import W24AskPageThumbnail, W24AskTitleBlock
from werk24.models.techread import (W24AskType, W24TechreadMessage,
                                    W24TechreadMessageSubtypeProgress,
                                    W24TechreadMessageType)
from werk24.techread_client import Hook, W24TechreadClient

from .utils import CWD, get_drawing
from .base import TestBase

DRAWING_BYTES = get_drawing()
""" Example Drawing in bytes """


class TestTitleBlock(TestBase):

    async def test_read_title_block(self):
        """ Is TitleBlock read correctly?

        User Story: As API user, I want to obtain the
        title block information from the Technical Drawing
        that I am submitting.
        """
        asks = [W24AskTitleBlock()]

        client = W24TechreadClient.make_from_env(None)
        async with client as session:
            request = session.read_drawing(DRAWING_BYTES, asks)

            # check whether the first message give us the state information
            message_first = await request.__anext__()
            self._assert_message_is_progress_started(message_first)
            print(message_first)

            # check whether the second message gives us the information
            # about the requested thumbnail
            message_second = await request.__anext__()
            print(message_second)
            self.assertEqual(
                message_second.message_type,
                W24TechreadMessageType.ASK)
            self.assertEqual(
                message_second.message_subtype,
                W24AskType.PAGE_THUMBNAIL)
            self.assertGreater(len(message_second.payload_bytes), 0)

            # check whether we close the iteration correctly
            with self.assertRaises(StopAsyncIteration):
                await request.__anext__()
