from typing import Optional, Sequence

# The console page where API keys are listed, created and deleted, kept
# importable from here. It comes from werk24.utils.urls, which imports
# nothing: the settings module would load pydantic_settings and dotenv into
# every import of werk24, including those that only use the models.
from werk24.utils.urls import API_KEYS_URL as API_KEYS_URL

#: The documentation page on how large a drawing can be.
FILE_SIZE_DOCS_URL = "https://v2.docs.werk24.io/limitations/file-size/"


class TechreadException(Exception):
    """
    Base exception for all exceptions raised by the Techread functionality.
    Provides default CLI message headers and bodies for consistent error reporting.
    """

    cli_message_header: str = "Techread Error"
    cli_message_body: str = "An error occurred while processing your request."

    def __init__(self, details: str = ""):
        """
        Initialize the exception with optional details for the CLI message.

        Args:
            details (str): Additional details to append to the default message.
        """
        if details:
            self.cli_message_body = f"{self.cli_message_body}\n\nDetails: {details}"
        super().__init__(self.cli_message_body)


class BadRequestException(TechreadException):
    """Exception raised when the request body cannot be interpreted by the server."""

    cli_message_header: str = "Bad Request"
    cli_message_body: str = (
        "The server could not interpret the request.\n\n"
        "This may indicate a problem with the request format or a server update that requires changes in the client. "
        "Please report this issue if it persists."
    )


class ResourceNotFoundException(TechreadException):
    """Exception raised when a requested resource cannot be found."""

    cli_message_header: str = "Resource Not Found"
    cli_message_body: str = "The requested resource was not found on the server."


class UnauthorizedException(TechreadException):
    """Exception raised when an action is forbidden or unauthorized."""

    cli_message_header: str = "Unauthorized"
    cli_message_body: str = (
        "You are not authorized to perform this action. Please check your credentials."
    )


class ApiKeyRejectedException(UnauthorizedException):
    """Raised when the Werk24 API refuses the API key the client sent.

    The server gives the same answer for a mistyped key, a deleted or revoked
    key, and a key whose account is closed or suspended, and does not say
    which. The message therefore names the key by its last four characters
    (the same ones the console shows), says where the client read it from,
    and points to the console page where keys are managed. The full key is
    never part of the message.

    A subclass of :class:`UnauthorizedException`, so an existing
    ``except UnauthorizedException`` keeps catching it.

    Attributes:
    ----------
    - key_suffix (Optional[str]): The last four characters of the key, or
      None when the key is too short to show any of it.
    - key_source (Optional[str]): Where the key was read from: the token
      argument, the ``W24TECHREAD_AUTH_TOKEN`` environment variable, or a
      license file named by its path. None when it is not known.
    - status_code (Optional[int]): The HTTP status the server refused with.
    """

    cli_message_header: str = "API Key Rejected"
    cli_message_body: str = (
        "The Werk24 API did not accept the API key this client sent.\n\n"
        "The key may be mistyped, or it may no longer be active: a key stops "
        "working when it is deleted, and when the account it belongs to is "
        "closed or suspended.\n\n"
        f"Check your keys or create a new one at {API_KEYS_URL}"
    )

    def __init__(
        self,
        details: str = "",
        key_suffix: Optional[str] = None,
        key_source: Optional[str] = None,
        status_code: Optional[int] = None,
    ):
        """Initialize the exception with what is known about the refused key.

        Args:
        ----
        - details (str): Additional details, appended after the key lines.
        - key_suffix (Optional[str]): The last four characters of the key.
        - key_source (Optional[str]): Where the key was read from.
        - status_code (Optional[int]): The HTTP status of the refusal.
        """
        self.details = details
        self.key_suffix = key_suffix
        self.key_source = key_source
        self.status_code = status_code

        lines = []
        if key_suffix:
            lines.append(f"Key: ending in '{key_suffix}'")
        if key_source:
            lines.append(f"Read from: {key_source}")
        if status_code:
            lines.append(f"Server response: HTTP {status_code}")
        if details:
            lines.append(details)
        super().__init__("\n".join(lines))

    def __reduce__(self):
        # See CallbackDrawingTooLargeException.__reduce__.
        return (
            type(self),
            (self.details, self.key_suffix, self.key_source, self.status_code),
        )


