# -*- coding: utf-8 -*-

class KoordinatesException(Exception):
    def __init__(self, message, **kwargs):
        super(KoordinatesException, self).__init__(message)
        for k, v in kwargs.items():
            self.k = v

# Client Errors
class ClientError(KoordinatesException):
    pass

class ClientValidationError(ClientError):
    """ Validation error pre-submission to the API """
    pass

class InvalidAPIVersion(ClientError):
    pass

# Server Errors
class ServerError(KoordinatesException):
    @classmethod
    def from_requests_error(cls, err):
        """
        Raises a subclass of ServerError based on the HTTP response code.
        """
        import requests
        if isinstance(err, requests.HTTPError):
            status_code = err.response.status_code
            return HTTP_ERRORS.get(status_code, cls)(error=err, response=err.response)
        else:
            return cls(error=err)

    def __init__(self, message=None, error=None, response=None):
        if not message:
            if response:
                message = "%s %s" % (response.status_code, response.reason)
                try:
                    # most API errors are of the form {"error": "description"}
                    message += ": %s" % response.json()['error']
                except:
                    pass
            else:
                message = str(error)
        super(ServerError, self).__init__(message, error=error, response=response)

    def __str__(self):
        if self.response:
            return "%s: %s" % (self.message, self.response.text)
        else:
            return super(ServerError, self).__str__()

class BadRequest(ServerError):
    """ Invalid request data or parameters. Check your request. """
    pass
class AuthenticationError(ServerError):
    """ The API token is invalid or expired. """
    pass
class Forbidden(ServerError):
    """ The API token or user doesn't have access to perform the request. """
    pass
class NotFound(ServerError):
    """ The requested object was not found. """
    pass
class NotAllowed(ServerError):
    """ The requested action isn't available for this object. """
    pass
class Conflict(ServerError):
    """ The requested action isn't available for this object due to a conflict. """
    pass
class RateLimitExceeded(ServerError):
    """ The request has exceeded the API rate limit. Retry the request again later. """
    pass
class InternalServerError(ServerError):
    """ An internal server error has occurred. """
    pass
class ServiceUnvailable(ServerError):
    """ The Koordinates service is currently unavailable. """
    pass


HTTP_ERRORS = {
    400: BadRequest,
    401: AuthenticationError,
    403: Forbidden,
    404: NotFound,
    405: NotAllowed,
    409: Conflict,
    422: BadRequest,
    429: RateLimitExceeded,
    500: InternalServerError,
    502: ServiceUnvailable,
    503: ServiceUnvailable,
    504: ServiceUnvailable,
}
