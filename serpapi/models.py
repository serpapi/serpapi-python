import json

from pprint import pformat
from collections import UserDict

import requests

from .exceptions import HTTPError


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

    def __getstate__(self):
        return self.data

    def __setstate__(self, state):
        self.data = state

    def __repr__(self):
        return json.dumps(self.data, indent=2)

    def as_dict(self):
        return self.data

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
