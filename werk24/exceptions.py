""" Module for all exceptions
"""


class TechreadException(Exception):
    """ Base Exception for all Exceptions raised by
    the Techread functionality

    """


class UnauthorizedException(TechreadException):
    """ Exception that is raised when
    (i) the response code is 403 - Unauthorized, or
    (ii) the requested action was forbidden by the gateway
    """


class UnknownException(TechreadException):
    """ A developer's favorite exception
    """


class RequestTooLargeException(TechreadException):
    """ Raised RequestTooLargeException the request exceeds the maximal
    request size (at the time of writing 6MB).
    """


class ServerException(TechreadException):
    """ Exception that is raised, when the server responded in an unexpected
    way.
    """


class BadRequestException(TechreadException):
    """ Raised when the request body cannot be interpreted by the server.
    This indicates that
    (i) someone has fiddled with with request body, or
    (ii) the server API version has been updated and the integration tests
        did not catch the problem.
    If you encounter this exception, please let us know
    """


class ResourceNotFoundException(TechreadException):
    """ Raised when we encounter a 404
    """


class UnsupportedMediaType(TechreadException):
    """ Raised when the uploaded file has a format
    that is not supported by the api
    """


class LicenseError(Exception):
    """ Error raised when the license information is
    incorrect
    """
