import os
import aiounittest
from pathlib import Path

from werk24.exceptions import LicenseError, UnauthorizedException
from werk24.techread_client import W24TechreadClient

CWD = Path(os.path.dirname(__file__))
LICENSE_PATH_INVALID_CREDS = CWD / "assets" / "invalid_creds.werk24"


class TestTechreadClient(aiounittest.AsyncTestCase):
    """ Test case for the basic Techread functionality
    """

    def test_license_missing(self):
        """ Test Missing Licence

        User Story: As API user, I want to obtain an exception
            message when the symstem did not find a license file,
            so that I can update the license_path
        """
        self.assertRaises(
            LicenseError,
            W24TechreadClient.make_from_env)

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

    # async def test_read_drawing(self):
    #     """ Test basic read_drawing functionality

    #     User Story: As API user, I want to