class RequestTooLargeException(TechreadException):
    """Exception raised when the request size exceeds the allowed limit."""

    cli_message_header: str = "Request Too Large"
    cli_message_body: str = (
        "The request size exceeds the maximum allowed size of 10MB.\n\n"
        "For more information, visit:\nhttps://v2.docs.werk24.io"
    )


class DrawingTooLargeException(RequestTooLargeException):
    """Raised when a drawing is larger than ``read_drawing`` can upload.

    ``read_drawing`` uploads the drawing through a presigned upload that
    accepts at most 10 MiB (10,485,760 bytes; a drawing of exactly that
    size is accepted). ``Werk24Client.check_drawing_size`` raises this
    before anything is sent when the drawing is over that limit. It is also
    raised when storage refuses an upload as ``EntityTooLarge``.

    ``drawing_bytes`` is the size as it would be uploaded. When the server
    asks for end-to-end encryption, that includes the encryption overhead,
    so a drawing just under the limit can end up over it.

    A subclass of :class:`RequestTooLargeException`, so an existing
    ``except RequestTooLargeException`` keeps catching it.

    ``read_drawing`` itself does not raise it: it reports
    ``DRAWING_FILE_SIZE_TOO_LARGE`` on each ask instead, as documented.

    Attributes:
    ----------
    - drawing_bytes (int): Size of the drawing that was refused.
    - max_drawing_bytes (int): The largest drawing the upload accepts.
    """

    cli_message_header: str = "Drawing Too Large"
    cli_message_body: str = (
        "The drawing is larger than read_drawing can upload.\n\n"
        "Reduce the file size, for example by lowering the resolution of a "
        "scanned drawing or compressing the images inside a PDF, and submit "
        "it again.\n\n"
        "For more information, visit:\n" + FILE_SIZE_DOCS_URL
    )

    def __init__(self, drawing_bytes: int, max_drawing_bytes: int):
        self.drawing_bytes = drawing_bytes
        self.max_drawing_bytes = max_drawing_bytes
        super().__init__(
            f"The drawing is {drawing_bytes} bytes; read_drawing can upload "
            f"at most {max_drawing_bytes} bytes."
        )

    def __reduce__(self):
        # The default rebuilds an exception from its message alone, which
        # this signature does not take (pickling across a process pool).
        return (type(self), (self.drawing_bytes, self.max_drawing_bytes))


class CallbackDrawingTooLargeException(RequestTooLargeException):
    """Raised before sending when a callback read cannot fit its request.

    ``read_drawing_with_callback`` carries the drawing in the body of one
    HTTPS request, which the API hands to a synchronous Lambda invoke. That
    invoke takes at most 6 MiB, and the body arrives base64-encoded, so the
    drawing has to stay under about 4.6 MB there. ``read_drawing`` uploads
    to storage instead and allows 10 MiB.

    A subclass of :class:`RequestTooLargeException`, so an existing
    ``except RequestTooLargeException`` keeps catching it.

    Attributes:
    ----------
    - drawing_bytes (int): Size of the drawing that was refused.
    - max_drawing_bytes (int): The largest drawing this request could carry,
      after the other form fields.
    """

    cli_message_header: str = "Drawing Too Large For A Callback Read"
    cli_message_body: str = (
        "The drawing is too large to be sent with read_drawing_with_callback, "
        "which carries it inside a single request of at most 6 MiB after "
        "base64 encoding (about 4.6 MB of drawing).\n\n"
        "Use read_drawing instead, which uploads the drawing separately and "
        "allows up to 10 MiB, or reduce the file size.\n\n"
        "For more information, visit:\nhttps://v2.docs.werk24.io"
    )

    def __init__(self, drawing_bytes: int, max_drawing_bytes: int):
        self.drawing_bytes = drawing_bytes
        self.max_drawing_bytes = max_drawing_bytes
        super().__init__(
            f"The drawing is {drawing_bytes} bytes; this request can carry "
            f"at most {max_drawing_bytes} bytes."
        )

    def __reduce__(self):
        # The default rebuilds an exception from its message alone, which
        # this signature does not take (pickling across a process pool).
        return (type(self), (self.drawing_bytes, self.max_drawing_bytes))


