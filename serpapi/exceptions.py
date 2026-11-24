import requests

from .utils import _response_json


class SerpApiError(Exception):
    """Base class for exceptions in this module."""

    pass


class APIKeyNotProvided(ValueError, SerpApiError):
    """API key is not provided."""

    pass


class SearchIDNotProvided(ValueError, SerpApiError):
    """Search ID is not provided."""

    pass


class HTTPError(requests.exceptions.HTTPError, SerpApiError):
    """HTTP Error."""

    def __init__(self, original_exception):
        if (isinstance(original_exception, requests.exceptions.HTTPError)):
            http_error_exception: requests.exceptions.HTTPError = original_exception

            self.status_code = http_error_exception.response.status_code
            # requests and httpx2 raise different JSON decoding errors; both are ValueErrors.
            try:
                self.error = _response_json(http_error_exception.response).get("error", None)
            except ValueError:
                self.error = None
        else:
            self.status_code = -1
            self.error = None
                
        super().__init__(*original_exception.args, response=getattr(original_exception, 'response', None), request=getattr(original_exception, 'request', None))



class HTTPConnectionError(HTTPError, requests.exceptions.ConnectionError, SerpApiError):
    """Connection Error."""

    pass


class TimeoutError(requests.exceptions.Timeout, SerpApiError):
    """Timeout Error."""

    pass
