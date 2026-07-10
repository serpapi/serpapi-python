---
title: "Request Options"
description: "Pass requests library options such as timeout, proxies, verify, stream, and cert."
guide-section: "Advanced Usage"
---

# Request Options

SerpApi Python separates SerpApi query parameters from options passed to the underlying `requests` library.

SerpApi parameters, such as `engine`, `q`, `location`, `hl`, `gl`, `no_cache`, and `json_restrictor`, are sent to SerpApi as API request parameters. Request options, such as `timeout` and `proxies`, configure the local HTTP request made by the Python client.

## Supported Request Options

The client passes these keyword arguments to `requests.Session.request()`:

| Option | Use |
| --- | --- |
| `timeout` | Override the client timeout for one request. |
| `proxies` | Send the request through HTTP or HTTPS proxies. |
| `verify` | Control TLS certificate verification. |
| `stream` | Ask `requests` to stream the HTTP response. |
| `cert` | Use a client certificate. |

These options are supported by `search()`, `search_archive()`, `account()`, and `locations()`.

## Per-Request Timeout

Set a default timeout when creating the client:

```python
client = serpapi.Client(api_key="secret_api_key", timeout=20)
```

Override it for a single request:

```python
results = client.search(
    engine="google",
    q="coffee",
    timeout=5,
)
```

`timeout=5` is passed to `requests`; it is not sent to SerpApi as a search parameter.

## Proxies

Pass a `requests`-style proxies dictionary:

```python
results = client.search(
    engine="google",
    q="coffee",
    proxies={
        "https": "http://proxy.example.com:8080",
    },
)
```

Keep proxy credentials in environment variables or your secret manager rather than hardcoding them in source files.

## TLS Verification

By default, `requests` verifies TLS certificates. You can pass a custom CA bundle path:

```python
results = client.search(
    engine="google",
    q="coffee",
    verify="/path/to/ca-bundle.pem",
)
```

Only disable verification for controlled local debugging:

```python
results = client.search(
    engine="google",
    q="coffee",
    verify=False,
)
```

Do not use `verify=False` in production code.

## Client Certificates

Pass a client certificate path, or a `(cert, key)` tuple, using `cert`:

```python
results = client.search(
    engine="google",
    q="coffee",
    cert=("/path/to/client-cert.pem", "/path/to/client-key.pem"),
)
```

## Combining Search Parameters and Request Options

Request options can be used alongside normal SerpApi parameters:

```python
results = client.search(
    engine="google",
    q="coffee",
    location="Austin, Texas",
    hl="en",
    gl="us",
    json_restrictor="organic_results[].{title, link}",
    timeout=10,
)
```

The client handles this in two steps:

- `timeout`, `proxies`, `verify`, `stream`, and `cert` are passed to `requests`.
- All remaining keyword arguments are sent to SerpApi as API parameters.

If you pass a parameter dictionary and keyword arguments together, the remaining keyword arguments update the dictionary before the request is sent:

```python
params = {"engine": "google", "q": "coffee"}
results = client.search(params, location="Austin, Texas", timeout=10)
```

In this example, `location` is added to the SerpApi request parameters, while `timeout` is passed to `requests`.

When you want to keep the original dictionary unchanged, pass a copy:

```python
params = {"engine": "google", "q": "coffee"}
results = client.search(params.copy(), location="Austin, Texas")
```