class CallbackFieldsTooLargeException(RequestTooLargeException):
    """Raised before sending when a callback read's other fields fill its request.

    ``callback_headers``, ``public_key``, the asks and the drawing's filename
    travel in the same request body as the drawing (see
    :class:`CallbackDrawingTooLargeException`). When they take all of it on
    their own, no drawing fits, and a smaller one or ``read_drawing`` is not
    the way out: those fields are.

    A subclass of :class:`RequestTooLargeException`, so an existing
    ``except RequestTooLargeException`` keeps catching it.

    Attributes:
    ----------
    - fields_bytes (int): What the request takes before any drawing.
    - max_body_bytes (int): The most the request body can take.
    """

    cli_message_header: str = "Callback Request Fields Too Large"
    cli_message_body: str = (
        "The fields sent with read_drawing_with_callback (callback_headers, "
        "public_key, the asks and the drawing's filename) fill its request "
        "on their own, which is at most 6 MiB after base64 encoding. No "
        "drawing fits beside them.\n\n"
        "Send fewer or shorter callback_headers, or a shorter filename.\n\n"
        "For more information, visit:\nhttps://v2.docs.werk24.io"
    )

    def __init__(self, fields_bytes: int, max_body_bytes: int):
        self.fields_bytes = fields_bytes
        self.max_body_bytes = max_body_bytes
        super().__init__(
            f"The fields take {fields_bytes} bytes before the drawing; this "
            f"request can carry at most {max_body_bytes} bytes."
        )

    def __reduce__(self):
        # See CallbackDrawingTooLargeException.__reduce__.
        return (type(self), (self.fields_bytes, self.max_body_bytes))


class UnsupportedMediaType(TechreadException):
    """Exception raised for unsupported file formats."""

    cli_message_header: str = "Unsupported Media Type"
    cli_message_body: str = (
        "The uploaded file format is not supported.\n\n"
        "For a list of supported formats, visit:\nhttps://v2.docs.werk24.io"
    )


class EncryptionException(TechreadException):
    """Exception raised when an error occurs during encryption."""

    cli_message_header: str = "Encryption Error"
    cli_message_body: str = (
        "An error occurred while encrypting the data. Please verify your input and try again."
    )


class SSLCertificateError(TechreadException):
    """Exception raised for SSL certificate verification errors."""

    cli_message_header: str = "SSL Certificate Error"
    cli_message_body: str = (
        "An error occurred while verifying the SSL certificate.\n\n"
        "Possible causes:\n"
        "1. Your company's firewall may use Packet Inspection to monitor and control internet traffic.\n"
        "2. A virus or malware may be intercepting your traffic.\n"
        "3. The server's SSL certificate may not be trusted or has expired.\n\n"
        "Steps to resolve:\n"
        "1. Contact your IT department if Packet Inspection is enabled and request an exception for Werk24's servers.\n"
        "2. Run a system antivirus scan.\n"
        "3. Ensure your system's certificate store is up to date.\n"
        "4. Try switching to a different network or reconfigure your proxy server.\n\n"
        "For further assistance, contact Werk24 support at support@werk24.io."
    )


class ServerException(TechreadException):
    """Exception raised for unexpected server responses."""

    cli_message_header: str = "Server Error"
    cli_message_body: str = (
        "A Server Error occurred while processing your request.\n\n"
        "The Werk24 service team has been notified and will investigate the issue. Please try again later."
    )


class RetryableServerError(ServerException):
    """A server-side failure that resending may resolve: 5xx.

    A subclass of :class:`ServerException` so every existing
    ``except ServerException`` keeps catching it. It exists because
    ``ServerException`` is also what 3xx and 416-499 map to, and those must
    not be retried - resending a request the server rejected as malformed
    only sends it again.
    """

    cli_message_header: str = "Server Error"
    cli_message_body: str = (
        "A Server Error occurred while processing your request.\n\n"
        "The Werk24 service team has been notified and will investigate the "
        "issue. Please try again later."
    )


