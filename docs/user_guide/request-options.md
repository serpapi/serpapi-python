---
title: "Request Options"
description: "Configure HTTPX timeouts, proxies, TLS verification, streaming compatibility, and client certificates."
---

# Request Options

Search parameters such as `engine`, `q`, `location`, `hl`, `gl`, `no_cache`,
and `json_restrictor` tell SerpApi what to search for and return. Request
options control how the Python client connects to SerpApi through HTTPX.

The examples use a client created as shown in [Client Usage](client-usage.md#create-a-client).

## Supported Request Options

The synchronous and asynchronous clients accept these options on `search()`,
`search_archive()`, `account()`, `locations()`, and `upload_image()`:

| Option | Use |
| --- | --- |
| `timeout` | Set a different timeout, in seconds, for one request. |
| `proxies` | Use a requests-style mapping of protocols to proxy URLs. |
| `verify` | Check the server's TLS certificate, disable verification, or use a custom CA bundle. |
| `stream` | Accepted for backward compatibility; SDK methods still fully read responses. |
| `cert` | Authenticate the request with a client certificate. |

HTTPX configures proxies and TLS on client instances rather than individual
requests. The SDK keeps the options above compatible by creating a scoped
HTTPX client when a request overrides those settings. Configure them on the
SerpApi client when several requests share the same settings so the connection
pool can be reused.

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

The same options work with `AsyncClient`. See [Errors and Timeouts](errors-and-timeouts.md#connection-errors-and-timeouts) for timeout behavior.

## Proxies

For connection reuse, set one proxy when constructing the client:

<!-- docs-test: skip uses an example proxy host -->
```python
client = serpapi.Client(
    api_key="secret_api_key",
    proxy="http://proxy.example.com:8080",
)
results = client.search(engine="google", q="coffee")
```

Existing requests-style per-call mappings remain supported:

<!-- docs-test: skip uses an example proxy host -->
```python
results = client.search(
    engine="google",
    q="coffee",
    proxies={"https": "http://proxy.example.com:8080"},
)
```

Keep proxy credentials in environment variables or a secret manager rather
than hardcoding them in source files.

## TLS Verification

By default, HTTPX checks the server's TLS certificate. If your network uses a
private certificate authority, configure its trusted bundle on the client:

<!-- docs-test: skip uses an example CA bundle path -->
```python
client = serpapi.Client(
    api_key="secret_api_key",
    verify="/path/to/ca-bundle.pem",
)
```

Only disable verification for controlled local debugging:

<!-- docs-test: skip intentionally disables TLS verification -->
```python
results = client.search(engine="google", q="coffee", verify=False)
```

Do not use `verify=False` in production code.

## Client Certificates

Some servers or proxies require a certificate to identify the client. Pass its
file path or a `(certificate, key)` pair when constructing the client:

<!-- docs-test: skip uses example client certificate paths -->
```python
client = serpapi.Client(
    api_key="secret_api_key",
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
    timeout=10,
)
```

The SDK sends `timeout`, `proxies`, `verify`, `stream`, and `cert` to its HTTP
compatibility layer. All remaining keyword arguments are SerpApi parameters.

If you pass a parameter dictionary and keyword arguments together, the keyword
parameters update that dictionary, preserving the existing SDK behavior:

```python
params = {"engine": "google", "q": "coffee"}
results = client.search(params, location="Austin, Texas", timeout=10)
```

Pass `params.copy()` when the original dictionary must remain unchanged.
