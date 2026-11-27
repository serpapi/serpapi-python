import asyncio
import io
import json
import os
import time
from collections.abc import Mapping

import requests

from .http import AsyncHTTPClient, HTTPClient
from .exceptions import SearchIDNotProvided, TimeoutError
from .models import AsyncSerpResults, SerpResults
from .utils import _response_json


class Client(HTTPClient):
    """A class that handles API requests to SerpApi in a user-friendly manner.

    Store your API key in an environment variable, then create a client with
    ``serpapi.Client(api_key=os.environ["SERPAPI_KEY"])``.

    :param api_key: The API Key to use for SerpApi.com.
    :param timeout: The default timeout to use for requests.
    """

    DASHBOARD_URL = "https://serpapi.com/dashboard"

    def __init__(self, *, api_key=None, timeout=None):
        super().__init__(api_key=api_key, timeout=timeout)

    def __repr__(self):
        return "<SerpApi Client>"

    def search(self, params: dict = None, **kwargs):
        """Fetch a page of results from SerpApi.

        Returns a ``serpapi.SerpResults`` object for JSON responses, or text
        when ``output="html"`` or ``output="md"`` is requested. Prefer passing SerpApi engine
        parameters as keyword arguments. A parameter dictionary is also accepted
        when your code already has parameters in a mapping.


        :param params: Optional mapping of SerpApi search parameters such as ``engine``, ``q``, ``location``, and ``output``.
        :param kwargs: Additional SerpApi parameters or request options. ``timeout``, ``proxies``, ``verify``, ``stream``, and ``cert`` are passed to the underlying HTTP request.


        **Learn more**: https://serpapi.com/search-api
        """
        if params is None:
            params = {}

        # These are arguments that should be passed to the underlying requests.request call.
        request_kwargs = {}
        for key in ["timeout", "proxies", "verify", "stream", "cert"]:
            if key in kwargs:
                request_kwargs[key] = kwargs.pop(key)

        if kwargs:
            params.update(kwargs)

        r = self.request("GET", "/search", params=params, **request_kwargs)

        return SerpResults.from_http_response(r, client=self)

    def extract(self, params: dict = None, **kwargs):
        """Extract content from a public URL using the Extract API.

        Accepts a parameter dictionary or keyword arguments, like :meth:`search`.
        Sets ``engine=extract`` and returns a :class:`SerpResults <serpapi.SerpResults>` object for JSON, or text for HTML and Markdown.

        .. code-block:: python

            results = client.extract(url="https://example.com/")
            markdown = client.extract(url="https://example.com/", output="md")
            results = client.extract({"url": "https://example.com/", "timeout": 30000}, timeout=60)

        :param params: Optional mapping of Extract API parameters, including the required ``url``. Put ``timeout`` here to set the API fetch timeout in milliseconds.
        :param kwargs: Additional API parameters or HTTP request options, as in :meth:`search`. The ``timeout`` keyword controls the HTTP client timeout in seconds.

        ``mode`` accepts ``scrape`` (default), ``map``, or ``crawl``. ``output`` accepts ``json`` (default), ``html``, or ``md``.
        JSON includes page content in the top-level ``markdown`` field by default,
        or in each ``pages`` entry for crawls. Set ``include_markdown=False`` to omit it.
        For a scraped page, ``output="md"`` returns the page Markdown without search metadata.

        Crawl mode can consume one search credit per successfully extracted page. Use ``max_pages`` to limit the number of pages.
        """
        params = dict(params) if params is not None else {}
        kwargs["engine"] = "extract"
        return self.search(params, **kwargs)

    def search_archive(self, params: dict = None, **kwargs):
        """Get a result from the SerpApi Search Archive API.

        :param params: Archive parameters. Must include ``search_id``. ``output`` accepts ``json`` (default), ``html``, or ``md``.
        :param kwargs: Additional archive parameters or request options. ``timeout``, ``proxies``, ``verify``, ``stream``, and ``cert`` are passed to the underlying HTTP request.

        **Learn more**: https://serpapi.com/search-archive-api
        """
        if params is None:
            params = {}

        # These are arguments that should be passed to the underlying requests.request call.
        request_kwargs = {}
        for key in ["timeout", "proxies", "verify", "stream", "cert"]:
            if key in kwargs:
                request_kwargs[key] = kwargs.pop(key)

        if kwargs:
            params.update(kwargs)

        try:
            search_id = params["search_id"]
        except KeyError:
            raise SearchIDNotProvided(
                f"Please provide 'search_id', found here: { self.DASHBOARD_URL }"
            )

        r = self.request("GET", f"/searches/{ search_id }", params=params, **request_kwargs)
        return SerpResults.from_http_response(r, client=self)

    def async_search(self, searches=None, *, queries=None, poll_interval=1, timeout=300, **kwargs):
        """Run a batch of searches asynchronously and wait for every result.

        Each search is submitted with ``{"async": True}``, then the Search
        Archive API is polled until every search finishes. This is the submit,
        poll and re-queue loop from the async search guide, without the
        bookkeeping.

        Searches are given as a list of parameter dictionaries, or as a list
        of query strings with shared parameters:

        .. code-block:: python

            results = client.async_search(
                queries=["burly", "creator", "doubtful", "minecraft"],
                engine="youtube",
                device="desktop",
            )

        A plain string in the list is shorthand for ``{"q": string}``.
        Parameters passed as keyword arguments apply to every search, and a
        search's own parameters take precedence over them. The ``proxies``,
        ``verify``, ``stream``, and ``cert`` keyword arguments are passed to
        the underlying HTTP requests, as in :meth:`search`.

        The returned list has one entry per search, in the same order as the
        input. An entry is a ``serpapi.SerpResults`` object once its search
        finishes, including searches whose final status is ``"Error"``. If a
        search could not be submitted or retrieved, or is still unfinished
        when ``timeout`` expires, its entry is the exception instead, so one
        failed search does not lose the rest of the batch.

        :param searches: A list of searches. Each item is a parameter
            dictionary like the one :meth:`search` accepts, or a query string.
        :param queries: A list of query strings, as an alternative to
            ``searches``. Combined with shared keyword parameters, such as
            ``engine``, this is the quickest way to run one search per query.
        :param poll_interval: Seconds to wait between rounds of archive
            checks. Defaults to 1.
        :param timeout: Overall deadline in seconds, covering submission and
            polling. Searches still unfinished at the deadline get a
            ``TimeoutError`` entry. Pass ``None`` to wait without a deadline.
            Defaults to 300.

        **Learn more**: https://serpapi.com/search-archive-api
        """
        if searches is None:
            searches = queries
        if searches is None:
            raise TypeError("async_search() requires a list of searches or queries")
        if isinstance(searches, (str, Mapping)):
            searches = [searches]

        # These are arguments that should be passed to the underlying requests.request call.
        request_kwargs = {}
        for key in ["proxies", "verify", "stream", "cert"]:
            if key in kwargs:
                request_kwargs[key] = kwargs.pop(key)

        results = [None] * len(searches)
        pending = {}

        for index, item in enumerate(searches):
            params = {"q": item} if isinstance(item, str) else dict(item)
            for key, value in kwargs.items():
                params.setdefault(key, value)
            params["async"] = True

            try:
                submitted = self.search(params, **request_kwargs)
                search_id = submitted["search_metadata"]["id"]
            except Exception as error:  # One failed search must not sink the batch.
                results[index] = error
            else:
                pending[index] = search_id

        deadline = None if timeout is None else time.monotonic() + timeout
        while pending:
            if deadline is not None and time.monotonic() >= deadline:
                break

            for index, search_id in list(pending.items()):
                try:
                    # Send only the search ID: reusing the search parameters
                    # (such as "q") makes the Search Archive API return an error.
                    result = self.search_archive(
                        {"search_id": search_id}, **request_kwargs
                    )
                except Exception as error:  # One failed search must not sink the batch.
                    results[index] = error
                    del pending[index]
                    continue

                metadata = (
                    result.get("search_metadata")
                    if isinstance(result, Mapping)
                    else None
                )
                status = metadata.get("status") if metadata else None
                if status is None or status in ("Success", "Cached", "Error"):
                    results[index] = result
                    del pending[index]

            if pending:
                time.sleep(poll_interval)

        for index, search_id in pending.items():
            results[index] = TimeoutError(
                f"Search {search_id} did not finish within {timeout} seconds"
            )

        return results

    def upload_image(self, image, **kwargs):
        """Upload an image to SerpApi's Image API.

        ``image`` can be a filesystem path or an open binary file object. The
        returned dictionary contains an ``image_id`` that can be passed to
        :meth:`search` for engines that accept uploaded images, such as Google
        Lens.

        :param image: a path or open binary file object containing a JPG/JPEG,
            PNG, or WebP image no larger than 500 KB.
        :param api_key: the API Key to use for SerpApi.com.
        :param **: any additional multipart form fields to pass to the API.

        **Learn more**: https://serpapi.com/image-api
        """
        request_kwargs = {}
        for key in ["timeout", "proxies", "verify", "stream", "cert"]:
            if key in kwargs:
                request_kwargs[key] = kwargs.pop(key)

        data = kwargs
        if "api_key" not in data:
            data["api_key"] = self.api_key

        image_file = None
        try:
            if isinstance(image, (str, os.PathLike)):
                image_file = open(image, "rb")
                image = image_file
            elif isinstance(image, io.TextIOBase):
                raise TypeError(
                    "image file must be opened in binary mode, e.g. open(path, 'rb')"
                )

            r = self.request(
                "POST",
                "/image",
                params={},
                data=data,
                files={"image": image},
                **request_kwargs,
            )
            return r.json()
        finally:
            if image_file is not None:
                image_file.close()

    def locations(self, params: dict = None, **kwargs):
        """Get a list of supported Google locations.


        :param params: Location API parameters such as ``q`` and ``limit``.
        :param kwargs: Additional location parameters or request options. ``timeout``, ``proxies``, ``verify``, ``stream``, and ``cert`` are passed to the underlying HTTP request.

        **Learn more**: https://serpapi.com/locations-api
        """
        if params is None:
            params = {}

        # These are arguments that should be passed to the underlying requests.request call.
        request_kwargs = {}
        for key in ["timeout", "proxies", "verify", "stream", "cert"]:
            if key in kwargs:
                request_kwargs[key] = kwargs.pop(key)

        if kwargs:
            params.update(kwargs)

        r = self.request(
            "GET",
            "/locations.json",
            params=params,
            assert_200=True,
            **request_kwargs,
        )
        return r.json()

    def account(self, params: dict = None, **kwargs):
        """Get SerpApi account information.

        :param params: Account API parameters.
        :param kwargs: Additional account parameters or request options. ``timeout``, ``proxies``, ``verify``, ``stream``, and ``cert`` are passed to the underlying HTTP request.

        **Learn more**: https://serpapi.com/account-api
        """

        if params is None:
            params = {}

        # These are arguments that should be passed to the underlying requests.request call.
        request_kwargs = {}
        for key in ["timeout", "proxies", "verify", "stream", "cert"]:
            if key in kwargs:
                request_kwargs[key] = kwargs.pop(key)

        if kwargs:
            params.update(kwargs)

        r = self.request("GET", "/account.json", params=params, assert_200=True, **request_kwargs)
        return r.json()