class ReadTimeoutError(TechreadException):
    """Raised when a read exceeds its deadline or goes quiet.

    Distinct from a connection failure: the socket is fine, the server simply
    has not delivered ``PROGRESS_COMPLETED`` - or anything at all - within the
    time allowed. Callers that retry should treat it as a server-side stall
    rather than as a transport problem.
    """

    cli_message_header: str = "Read Timed Out"
    cli_message_body: str = (
        "The read did not finish within the time allowed.\n\n"
        "The drawing may be unusually large, or the service may be degraded. "
        "Please try again; if it persists, contact the Werk24 team."
    )


class InsufficientCreditsException(ServerException):
    """Raised when the account's request quota is used up.

    The API refuses the request with HTTP 429, or with the same refusal on
    the WebSocket at INITIALIZE or READ. The quota does not reset by
    waiting, so sending the request again does not help; top up the account
    first.

    A subclass of :class:`ServerException`, so existing handlers keep
    catching it, and deliberately not of :class:`RetryableServerError`, so
    the client's own retries skip it.
    """

    cli_message_header: str = "Insufficient Credits"
    cli_message_body: str = (
        "You do not have enough credits left for this request: your account's request quota is used up.\n\n"
        "The quota does not reset by waiting, so retrying will not help. "
        "Please top up your account, or contact your Werk24 account manager or support@werk24.io to raise the limit."
    )


class UserInputError(TechreadException):
    """Exception raised when the user provides invalid input."""

    cli_message_header: str = "Invalid Input"
    cli_message_body: str = (
        "The input provided is invalid. Please verify your input and try again."
    )


class OptionalDependencyMissingError(UserInputError):
    """Raised when an option needs a package that werk24 does not install.

    werk24 keeps packages that only one CLI option uses out of its
    dependencies, so that code importing the library does not install them.
    Such a package is installed through an extra instead, and this error
    names that extra.

    A subclass of :class:`UserInputError`, which the CLI raised for this
    before, so an existing ``except UserInputError`` keeps catching it.

    Attributes:
    ----------
    - package (str): The package that could not be imported, e.g. "Pillow".
    - extra (str): The werk24 extra that installs it, e.g. "images".
    - details (str): What needed the package, e.g. the option that was set.
    - install_command (str): The command that installs the extra.
    """

    cli_message_header: str = "Optional Dependency Missing"
    cli_message_body: str = (
        "This option needs a package that werk24 does not install by default."
    )

    def __init__(self, package: str, extra: str, details: str = ""):
        self.package = package
        self.extra = extra
        self.details = details
        self.install_command = f'pip install "werk24[{extra}]"'
        text = f"{package} is not installed. Install it with: {self.install_command}"
        super().__init__(f"{details} {text}" if details else text)

    def __reduce__(self):
        # See CallbackDrawingTooLargeException.__reduce__.
        return (type(self), (self.package, self.extra, self.details))


class InvalidLicenseException(TechreadException):
    """Exception raised when the provided license is invalid.

    Attributes:
    ----------
    - reason (str): Why the key cannot be used, in a few words, for a
      message such as "That key cannot be used: <reason>". Empty when no
      reason was given.
    """

    cli_message_header: str = "Invalid License"
    cli_message_body: str = (
        "The provided license is invalid or has expired.\n\n"
        "Please ensure that you provide a valid token."
    )

    def __init__(self, details: str = ""):
        """Initialize the exception.

        Args:
        ----
        - details (str): Why the key cannot be used. Kept as ``reason`` and
          appended to the message.
        """
        self.reason = details
        super().__init__(details)

    def __reduce__(self):
        # The default rebuilds the exception from its full message, which
        # would append the message to itself a second time.
        return (type(self), (self.reason,))


