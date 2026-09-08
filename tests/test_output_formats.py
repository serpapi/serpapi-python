from unittest.mock import Mock

import pytest
import requests

import serpapi


def response(content_type, content):
    response = requests.Response()
    response.status_code = 200
    response.headers["Content-Type"] = f"{content_type}; charset=utf-8"
    response._content = content.encode("utf-8")
    return response


def test_search_json_returns_serp_results():
    client = serpapi.Client(api_key="test-api-key")
    client.session.request = Mock(
        return_value=response(
            "application/json",
            '{"search_metadata": {"id": "search-123"}}',
        )
    )

    result = client.search(engine="google", q="Coffee", output="json")

    assert isinstance(result, serpapi.SerpResults)
    assert result["search_metadata"]["id"] == "search-123"
    assert result.client is client
    _, request_kwargs = client.session.request.call_args
    assert request_kwargs["params"]["output"] == "json"


@pytest.mark.parametrize(
    ("output", "content_type"),
    [
        ("html", "text/html"),
        ("md", "text/markdown"),
    ],
)
def test_search_text_outputs_return_raw_text(output, content_type):
    content = '{"looks": "like JSON"}'
    client = serpapi.Client(api_key="test-api-key")
    client.session.request = Mock(return_value=response(content_type, content))

    result = client.search(engine="google", q="Coffee", output=output)

    assert result == content
    assert isinstance(result, str)
    _, request_kwargs = client.session.request.call_args
    assert request_kwargs["params"]["output"] == output