def _pop_request_options(kwargs):
    # These are arguments that should be passed to the underlying HTTP request.
    request_kwargs = {}
    for key in ["timeout", "proxies", "verify", "stream", "cert"]:
        if key in kwargs:
            request_kwargs[key] = kwargs.pop(key)

    return request_kwargs


def _async_response_json(response):
    try:
        return _response_json(response)
    except json.JSONDecodeError as error:
        raise requests.exceptions.JSONDecodeError(
            error.msg, error.doc, error.pos
        ) from error


def _read_upload_image(image):
    if isinstance(image, (str, os.PathLike)):
        with open(image, "rb") as image_file:
            return _read_upload_image(image_file)
    if isinstance(image, io.TextIOBase):
        raise TypeError("image file must be opened in binary mode, e.g. open(path, 'rb')")
    if hasattr(image, "read"):
        return (requests.utils.guess_filename(image) or "image", image.read())
    return image


async def _prepare_upload_image(image):
    if not hasattr(image, "read"):
        return await asyncio.to_thread(_read_upload_image, image)

    # A worker cannot be cancelled mid-read. Don't return a borrowed file to
    # its caller until the worker has finished with it, even on cancellation.
    # Keep the executor future itself; a shutdown sweep can cancel all asyncio tasks.
    read = asyncio.get_running_loop().run_in_executor(None, _read_upload_image, image)
    cancelled = None
    while not read.done():
        try:
            await asyncio.wait((read,))
        except asyncio.CancelledError as exc:
            cancelled = exc
    if cancelled is not None:
        if not read.cancelled():
            read.exception()
        raise cancelled
    return read.result()


