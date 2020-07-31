import os
from pathlib import Path
from typing import List

import aiounittest
from dotenv import load_dotenv
from werk24.models.ask import W24Ask, W24AskPageThumbnail
from werk24.techread_client import (W24TechreadArchitecture,
                                    W24TechreadArchitectureStatus,
                                    W24TechreadClient, W24TechreadMessageType)


class TechreadIntegrationTest(aiounittest.AsyncTestCase):

    """ List of the environment variables that
    are required by the application
    """
    envs_required = [
        "W24TECHREAD_SERVER_HTTPS",
        "W24TECHREAD_SERVER_WSS",
        "W24TECHREAD_VERSION",
        "W24TECHREAD_AUTH_REGION",
        "W24TECHREAD_AUTH_IDENTITY_POOL_ID",
        "W24TECHREAD_AUTH_CLIENT_ID",
        "W24TECHREAD_AUTH_CLIENT_SECRET",
        "W24TECHREAD_AUTH_USERNAME",
        "W24TECHREAD_AUTH_PASSWORD"]

    def setUp(self) -> None:
        self._load_env()
        self.client = W24TechreadClient.make_from_env()
        assert isinstance(self.client, W24TechreadClient)

        # set the drawing path
        base_path = Path(os.path.dirname(os.path.realpath(__file__)))
        self.drawing_path = base_path / "fixtures" / "techdraw.png"

    def _load_env(self)-> None:
        """ load the environment variables and test that they
        are available
        """
        load_dotenv(".werk24")
        for cur_env in self.envs_required:
            self.assertIsNotNone(os.environ.get(cur_env))

    def _get_drawing_bytes(self)-> bytes:
        with open(self.drawing_path, "rb") as drawing_handle:
            return drawing_handle.read()

    @staticmethod
    def _make_asks_list()-> List[W24Ask]:
        return [
            W24AskPageThumbnail()
        ]

    async def test_techread(self) -> None:

        # start a session
        async with self.client as session:

            # check whether we have obtained a token
            self.assertIsNotNone(session._auth_client.token)  # noqa

            # get the architecture status
            architecture_status = await session.get_architecture_status(
                W24TechreadArchitecture.GPU_V1)

            # check whether that value is valid
            self.assertIsInstance(
                architecture_status,
                W24TechreadArchitectureStatus)

            # now get the file
            drawing_bytes = self._get_drawing_bytes()

            asks_list = self._make_asks_list()

            # and make the request
            is_first_message = True
            async for message in session.read_drawing(
                    drawing_bytes, asks_list):

                # the first message needs to be a TECHREAD_STARTED
                if is_first_message:
                    self.assertEqual(
                        message.message_type,
                        W24TechreadMessageType.PROGRESS)
                    is_first_message = False

                # if the message tells us about an error, we nee to raise it
                self.assertNotEqual(
                    message.message_type,
                    W24TechreadMessageType.ERROR)
