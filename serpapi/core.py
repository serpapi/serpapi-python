import atexit
import io
import os
from contextlib import contextmanager

from .exceptions import SearchIDNotProvided
from .http import REQUEST_OPTIONS, AsyncHTTPClient, HTTPClient
from .models import AsyncSerpResults, SerpResults

__all__ = [
    "AsyncClient",
    "AsyncSerpResults",
    "Client",
    "SerpResults",
    "account",
    "locations",
    "search",
    "search_archive",
    "upload_image",
]

DASHBOARD_URL = "https://serpapi.com/dashboard"


def _split_parameters(params, kwargs):
    if params is None:
        params = {}

    request_kwargs = {}
    for key in REQUEST_OPTIONS:
        if key in kwargs:
            request_kwargs[key] = kwargs.pop(key)

    if kwargs:
        params.update(kwargs)
    return params, request_kwargs


def _search_id(params):
    try:
        return params["search_id"]
    except KeyError:
        raise SearchIDNotProvided(
            f"Please provide 'search_id', found here: {DASHBOARD_URL}"
        ) from None


@contextmanager
def _image_stream(image):
    if isinstance(image, (str, os.PathLike)):
        with open(image, "rb") as image_file:
            yield image_file
        return
    if isinstance(image, io.TextIOBase):
        raise TypeError(
            "image file must be opened in binary mode, e.g. open(path, 'rb')"
        )
    yield image


class Client(HTTPClient):
    """A synchronous client for SerpApi.

    :param api_key: The API key to use for SerpApi.com.
    :param timeout: Default request timeout in seconds. ``None`` waits without
        a timeout, matching previous SDK releases.
    :param proxy: Optional HTTPX proxy URL used by every request.
    :param verify: TLS verification setting or custom CA bundle.
    :param cert: Client certificate path or ``(certificate, key)`` pair.
    :param trust_env: Whether HTTPX reads proxy and certificate environment
        variables.
    """

    DASHBOARD_URL = DASHBOARD_URL

    def __init__(
        self,
        *,
        api_key=None,
        timeout=None,
        proxy=None,
        verify=True,
        cert=None,
        trust_env=True,
    ):
        super().__init__(
            api_key=api_key,
            timeout=timeout,
            proxy=proxy,
            verify=verify,
            cert=cert,
            trust_env=trust_env,
        )

    def __repr__(self):
        return "<SerpApi Client>"

    def search(self, params=None, **kwargs):
        """Fetch one page of search results from SerpApi.

        :param params: Optional mapping of SerpApi search parameters.
        :param kwargs: Additional search parameters or supported request
            options.
        :return: ``SerpResults`` for JSON, or ``str`` for HTML and Markdown.
        """
        params, request_kwargs = _split_parameters(params, kwargs)
        response = self.request("GET", "/search", params=params, **request_kwargs)
        return SerpResults.from_http_response(response, client=self)

    def search_archive(self, params=None, **kwargs):
        """Get a result from the SerpApi Search Archive API.

        :param params: Archive parameters including ``search_id``.
        :param kwargs: Additional archive parameters or request options.
        :return: ``SerpResults`` for JSON, or ``str`` for HTML and Markdown.
        :raises SearchIDNotProvided: if no ``search_id`` is supplied.
        """
        params, request_kwargs = _split_parameters(params, kwargs)
        search_id = _search_id(params)
        response = self.request(
            "GET", f"/searches/{search_id}", params=params, **request_kwargs
        )
        return SerpResults.from_http_response(response, client=self)

    def upload_image(self, image, **kwargs):
        """Upload an image to SerpApi's Image API.

        :param image: Path or open binary file containing a supported image.
        :param kwargs: Multipart fields or supported request options.
        :return: Parsed JSON response containing the temporary ``image_id``.
        """
        _, request_kwargs = _split_parameters({}, kwargs)
        data = kwargs
        if "api_key" not in data:
            data["api_key"] = self.api_key

        with _image_stream(image) as image_stream:
            response = self.request(
                "POST",
                "/image",
                params={},
                data=data,
                files={"image": image_stream},
                **request_kwargs,
            )
            return response.json()

    def locations(self, params=None, **kwargs):
        """Get a list of supported Google locations.

        :param params: Location API parameters such as ``q`` and ``limit``.
        :param kwargs: Additional location parameters or request options.
        :return: A list of matching location dictionaries.
        """
        params, request_kwargs = _split_parameters(params, kwargs)
        response = self.request(
            "GET",
            "/locations.json",
            params=params,
            assert_200=True,
            **request_kwargs,
        )
        return response.json()

    def account(self, params=None, **kwargs):
        """Get SerpApi account information.

        :param params: Optional Account API parameters.
        :param kwargs: Additional account parameters or request options.
        :return: The account response as a dictionary.
        """
        params, request_kwargs = _split_parameters(params, kwargs)
        response = self.request(
            "GET",
            "/account.json",
            params=params,
            assert_200=True,
            **request_kwargs,
        )
        return response.json()


