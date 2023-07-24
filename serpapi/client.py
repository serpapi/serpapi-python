from pprint import PrettyPrinter
from collections import UserDict

import requests

from .exceptions import (
    APIKeyNotProvided,
    HTTPError,
    HTTPConnectionError,
    SearchIDNotProvided,
)
from .__version__ import __version__


class SerpResults(UserDict):
    """A dictionary-like object that represents the results of a SerpAPI request.

    .. code-block:: python

        >>> serpapi = SerpAPI(api_key=os.environ["API_KEY"])
        >>> search = serpapi.search(q="Coffee", location="Austin, Texas, United States")

        >>> print(search["search_metadata"].keys())
        dict_keys(['id', 'status', 'json_endpoint', 'created_at', 'processed_at', 'google_url', 'raw_html_file', 'total_time_taken'])

    An instance of this class is returned if the response is a valid JSON object.
    It can be used like a dictionary, but also has some additional methods.
    """

    def __init__(self, data, *, client):
        super().__init__(data)
        self.client = client
        self.request = None
        self.response = None

    def __repr__(self):
        pp = PrettyPrinter(
            indent=2,
        )
        return f"{pp.pformat(self.data)}"

    def html(self, **extras):
        html_url = self.get("search_metadata", {}).get("raw_html_file")

        r = self.client.request("GET", html_url, params={}, **extras)
        return r.text

    @property
    def next_page_url(self):
        """The URL of the next page of results, if any."""

        serpapi_pagination = self.data.get("serpapi_pagination")

        if serpapi_pagination:
            return serpapi_pagination.get("next_link")

    def next_page(self):
        """Return the next page of results, if any."""

        if self.next_page_url:
            # Include support for the API key, as it is not included in the next page URL.
            params = {"api_key": self.client.api_key}

            r = self.client.request("GET", path=self.next_page_url, params=params)
            return SerpResults.from_http_response(r, client=self.client)

    def yield_pages(self, max_pages=1_000):
        """A generator that ``yield`` s the next ``n`` pages of search results, if any.

        :param max_pages: limit the number of pages yielded to ``n``.
        """

        current_page_count = 0

        current_page = self
        while current_page.next_page_url and current_page_count < max_pages:
            current_page = current_page.next_page()
            current_page_count += 1
            yield current_page

    @classmethod
    def from_http_response(cls, r, *, assert_200=True, client=None):
        """Construct a SerpResults object from an HTTP response.

        :param assert_200: if ``True`` (default), raise an exception if the status code is not 200.
        :param client: the Client instance which was used to send this request.

        An instance of this class is returned if the response is a valid JSON object.
        Otherwise, the raw text (as a properly decoded unicode string) is returned.
        """

        # Raise an exception if the status code is not 200.
        if assert_200:
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise HTTPError(e)

        try:
            cls = cls(r.json(), client=client)
            cls.request = r.request
            cls.response = r

            return cls
        except ValueError:
            # If the response is not JSON, return the raw text.
            return r.text


class HTTPClient:
    """A class that handles the HTTP requests to the SERP API."""

    BASE_DOMAIN = "https://serpapi.com"
    DASHBOARD_URL = "https://serpapi.com/dashboard"
    USER_AGENT = f"SerpApi Python Client, v{__version__}"

    def __init__(self, *, api_key=None):
        # Used to authenticate requests.
        # TODO: do we want to support the environment variable? Seems like a security risk.
        self.api_key = api_key
        self.session = requests.Session()

    @staticmethod
    def assert_api_key(self, params):
        if params["api_key"] is None:
            raise APIKeyNotProvided(
                f"Please provide an API key, found here: { self.DASHBOARD_URL }"
            )

    def request(
        self, method, path, params, *, assert_api_key=True, assert_200=False, **kwargs
    ):
        # Inject the API Key into the params.
        if "api_key" not in params:
            params["api_key"] = self.api_key

        # If the api_key is not provided, raise an exception.
        # Note: This is not the case for all endpoints (e.g. location).
        if assert_api_key:
            self.assert_api_key(self, params)

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
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise HTTPError(e)
        return r


class Client(HTTPClient):
    """A class that handles API requests to SerpAPI in a user–friendly manner.

    :param api_key: The API Key to use for SerpAPI.com.

    Please provide ``api_key`` when instantiating this class. We recommend storing this in an environment variable, like so:

        .. code-block:: bash

            $ export SERPAPI_KEY=YOUR_API_KEY

        .. code-block:: python

            import os
            import serpapi

            serpapi = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])

    """

    def __repr__(self):
        return "<SerpAPI Client>"

    def search(self, **params):
        """Fetch a page of results from SerpAPI. Returns a :class:`SerpResults <serpapi.client.SerpResults>` object, or unicode text (*e.g.* if ``'output': 'html'`` was passed).

        The following two calls are equivalent:

        .. code-block:: python

            >>> s = serpapi.search(q="Coffee", location="Austin, Texas, United States")

        .. code-block:: python

            >>> params = {"q": "Coffee", "location": "Austin, Texas, United States"}
            >>> s = serpapi.search(**params)


        :param q: typically, this is the parameter for the search engine query.
        :param engine: the search engine to use. Defaults to ``google``.
        :param output: The output format desired (``html`` or ``json``). Defaults to ``json``.
        :param api_key: The API Key to use for SerpAPI.com.
        :param **: any additional parameters to pass to the API.


        **Learn more**: https://serpapi.com/search-api
        """

        r = self.request("GET", "/search", params=params)

        return SerpResults.from_http_response(r, client=self)

    def search_archive(self, **params):
        """Get a result from the SerpAPI Search Archive API.

        **Learn more**: https://serpapi.com/search-archive-api
        """

        try:
            search_id = params["search_id"]
        except KeyError:
            raise SearchIDNotProvided(
                f"Please provide 'search_id', found here: { self.DASHBOARD_URL }"
            )

        r = self.request("GET", f"/searches/{ search_id }", params=params)
        return SerpResults.from_http_response(r, client=self)

    def locations(self, **params):
        """Get a list of supported Google locations.

        **Learn more**: https://serpapi.com/locations-api
        """

        r = self.request(
            "GET",
            "/locations.json",
            params=params,
            assert_api_key=False,
            assert_200=True,
        )
        return r.json()

    def account(
        self,
        **params,
    ):
        """Get SerpAPI account information.

        **Learn more**: https://serpapi.com/account-api
        """

        r = self.request("GET", "/account.json", params=params, assert_200=True)
        return r.json()
