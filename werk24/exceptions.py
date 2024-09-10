""" Module for all exceptions
"""


class TechreadException(Exception):
    """Base Exception for all Exceptions raised by
    the Techread functionality

    """

    cli_message_header: str = "Techread Error"
    cli_message_body: str = "An error occurred while processing your request"


class UnauthorizedException(TechreadException):
    """Exception that is raised when
    (i) the response code is 403 - Unauthorized, or
    (ii) the requested action was forbidden by the gateway
    """


class UnknownException(TechreadException):
    """A developer's favorite exception"""


class RequestTooLargeException(TechreadException):
    """Raised RequestTooLargeException the request exceeds the maximal
    request size (at the time of writing 6MB).
    """

    cli_message_header: str = "Request Too Large"
    cli_message_body: str = """The request size exceeds the maximal request size of 10MB.

Please check https://docs.werk24.io/limitations/drawing_file_size.html
for the most up-to-date information on the maximal request size.
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

class BadRequestException(TechreadException):
    """Raised when the request body cannot be interpreted by the server.
    This indicates that
    (i) someone has fiddled with with request body, or
    (ii) the server API version has been updated and the integration tests
        did not catch the problem.
    If you encounter this exception, please let us know
    """


class ResourceNotFoundException(TechreadException):
    """Raised when we encounter a 404"""


class UnsupportedMediaType(TechreadException):
    """Raised when the uploaded file has a format
    that is not supported by the api
    """

    cli_message_header: str = "Unsupported Media Type"
    cli_message_body: str = """The file format you uploaded is not supported by Werk24.
Please check https://docs.werk24.io/limitations/drawing_file_format.html
for a current list of supported file formats.
"""


class LicenseError(TechreadException):
    cli_message_header: str = "License Error"
    cli_message_body: str = """An error occurred while verifying the license information.

    Please ensure that the license information is in a location where it can be found
    by the client. The client is currently looking for the license information in the
    following locations:

    1. The environment variables W24_AUTH_TOKEN
    2. The file werk24_license.txt in the current directory, and
    3. for backwards compatiability in the file .werk24 in the current directory
    """


class SSLCertificateError(TechreadException):
    """Error raised when the SSL certificate is not valid"""

    cli_message_header: str = "SSL Certificate Error"
    cli_message_body: str = """An error occurred while verifying the SSL certificate.

This typically can have two reasons:

1. Your IT department has activated the Packet Inspection in your firewall.
    This is a common practice in companies to prevent employees from accessing
    certain websites.

2. You might have a virus on your computer that is trying to intercept your
    internet traffic.

In both cases, please contact your IT department to resolve the issue.
Please understand, that this topic is outside of Werk24's influence.
"""
