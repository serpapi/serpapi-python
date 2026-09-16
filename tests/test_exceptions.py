import httpx

import serpapi


def test_http_error():
    """Ensure that an HTTPError has the correct status code and error."""
    request = httpx.Request("GET", "https://serpapi.com/account.json")
    response = httpx.Response(
        401,
        json={"error": "Invalid API key"},
        request=request,
    )
    original = httpx.HTTPStatusError(
        "401 Unauthorized",
        request=request,
        response=response,
    )
    http_error = serpapi.HTTPError(original)

    assert http_error.status_code == 401
    assert http_error.error == "Invalid API key"
    assert http_error.response == response
    assert http_error.request == request
    assert isinstance(http_error, httpx.HTTPError)
