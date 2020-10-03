from unittest import mock

import aioboto3
import aiounittest
from botocore.exceptions import ClientError
from werk24._version import __version__
from werk24.exceptions import LicenseError, UnauthorizedException
from werk24.models.techread import W24TechreadRequest
from werk24.techread_client import W24TechreadClient

from .utils import CWD

LICENSE_PATH_INVALID_CREDS = CWD / "assets" / "invalid_creds.werk24"
""" Path to the license file with invalid credentials """


class TestTechreadClient(aiounittest.AsyncTestCase):
    """ Test case for the basic Techread functionality
    """

    def test_license_path_invalid(self):
        """ Test Invalid License Path

        User Story: As API user, I want to obtain an exception
            if the path that I provided to the license file is
            invalid, so that I can detect problems before they
            go into production.
        """
        self.assertRaises(
            LicenseError,
            W24TechreadClient.make_from_env,
            license_path="invalid_path")

    async def test_license_invalid(self):
        """ Test Invalid License File

        User Story: As API user, I want to obtain an exception
            when the license that I supplied is invalid, so that
            I know that the license expired / was disabled / ...
        """
        client = W24TechreadClient.make_from_env(
            license_path=LICENSE_PATH_INVALID_CREDS)

        with self.assertRaises(UnauthorizedException):
            async with client:
                pass

    async def test_cognito_error(self):
        """ Test UnauthorizedException if Cognito Identity is unavailable

        User Story: As API user, I want to obtain an exception
            when the Cognito service is down, so that I can
            retry.
        """
        # start the client
        client = W24TechreadClient.make_from_env(None)

        # mock the boto3 client to raise a ClientError
        aiboto3_client = aioboto3.client
        m = mock.Mock()
        m.side_effect = ClientError({}, {})
        mock.patch('aioboto3.client', m).start()

        # assert
        with self.assertRaises(UnauthorizedException):
            async with client:
                pass

        # restore
        aioboto3.client = aiboto3_client

    async def test_client_version(self) -> None:
        """ Test whether Client sends version

        User Story: As Werk24 API developer I want to
        know which client versionns are still being used,
        so that I can decide whether it is safe to deprecate
        an old feature

        Github Issue #1
        """
        request = W24TechreadRequest(asks=[])
        self.assertEqual(__version__, request.client_version)
