import requests


class SerpAPIError(Exception):
    """Base class for exceptions in this module."""

    pass


class APIKeyNotProvided(ValueError, SerpAPIError):
    """API key is not provided."""

    pass


class SearchIDNotProvided(ValueError, SerpAPIError):
    """Search ID is not provided."""

    pass


class HTTPConnectionError(requests.exceptions.ConnectionError, SerpAPIError):
    """Connection Error."""

    pass


class HTTPError(requests.exceptions.HTTPError, SerpAPIError):
    """HTTP Error."""

    pass
