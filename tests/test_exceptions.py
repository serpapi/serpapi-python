import pytest
from unittest.mock import Mock, patch
import requests
import serpapi


def test_http_error():
    """Ensure that an HTTPError has the correct status code and error."""
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.json.return_value = { "error": "Invalid API key" }
    
    requests_error = requests.exceptions.HTTPError(response=mock_response, request=Mock())
    http_error = serpapi.HTTPError(requests_error)
        
    assert http_error.status_code == 401
    assert http_error.error == "Invalid API key"
    assert http_error.response == mock_response