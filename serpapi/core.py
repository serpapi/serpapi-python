import asyncio
import io
import json
import os

import requests

from .http import AsyncHTTPClient, HTTPClient
from .exceptions import SearchIDNotProvided
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
upload_image = _client.upload_image
locations = _client.locations
account = _client.account
