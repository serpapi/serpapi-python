import requests


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
            try:
                self.error = http_error_exception.response.json().get("error", None)
            except requests.exceptions.JSONDecodeError:
                self.error = None
        else:
            self.status_code = -1
            self.error = None
                
        super().__init__(*original_exception.args, response=getattr(original_exception, 'response', None), request=getattr(original_exception, 'request', None))



class HTTPConnectionError(HTTPError, requests.exceptions.ConnectionError, SerpApiError):
    """Connection Error."""

    pass