class AsyncClient(AsyncHTTPClient):
    """An asynchronous version of :class:`Client <serpapi.Client>` for use with ``await``.

    It has the same methods, parameters, and request options as ``Client``, and
    each method is a coroutine. ``AsyncClient`` needs Python 3.11 or later and
    the ``async`` extra: ``pip install "serpapi[async]"``. It sends requests with
    `httpx2 <https://pypi.org/project/httpx2/>`_ instead of ``requests``.

    .. code-block:: python

        async with serpapi.AsyncClient(api_key=os.environ["SERPAPI_KEY"]) as client:
            results = await client.search(engine="google", q="coffee")

    Use the client in an ``async with`` block, or call ``await client.aclose()``
    when you are done with it, to close its connections. Use each client in a
    single event loop. You can send several requests at once with the same client.

    :param api_key: The API Key to use for SerpApi.com.
    :param timeout: The default timeout to use for requests.
    """

    DASHBOARD_URL = "https://serpapi.com/dashboard"

    def __init__(self, *, api_key=None, timeout=None):
        super().__init__(api_key=api_key, timeout=timeout)

    def __repr__(self):
        return "<SerpApi AsyncClient>"

    async def search(self, params: dict = None, **kwargs):
        """Fetch a page of results from SerpApi. Use it with ``await``.

        Returns a ``serpapi.AsyncSerpResults`` object for JSON responses, or text
        when ``output="html"`` or ``output="md"`` is requested. Accepts the same
        parameters as :meth:`Client.search <serpapi.Client.search>`.

        :param params: Optional mapping of SerpApi search parameters such as ``engine``, ``q``, ``location``, and ``output``.
        :param kwargs: Additional SerpApi parameters or request options. ``timeout``, ``proxies``, ``verify``, and ``cert`` are applied to the underlying HTTP request. ``stream`` is accepted but ignored.

        **Learn more**: https://serpapi.com/search-api
        """
        request_kwargs = _pop_request_options(kwargs)
        params = dict(params or {}, **kwargs)

        r = await self.request("GET", "/search", params=params, **request_kwargs)

        return AsyncSerpResults.from_http_response(r, client=self)

    async def extract(self, params: dict = None, **kwargs):
        """Extract content from a public URL using the Extract API. Use it with ``await``.

        Accepts the same parameters as :meth:`Client.extract <serpapi.Client.extract>`.
        Sets ``engine=extract`` and returns a :class:`AsyncSerpResults <serpapi.AsyncSerpResults>` object for JSON, or text for HTML and Markdown.

        :param params: Optional mapping of Extract API parameters, including the required ``url``. Put ``timeout`` here to set the API fetch timeout in milliseconds.
        :param kwargs: Additional API parameters or HTTP request options, as in :meth:`search`. The ``timeout`` keyword controls the HTTP client timeout in seconds.
        """
        kwargs["engine"] = "extract"
        return await self.search(params, **kwargs)

    async def search_archive(self, params: dict = None, **kwargs):
        """Get a result from the SerpApi Search Archive API. Use it with ``await``.

        :param params: Archive parameters. Must include ``search_id``. ``output`` accepts ``json`` (default), ``html``, or ``md``.
        :param kwargs: Additional archive parameters or request options. ``timeout``, ``proxies``, ``verify``, and ``cert`` are applied to the underlying HTTP request. ``stream`` is accepted but ignored.

        **Learn more**: https://serpapi.com/search-archive-api
        """
        request_kwargs = _pop_request_options(kwargs)
        params = dict(params or {}, **kwargs)

        try:
            search_id = params["search_id"]
        except KeyError:
            raise SearchIDNotProvided(
                f"Please provide 'search_id', found here: { self.DASHBOARD_URL }"
            )

        r = await self.request(
            "GET", f"/searches/{ search_id }", params=params, **request_kwargs
        )
        return AsyncSerpResults.from_http_response(r, client=self)

    async def upload_image(self, image, **kwargs):
        """Upload an image to SerpApi's Image API. Use it with ``await``.

        ``image`` can be a filesystem path or an open binary file object. The
        returned dictionary contains an ``image_id`` that can be passed to
        :meth:`search` for engines that accept uploaded images, such as Google
        Lens.

        :param image: a path or open binary file object containing a JPG/JPEG,
            PNG, or WebP image no larger than 500 KB.
        :param api_key: the API Key to use for SerpApi.com.
        :param **: any additional multipart form fields to pass to the API.

        **Learn more**: https://serpapi.com/image-api
        """
        request_kwargs = _pop_request_options(kwargs)

        data = kwargs
        if self.api_key is not None and "api_key" not in data:
            data["api_key"] = self.api_key

        self._check_can_request()
        image = await _prepare_upload_image(image)
        r = await self.request(
            "POST", "/image", params={}, data=data, files={"image": image}, **request_kwargs
        )
        return _async_response_json(r)

    async def locations(self, params: dict = None, **kwargs):
        """Get a list of supported Google locations. Use it with ``await``.

        :param params: Location API parameters such as ``q`` and ``limit``.
        :param kwargs: Additional location parameters or request options. ``timeout``, ``proxies``, ``verify``, and ``cert`` are applied to the underlying HTTP request. ``stream`` is accepted but ignored.

        **Learn more**: https://serpapi.com/locations-api
        """
        request_kwargs = _pop_request_options(kwargs)
        params = dict(params or {}, **kwargs)

        r = await self.request(
            "GET",
            "/locations.json",
            params=params,
            assert_200=True,
            **request_kwargs,
        )
        return _async_response_json(r)

    async def account(self, params: dict = None, **kwargs):
        """Get SerpApi account information. Use it with ``await``.

        :param params: Account API parameters.
        :param kwargs: Additional account parameters or request options. ``timeout``, ``proxies``, ``verify``, and ``cert`` are applied to the underlying HTTP request. ``stream`` is accepted but ignored.

        **Learn more**: https://serpapi.com/account-api
        """
        request_kwargs = _pop_request_options(kwargs)
        params = dict(params or {}, **kwargs)

        r = await self.request(
            "GET", "/account.json", params=params, assert_200=True, **request_kwargs
        )
        return _async_response_json(r)


# An un-authenticated client instance.
_client = Client()
search = _client.search
extract = _client.extract
search_archive = _client.search_archive
async_search = _client.async_search
upload_image = _client.upload_image
locations = _client.locations
account = _client.account
