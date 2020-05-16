""" HTTPS-part of the Werk24 client
"""
import base64
import json
from typing import Optional, Type
from types import TracebackType
from urllib.parse import urlparse

import aiohttp
from pydantic import HttpUrl, UUID4
from werk24.exceptions import (BadRequestException, RequestTooLargeException,
                               ResourceNotFoundException, ServerException,
                               UnauthorizedException,
                               UnsupportedMediaTypeException)

from .auth_client import AuthClient


class TechreadClientHttps:

    """ Translation map from the server response
    to the W24TechreadArchitectureStatus enum
    """

    MAX_REQUEST_PAYLOAD = 6 * 1024 * 1024  # 6MB

    def __init__(self, techread_server_https: str, techread_version: str):
        """ Intialize a new session with the https server

        Arguments:
            techread_server_https {str} -- Domain of the Techread https server
            techread_version {str} -- Techread Version
        """
        self._techread_server = techread_server_https
        self._techread_version = techread_version
        self._techread_session_https: Optional[aiohttp.ClientSession] = None
        self._auth_client: Optional[AuthClient] = None

    async def __aenter__(
            self
    ) -> 'TechreadClientHttps':
        """ Create a new HTTP session that is being used for the whole
        connection. Be sure to keep the session alive.

        Raises:
            RuntimeError  -- Raise when the developer enters the session
                without having called register_auth_client()

        Returns:
            TechreadClientHttps -- TechreadClientHttps version with active
                session
        """

        # make sure that we have an AuthClient
        if self._auth_client is None:
            raise RuntimeError(
                "You need to call register_auth_client() before you can start"
                + " the session")

        headers = {"Authorization": f"Bearer {self._auth_client.token}"}
        self._techread_session_https = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType]
    ) -> None:

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
            request_id: UUID4,
            file_type: str,
            content: Optional[bytes]) -> None:
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

            BadRequestException: Raised when the request body
                cannot be interpreted. This normally indicates
                that the API version has been updated and that
                we missed a corner case. If you encounter this
                exception, it is very likely our mistake. Please
                get in touch!

            UnauthorizedException: Raised when the token
                or the requested file have expired

            ResourceNotFoundException: Raised when you are requesting
                an endpoint that does not exist. Again, you should
                not encounter this, but if you do, let us know.

            RequestTooLargeException: Raised when the status
                code was 413

            UnsupportedMediaTypException: Raised when the file you
                submitted cannot be read (because its media type
                is not supported by the API).

            ServerException: Raised for all other status codes
                that are not 2xx

        """

        # Check if the content variable is empty.
        # If so, silently return
        if content is None:
            return

        # make the data
        data = json.dumps({
            file_type: base64.b64encode(content).decode()
        })

        # check whether the payload is too large
        if len(data) > self.MAX_REQUEST_PAYLOAD:
            raise RequestTooLargeException()

        # make the endpoint and the headers
        endpoint = self._make_endpoint_url(f"upload/{request_id}")
        try:
            await self._post(
                url=endpoint,
                data=data
            )

        # reraise the exception if we are unauhtorizer
        except (UnauthorizedException,  # pylint: disable=try-except-raise
                RequestTooLargeException,
                ServerException, BadRequestException,
                ResourceNotFoundException):
            raise  # noqa

    def _make_endpoint_url(
            self,
            subpath: str
    ) -> str:
        """ Make the endpoint url of the subpath.
        This will create a fully valid http url
        that can be used in the post and get requests

        Arguments:
            subpath {str} -- Path of the endpoint on
                the TechreadAPI

        Returns:
            str -- Fully qualified url including
                the server name and api version
        """
        return "https://{}/{}/{}".format(
            self._techread_server,
            self._techread_version,
            subpath)

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

            BadRequestException: Raised when the request body
                cannot be interpreted. This normally indicates
                that the API version has been updated and that
                we missed a corner case. If you encounter this
                exception, it is very likely our mistake. Please
                get in touch!

            UnauthorizedException: Raised when the token
                or the requested file have expired

            ResourceNotFoundException: Raised when you are requesting
                an endpoint that does not exist. Again, you should
                not encounter this, but if you do, let us know.

            RequestTooLargeException: Raised when the status
                code was 413

            UnsupportedMediaTypException: Raised when the file you
                submitted cannot be read (because its media type
                is not supported by the API).

            ServerException: Raised for all other status codes
                that are not 2xx
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

        # send the get request to the endpoint
        try:
            response = await self._get(payload_url)

        # reraise the exceptions
        except (UnauthorizedException,  # pylint: disable=try-except-raise
                RequestTooLargeException,
                ServerException, BadRequestException,
                ResourceNotFoundException):
            raise

        # otherwise return the response text
        return base64.b64decode(await response.text())

    async def _get(
            self,
            url: str
    ) -> aiohttp.ClientResponse:
        """ Send a GET request request and return the
        response object. The method automatically
        injects the authentication token into the
        request.

        Arguments:
            url {str} -- URL that is to be requested

        Raises:
            BadRequestException: Raised when the request body
                cannot be interpreted. This normally indicates
                that the API version has been updated and that
                we missed a corner case. If you encounter this
                exception, it is very likely our mistake. Please
                get in touch!

            UnauthorizedException: Raised when the token
                or the requested file have expired

            ResourceNotFoundException: Raised when you are requesting
                an endpoint that does not exist. Again, you should
                not encounter this, but if you do, let us know.

            RequestTooLargeException: Raised when the status
                code was 413

            UnsupportedMediaTypException: Raised when the file you
                submitted cannot be read (because its media type
                is not supported by the API).

            ServerException: Raised for all other status codes
                that are not 2xx

        Returns:
            aiohttp.ClientResponse -- Client response for the get request
        """

        # ensure that the session was started
        if self._techread_session_https is None:
            raise RuntimeError(
                "You executed a command without opening a session")

        # send the request
        response = await self._techread_session_https.get(url)

        # check the status code of the response and
        # raise the appropriate exception
        try:
            self._raise_for_status(url, response.status)
        except (UnauthorizedException, ServerException) as exception:
            raise exception

        # if the call was successful, return
        return response

    async def _post(
            self,
            url: str,
            data: str
    ) -> aiohttp.ClientResponse:
        """ Send a POST request request and return the
        response object. The method automatically
        injects the authentication token into the
        request.

        Arguments:
            url {str} - - URL that is to be requested

            data {str} - - Data that is sent in the request body

        Raises:
            BadRequestException: Raised when the request body
                cannot be interpreted. This normally indicates
                that the API version has been updated and that
                we missed a corner case. If you encounter this
                exception, it is very likely our mistake. Please
                get in touch!

            UnauthorizedException: Raised when the token
                or the requested file have expired

            ResourceNotFoundException: Raised when you are requesting
                an endpoint that does not exist. Again, you should
                not encounter this, but if you do, let us know.

            RequestTooLargeException: Raised when the status
                code was 413

            UnsupportedMediaTypException: Raised when the file you
                submitted cannot be read(because its media type
                is not supported by the API).

            ServerException: Raised for all other status codes
                that are not 2xx

        Returns:
            aiohttp.ClientResponse - - Client response for the post request
        """

        # ensure that the session was started
        if self._techread_session_https is None:
            raise RuntimeError(
                "You executed a command without opening a session")

        # send the request
        response = await self._techread_session_https.post(url, data=data)

        # check the status code of the response and
        # raise the appropriate exception
        self._raise_for_status(url, response.status)

        # return the response
        return response

    @staticmethod
    def _raise_for_status(
            url: str,
            status_code: int
    ) -> None:
        """ Raise the correct exception depending on the
        status code

        Arguments:
            url {str} - - requested url
            status_code {int} - - response status code

        Raises:
            BadRequestException: Raised when the request body
                cannot be interpreted. This normally indicates
                that the API version has been updated and that
                we missed a corner case. If you encounter this
                exception, it is very likely our mistake. Please
                get in touch!

            UnauthorizedException: Raised when the token
                or the requested file have expired

            ResourceNotFoundException: Raised when you are requesting
                an endpoint that does not exist. Again, you should
                not encounter this, but if you do, let us know.

            RequestTooLargeException: Raised when the status
                code was 413

            UnsupportedMediaTypException: Raised when the file you
                submitted cannot be read(because its media type
                is not supported by the API).

            ServerException: Raised for all other status codes
                that are not 2xx

        """

        # raise a bad request exception if the status
        # code 400 was returned. This normally indicates
        # that the API has been updated and the integration
        # tests have missed a case
        if status_code == 400:
            raise BadRequestException()

        # raise an unauthorized exception if the
        # status code is
        # * 401 (Unauthorized) or
        # * 403 (Forbidden)
        if status_code in [401, 403]:
            raise UnauthorizedException()

        # NOTE: a 404 does not occur, as the
        # server does not want to tell you
        # whether the file does not exist
        # or whether your token is wrong.
        # Makes brute force attacks more expensive.
        # We deal with it anyway so we can change
        # in the future
        if status_code == 404:
            raise ResourceNotFoundException()

        # if the status code is 413, you have submitted
        # a file that is too large.
        if status_code == 413:
            raise RequestTooLargeException()

        # if the status code is 415, you have submitted
        # a file whose media type is not supported by the API
        if status_code == 415:
            raise UnsupportedMediaTypeException()

        # If the resposne code is anything other
        # than unauthorized or 200 (OK), we trigger
        # a ServerException.
        if not 200 <= status_code <= 299:
            raise ServerException(
                f"Request failed '%s' with code %s", url, status_code)