class LicenseNotFoundException(InvalidLicenseException):
    """Raised when no API key is configured anywhere the client looks.

    A subclass of :class:`InvalidLicenseException`, so an existing
    ``except InvalidLicenseException`` keeps catching it. Its message lists
    every place the client looked, what it found there, and how to set up a
    key.

    Attributes:
    ----------
    - searched (list[tuple[str, str]]): Each place the client looked, with
      what it found there, for example ``("/home/me/.werk24", "not found")``.
    - save_path (Optional[str]): Where ``werk24 init`` saves a key.
    - keys_url (str): The page where API keys are created and managed.
    """

    cli_message_header: str = "No API Key Found"
    cli_message_body: str = "No Werk24 API key was found."

    def __init__(
        self,
        searched: Sequence[tuple[str, str]] = (),
        save_path: Optional[str] = None,
        keys_url: Optional[str] = None,
    ):
        """Initialize the exception with where the client looked.

        Args:
        ----
        - searched (Sequence[tuple[str, str]]): Each place the client looked
          and what it found there.
        - save_path (Optional[str]): Where ``werk24 init`` saves a key.
        - keys_url (Optional[str]): The page where API keys are managed.
          Defaults to the Werk24 console.
        """
        self.searched = [tuple(entry) for entry in searched]
        self.save_path = save_path
        self.keys_url = keys_url if keys_url is not None else API_KEYS_URL

        sections = [type(self).cli_message_body]
        if self.searched:
            sections.append(
                "Looked in:\n"
                + "\n".join(
                    f"  - {location}: {outcome}" for location, outcome in self.searched
                )
            )

        init_hint = '  - Run "werk24 init" and paste your API key.'
        if save_path:
            init_hint += (
                f" It is saved to {save_path}, where the client finds it from"
                " any folder."
            )
        sections.append(
            "To fix this, do one of the following:\n"
            f"{init_hint}\n"
            "  - Set the environment variable W24TECHREAD_AUTH_TOKEN to your"
            " API key.\n"
            '  - Pass the key to the client: Werk24Client(token="...").'
        )
        if self.keys_url:
            sections.append(f"You can create and manage API keys at {self.keys_url}")

        self.cli_message_body = "\n\n".join(sections)
        TechreadException.__init__(self)
        self.reason = "no API key was found"

    def __reduce__(self):
        # See CallbackDrawingTooLargeException.__reduce__.
        return (type(self), (self.searched, self.save_path, self.keys_url))


class W24AuthenticationError(TechreadException):
    """Not raised by ``Werk24Client``; kept so existing imports keep working.

    The client reports a refused API key as :class:`ApiKeyRejectedException`,
    a subclass of :class:`UnauthorizedException` (a 403 when the connection
    opens, or a 401 from ``read_drawing_with_callback``); other 401 and 403
    answers as :class:`UnauthorizedException`, or as
    :class:`PriorityTooHighError` when they refuse the requested priority;
    and a missing or unusable key as :class:`InvalidLicenseException`. An
    ``except W24AuthenticationError`` never matches an error from this
    client; catch those classes instead.

    Attributes:
        error_code: The specific error code from the API response
        error_details: Additional details about the authentication failure
        request_id: Unique identifier for the failed request
    """

    cli_message_header: str = "Authentication Failed"
    cli_message_body: str = (
        "Authentication with the Werk24 API failed.\n\n"
        "Please verify that:\n"
        "1. Your API token is valid and has not expired\n"
        "2. Your token has the necessary permissions\n"
        "3. You are using the correct region\n\n"
        "For assistance, contact support@werk24.io"
    )

    def __init__(
        self,
        details: str = "",
        error_code: str = "401",
        error_details: dict = None,
        request_id: str = None,
    ):
        """Initialize the authentication error with structured error information.

        Args:
            details: Human-readable error message
            error_code: HTTP status code or application-specific error code
            error_details: Additional context about the error
            request_id: Unique identifier for the request
        """
        self.error_code = error_code
        self.error_details = error_details or {}
        self.request_id = request_id
        super().__init__(details)


