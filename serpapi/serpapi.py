"""SerpApi package for python"""
import json
import urllib3
from .error import SerpApiException
from .object_decoder import ObjectDecoder

class Client(ObjectDecoder):
    """
    Client performend http query to serpApi.com
     using urllib3 under the hood.

    The HTTP connection be tuned to allow
     - retries : attempt to reconnect if the connection fail by default: False
     - timeout : connection timeout by default 60s
    for more details:  https://urllib3.readthedocs.io/en/stable/user-guide.html
    """

    BACKEND = 'https://serpapi.com'
    SUPPORTED_DECODER = ['json', 'html', 'object']

    def __init__(self, parameter=None):
        # define default parameter
        if parameter is None:
            self.parameter = {}
        else:
            self.parameter = parameter
        # urllib3 options
        # 60s default
        self.timeout = 60.0
        # no HTTP retry
        self.retries = False
        # override default
        if 'timeout' in parameter:
            self.timeout = parameter['timeout']
        if 'retries' in parameter:
            self.retries = parameter['retries']
        # initialize the http client
        self.http = urllib3.PoolManager()

    def search(self, parameter=None, decoder='json'):
        """
        make search then decode the output
         decoder supported 'json', 'html', 'object'

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
             object if decoder = 'object'
        """
        return self.run(path='/search', decoder=decoder, parameter=parameter)

    def html(self, parameter=None):
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
        return self.run('/search', 'html', parameter)

    def location(self, parameter=None):
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
        return self.run('/locations.json', 'json', parameter)

    def search_archive(self, search_id, decoder='json'):
        """
        Retrieve search results from the Search Archive API

        Parameters:

        """
        path = "/searches/" + str(search_id) + "."
        if decoder in self.SUPPORTED_DECODER:
            if decoder == "object":
                path += "json"
            else:
                path += decoder
        else:
            raise SerpApiException('decoder must be json or html or object')
        return self.run(path, decoder, {})

    def account(self, api_key=None):
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
        return self.run('/account', 'json', self.parameter)

    def run(self, path, decoder='json', parameter=None):
        """
        run HTTP request and decode response using urllib3
         the response is decoded using the selected decoder:
          - html: raw HTML response
          - json: deep dict contains search results
          - object: containing search results as a dynamic object

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
        dict|str|object
        decoded HTTP response
        """
        # set client language
        self.parameter['source'] = 'python'

        # set output type
        if decoder == 'object':
            self.parameter['output'] = 'json'
        else:
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

        # handle HTTP error
        if response.status != 200:
            try:
                raw = response.data.decode('utf-8')
                payload = json.loads(raw)
                raise SerpApiException(payload['error'])
            except Exception as ex:
                raise SerpApiException(raw) from ex

        payload = response.data.decode('utf-8')

        # successful response decoding
        if decoder == 'json':
            return dict(json.loads(payload))

        if decoder == 'html':
            return payload

        if decoder == 'object':
            data = dict(json.loads(payload))
            return self.dict2object(data, 'response')

        raise SerpApiException("invalid decoder: " +
                               decoder + ", available: json, html, object")
