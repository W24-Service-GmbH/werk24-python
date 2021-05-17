from werk24.models.techread import (W24AskType, W24TechreadMessage,
                                    W24TechreadMessageSubtype,
                                    W24TechreadMessageSubtypeProgress,
                                    W24TechreadMessageType)
from uuid import UUID
from test.utils import AsyncTestCase


class TestBase(AsyncTestCase):

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
        self._check_request_id(message)
        self._check_message_type(
            message,
            W24TechreadMessageType.PROGRESS,
            W24TechreadMessageSubtypeProgress.STARTED)

    def _assert_message_is_ask_response(
        self,
        message: W24TechreadMessage,
        ask_type: W24AskType,
    ) -> None:
        """ Assert that the received message is a response
        to the Ask request of type `ask_type`

        Args:
            message (W24TechreadMessage): Message to check
            ask_type (W24AskType): Ask type to check for
        """
        self._check_request_id(message)
        self._check_message_type(
            message,
            W24TechreadMessageType.ASK,
            ask_type)

    def _check_request_id(
        self,
        message: W24TechreadMessage
    ) -> None:
        """ Check whether the request id of the response
        is correct

        Args:
            message (W24TechreadMessage): Message to test
        """
        self.assertEqual(type(message.request_id), UUID)

    def _check_message_type(
        self,
        message: W24TechreadMessage,
        message_type: W24TechreadMessageType,
        message_subtype: W24TechreadMessageSubtype
    ) -> None:
        """ Check whether the message type is correct

        Args:
            message (W24TechreadMessage): Message to test
            message_type (W24TechreadMessageType): desired
                request type
        """
        self.assertEqual(message.message_type, message_type)
        self.assertEqual(message.message_subtype, message_subtype)