class W24ValidationError(TechreadException):
    """Not raised by ``Werk24Client``; kept so existing imports keep working.

    The client reports a malformed request as :class:`BadRequestException`
    (for example an unknown ask type), an invalid priority as
    :class:`InvalidPriorityError`, and a drawing of the wrong type or a
    refused file format as :class:`UnsupportedMediaType`. An
    ``except W24ValidationError`` never matches an error from this client;
    catch those classes instead.

    Attributes:
        error_code: The specific error code from the API response
        error_details: Detailed validation errors (e.g., invalid fields, invalid ask types)
        request_id: Unique identifier for the failed request
    """

    cli_message_header: str = "Validation Error"
    cli_message_body: str = (
        "The request failed validation.\n\n"
        "Please check your request parameters and ensure:\n"
        "1. All required fields are provided\n"
        "2. Field values are in the correct format\n"
        "3. Ask types are valid and supported\n"
        "4. File format is supported (PDF, PNG, JPEG, TIFF)\n\n"
        "For more information, visit: https://v2.docs.werk24.io"
    )

    def __init__(
        self,
        details: str = "",
        error_code: str = "400",
        error_details: dict = None,
        request_id: str = None,
    ):
        """Initialize the validation error with structured error information.

        Args:
            details: Human-readable error message
            error_code: HTTP status code or application-specific error code
            error_details: Detailed validation errors (e.g., invalid_asks, valid_asks)
            request_id: Unique identifier for the request
        """
        self.error_code = error_code
        self.error_details = error_details or {}
        self.request_id = request_id

        # Enhance message with validation details if available
        if error_details:
            detail_lines = []
            if "invalid_asks" in error_details:
                detail_lines.append(
                    f"Invalid ask types: {', '.join(error_details['invalid_asks'])}"
                )
            if "valid_asks" in error_details:
                detail_lines.append(
                    f"Valid ask types: {', '.join(error_details['valid_asks'][:5])}..."
                    if len(error_details["valid_asks"]) > 5
                    else f"Valid ask types: {', '.join(error_details['valid_asks'])}"
                )
            if "field" in error_details:
                detail_lines.append(
                    f"Field '{error_details['field']}': {error_details.get('error', 'invalid')}"
                )
            if detail_lines:
                details = (
                    f"{details}\n\n" + "\n".join(detail_lines)
                    if details
                    else "\n".join(detail_lines)
                )

        super().__init__(details)


class W24RateLimitError(TechreadException):
    """Not raised by ``Werk24Client``; kept so existing imports keep working.

    The client reports HTTP 429 as :class:`InsufficientCreditsException`:
    the account's request quota is used up, and it does not reset by
    waiting, so there is no ``retry_after`` to honour. Top up the account
    instead. An ``except W24RateLimitError`` never matches an error from
    this client.

    Attributes:
        error_code: The specific error code from the API response
        error_details: Rate limit information (e.g., retry_after, limit, current)
        request_id: Unique identifier for the failed request
        retry_after: Number of seconds to wait before retrying
    """

    cli_message_header: str = "Rate Limit Exceeded"
    cli_message_body: str = (
        "You have exceeded the API rate limit.\n\n"
        "Please wait before sending additional requests.\n"
        "Consider implementing exponential backoff in your application.\n\n"
        "For information about rate limits, visit: https://v2.docs.werk24.io"
    )

    def __init__(
        self,
        details: str = "",
        error_code: str = "429",
        error_details: dict = None,
        request_id: str = None,
        retry_after: int = None,
    ):
        """Initialize the rate limit error with structured error information.

        Args:
            details: Human-readable error message
            error_code: HTTP status code or application-specific error code
            error_details: Rate limit details (retry_after, limit, current)
            request_id: Unique identifier for the request
            retry_after: Number of seconds to wait before retrying
        """
        self.error_code = error_code
        self.error_details = error_details or {}
        self.request_id = request_id
        self.retry_after = (
            retry_after or error_details.get("retry_after") if error_details else None
        )

        # Enhance message with retry information
        if self.retry_after:
            details = (
                f"{details}\n\nPlease retry after {self.retry_after} seconds."
                if details
                else f"Please retry after {self.retry_after} seconds."
            )

        if error_details and "limit" in error_details:
            limit_info = f"Rate limit: {error_details.get('current', '?')}/{error_details['limit']} requests"
            details = f"{details}\n{limit_info}" if details else limit_info

        super().__init__(details)


