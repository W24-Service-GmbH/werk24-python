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


class RequestTooLargeException(TechreadException):
    """Exception raised when the request size exceeds the allowed limit."""

    cli_message_header: str = "Request Too Large"
    cli_message_body: str = (
        "The request size exceeds the maximum allowed size of 10MB.\n\n"
        "For more information, visit:\nhttps://v2.docs.werk24.io"
    )


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


class InsufficientCreditsException(ServerException):
    """Raised when the user has insufficient credits for an action."""

    cli_message_header: str = "Insufficient Credits"
    cli_message_body: str = (
        "You do not have enough credits to perform the requested action.\n\n"
        "Please check your account balance and top up if necessary."
    )


class UserInputError(TechreadException):
    """Exception raised when the user provides invalid input."""

    cli_message_header: str = "Invalid Input"
    cli_message_body: str = (
        "The input provided is invalid. Please verify your input and try again."
    )


class InvalidLicenseException(TechreadException):
    """Exception raised when the provided license is invalid."""

    cli_message_header: str = "Invalid License"
    cli_message_body: str = (
        "The provided license is invalid or has expired.\n\n"
        "Please ensure that you provide a token AND a region."
    )


class W24AuthenticationError(TechreadException):
    """Exception raised when authentication fails (401 responses).

    This exception is raised when the API returns a 401 status code,
    indicating that the authentication credentials are invalid, expired,
    or missing.

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
    """Exception raised when request validation fails (400 responses).

    This exception is raised when the API returns a 400 status code,
    indicating that the request contains invalid data, malformed input,
    or violates validation rules.

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
    """Exception raised when rate limit is exceeded (429 responses).

    This exception is raised when the API returns a 429 status code,
    indicating that the client has sent too many requests in a given
    time period.

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
    """Exception raised for server errors (500/503 responses).

    This exception is raised when the API returns a 500 (Internal Server Error)
    or 503 (Service Unavailable) status code, indicating a problem on the
    server side.

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
