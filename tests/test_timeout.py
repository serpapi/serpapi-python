import pytest
import requests
from serpapi import Client

def test_client_timeout_setting():
    """Test that timeout can be set on the client and is passed to the request."""
    client = Client(api_key="test_key", timeout=10)
    assert client.timeout == 10

def test_request_timeout_override(monkeypatch):
    """Test that timeout can be overridden in the search method."""
    client = Client(api_key="test_key", timeout=10)
    
    def mock_request(method, url, params, headers, timeout, **kwargs):
        assert timeout == 5
        # Return a mock response object
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = b'{"search_metadata": {"id": "123"}}'
        return mock_response

    monkeypatch.setattr(client.session, "request", mock_request)
    
    client.search(q="coffee", timeout=5)

def test_request_default_timeout(monkeypatch):
    """Test that the client's default timeout is used if none is provided in search."""
    client = Client(api_key="test_key", timeout=10)
    
    def mock_request(method, url, params, headers, timeout, **kwargs):
        assert timeout == 10
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = b'{"search_metadata": {"id": "123"}}'
        return mock_response

    monkeypatch.setattr(client.session, "request", mock_request)
    
    client.search(q="coffee")
