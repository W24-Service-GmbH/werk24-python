from contextlib import suppress
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from pydantic import (
    UUID4,
    BaseModel,
    Field,
    HttpUrl,
    Json,
    ValidationError,
    ValidationInfo,
    field_validator,
)

from werk24 import __version__
from werk24.models.v1.ask import (
    W24AskResponse,
    W24AskType,
    deserialize_ask_response,
)
from werk24.models.v2.asks import AskType, AskUnion
from werk24.models.v2.enums import TechreadExceptionLevel
from werk24.models.v2.responses import RESPONSE_SUBCLASSES, ResponseUnion


class TechreadMessageType(str, Enum):
    """Message Type of the message that is sent
    from the server to the client in response to
    a request.
    """

    ASK = "ASK"
    PROGRESS = "PROGRESS"
    ERROR = "ERROR"


class TechreadMessageSubtype(str, Enum):
    """Message Subtype for the MessageType: PROGRESS"""

    PROGRESS_COMPLETED = "COMPLETED"
    PROGRESS_INITIALIZATION_SUCCESS = "INITIALIZATION_SUCCESS"
    PROGRESS_STARTED = "STARTED"
    ERROR_INTERNAL = "INTERNAL"


class TechreadRequest(BaseModel):
    asks: List[AskUnion] = Field(..., description="List of asks")
    client_version: str = Field(default=__version__, description="Client version")
    max_pages: int = Field(..., ge=1, description="Maximum number of pages to process")


class TechreadAction(str, Enum):
    """List of supported actions by the Techread API"""

    INITIALIZE = "INITIALIZE"
    READ = "READ"


class Hook(BaseModel):
    """
    A Utility class to register callback requests for a specific message_type or W24Ask.

    The 'Hook' object is used for handling and maintaining callback requests. Registering
    an 'ask' should include a complete W24Ask definition, not just the ask type.

    Attributes:
    ----------
    message_type (Optional[W24TechreadMessageType]): Specifies the type of the message.
    message_subtype (Optional[W24TechreadMessageSubtype]): Specifies the subtype of the message.
    ask (Optional[W24Ask]): The complete definition of W24Ask, if any.
    function (Callable): The callback function to be invoked when the resulting information
        is available.

    Note:
    ----
    Either a message_type or an ask must be registered. Be careful when registering an ask;
    a complete W24Ask definition is required, not just the ask type.
    """

    message_type: Optional[TechreadMessageType] = None
    message_subtype: Optional[TechreadMessageSubtype] = None
    ask: Optional[AskUnion] = None
    function: Callable


class EncryptionKeys(BaseModel):
    """
    A class to hold the encryption keys for the client.

    Attributes:
    ----------
    public_key_pem (str): The public key in PEM format.
    private_key_pem (str): The private key in PEM format.
    """

    client_public_key_pem: bytes
    client_private_key_pem: bytes
    client_private_key_passphrase: Optional[bytes] = None


class TechreadExceptionType(str, Enum):
    """List of all the error types that can possibly
    be associated to the error type.
    """

    DRAWING_FILE_FORMAT_UNSUPPORTED = "DRAWING_FILE_FORMAT_UNSUPPORTED"
    """ The Drawing was submitted in a file format that is not supproted
    by the API at this stage.
    """

    DRAWING_FILE_SIZE_TOO_LARGE = "DRAWING_FILE_SIZE_TOO_LARGE"
    """ The Drawing file size exceeded the limit
    """

    DRAWING_RESOLUTION_TOO_LOW = "DRAWING_RESOLUTION_TOO_LOW"
    """ The resolution (dots per inch) was too low to be
    processed
    """

    DRAWING_CONTENT_NOT_UNDERSTOOD = "DRAWING_CONTENT_NOT_UNDERSTOOD"
    """ The file you submitted as drawing might not actually
    be a drawing
    """

    DRAWING_PAPER_SIZE_TOO_LARGE = "DRAWING_PAPER_SIZE_TOO_LARGE"
    """ The paper size is larger that the allowed paper size
    """


class TechreadException(BaseModel):
    """
    Error message that accompanies the W24TechreadMessage
    if an error occured.

    Attributes:
    ----------
    - exception_type (TechreadExceptionType): Error Type that allows the
        API-user to translate the message to a user-info.
    """

    exception_level: TechreadExceptionLevel
    exception_type: TechreadExceptionType


class TechreadBaseResponse(BaseModel):
    """
    BaseFormat for messages returned by the server.

    Attributes:
    ----------
    - exceptions (List[W24TechreadException]): List of exceptions
      that occured during the processing.
    """

    exceptions: List[TechreadException] = []

    @property
    def is_successful(self) -> bool:
        """Check whether an exception of the ERROR level was returned.

        Otherwise return True.

        Returns:
        -------
        - True if no exceptions occured,False otherwise.
        """
        return not self.exceptions


class PresignedPost(BaseModel):
    """
    Represents the details of a presigned POST request for uploading a file
    to the Werk24 file system.

    Attributes:
    ----------
    - url (HttpUrl): The URL where the POST request should be sent.
    - fields (Dict[str, str]): A dictionary of form fields to include in the POST request.
    """

    url: HttpUrl
    fields: Dict[str, str] = Field(alias="fields", default={})


class TechreadInitResponse(TechreadBaseResponse):
    """API response to the Initialize request

    Attributes:
    ----------
    - drawing_presigned_post: Presigned Post for uploading the drawing
    - model_presigned_post: Presigned Post for uploading the model
    - exceptions (List[W24TechreadException]): List of exceptions that occured
    """

    drawing_presigned_post: PresignedPost
    model_presigned_post: Optional[PresignedPost] = None
    public_key: Optional[str] = None


