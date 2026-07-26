import json
from typing import Any, Dict, Iterator, Optional, Union, TYPE_CHECKING

from collections import UserDict

import requests

from .textui import prettify_json

if TYPE_CHECKING:
    from .core import Client


class SerpResults(UserDict[str, Any]):
    """A dictionary-like object that represents the results of a SerpApi request.

    .. code-block:: python

        >>> search = serpapi.search(q="Coffee", location="Austin, Texas, United States")

        >>> print(search["search_metadata"].keys())
        dict_keys(['id', 'status', 'json_endpoint', 'created_at', 'processed_at', 'google_url', 'raw_html_file', 'total_time_taken'])

    An instance of this class is returned if the response is a valid JSON object.
    It can be used like a dictionary, but also has some additional methods.
    """

    def __init__(self, data: Dict[str, Any], *, client: Optional["Client"]) -> None:
        super().__init__(data)
        self.client = client

    def __getstate__(self) -> Dict[str, Any]:
        return self.data

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.data = state

    def __repr__(self) -> str:
        """The visual representation of the data, which is pretty printed, for
        ease of use.
        """

        return prettify_json(json.dumps(self.data, indent=4))

    def as_dict(self) -> Dict[str, Any]:
        """Returns the data as a standard Python dictionary.
        This can be useful when using ``json.dumps(search), for example."""

        return self.data.copy()

    @property
    def next_page_url(self) -> Optional[str]:
        """The URL of the next page of results, if any."""

        serpapi_pagination = self.data.get("serpapi_pagination")

        if serpapi_pagination:
            return serpapi_pagination.get("next")
        return None

    def next_page(self) -> Optional[Union["SerpResults", str]]:
        """Return the next page of results, if any."""

        if self.next_page_url and self.client is not None:
            # Include support for the API key, as it is not included in the next page URL.
            params = {"api_key": self.client.api_key}

            r = self.client.request("GET", path=self.next_page_url, params=params)
            return SerpResults.from_http_response(r, client=self.client)

        return None

    def yield_pages(self, max_pages: int = 1_000) -> Iterator[Union["SerpResults", str]]:
        """A generator that ``yield`` s the next ``n`` pages of search results, if any.

        :param max_pages: limit the number of pages yielded to ``n``.
        """

        current_page_count = 0
        current_page = self
        while current_page and current_page_count < max_pages:
            yield current_page
            current_page_count += 1
            if current_page.next_page_url:
                current_page = current_page.next_page()
            else:
                break
            

    @classmethod
    def from_http_response(cls, r: requests.Response, *, client: Optional["Client"] = None) -> Union["SerpResults", str]:
        """Construct a SerpResults object from an HTTP response.

        :param assert_200: if ``True`` (default), raise an exception if the status code is not 200.
        :param client: the Client instance which was used to send this request.

        An instance of this class is returned if the response is a valid JSON object.
        Otherwise, the raw text (as a properly decoded unicode string) is returned.
        """

        try:
            inst = cls(r.json(), client=client)

            return inst
        except ValueError:
            # If the response is not JSON, return the raw text.
            return r.text
