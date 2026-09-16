import httpx


class SerpApiError(Exception):
    """Base class for exceptions in this module."""


class APIKeyNotProvided(ValueError, SerpApiError):
    """API key is not provided."""


class SearchIDNotProvided(ValueError, SerpApiError):
    """Search ID is not provided."""


class HTTPError(httpx.HTTPError, SerpApiError):
    """An unsuccessful HTTP response from SerpApi."""

    def __init__(self, original_exception):
        self.original_exception = original_exception
        request = getattr(original_exception, "request", None)
        self.response = getattr(original_exception, "response", None)
        self.status_code = (
            self.response.status_code if self.response is not None else -1
        )
        self.error = None

        if self.response is not None:
            try:
                payload = self.response.json()
                if isinstance(payload, dict):
                    self.error = payload.get("error")
            except ValueError:
                pass

        message = str(original_exception)
        httpx.HTTPError.__init__(self, message)
        if request is not None:
            self.request = request


class HTTPConnectionError(HTTPError):
    """A network error while connecting to or reading from SerpApi."""


class TimeoutError(httpx.TimeoutException, SerpApiError):
    """A request to SerpApi exceeded its configured timeout."""

    def __init__(self, original_exception):
        self.original_exception = original_exception
        httpx.TimeoutException.__init__(
            self,
            str(original_exception),
            request=getattr(original_exception, "request", None),
        )
