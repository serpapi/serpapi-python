"""Client for SerpApi.com"""
import json
import urllib3
from .error import SerpApiException
from ._version import __version__

class HttpClient:
    """Simple HTTP client wrapper around urllib3"""

    BACKEND = 'https://serpapi.com'
    SUPPORTED_DECODER = ['json', 'html']

    def __init__(self, parameter: dict = None):
        """Initialize a SerpApi Client with the default parameters provided.
        An instance of urllib3 will be created
         where
          timeout is 60s by default
          retries is disabled by default
        both properties can be override by the parameter.
          """
        # initialize the http client
        self.http = urllib3.PoolManager()

        # initialize default client parameter
        self.parameter = parameter

        # urllib3 configurations
        # HTTP connect timeout
        if 'timeout' in parameter:
            self.timeout = parameter['timeout']
            del parameter['timeout']
        else:
            # 60s default
            self.timeout = 60.0

        # no HTTP retry
        if 'retries' in parameter:
            self.retries = parameter['retries']
            del parameter['retries']
        else:
            self.retries = False

    def start(self, path: str, parameter: dict = None, decoder: str = 'json'):
        """start HTTP request and decode response using urllib3.
         The response is decoded using the selected decoder:
          - html: raw HTML response
          - json: deep dict contains search results

        Parameters:
        ---
        path: str
          HTTP endpoint path under serpapi.com/<path>
        decoder: str
          define how to post process the HTTP response.
           for example: json -> convert response to a dict
            using the default JSON parser from Python
        parameter: dict
          search query

        Returns:
        ---
        dict|str
        decoded HTTP response"""
        # track client language
        self.parameter['source'] = 'serpapi-python:' + __version__
        self.parameter['output'] = decoder

        # merge parameter defaults and overrides
        fields = self.parameter.copy()
        fields.update(parameter)

        # execute HTTP get request
        response = self.http.request('GET',
                                     self.BACKEND + path,
                                     fields=fields,
                                     timeout=self.timeout,
                                     retries=self.retries)
        # decode response
        return self.decode(response, decoder)

    def decode(self, response: any, decoder: str):
        """Decode HTTP response using a given decoder"""
        # handle HTTP error
        if response.status != 200:
            try:
                raw = response.data.decode('utf-8')
                payload = json.loads(raw)
                raise SerpApiException(payload['error'])
            except Exception as ex:
                raise SerpApiException(raw) from ex

        # HTTP success 200
        payload = response.data.decode('utf-8')

        # successful response decoding
        if decoder == 'json':
            return json.loads(payload)

        if decoder == 'html':
            return payload

        raise SerpApiException("Invalid decoder: " +
                               decoder + ", available: json, html")


class Client(HttpClient):
    """
    Client performend http query to serpApi.com using urllib3 under the hood.

    The HTTP connection be tuned to allow
     - retries : attempt to reconnect if the connection fail by default: False
     - timeout : connection timeout by default 60s
    for more details:  https://urllib3.readthedocs.io/en/stable/user-guide.html

    """

    def __init__(self, parameter: dict = None):
        # define default parameter
        if parameter is None:
            parameter = {}
        # initialize HTTP client
        HttpClient.__init__(self, parameter)

    def search(self, parameter: dict = None, decoder: str = 'json'):
        """
        make search then decode the output
         decoder supported 'json', 'html'

        Parameters
        ----------
        parameter : dict
            search query
        decoder : str
            set decoder to convert the datastructure received from

        Returns
        -------
        dict|str
            search results returns as :
             dict if decoder = 'json'
             str if decoder = 'html'
        """
        return self.start(path='/search', parameter=parameter, decoder=decoder)

    def html(self, parameter: dict = None):
        """
        html search

        Parameters
        ----------
        parameter : dict
            search query see: https://serpapi.com/search-api

        Returns
        -------
        str
        raw html search results directly from the search engine
        """
        return self.start('/search', parameter, 'html')

    def location(self, parameter: dict = None):
        """
        Get location using Location API

        Parameters
        ----------
        parameter : dict
            location query like: {q: "Austin", limit: 5}
             see: https://serpapi.com/locations-api

        Returns
        -------
        array
        list of matching locations
        """
        return self.start('/locations.json', parameter, 'json')

    def search_archive(self, search_id: str, decoder: str = 'json'):
        """
        Retrieve search results from the Search Archive API

        Parameters:
        -----
        search_id: str
            id from a previous client. in the JSON search response it is search_metadata.id

        """
        path = "/searches/" + str(search_id) + "."
        if decoder in self.SUPPORTED_DECODER:
            path += decoder
        else:
            raise SerpApiException('Decoder must be json or html')
        return self.start(path, {}, decoder)

    def account(self, api_key: str = None):
        """
        Get account information using Account API

        Parameters
        ---
        api_key: str
        secret user key provided by serpapi.com

        Returns
        ---
        dict
        user account information
        """
        if api_key is not None:
            self.parameter['api_key'] = api_key
        return self.start('/account', self.parameter, 'json')
