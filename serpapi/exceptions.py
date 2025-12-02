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

    def __init__(self, http_error_exception: requests.exceptions.HTTPError):
        self.status_code = http_error_exception.response.status_code
        self.error = http_error_exception.response.json().get("error", None)
        super().__init__(*http_error_exception.args, response=http_error_exception.response, request=http_error_exception.request)


class HTTPConnectionError(HTTPError, requests.exceptions.ConnectionError, SerpApiError):
    """Connection Error."""

    pass
