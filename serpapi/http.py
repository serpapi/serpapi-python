import requests

from .exceptions import (
    HTTPError,
    HTTPConnectionError,
)
from .__version__ import __version__


class HTTPClient:
    """This class handles outgoing HTTP requests to SerpApi.com."""

    BASE_DOMAIN = "https://serpapi.com"
    USER_AGENT = f"serpapi-python, v{__version__}"

    def __init__(self, *, api_key=None):
        # Used to authenticate requests.
        # TODO: do we want to support the environment variable? Seems like a security risk.
        self.api_key = api_key
        self.session = requests.Session()

    def request(self, method, path, params, *, assert_200=True, **kwargs):
        # Inject the API Key into the params.
        if "api_key" not in params:
            params["api_key"] = self.api_key

        # Build the URL, as needed.
        if not path.startswith("http"):
            url = self.BASE_DOMAIN + path
        else:
            url = path

        # Make the HTTP request.
        try:
            headers = {"User-Agent": self.USER_AGENT}

            r = self.session.request(
                method=method, url=url, params=params, headers=headers, **kwargs
            )

        except requests.exceptions.ConnectionError as e:
            raise HTTPConnectionError(e)

        # Raise an exception if the status code is not 200.
        if assert_200:
            try:
                raise_for_status(r)
            except requests.exceptions.HTTPError as e:
                raise HTTPError(e)

        return r


def raise_for_status(r):
    """Raise an exception if the status code is not 200."""
    # TODO: put custom behavior in here for various status codes.

    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise HTTPError(e)
