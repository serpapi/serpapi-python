import json
from unittest.mock import Mock

import pytest
import requests

import serpapi


@pytest.mark.parametrize(
    ("max_pages", "available_pages", "expected_pages"),
    [(1, 3, 1), (2, 3, 2), (3, 3, 3), (5, 3, 3), (5, 1, 1), (0, 3, 0)],
)
def test_yield_pages_does_not_request_unused_pages(
    max_pages, available_pages, expected_pages
):
    responses = []
    for page_number in range(1, available_pages + 1):
        data = {"search_information": {"page_number": page_number}}
        if page_number < available_pages:
            data["serpapi_pagination"] = {
                "next": f"https://serpapi.com/search?engine=google&q=Coffee&start={page_number * 10}"
            }
        response = requests.Response()
        response.status_code = 200
        response.headers["Content-Type"] = "application/json"
        response._content = json.dumps(data).encode("utf-8")
        responses.append(response)

    client = serpapi.Client(api_key="test-api-key")
    client.session.request = Mock(side_effect=responses)
    results = client.search(engine="google", q="Coffee")

    pages = list(results.yield_pages(max_pages=max_pages))

    assert [page["search_information"]["page_number"] for page in pages] == list(
        range(1, expected_pages + 1)
    )
    assert client.session.request.call_count == max(1, expected_pages)
