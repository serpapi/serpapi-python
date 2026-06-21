from .http import HTTPClient
from .exceptions import SearchIDNotProvided
from .models import SerpResults


class Client(HTTPClient):
    """A class that handles API requests to SerpApi in a user-friendly manner.

    :param api_key: The API Key to use for SerpApi.com.
    :param timeout: The default timeout to use for requests.

    Please provide ``api_key`` when instantiating this class. We recommend storing this in an environment variable, like so:

        .. code-block:: bash

            $ export SERPAPI_KEY=YOUR_API_KEY

        .. code-block:: python

            import os
            import serpapi

            serpapi = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])

    """

    DASHBOARD_URL = "https://serpapi.com/dashboard"

    def __init__(self, *, api_key=None, timeout=None):
        super().__init__(api_key=api_key, timeout=timeout)

    def __repr__(self):
        return "<SerpApi Client>"

    def search(self, params: dict = None, **kwargs):
        """Fetch a page of results from SerpApi. Returns a :class:`SerpResults <serpapi.client.SerpResults>` object, or unicode text (*e.g.* if ``'output': 'html'`` was passed).

        Dictionary parameters and keyword parameters are both supported:

        .. code-block:: python

            >>> import types
            >>> client = Client(api_key="secret_api_key")
            >>> client.request = lambda method, path, params, **kwargs: types.SimpleNamespace(json=lambda: {"search_parameters": params}, text="")
            >>> client.search({"engine": "google", "q": "Coffee"})["search_parameters"]["q"]
            'Coffee'
            >>> client.search(engine="google", q="Coffee")["search_parameters"]["engine"]
            'google'


        :param params: SerpApi search parameters such as ``engine``, ``q``, ``location``, and ``output``.
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

    def search_archive(self, params: dict = None, **kwargs):
        """Get a result from the SerpApi Search Archive API.

        :param params: Archive parameters. Must include ``search_id``.
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


# An un-authenticated client instance.
_client = Client()
search = _client.search
search_archive = _client.search_archive
locations = _client.locations
account = _client.account
