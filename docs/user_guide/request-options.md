---
title: "Request Options"
description: "Pass requests library options such as timeout, proxies, verify, stream, and cert."
---

# Request Options

Search parameters such as `engine`, `q`, `location`, `hl`, `gl`, `no_cache`, and `json_restrictor` tell SerpApi what to search for and return. Request options such as `timeout` and `proxies` control how your Python program connects to SerpApi through the `requests` library.

The examples use a client created as shown in [Client Usage](client-usage.md#create-a-client).

## Supported Request Options

The client passes these keyword arguments to `requests.Session.request()`:

| Option | Use |
| --- | --- |
| `timeout` | Set a different timeout, in seconds, for one request. |
| `proxies` | Send the request through HTTP or HTTPS proxies. |
| `verify` | Check the server's TLS certificate, or use a custom certificate authority bundle. |
| `stream` | Set the `requests` streaming option. The client still reads the response before returning results. |
| `cert` | Authenticate the request with a client certificate. |

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

`timeout=5` sets the connection and read timeout to five seconds. It is passed to `requests`. See [Errors and Timeouts](errors-and-timeouts.md#connection-errors-and-timeouts) for timeout behavior.

## Proxies

To connect through a proxy server, pass a dictionary that maps the request protocol to the proxy URL:

<!-- docs-test: skip uses an example proxy host -->
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

By default, `requests` checks the server's TLS certificate to verify its identity. If your network uses a private certificate authority (CA), pass the path to its trusted certificate bundle:

<!-- docs-test: skip uses an example CA bundle path -->
```python
results = client.search(
    engine="google",
    q="coffee",
    verify="/path/to/ca-bundle.pem",
)
```

Only disable verification for controlled local debugging:

<!-- docs-test: skip intentionally disables TLS verification -->
```python
results = client.search(
    engine="google",
    q="coffee",
    verify=False,
)
```

Do not use `verify=False` in production code.

## Client Certificates

Some servers or proxies require a certificate to identify the client. Pass its file path with `cert`, or pass a `(cert, key)` tuple if the certificate and private key are in separate files:

<!-- docs-test: skip uses example client certificate paths -->
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

The client sends the arguments to two places:

- `timeout`, `proxies`, `verify`, `stream`, and `cert` are passed to `requests`.
- All remaining keyword arguments are sent to SerpApi as API parameters.

If you pass a parameter dictionary and keyword arguments together, the search parameters in the keyword arguments update your dictionary:

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
