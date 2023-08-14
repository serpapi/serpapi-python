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

    pass


class HTTPConnectionError(HTTPError, requests.exceptions.ConnectionError, SerpApiError):
    """Connection Error."""

    pass
