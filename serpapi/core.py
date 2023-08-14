from .http import HTTPClient
from .exceptions import SearchIDNotProvided
from .models import SerpResults


class Client(HTTPClient):
    """A class that handles API requests to SerpApi in a user–friendly manner.

    :param api_key: The API Key to use for SerpApi.com.

    Please provide ``api_key`` when instantiating this class. We recommend storing this in an environment variable, like so:

        .. code-block:: bash

            $ export SERPAPI_KEY=YOUR_API_KEY

        .. code-block:: python

            import os
            import serpapi

            serpapi = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])

    """

    DASHBOARD_URL = "https://serpapi.com/dashboard"

    def __repr__(self):
        return "<SerpApi Client>"

    def search(self, params: dict = None, **kwargs):
        """Fetch a page of results from SerpApi. Returns a :class:`SerpResults <serpapi.client.SerpResults>` object, or unicode text (*e.g.* if ``'output': 'html'`` was passed).

        The following three calls are equivalent:

        .. code-block:: python

            >>> s = serpapi.search(q="Coffee", location="Austin, Texas, United States")

        .. code-block:: python

            >>> params = {"q": "Coffee", "location": "Austin, Texas, United States"}
            >>> s = serpapi.search(**params)

        .. code-block:: python

            >>> params = {"q": "Coffee", "location": "Austin, Texas, United States"}
            >>> s = serpapi.search(params)


        :param q: typically, this is the parameter for the search engine query.
        :param engine: the search engine to use. Defaults to ``google``.
        :param output: the output format desired (``html`` or ``json``). Defaults to ``json``.
        :param api_key: the API Key to use for SerpApi.com.
        :param **: any additional parameters to pass to the API.


        **Learn more**: https://serpapi.com/search-api
        """
        if params is None:
            params = {}

        if kwargs:
            params.update(kwargs)

        r = self.request("GET", "/search", params=params)

        return SerpResults.from_http_response(r, client=self)

    def search_archive(self, params: dict = None, **kwargs):
        """Get a result from the SerpApi Search Archive API.

        :param search_id: the Search ID of the search to retrieve from the archive.
        :param api_key: the API Key to use for SerpApi.com.
        :param output: the output format desired (``html`` or ``json``). Defaults to ``json``.
        :param **: any additional parameters to pass to the API.

        **Learn more**: https://serpapi.com/search-archive-api
        """
        if params is None:
            params = {}

        if kwargs:
            params.update(kwargs)

        try:
            search_id = params["search_id"]
        except KeyError:
            raise SearchIDNotProvided(
                f"Please provide 'search_id', found here: { self.DASHBOARD_URL }"
            )

        r = self.request("GET", f"/searches/{ search_id }", params=params)
        return SerpResults.from_http_response(r, client=self)

    def locations(self, params: dict = None, **kwargs):
        """Get a list of supported Google locations.


        :param q: restricts your search to locations that contain the supplied string.
        :param limit: limits the number of locations returned.
        :param **: any additional parameters to pass to the API.

        **Learn more**: https://serpapi.com/locations-api
        """
        if params is None:
            params = {}

        if kwargs:
            params.update(kwargs)

        r = self.request(
            "GET",
            "/locations.json",
            params=params,
            assert_200=True,
        )
        return r.json()

    def account(self, params: dict = None, **kwargs):
        """Get SerpApi account information.

        :param api_key: the API Key to use for SerpApi.com.
        :param **: any additional parameters to pass to the API.

        **Learn more**: https://serpapi.com/account-api
        """

        if params is None:
            params = {}

        if kwargs:
            params.update(kwargs)

        r = self.request("GET", "/account.json", params=params, assert_200=True)
        return r.json()


# An un-authenticated client instance.
_client = Client()
search = _client.search
search_archive = _client.search_archive
locations = _client.locations
account = _client.account
