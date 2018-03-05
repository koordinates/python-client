# -*- coding: utf-8 -*-
from six import string_types

class KoordinatesException(Exception):
    """ Base class for all koordinates module errors """
    def __init__(self, message, **kwargs):
        super(KoordinatesException, self).__init__(message)
        for k, v in kwargs.items():
            setattr(self, k, v)

# Client Errors
class ClientError(KoordinatesException):
    """ Base class for client errors """
    pass

class ClientValidationError(ClientError):
    """ Client-side validation error """
    pass

class InvalidAPIVersion(ClientError):
    """ Invalid API Version """
    pass

# Server Errors
class ServerError(KoordinatesException):
    """ Base class for errors returned from the API Servers """
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
        self.response = response
        if not message:
            message = self._get_message(error, response)
        super(ServerError, self).__init__(message, error=error, response=response)

    def _get_message(self, error, response):
        if response:
            message = "%s %s" % (response.status_code, response.reason)
            try:
                # most API errors are of the form {"error": "description"}
                message += ": %s" % response.json()["error"]
            except:
                pass
        else:
            message = str(error)
        return message

    def __str__(self):
        if self.response:
            return "%s: %s" % (self.args[0], self.response.text)
        else:
            return super(ServerError, self).__str__()

    def __repr__(self):
        return "%s('%s')" % (self.__class__.__name__, str(self))


class BadRequest(ServerError):
    """ Invalid request data or parameters. Check your request. (400) """
    def _get_message(self, error, response):
        try:
            messages = []
            for field, errors in sorted(response.json().items()):
                errors = errors if isinstance(errors, string_types) else "; ".join(errors)
                messages.append("%s: %s" % (field, errors))
            return "\n".join(messages)
        except Exception as e:
            return super(BadRequest, self)._get_message(error, response)

class AuthenticationError(ServerError):
    """ The API token is invalid or expired. (401) """
    pass
class Forbidden(ServerError):
    """ The API token or user doesn't have access to perform the request. (403) """
    pass
class NotFound(ServerError):
    """ The requested object was not found. (404) """
    pass
class NotAllowed(ServerError):
    """ The requested action isn't available for this object. (405) """
    pass
class Conflict(ServerError):
    """ The requested action isn't available for this object due to a conflict. (409) """
    pass
class RateLimitExceeded(ServerError):
    """ The request has exceeded the API rate limit. Retry the request again later. (429) """
    pass
class InternalServerError(ServerError):
    """ An internal server error has occurred. (500) """
    pass
class ServiceUnvailable(ServerError):
    """ The Koordinates service is currently unavailable. (502/503/504) """
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
