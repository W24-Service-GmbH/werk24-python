""" Integration test to verify that we can send AskTitleBlock request
and receive a response that fits the expected format
"""
from werk24.models.ask import W24AskTitleBlock
from werk24.models.title_block import W24TitleBlock
from werk24.models.techread import W24AskType, W24TechreadMessageSubtypeProgress
from werk24.techread_client import W24TechreadClient

from .base import TestBase
from .utils import get_drawing

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
            self._assert_message_is_progress_started(
                await request.__anext__())

            # check whether the second message gives us the information
            # about the requested thumbnail
            response = await request.__anext__()
            self._assert_message_is_ask_response(
                response,
                W24AskType.TITLE_BLOCK)

            # check whether we close the iteration correctly
            completed = await request.__anext__()
            self.assertEqual(completed.message_subtype, W24TechreadMessageSubtypeProgress.COMPLETED)

            # check whether the payload can be parsed correctly
            W24TitleBlock.parse_obj(response.payload_dict)
