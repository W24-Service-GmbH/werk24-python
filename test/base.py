from unittest import mock
from uuid import UUID

import aiounittest
from werk24.models.ask import W24AskPageThumbnail, W24AskTitleBlock
from werk24.models.techread import (W24AskType, W24TechreadMessage,
                                    W24TechreadMessageSubtypeProgress,
                                    W24TechreadMessageType)
from werk24.techread_client import Hook, W24TechreadClient


class TestBase(aiounittest.AsyncTestCase):

    def _assert_message_is_progress_started(
        self,
        message: W24TechreadMessage
    ) -> None:
        """ Assert that the received message indicates that
        the processing of the file has started

        Args:
            message (W24TechreadMessage): First response
                message that we obtain from the API
        """
        self.assertEqual(type(message.request_id), UUID)
        self.assertEqual(
            message.message_type,
            W24TechreadMessageType.PROGRESS)
        self.assertEqual(
            message.message_subtype,
            W24TechreadMessageSubtypeProgress.STARTED)
