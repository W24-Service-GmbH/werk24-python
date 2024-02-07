""" HTTPS-part of the Werk24 client
"""

import uuid
from werk24.exceptions import SSLCertificateError
import json
import urllib.parse
from pydantic import UUID4
from werk24.models.ask import W24AskUnion
from typing import List
from types import TracebackType
from typing import Dict, Optional, Type
from io import BufferedReader
import aiohttp
from pydantic import HttpUrl
from typing import Union
from werk24.auth_client import AuthClient
from werk24.exceptions import (
    BadRequestException,
    RequestTooLargeException,
    ResourceNotFoundException,
    ServerException,
    UnauthorizedException,
    UnsupportedMediaType,
)
from werk24.models.helpdesk import W24HelpdeskTask
from werk24.models.techread import W24PresignedPost


EXCEPTION_CLASSES = {
    range(200, 300): None,
    range(400, 401): BadRequestException,
    range(401, 403): UnauthorizedException,
    range(404, 405): ResourceNotFoundException,
    range(413, 414): RequestTooLargeException,
    range(415, 416): UnsupportedMediaType,
    range(300, 400): ServerException,
    range(500, 600): ServerException,
    range(416, 500): ServerException,
}


class TechreadClientHttps:
    """Translation map from the server response
    to the W24TechreadArchitectureStatus enum
    """

    def __init__(self, techread_version: str, support_base_url: str):
        """
        Initialize a new session with the https server.

        Arguments:
            techread_server_https {str} -- Domain of the Techread https server
            techread_version {str} -- Techread Version
            support_base_url {str} -- Base URL for support requests
        """
        self._techread_version = techread_version
        self._techread_session_https: Optional[aiohttp.ClientSession] = None
        self._auth_client: Optional[AuthClient] = None
        self.support_base_url = support_base_url

    async def __aenter__(self) -> "TechreadClientHttps":
        """
        Create a new HTTP session that is being used for the whole connection.
        Be sure to keep the session alive.

        Raises:
        ------
        RuntimeError: Exception raised when the developer tries to start the
            session without a token.

        Returns:
        -------
        TechreadClientHttps: Instance of the class itself with active session.
        """
        if self._auth_client is None:
            raise RuntimeError("No AuthClient was registered")

        self._techread_session_https = aiohttp.ClientSession()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """
        Close the session.

        Args:
        ----
        exc_type (Optional[Type[BaseException]]): The type of exception that
            caused the context manager to be exited.
        exc_value (Optional[BaseException]): The instance of the exception that
            caused the exit.
        traceback (Optional[TracebackType]): A traceback from the exception.

        Returns:
        --------
        None
        """
        if self._techread_session_https:
            await self._techread_session_https.close()
            self._techread_session_https = None

    def register_auth_client(self, auth_client: AuthClient) -> None:
        """Register the reference to the authentication service

        Arguments:
            auth_client {AuthClient} -- Reference to Authentication
                client
        """
        self._auth_client = auth_client

    async def upload_associated_file(
        self,
        presigned_post: W24PresignedPost,
        content: Optional[Union[bytes, BufferedReader]],
    ) -> None:
        """
        Uploads an associated file to the API.

        This can either be a technical drawing or a 3D model.
        NOTE: The complete message size must not be larger than 10 MB.

        Args:
        ----
        presigned_post (W24PresignedPost): Presigned post object for
            file upload.
        content (Optional[bytes]): Content of the file as bytes.

        Raises:
        -------
        Various exceptions based on the issues with API, authentication
            or the requested file.

        Returns:
        --------
        None
        """
        # ignore if payload is empty
        if content is None:
            return

        # generate the form data by merging the presigned
        # fields with the file
        form = aiohttp.FormData()
        for key, value in presigned_post.fields_.items():
            form.add_field(key, value)
        form.add_field("file", content)

        # create a new fresh session that does not
        # carry the authentication token
        presigned_post_str = str(presigned_post.url)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(presigned_post_str, data=form) as response:
                    self._raise_for_status(presigned_post_str, response.status)

        # Raise SSLCertificateError if the certificate is not trusted
        except aiohttp.ClientConnectorCertificateError as exception:
            raise SSLCertificateError() from exception

    async def download_payload(self, payload_url: HttpUrl) -> bytes:
        """Return the payload from the server

        Args:
        ----
        payload_url {HttpUrl} -- Url of the payload

        Raises:
        ------
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
        -------
        bytes -- Payload
        """
        # send the get request to the endpoint
        try:
            response = await self._get(payload_url)

        # reraise the exceptions
        except (
            UnauthorizedException,  # pylint: disable=try-except-raise
            RequestTooLargeException,
            ServerException,
            BadRequestException,
            ResourceNotFoundException,
        ):
            raise

        # otherwise return the response text
        return await response.content.read()

    async def _get(self, url: str) -> aiohttp.ClientResponse:
        """Send a GET request request and return the
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
            raise RuntimeError("You executed a command without opening a session")

        # send the request
        response = await self._techread_session_https.get(str(url))

        # check the status code of the response and
        # raise the appropriate exception
        try:
            self._raise_for_status(url, response.status)
        except (UnauthorizedException, ServerException) as exception:
            raise exception

        # if the call was successful, return
        return response

    @staticmethod
    def _raise_for_status(url: str, status_code: int) -> None:
        """Raise the correct exception depending on the status code.

        Args:
        ----
        url (str): The requested URL
        status_code (int): The received response status code

        Raises:
        ------
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
        for key, exception_class in EXCEPTION_CLASSES.items():
            if status_code in key:
                if exception_class is not None:
                    raise exception_class(
                        f"Request failed '{url}' with code {status_code}"
                    )
                return None

        # If the resposne code is anything other than unauthorized or 200 (OK), we trigger a ServerException.
        raise ServerException(f"Request failed '{url}' with code {status_code}")

    async def create_helpdesk_task(self, task: W24HelpdeskTask) -> W24HelpdeskTask:
        """
        Create a Helpdesk ticket.

        Args:
        ----
        task (W24HelpdeskTask): Helpdesk task to be created

        Raises:
        ------
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
        -------
        W24HelpdeskTask: Created helpdesk task with an updated task_id.
        """
        headers = self._make_helpdesk_headers()
        url = self._make_support_url("helpdesk/create-task")
        async with aiohttp.ClientSession(headers=headers) as session:
            response = await session.post(url, json=task.json())
            self._raise_for_status(url, response.status)

        # return the updated task
        return W24HelpdeskTask.parse_raw(await response.text())

    def _make_support_url(self, path: str) -> str:
        """Make the support url for the help desk requests.

        Args:
        ----
        path (str): Path to the endpoint

        Returns:
        -------
        str: URL to the endpoint
        """
        return urllib.parse.urljoin(f"https://{self.support_base_url}", path)

    def _make_helpdesk_headers(self) -> Dict[str, str]:
        """
        Make the headers for the help desk requests.

        Simply the authorization header at this stage.

        Returns:
        -------
        Dict[str, str]: Help desk headers
        """
        return self._auth_client.get_headers()

    async def read_drawing_with_callback(
        self,
        drawing: Union[BufferedReader, bytes],
        asks: List[W24AskUnion],
        callback_url: str,
        max_pages: int = 5,
        drawing_filename: Optional[str] = None,
    ) -> UUID4:
        """
        Read a drawing with a callback.

        Args:
        ----
        drawing (Union[BufferedReader, bytes]): Drawing to be read
        asks (List[W24Ask]): List of asks
        callback_url (str): Callback URL
        max_pages (int, optional): Maximum number of pages to be read.
            Defaults to 5.
        drawing_filename (Optional[str], optional): Filename of the drawing.
            Defaults to None.

        Raises:
        ------
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
        -------
        UUID4: Request ID
        """

        # Set a default drawing filename if none is provided
        drawing_filename = drawing_filename or "drawing.pdf"

        # create the form data
        data = aiohttp.FormData()
        data.add_field("drawing", drawing, filename=drawing_filename)
        data.add_field(
            "asks",
            json.dumps([ask.model_dump(mode="json") for ask in asks]),
        )
        data.add_field("callback_url", callback_url)
        data.add_field("max_pages", str(max_pages))
        data.add_field("client_version", self._techread_version)
        data.add_field("drawing_filename", drawing_filename)

        # send the request
        headers = self._auth_client.get_auth_headers()
        url = self._make_support_url("techread/read-with-callback")
        async with aiohttp.ClientSession(headers=headers) as session:
            response = await session.post(url, data=data)
            response_json = await response.json(content_type=None)
            self._raise_for_status(url, response.status)

        try:
            return uuid.UUID(response_json["request_id"])
        except (ValueError, KeyError):
            raise BadRequestException(f"Request failed: {response_json}")
