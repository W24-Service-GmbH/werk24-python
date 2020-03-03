import base64
import json
from urllib.parse import urlparse

import aiohttp
from pydantic import HttpUrl

from .exceptions import ServerException, UnauthorizedException
from .auth_client import AuthClient


class TechreadClientHttps:

    def __init__(self, techread_server_https: str, techread_version: str):
        """ Intialize a new session with the https server

        Arguments:
            techread_server_https {str} -- Domain of the Techread https server
            techread_version {str} -- Techread Version
        """
        self._techread_server = techread_server_https
        self._techread_version = techread_version
        self._techread_session_https = None
        self._auth_client = None

    async def __aenter__(self):
        """ Create a new HTTP session that is being used for the whole
        connection. Be sure to keep the session alive.

        Returns:
            TechreadClientHttps -- TechreadClientHttps version with active session
        """
        headers = {"Authorization": f"Bearer {self._auth_client.token}"}
        self._techread_session_https = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """ Close the session
        """
        if self._techread_session_https is not None:
            await self._techread_session_https.close()

    def register_auth_client(self, auth_client: AuthClient) -> None:
        """Register the reference to the authentication service

        Arguments:
            auth_client {AuthClient} -- Reference to Authentication
                client
        """
        self._auth_client = auth_client

    async def upload_associated_file(
            self,
            request_id: str,
            file_type: str,
            content: bytes) -> None:
        """ Upload an associated file to the API.
        This can either be a technical drawing or a
        3D model. Potentially we will sometime extend
        this to also include cover pages.

        NOTE: the complete message size must not be
        larger than 10 MB

        Arguments:
            request_id {str} -- UUID4 request id that you obtained
                from the websocket

            filetype {str} -- filetype that we want to upload.
                currently supported: drawing, model

            content {bytes} -- content of the file as bytes

        Raises:
            UnauthorizedException: Raised when the token
                or the requested file have expired

            ServerException: Raised when the status code
                returned by the server is not 200
        """

        # Check if the content variable is empty.
        # If so, silently return
        if content is None:
            return

        # make the endpoint and the headers
        endpoint = self._make_endpoint_url(f"upload/{request_id}")
        try:
            await self._post(
                url=endpoint,
                data=json.dumps({file_type: base64.b64encode(content).decode()}))

        # if any exceptions occure, pass them on
        except (UnauthorizedException, ServerException) as exception:
            raise exception

    def _make_endpoint_url(self, subpath):
        """ Make the endpoint url of the subpath.
        This will create a fully valid http url
        that can be used in the post and get requests

        Arguments:
            subpath {str} -- Path of the endpoint on
                the TechreadAPI

        Returns:
            HttpUrl -- Fully qualified url including
                the server name and api version
        """
        return f"https://{self._techread_server}/{self._techread_version}/{subpath}"

    async def download_payload(self, payload_url: HttpUrl) -> bytes:
        """ Return the payload from the server

        Arguments:
            payload_url {HttpUrl} -- Url of the payload

        Raises:
            RuntimeError: Hard Error that is raised when
                the function is asked to download a payload
                from an untrusted source.
                This provides some sort of protection against
                payload-injection and token-theft. When you
                see this error showing up, you should
                definitely INVESTIGATE AND LET US KNOW
                IMMEDIATELY!!!
                Call all our numbers on a Sunday morning
                at 3am if it must be. Even if its Christmas
                and Easter on the same day.

            ServerException: Raised when the server responded
                in a way we did not anticipate (i.e., when
                the status code is anything other than 200)

        Returns:
            bytes -- Payload
        """

        # Parse the payload_url and enure that you are downloading
        # the data from the server you talked to in the first place.
        # This works as a defence mechanism against token theft.
        url_parsed = urlparse(payload_url)
        if url_parsed.netloc != self._techread_server:
            raise RuntimeError(
                f"INTRUSION!!! Payload_url '%s' not allowed. INVESTIGATE!!!",
                payload_url)

        # payload_url = payload_url.replace(
        #     "techread.w24.io/v1",
        #     "be4d09pom7.execute-api.eu-central-1.amazonaws.com")
        # print(payload_url)

        # send the get request to the endpoint
        try:
            response = await self._get(payload_url)

        # if an exception occured,
        # raise it again
        except ServerException as exception:
            raise exception

        # otherwise return the response text
        return base64.b64decode(await response.text())

    async def _get(self, url: HttpUrl):
        """ Send a GET request request and return the
        response object. The method automatically
        injects the authentication token into the
        request.

        Arguments:
            url {HttpUrl} -- URL that is to be requested

        Raises:
            UnauthorizedException: Raised when the token
                or the requested file have expired

            ServerException: Raised when the status code
                returned by the server is not 200

        Returns:
            ??? -- [description]
        """

        # send the request
        response = await self._techread_session_https.get(url)

        # check the status code of the response and
        # raise the appropriate exception
        try:
            self._check_status_code(url, response.status)
        except (UnauthorizedException, ServerException) as exception:
            raise exception

        # if the call was successful, return
        return response

    async def _post(self, url: HttpUrl, data: str):
        """ Send a POST request request and return the
        response object. The method automatically
        injects the authentication token into the
        request.

        Arguments:
            url {HttpUrl} -- URL that is to be requested

            data {str} -- Data that is sent in the request body

        Raises:
            UnauthorizedException: Raised when the token
                or the requested file have expired

            ServerException: Raised when the status code
                returned by the server is not 200

        Returns:
            ??? -- [description]
        """

        # send the request
        response = await self._techread_session_https.post(url, data=data)
        print(response)

        # check the status code of the response and
        # raise the appropriate exception
        try:
            self._check_status_code(url, response.status)
        except (UnauthorizedException, ServerException) as exception:
            raise exception

        # return the response
        return response

    @staticmethod
    def _check_status_code(url, status_code):
        # raise an unauthorized exception if the
        # status code is
        # * 401 (Unauthorized) or
        # * 403 (Forbidden)
        #
        # NOTE: a 404 does not occur, as the
        # server does not want to tell you
        # whether the file does not exist
        # or whether your token is wrong.
        # Makes brute force attacks more expensive
        if status_code in [401, 403]:
            raise UnauthorizedException()

        # If the resposne code is anything other
        # than unauthorized or 200 (OK), we trigger
        # a ServerException.
        if status_code != 200:
            raise ServerException(
                f"Get Request failed '%s' with code %s",
                url,
                status_code)
