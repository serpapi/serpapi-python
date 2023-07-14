from pprint import PrettyPrinter
from collections import UserDict

import requests

from .exceptions import APIKeyNotProvided, HTTPError, HTTPConnectionError
from .__version__ import __version__


class SerpResults(UserDict):
    def __init__(self, data, *, client):
        super().__init__(data)
        self.client = client
        self.request = None
        self.response = None

    def __repr__(self):
        pp = PrettyPrinter(indent=2, compact=True, width=79)
        return f"{pp.pprint(self.data)}"

    @property
    def next_page_url(self):
        serpapi_pagination = self.data.get("serpapi_pagination")

        if serpapi_pagination:
            return serpapi_pagination.get("next")

    def next_page(self):
        if self.next_page_url:
            params = {"api_key": self.client.api_key}
            r = self.client.request("GET", path=self.next_page_url, params=params)
            return SerpResults.from_http_response(r, client=self.client)

    def yield_pages(self, max_pages=1_000):
        current_page_count = 0

        current_page = self
        while current_page.next_page_url and current_page_count < max_pages:
            current_page = current_page.next_page()
            current_page_count += 1
            yield current_page

    @classmethod
    def from_http_response(cls, r, *, assert_200=True, client=None):
        # Raise an exception if the status code is not 200.
        if assert_200:
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise HTTPError(e)

        cls = cls(r.json(), client=client)
        cls.request = r.request
        cls.response = r

        return cls


class SerpAPIHTTP:
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


class SerpAPI(SerpAPIHTTP):
    def search(self, params, *, assert_200=True, **extras):
        r = self.request("get", "/search", params=params, **extras)
        return SerpResults.from_http_response(r, assert_200=assert_200, client=self)

    def search_html(self, params, *, assert_200=True, **extras):
        search = self.search(params, assert_200=assert_200, **extras)
        html_url = search.get("search_metadata", {}).get("raw_html_file")

        r = self.request("GET", html_url, params={}, assert_200=assert_200, **extras)
        return r.text

    def search_archive(self, params, *, assert_200=True, **extras):
        r = self.request("get", "/searches", params=params, **extras)
        return SerpResults.from_http_response(r, assert_200=assert_200, client=self)

    def location(self, params, *, assert_200=True, **extras):
        r = self.request("get", "/locations.json", params=params, **extras)
        return SerpResults.from_http_response(r, assert_200=assert_200, client=self)