class W24ServerError(TechreadException):
    """Not raised by ``Werk24Client``; kept so existing imports keep working.

    The client reports a server error (5xx) that outlasts its own retries
    as :class:`RetryableServerError`, a read that runs out of time as
    :class:`ReadTimeoutError`, and any other server-side failure as
    :class:`ServerException`. An ``except W24ServerError`` never matches an
    error from this client; catch those classes instead.

    Attributes:
        error_code: The specific error code from the API response
        error_details: Additional context about the server error
        request_id: Unique identifier for the failed request
        is_transient: Whether the error is likely temporary (503) or persistent (500)
    """

    cli_message_header: str = "Server Error"
    cli_message_body: str = (
        "The Werk24 API encountered an error while processing your request.\n\n"
        "The service team has been notified and will investigate the issue.\n"
        "Please try again later.\n\n"
        "If the problem persists, contact support@werk24.io with your request ID."
    )

    def __init__(
        self,
        details: str = "",
        error_code: str = "500",
        error_details: dict = None,
        request_id: str = None,
        is_transient: bool = False,
    ):
        """Initialize the server error with structured error information.

        Args:
            details: Human-readable error message
            error_code: HTTP status code (500 or 503)
            error_details: Additional context about the error
            request_id: Unique identifier for the request
            is_transient: True for 503 (temporary), False for 500 (persistent)
        """
        self.error_code = error_code
        self.error_details = error_details or {}
        self.request_id = request_id
        self.is_transient = is_transient or error_code == "503"

        # Enhance message based on error type
        if self.is_transient:
            self.cli_message_header = "Service Temporarily Unavailable"
            retry_msg = (
                "The service is temporarily unavailable. Please retry your request."
            )
            if error_details and "retry_after" in error_details:
                retry_msg += (
                    f" Estimated wait time: {error_details['retry_after']} seconds."
                )
            details = f"{details}\n\n{retry_msg}" if details else retry_msg

        if request_id:
            details = (
                f"{details}\n\nRequest ID: {request_id}"
                if details
                else f"Request ID: {request_id}"
            )

        super().__init__(details)


class PriorityTooHighError(TechreadException):
    """Exception raised when requested priority exceeds account tier (403).

    This exception is raised when a user requests a priority level that is
    higher than their account tier allows. For example, if an account has
    PRIO2 tier and requests PRIO1 processing.

    Attributes:
        account_tier: The maximum priority level allowed by the account
        requested_priority: The priority level that was requested
    """

    cli_message_header: str = "Priority Too High"
    cli_message_body: str = (
        "The requested priority exceeds your account tier.\n\n"
        "You can only request priorities at or below your account tier level.\n"
        "For example, if your account tier is PRIO2, you can request PRIO2 or PRIO3."
    )

    def __init__(
        self,
        details: str = "",
        account_tier: str = None,
        requested_priority: str = None,
    ):
        """Initialize the priority too high error with structured error information.

        Args:
            details: Human-readable error message
            account_tier: The maximum priority level allowed by the account
            requested_priority: The priority level that was requested
        """
        self.account_tier = account_tier
        self.requested_priority = requested_priority

        # Enhance message with priority details if available
        if account_tier and requested_priority:
            priority_info = (
                f"Account tier: {account_tier}\n"
                f"Requested priority: {requested_priority}"
            )
            details = f"{details}\n\n{priority_info}" if details else priority_info

        super().__init__(details)


class InvalidPriorityError(TechreadException):
    """Exception raised when priority value is invalid (400).

    This exception is raised when a user provides a priority value that
    is not one of the valid options (PRIO1, PRIO2, PRIO3).

    Attributes:
        invalid_value: The invalid priority value that was provided
    """

    cli_message_header: str = "Invalid Priority"
    cli_message_body: str = (
        "The provided priority value is invalid.\n\n"
        "Valid priority values are: PRIO1, PRIO2, PRIO3"
    )

    def __init__(
        self,
        details: str = "",
        invalid_value: str = None,
    ):
        """Initialize the invalid priority error with structured error information.

        Args:
            details: Human-readable error message
            invalid_value: The invalid priority value that was provided
        """
        self.invalid_value = invalid_value

        # Enhance message with the invalid value if available
        if invalid_value:
            value_info = f"Invalid value provided: '{invalid_value}'"
            details = f"{details}\n\n{value_info}" if details else value_info

        super().__init__(details)