class AsyncClient(AsyncHTTPClient):
    """An asynchronous client for SerpApi.

    Reuse one instance for concurrent requests and close it with ``aclose()``,
    or use ``async with serpapi.AsyncClient(...) as client``.

    Constructor arguments match :class:`Client`.
    """

    DASHBOARD_URL = DASHBOARD_URL

    def __init__(
        self,
        *,
        api_key=None,
        timeout=None,
        proxy=None,
        verify=True,
        cert=None,
        trust_env=True,
    ):
        super().__init__(
            api_key=api_key,
            timeout=timeout,
            proxy=proxy,
            verify=verify,
            cert=cert,
            trust_env=trust_env,
        )

    def __repr__(self):
        return "<SerpApi AsyncClient>"

    async def search(self, params=None, **kwargs):
        """Asynchronously fetch one page of search results from SerpApi.

        Parameters and return values match :meth:`Client.search`.
        """
        params, request_kwargs = _split_parameters(params, kwargs)
        response = await self.request("GET", "/search", params=params, **request_kwargs)
        return AsyncSerpResults.from_http_response(response, client=self)

    async def search_archive(self, params=None, **kwargs):
        """Asynchronously get a result from the Search Archive API.

        Parameters, return values, and errors match
        :meth:`Client.search_archive`.
        """
        params, request_kwargs = _split_parameters(params, kwargs)
        search_id = _search_id(params)
        response = await self.request(
            "GET", f"/searches/{search_id}", params=params, **request_kwargs
        )
        return AsyncSerpResults.from_http_response(response, client=self)

    async def upload_image(self, image, **kwargs):
        """Asynchronously upload an image to SerpApi's Image API.

        Parameters and return values match :meth:`Client.upload_image`.
        """
        _, request_kwargs = _split_parameters({}, kwargs)
        data = kwargs
        if "api_key" not in data:
            data["api_key"] = self.api_key

        with _image_stream(image) as image_stream:
            response = await self.request(
                "POST",
                "/image",
                params={},
                data=data,
                files={"image": image_stream},
                **request_kwargs,
            )
            return response.json()

    async def locations(self, params=None, **kwargs):
        """Asynchronously get supported Google locations.

        Parameters and return values match :meth:`Client.locations`.
        """
        params, request_kwargs = _split_parameters(params, kwargs)
        response = await self.request(
            "GET",
            "/locations.json",
            params=params,
            assert_200=True,
            **request_kwargs,
        )
        return response.json()

    async def account(self, params=None, **kwargs):
        """Asynchronously get SerpApi account information.

        Parameters and return values match :meth:`Client.account`.
        """
        params, request_kwargs = _split_parameters(params, kwargs)
        response = await self.request(
            "GET",
            "/account.json",
            params=params,
            assert_200=True,
            **request_kwargs,
        )
        return response.json()


# Backward-compatible synchronous module helpers use one shared client.
_client = Client()
atexit.register(_client.close)
search = _client.search
search_archive = _client.search_archive
upload_image = _client.upload_image
locations = _client.locations
account = _client.account
