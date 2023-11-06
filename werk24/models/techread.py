""" Defintions of all objects required to communicate with
the W24 Techread API.
"""
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import UUID4, BaseModel, Field, HttpUrl, Json, validator, ConfigDict

from werk24._version import __version__

from .ask import W24AskType, deserialize_ask, W24AskUnion


class W24TechreadAction(str, Enum):
    """List of supported actions by the Techread API"""

    INITIALIZE = "INITIALIZE"
    READ = "READ"


class W24TechreadCommand(BaseModel):
    """Command that is sent from the client to the Server"""

    action: W24TechreadAction
    message: Json


class W24TechreadMessageType(str, Enum):
    """Message Type of the message that is sent
    from the server to the client in response to
    a request.
    """

    ASK = "ASK"
    ERROR = "ERROR"  # !!! DEPRECATED
    PROGRESS = "PROGRESS"
    REJECTION = "REJECTION"


class W24TechreadMessageSubtypeError(str, Enum):
    """Message Subtype for the MessageType: ERROR

    !!! danger
        The SubtypeError is deprecated in favor of
        the exceptions attribute that is attached to
        the W24AskMessage.
    """

    UNSUPPORTED_DRAWING_FILE_FORMAT = "UNSUPPORTED_DRAWING_FILE_FORMAT"
    INTERNAL = "INTERNAL"
    TIMEOUT = "TIMEOUT"


class W24TechreadMessageSubtypeRejection(str, Enum):
    """Message Subtype for the MessageType: REJECTION"""

    COMPLEXITY_EXCEEDED = "COMPLEXITY_EXCEEDED"
    PAPER_SIZE_LIMIT_EXCEEDED = "PAPER_SIZE_LIMIT_EXCEEDED"


class W24TechreadMessageSubtypeProgress(str, Enum):
    """Message Subtype for the MessageType: PROGRESS"""

    INITIALIZATION_SUCCESS = "INITIALIZATION_SUCCESS"
    COMPLETED = "COMPLETED"
    STARTED = "STARTED"


W24TechreadMessageSubtypeAsk = W24AskType
""" The MessageType: ASK will return the subtypes
defined in W24AskTypes
"""

W24TechreadMessageSubtype = Union[
    W24TechreadMessageSubtypeError,
    W24TechreadMessageSubtypeProgress,
    W24TechreadMessageSubtypeAsk,
]
""" Shorthand to summorize all the supported
MessageTypes
"""


class W24TechreadExceptionType(str, Enum):
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

    DRAWING_NOISE_TOO_HIGH = "DRAWING_NOISE_TOO_HIGH"
    """ The amount of noise on the drawing was too hight for us
    to understand the drawing
    """

    DRAWING_CONTENT_NOT_UNDERSTOOD = "DRAWING_CONTENT_NOT_UNDERSTOOD"
    """ The file you submitted as drawing might not actually
    be a drawing
    """

    DRAWING_PAPER_SIZE_TOO_LARGE = "DRAWING_PAPER_SIZE_TOO_LARGE"
    """ The paper size is larger that the allowed paper size
    """

    DRAWING_MEASURE_SYSTEM_INCOMPLETE = "DRAWING_MEASURE_SYSTEM_INCOMPLETE"
    """ The file you submitted contains too few measures to be
    manufacturable
    """

    MODEL_FILE_FORMAT_UNSUPPORTED = "MODEL_FILE_FORMAT_UNSUPPORTED"
    """ The Model was submitted in a file format that is not supported
    by the API at this stage.
    """

    MODEL_FILE_SIZE_TOO_LARGE = "MODEL_FILE_SIZE_TOO_LARGE"
    """ The Model fiel size exceeded the limit
    """

    SUB_ACCOUNT_ACCESS_DENIED = "SUB_ACCOUNT_ACCESS_DENIED"
    """Raised when the sub_account does not belong to the
    main account.
    """

    SUB_ACCOUNT_NO_BALANCE = "SUB_ACCOUNT_NO_BALANCE"
    """Raised when the sub account is pre-paid and the budget
    is exhausted.
    """


class W24TechreadExceptionLevel(str, Enum):
    """Severity level for the Error

    !!! note
        This is defined for future-compatibility.
        The only value that is currently used is ERROR.
        The INFO level will follow shortly.
    """

    ERROR = "ERROR"
    """ Set when the processing was stopped
    """

    INFO = "INFO"
    """ Set when the process was completed successfully,
    but we want to bring something to your awareness
    (e.g,. that you are using a feature that will soon
    be deprecated)
    """