class TechreadMessage(TechreadBaseResponse):
    """
    Represents a message sent from the server to the client.

    This class encapsulates the structure of a message that the server sends to
    the client, providing metadata and payload for processing.

    Attributes:
    ----------
    - request_id (UUID4): Unique identifier (UUID4) for the request, generated by
      the server.
    - message_type (TechreadMessageType): The main message type indicating the
      category of the message.
    - message_subtype (TechreadMessageSubtype): The subtype specifying additional
      details about the message.
    - page_number (int): The page number the message corresponds to (starting from 0).
    - payload_dict (Optional[AskResponse]): A dictionary containing the structured payload data.
    - payload_url (Optional[HttpUrl]): A URL for downloading binary data
      (e.g., images or large files).
    - payload_bytes (Optional[bytes]): Binary content downloaded from the `payload_url`.
      This wil initially be None, and will be populated when the client downloads the
      content from the `payload_url`. If you implement your own client, you need to
      download the content from the `payload_url` and set the `payload_bytes` attribute.
    """

    request_id: UUID4
    message_type: TechreadMessageType
    message_subtype: Union[TechreadMessageSubtype, AskType, W24AskType]
    page_number: int = 0
    payload_dict: Union[
        ResponseUnion, TechreadInitResponse, W24AskResponse, dict, None
    ] = None
    payload_url: Optional[HttpUrl] = None
    payload_bytes: Optional[bytes] = None

    @field_validator("payload_dict", mode="plain")
    @classmethod
    def deserialize_payload(
        cls,
        v: Any,
        info: ValidationInfo,
    ) -> Union[ResponseUnion, TechreadInitResponse, W24AskResponse, dict, None]:

        # If we have a None value, return None
        if v is None:
            return None

        # If it is already deserialized, return it
        if isinstance(v, (ResponseUnion, TechreadInitResponse, W24AskResponse)):
            return v

        # Special Case for TechreadInitResponse
        if (
            info.data["message_subtype"]
            == TechreadMessageSubtype.PROGRESS_INITIALIZATION_SUCCESS
        ):
            return TechreadInitResponse.model_validate(v)

        # Deserialize V2 responses
        if v.get("ask_version") == "v2":
            for c_class in RESPONSE_SUBCLASSES:
                with suppress(ValidationError):
                    return c_class.model_validate(v)

        # Desirialize V1 responses
        try:
            return deserialize_ask_response(v, info)

        # Fallback to pure dictionary
        except ValidationError:
            return v


class TechreadWithCallbackPayload(BaseModel):
    """
    Payload sent to the API to trigger a drawing read process with a callback URL.

    This class encapsulates the details required for initiating a drawing read request
    and registering a callback URL to receive the results.

    Attributes:
    ----------
    - asks (List[W24AskUnion]): List of asks specifying the required information.
    - callback_url (HttpUrl): The URL to call once processing is completed.
    - callback_headers (Optional[Dict[str, str]]): Headers to include with the callback
      request.
    - max_pages (int): Maximum number of pages to process. Defaults to 5.
    - client_version (str): The version of the client making the request.
    - public_key (Optional[str]): Public key for encrypting the callback payload,
      if applicable.
    """

    asks: List[AskUnion] = Field(
        default_factory=list,
        description="List of asks specifying the desired information to extract from the drawing.",
    )

    callback_url: HttpUrl = Field(
        ...,
        description="The URL to which the API will send the callback request after processing is completed.",
    )

    callback_headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional headers to include in the callback request. Headers must start with 'X-' or be whitelisted.",
    )

    max_pages: int = Field(
        ...,
        ge=1,
        description="Maximum number of pages to process. Must be at least 1.",
    )

    client_version: str = Field(
        default=__version__, description="Version of the client making the request."
    )
    public_key: Optional[str] = Field(
        default=None,
        description="Optional public key for encrypting the callback payload. Feature availability depends on the service level.",
    )

    @field_validator("callback_headers", mode="before")
    @classmethod
    def validate_callback_headers(
        cls,
        headers: Optional[Dict[str, str]],
        max_name_length: int = 128,
        max_value_length: int = 4096,
    ) -> Optional[Dict[str, str]]:
        """
        Validate the callback headers to ensure compliance with server-side constraints.

        Headers must:
        - Be either whitelisted (`authorization`) or prefixed with "X-".
        - Not exceed the maximum length for names and values.

        Args:
        ----
        - headers (Optional[Dict[str, str]]): The callback headers to validate.
        - max_name_length (int): Maximum allowed length for header names.
        - max_value_length (int): Maximum allowed length for header values.

        Returns:
        -------
        - Optional[Dict[str, str]]: The validated callback headers.

        Raises:
        ------
        - ValueError: If any header name or value violates the constraints.
        """
        ALLOWED_CALLBACK_HEADERS = {"authorization"}

        if headers is None:
            return None

        for name, value in headers.items():
            # Validate header name
            if (
                name.lower() not in ALLOWED_CALLBACK_HEADERS
                and not name.lower().startswith("x-")
            ):
                raise ValueError(
                    f'Invalid header "{name}": must start with "X-" or be one of {ALLOWED_CALLBACK_HEADERS}.'
                )

            if len(name) > max_name_length:
                raise ValueError(
                    f'Header name "{name}" exceeds maximum length of {max_name_length} characters.'
                )

            # Validate header value
            if len(value) > max_value_length:
                raise ValueError(
                    f'Header value for "{name}" exceeds maximum length of {max_value_length} characters.'
                )

        return headers


class TechreadCommand(BaseModel):
    """Command that is sent from the client to the Server"""

    action: TechreadAction
    message: Json
