import json

from pprint import pformat
from collections import UserDict

from .textui import prettify_json
from .exceptions import HTTPError


class SerpResults(UserDict):
    """A dictionary-like object that represents the results of a SerpApi request.

    .. code-block:: python

        >>> search = serpapi.search(q="Coffee", location="Austin, Texas, United States")

        >>> print(search["search_metadata"].keys())
        dict_keys(['id', 'status', 'json_endpoint', 'created_at', 'processed_at', 'google_url', 'raw_html_file', 'total_time_taken'])

    An instance of this class is returned if the response is a valid JSON object.
    It can be used like a dictionary, but also has some additional methods.
    """

    def __init__(self, data, *, client):
        super().__init__(data)
        self.client = client

    def __getstate__(self):
        return self.data

    def __setstate__(self, state):
        self.data = state

    def __repr__(self):
        """The visual representation of the data, which is pretty printed, for
        ease of use.
        """

        return prettify_json(json.dumps(self.data, indent=4))

    def as_dict(self):
        """Returns the data as a standard Python dictionary.
        This can be useful when using ``json.dumps(search), for example."""

        return self.data.copy()

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
    def from_http_response(cls, r, *, client=None):
        """Construct a SerpResults object from an HTTP response.

        :param assert_200: if ``True`` (default), raise an exception if the status code is not 200.
        :param client: the Client instance which was used to send this request.

        An instance of this class is returned if the response is a valid JSON object.
        Otherwise, the raw text (as a properly decoded unicode string) is returned.
        """

        try:
            cls = cls(r.json(), client=client)

            return cls
        except ValueError:
            # If the response is not JSON, return the raw text.
            return r.text