class W24TechreadException(BaseModel):
    """Error message that accompanies the W24TechreadMessage
    if an error occured.

    Attributes:
        exception_level: Error level indicating the severity of the error

        exception_type: Error Type that allows the API-user to translate
            the message to a user-info.
    """

    exception_level: W24TechreadExceptionLevel

    exception_type: W24TechreadExceptionType


class W24TechreadBaseResponse(BaseModel):
    """BaseFormat for messages returned by the server.

    Attributes:
        exceptions (List[W24TechreadException]): List of exceptions
            that occured during the processing.

    """

    exceptions: List[W24TechreadException] = []

    @property
    def is_successful(self) -> bool:
        """Check whether an exception of the ERROR level was returned.

        Otherwise return True.

        Returns: True if none of the attached exceptions
            has the Exception Level ERROR. False otherwise.
        """
        return not any(
            e.exception_level == W24TechreadExceptionLevel.ERROR
            for e in self.exceptions
        )


class W24TechreadMessage(W24TechreadBaseResponse):
    """Message format for messages that are sent
    from the server to the client.

    Attributes:
        request_id: unique UUID4 identifier that is generated by the
            server to identify the request

        message_type: Main Message Type (see W24TechreadMessageType)

        message_subtype: Message SubType (see W24TechreadMessageSubtype)

        page_number: Page number that the response belongs to. Starts at
            zero.

        payload_dict: Payload dictionary containing the response
            as dict. The MessageType/Subtype will tell the
            interpreter how to turn the payload back into
            the corresponding object

        payload_url: For binary data, the API will return a download
            url which carries the data. This allows us to transfer
            larger images etc.

        payload_bytes:  Binary reference of the payload. This will only
            become available after the client has downloaded the
            payload_url.


    """

    request_id: UUID4

    message_type: W24TechreadMessageType

    message_subtype: W24TechreadMessageSubtype

    page_number: int = 0

    payload_dict: Optional[Dict] = None

    payload_url: Optional[HttpUrl] = None

    payload_bytes: Optional[bytes] = None


class W24TechreadRequest(BaseModel):
    """Definition of a W24DrawingReadRequest containing
    all the asks (i.e., things you want to learn about
    the technical drawing).

    Attributes:

        asks: List of asks

        development_key: The development_key is used for internal purposes.
            It wil give you access to pre-release versions of our software.
            You will only understand the details if you...

        client_version: Current version of the client. For backward
            compatibility, this defaults to 'legacy'

        max_pages: Maximum number of pages that shall be processed.

        drawing_filename (Optional[str]): Optional filename

        sub_account (Optional[UUID4]): Sub-account that this request should
            be attributed to. Sub-accounts allow you to keep the requests
            of multiple of your customers separate.
    """

    asks: List[W24AskUnion] = []

    development_key: Optional[str] = None

    client_version: str = __version__

    max_pages: int = 1

    drawing_filename: Optional[str] = None

    sub_account: Optional[UUID4] = None

    @validator("asks", pre=True)
    def ask_list_validator(cls, raw: List[Dict[str, Any]]) -> List[W24AskUnion]:
        """Validator to de-serialize the asks. The de-serialization
        is based on the ask_type attribute of the object. Pydantic
        does not support this out-of-the box

        Args:
            raw (Dict[str, Any]): Raw json of the asks list

        Returns:
            List[W24AskUnion]: List of deserialized Asks
        """
        return [deserialize_ask(a) for a in raw]


class W24PresignedPost(BaseModel):
    """Details of the presigned post that allow you to upload
    a file to our file system.

    Attributes:
        url: Url to which the request shall be sent
        fields_: Dictionary of fields

    """

    url: HttpUrl

    fields_: Dict[str, str] = Field(alias="fields", default={})


class W24TechreadInitResponse(W24TechreadBaseResponse):
    """API response to the Initialize request

    Attributes:
        drawing_presigned_post: Presigned Post for uploading the drawing

        model_presigned_post: Presigned Post for uploading the model

        exceptions (List[W24TechreadException]): List of exceptions that
            occured

    """

    # Pydantic in Version 2.0 claims the whole `model_` variable space
    # as its own. This collides with the model variable that is already
    # in use. This configuration at least suppresses the warning.
    # See https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.protected_namespaces
    model_config = ConfigDict(protected_namespaces=())

    drawing_presigned_post: W24PresignedPost

    model_presigned_post: W24PresignedPost
