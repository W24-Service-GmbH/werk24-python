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
    cli_message_body: str = """The server could not interpret the request.

This may indicate a problem with the request format or a server update that requires changes in the client. Please report this issue if it persists.
"""


class ResourceNotFoundException(TechreadException):
    """Raised when we encounter a 404"""


class UnauthorizedException(TechreadException):
    """Exception that is raised when
    (i) the response code is 403 - Unauthorized, or
    (ii) the requested action was forbidden by the gateway
    """

    cli_message_header: str = "Unauthorized"
    cli_message_body: str = """You are not authorized to perform this action."""


class RequestTooLargeException(TechreadException):
    """Exception raised when the request size exceeds the allowed limit."""

    cli_message_header: str = "Request Too Large"
    cli_message_body: str = """The request size exceeds the maximum allowed size of 10MB.

For more information, visit:
https://docs.werk24.io/limitations/drawing_file_size.html
"""


class UnsupportedMediaType(TechreadException):
    """Exception raised for unsupported file formats."""

    cli_message_header: str = "Unsupported Media Type"
    cli_message_body: str = """The uploaded file format is not supported.

For a list of supported formats, visit:
https://docs.werk24.io/limitations/drawing_file_format.html
"""


class EncryptionException(TechreadException):
    """Exception raised when an error occurs during encryption."""

    cli_message_header: str = "Encryption Error"
    cli_message_body: str = """An error occurred while encrypting the data."""


class SSLCertificateError(TechreadException):
    """Exception raised for SSL certificate verification errors."""

    cli_message_header: str = "SSL Certificate Error"
    cli_message_body: str = """An error occurred while verifying the SSL certificate.

Possible causes:
---------------
1. Your company's firewall may use Packet Inspection to monitor and control internet traffic. This can interfere with SSL certificate validation.
2. A virus or malware may be intercepting your internet traffic.
3. The server's SSL certificate may not be trusted or has expired.

Steps to resolve:
----------------
1. If you are using a company network, contact your IT department to confirm if Packet Inspection is enabled and request an exception for Werk24's servers.
2. Run a full system antivirus scan to rule out malware or viruses that could be intercepting your traffic.
3. Verify your internet connection by trying to access other secure websites. If the issue persists, try switching to a different network.
4. Ensure that your system's certificate store is up to date. On Windows, update your operating system. On Linux, update the `ca-certificates` package.
5. If you are using a proxy server, ensure it is properly configured and not interfering with the SSL connection.

If none of the above steps resolve the issue, please contact Werk24 support at support@werk24.io for further assistance. Note that SSL certificate validation is outside Werk24's control.
"""


class ServerException(TechreadException):
    """Exception that is raised, when the server responded in an unexpected
    way.
    """

    cli_message_header: str = "Server Error"
    cli_message_body: str = """A Server Error occurred while processing your request.

This indicates a problem with the server. The Werk24 service team has been notified and
will investigate the issue. Please try again later. If the problem persists, please
contact us at info@werk24.io.
"""


class InsufficientCreditsException(ServerException):
    """Raised when the user has insufficient credits to perform the requested action

    NOTE: It inherits from ServerException to backwards compatibility.
    """

    cli_message_header: str = "Insufficient Credits"
    cli_message_body: str = """You do not have enough credits to perform the requested action.

Please check your account balance and top up your account if necessary.
"""
