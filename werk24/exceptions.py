class TechreadException(Exception):
    pass


class UnauthorizedException(TechreadException):
    """ Exception that is raised when
    (i) the response code is 403 - Unauthorized, or
    (ii) the requested action was forbidden by the gateway
    """


class UnknownException(TechreadException):
    pass


class RequestTooLargeException(TechreadException):
    """ Raised when the request exceeds the maximal
    request size (at the time of writing 6MB).
    """


class ServerException(TechreadException):
    """ Exception that is raised, when the server responded in an unexpected way.
    """
