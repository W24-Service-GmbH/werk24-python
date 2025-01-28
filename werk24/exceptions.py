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
        "For more information, visit:\nhttps://docs.werk24.io/limitations/drawing_file_size.html"
    )


class UnsupportedMediaType(TechreadException):
    """Exception raised for unsupported file formats."""

    cli_message_header: str = "Unsupported Media Type"
    cli_message_body: str = (
        "The uploaded file format is not supported.\n\n"
        "For a list of supported formats, visit:\nhttps://docs.werk24.io/limitations/drawing_file_format.html"
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
