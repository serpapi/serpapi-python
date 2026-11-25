import json

from collections import UserDict

from .textui import prettify_json
from .utils import _response_json


class _BaseSerpResults(UserDict):

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

        This can be useful when passing results to libraries that expect a
        plain ``dict``.
        """

        return self.data.copy()

    @property
    def next_page_url(self):
        """The URL of the next page of results, if any."""

        serpapi_pagination = self.data.get("serpapi_pagination")

        if serpapi_pagination:
            return serpapi_pagination.get("next")

    @classmethod
    def from_http_response(cls, r, *, client=None):
        """Construct results from an HTTP response.

        :param r: The HTTP response to parse.
        :param client: The client that sent the request.

        An instance of this class is returned if the response is a valid JSON object.
        Otherwise, the raw text (as a properly decoded unicode string) is returned.
        """
        content_type = r.headers.get("Content-Type", "").split(";", 1)[0].lower()
        if content_type in {"text/html", "text/markdown"}:
            return r.text

        try:
            return cls(_response_json(r), client=client)
        except ValueError:
            return r.text


class SerpResults(_BaseSerpResults):
    """A dictionary-like object that represents the results of a SerpApi request.

    An instance of this class is returned if the response is a valid JSON object.
    It can be used like a dictionary, but also has some additional methods.
    """

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
        while current_page and current_page_count < max_pages:
            yield current_page
            current_page_count += 1
            if current_page_count >= max_pages:
                break
            if current_page.next_page_url:
                current_page = current_page.next_page()
            else:
                break


class AsyncSerpResults(_BaseSerpResults):
    """A dictionary-like object that represents the results of a :class:`AsyncClient <serpapi.AsyncClient>` request.

    It works like :class:`SerpResults <serpapi.SerpResults>`, but :meth:`next_page`
    is a coroutine and :meth:`yield_pages` is an asynchronous generator.
    """

    async def next_page(self):
        """Return the next page of results, if any. Use it with ``await``."""

        if self.next_page_url:
            r = await self.client.request("GET", path=self.next_page_url, params={})
            return AsyncSerpResults.from_http_response(r, client=self.client)

    async def yield_pages(self, max_pages=1_000):
        """An asynchronous generator that ``yield`` s the next ``n`` pages of search results, if any.

        Use it with ``async for``.

        :param max_pages: limit the number of pages yielded to ``n``.
        """

        current_page_count = 0

        current_page = self
        while current_page and current_page_count < max_pages:
            yield current_page
            current_page_count += 1
            if current_page_count >= max_pages:
                break
            if current_page.next_page_url:
                current_page = await current_page.next_page()
            else:
                break
