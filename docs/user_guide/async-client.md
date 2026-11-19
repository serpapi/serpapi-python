---
title: "Async Client"
description: "Migrate from Client to AsyncClient, compare their behavior, and run SerpApi searches concurrently with asyncio."
---

# Async Client

`serpapi.AsyncClient` is a version of `serpapi.Client` for programs that use Python's `asyncio`, such as FastAPI or aiohttp applications. It has the same SDK methods and API parameters, with the [transport differences](#differences-from-client) described below. Call its request methods with `await`. While one request waits for a response, your program can run other requests and tasks.

Python's `asyncio` is separate from SerpApi's `async` search parameter, which submits a search to retrieve later. You can use that parameter with either client. See [Async Search Archive](async-search-archive.md).

## Installation

`AsyncClient` requires Python 3.11 or newer and the `async` extra, which installs the [httpx2](https://pypi.org/project/httpx2/) HTTP library:

::::{tab-set}

:::{tab-item} pip

```bash
pip install "serpapi[async]"
```

:::

:::{tab-item} uv project

```bash
uv add "serpapi[async]"
```

:::

:::{tab-item} uv environment

```bash
uv pip install "serpapi[async]"
```

:::

::::

`serpapi.Client` doesn't need the extra. It uses the `requests` library and supports Python 3.6 or newer. If httpx2 isn't installed, creating an `AsyncClient` raises `ImportError` with the command to install the extra:

```text
serpapi.AsyncClient requires Python 3.11 or later and the httpx2 package. Install the async extra with: pip install "serpapi[async]"
```

## First Search

After [setting your API key](getting-started.md#installation), run this example:

```python
import asyncio
import os

import serpapi


async def main():
    async with serpapi.AsyncClient(api_key=os.environ["SERPAPI_KEY"], timeout=20) as client:
        results = await client.search(
            engine="google",
            q="coffee",
            location="Austin, Texas",
        )

    print(results["organic_results"][0]["link"])


asyncio.run(main())
```

`asyncio.run()` starts an event loop and runs `main()` in it. `async with` closes the client's connections at the end of the block. If you can't use `async with`, for example when your application creates the client at startup, call `await client.aclose()` when you no longer need the client.

For JSON responses, the client returns a `serpapi.AsyncSerpResults` object. It is not a subclass of `SerpResults`: both have the same dictionary helpers, but their pagination methods use different protocols. With `output="md"` or `output="html"`, the client returns a string.

The other examples on this page use the same imports.

## Migrating from Sync to Async

You can keep using `Client` for synchronous code; installing the `async` extra does not replace it or remove `requests`. To migrate a call path:

1. Use Python 3.11 or newer and [install `serpapi[async]`](#installation).
2. Replace `Client` with `AsyncClient`, and manage its lifetime with `async with` or `await client.aclose()`.
3. Make the calling function `async def` and add `await` to requests and `next_page()`. Callers of that function must also await it. Replace pagination's `for` with `async for`.
4. Keep API parameters, supported request options, result-field access, and SDK exception handlers. Review [Differences from Client](#differences-from-client) if you customize the HTTP session or rely on transport-specific behavior.

These examples perform the same search and read up to two pages:

::::{tab-set}

:::{tab-item} Before: synchronous

```python
import os

import serpapi


client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)
try:
    results = client.search(engine="google", q="coffee", timeout=(3, 20))
    for page in results.yield_pages(max_pages=2):
        print(len(page.get("organic_results", [])))
finally:
    client.session.close()
```

:::

:::{tab-item} After: asynchronous

```python
import asyncio
import os

import serpapi


async def main():
    async with serpapi.AsyncClient(api_key=os.environ["SERPAPI_KEY"], timeout=20) as client:
        results = await client.search(engine="google", q="coffee", timeout=(3, 20))
        async for page in results.yield_pages(max_pages=2):
            print(len(page.get("organic_results", [])))


asyncio.run(main())
```

:::

::::

Only operations that fetch data need asynchronous calls. Reading `results["organic_results"]`, calling `results.get(...)` or `results.as_dict()`, and formatting results remain synchronous. Keep pagination inside the client's lifetime; it fetches additional pages through that client.

Use `asyncio.run()` at a script's entry point. Inside an async web handler or a notebook with an event loop already running, use `await main()` instead; do not nest `asyncio.run()`. Share an application client within one event loop, finish its requests before closing it, and do not reuse it across separate `asyncio.run()` calls.

Sequential `await` calls still send one request at a time. Use [concurrent searches](#run-searches-at-the-same-time) when requests are independent. If your code polls with `time.sleep()`, replace it with `await asyncio.sleep()` so it doesn't block the event loop. Module helpers such as `serpapi.search()` remain blocking and cannot be made asynchronous by adding `await`; use the client methods below instead.

You do not need to add the API parameter `{"async": True}` to migrate. That parameter controls SerpApi's server-side search jobs, not Python's event loop.

## Methods

Each `Client` method has an `AsyncClient` coroutine with the same name and parameters:

| `Client` | `AsyncClient` |
| --- | --- |
| `client.search(...)` | `await client.search(...)` |
| `client.extract(...)` | `await client.extract(...)` |
| `client.search_archive(...)` | `await client.search_archive(...)` |
| `client.upload_image(...)` | `await client.upload_image(...)` |
| `client.locations(...)` | `await client.locations(...)` |
| `client.account(...)` | `await client.account(...)` |
| `results.next_page()` | `await results.next_page()` |
| `for page in results.yield_pages():` | `async for page in results.yield_pages():` |

Module functions such as `serpapi.search()` use a synchronous client. Create an `AsyncClient` to send asynchronous requests.

This example checks your account while it uploads an image, then searches Google Lens with the uploaded image. Place an image named `image.png` in the directory where you run the script, or replace `image.png` with the path to your file:

```python
async def main():
    async with serpapi.AsyncClient(api_key=os.environ["SERPAPI_KEY"], timeout=30) as client:
        account, upload = await asyncio.gather(
            client.account(),
            client.upload_image("image.png"),
        )
        results = await client.search(
            engine="google_lens",
            image_id=upload["image_id"],
            type="visual_matches",
            hl="en",
        )

    print("Searches left:", account["total_searches_left"])
    for match in results.get("visual_matches", [])[:3]:
        print(match.get("title"))


asyncio.run(main())
```

`asyncio.gather()` runs the account request and the upload at the same time, and returns their results in order.

`upload_image()` reads the image off the event loop. If you pass an open file, it stays yours: the SDK doesn't close it, and cancellation waits for any in-progress read to finish before returning control to you.

## Run Searches at the Same Time

Pass several searches to `asyncio.gather()` to send them at once:

```python
async def main():
    countries = ["us", "gb", "ca"]

    async with serpapi.AsyncClient(api_key=os.environ["SERPAPI_KEY"], timeout=20) as client:
        pages = await asyncio.gather(*(
            client.search(engine="google", q="best coffee beans", gl=country, hl="en")
            for country in countries
        ))

    for country, results in zip(countries, pages):
        organic_results = results.get("organic_results", [])
        first = organic_results[0] if organic_results else {}
        print(country, first.get("title"))


asyncio.run(main())
```

One client can send many requests at once and reuses its connections between them. Share one client rather than creating a client for each search. You can also reuse a base parameter dictionary: async methods don't write per-call overrides or the client's API key back into it.

### Limit Concurrent Searches

`asyncio.gather()` starts every search right away. For a long list of searches, use an `asyncio.Semaphore` to limit how many run at once. This example runs up to two searches at a time and reports failed searches without stopping the others:

```python
async def search_country(client, limit, country):
    async with limit:
        return await client.search(
            engine="google", q="best coffee beans", gl=country, hl="en"
        )


async def main():
    countries = ["us", "gb", "ca", "au", "in"]
    limit = asyncio.Semaphore(2)

    async with serpapi.AsyncClient(api_key=os.environ["SERPAPI_KEY"], timeout=20) as client:
        pages = await asyncio.gather(
            *(search_country(client, limit, country) for country in countries),
            return_exceptions=True,
        )

    for country, results in zip(countries, pages):
        if isinstance(results, Exception):
            print("Failed:", country, results)
        else:
            print("Finished:", country, len(results.get("organic_results", [])))


asyncio.run(main())
```

`return_exceptions=True` makes `gather()` return an exception in place of a failed search's results, so one failure doesn't stop the other searches. Start with a small limit and increase it based on your account's search limits and response times.

Each HTTP connection pool opens up to 100 connections at once by default. With the shared numeric, tuple, or `None` timeout forms, additional requests wait for a free connection without a pool-wait timeout. Distinct proxy or TLS settings use separate pools, so use a semaphore when you need one concurrency limit across all requests.

## Pagination

`next_page()` and `yield_pages()` send requests with the client that made the search, so use them before the client is closed:

```python
async def main():
    async with serpapi.AsyncClient(api_key=os.environ["SERPAPI_KEY"], timeout=20) as client:
        results = await client.search(engine="google", q="coffee", location="Austin, Texas")

        next_results = await results.next_page()
        if next_results:
            print(len(next_results.get("organic_results", [])))

        async for page in results.yield_pages(max_pages=3):
            current = page.get("serpapi_pagination", {}).get("current")
            print(current, len(page.get("organic_results", [])))


asyncio.run(main())
```

`next_page()` returns `None` when there is no next page. Each page's URL comes from the previous page, so `yield_pages()` fetches one page at a time. To fetch several Google pages at once, pass each page's `start` value to `search()` with `asyncio.gather()`. See [Google `start` Offsets](pagination.md#google-start-offsets).

## Request Options

`AsyncClient` accepts the same [request option names](request-options.md) as `Client`: `timeout`, `proxies`, `verify`, `stream`, and `cert`, with the [differences below](#differences-from-client), including buffered responses regardless of `stream`. It uses requests-compatible URL, search-parameter, and form-data encoding. For example, set a default timeout for the client and override it for one search:

```python
async def main():
    async with serpapi.AsyncClient(api_key=os.environ["SERPAPI_KEY"], timeout=20) as client:
        results = await client.search(engine="google", q="coffee", timeout=10)

    print(results["search_metadata"]["status"])


asyncio.run(main())
```

Both constructors accept `api_key` and `timeout`. Pass `proxies`, `verify`, `stream`, and `cert` to individual method calls, not to the constructor.

As with `Client`, a timeout in seconds applies to connecting and to each wait for data, and a `(connect, read)` tuple sets them separately. A per-request `timeout=None` disables the timeout, including a client default. Per-request zero, negative, and boolean timeout values are rejected.

Both clients use certifi's CA bundle by default. They read `REQUESTS_CA_BUNDLE` (or `CURL_CA_BUNDLE` as a fallback) per request; an explicit `verify` path or `verify=False` overrides those variables. `SSL_CERT_FILE` and `SSL_CERT_DIR` do not override certifi. CA bundle files, CA directories, and client certificates supplied as a PEM file or `(cert, key)` pair work with `AsyncClient`.

The async client loads CA bundle and client-certificate contents into an SSL context when an option-specific session is created. If you replace either file at the same path, close the existing `AsyncClient` and create a new one before making another request so the new contents are loaded.

HTTP/HTTPS proxy dictionaries use the same selection rules as `requests`, including credentials in proxy URLs, scheme/host-specific entries, environment proxies, and `NO_PROXY`. A redirect selects the proxy for the new URL without restarting authentication. For example, passing `auth=None` to `AsyncClient.request()` disables session authentication for the entire redirect chain. See [Differences from Client](#differences-from-client) for the remaining transport differences.

## Errors

`AsyncClient` uses the SDK's `HTTPError`, `HTTPConnectionError`, and `TimeoutError` types for HTTP status, connection, and timeout failures, so these handlers can stay the same:

```python
async def main():
    async with serpapi.AsyncClient(api_key=os.environ["SERPAPI_KEY"], timeout=10) as client:
        try:
            results = await client.search(engine="google", q="coffee")
        except serpapi.TimeoutError:
            print("The request timed out.")
        except serpapi.HTTPConnectionError:
            print("Could not connect to SerpApi.")
        except serpapi.HTTPError as exc:
            print(exc.status_code, exc.error)
        else:
            print(results["search_metadata"]["status"])


asyncio.run(main())
```

See [Errors and Timeouts](errors-and-timeouts.md) for what each exception means.

## Event Loops

Use each client in only one event loop. Each `asyncio.run()` call starts a new event loop, so create the client inside the coroutine you pass to `asyncio.run()`, as the examples on this page do. In a long-running application, create one client when the application starts, share it, and close it with `await client.aclose()` when the application stops.

`AsyncClient` runs on `asyncio` only. On another backend, such as Trio, it raises `RuntimeError` before entering the client, sending a request, or starting cleanup.

## Differences from Client

`AsyncClient` sends requests with httpx2 instead of `requests`; it is not a drop-in replacement for a customized `requests.Session`. Both clients retain the same API parameter names, dictionary-style result access, certifi-based default trust, HTTP/HTTPS proxy-selection rules, and common SDK exception types.

| Area | `Client` | `AsyncClient` |
| --- | --- | --- |
| Installation | Base `serpapi` package; Python 3.6+. | `serpapi[async]`; Python 3.11+. |
| Execution and lifetime | Blocking requests; close the underlying session with `client.session.close()`. | Await requests inside one asyncio event loop; use `async with` or `await client.aclose()`. A closed client cannot be reused. |
| Results and pagination | `SerpResults`; `next_page()` and regular iteration. | `AsyncSerpResults`; `await next_page()` and `async for`. Dictionary helpers remain synchronous. |
| HTTP session | `requests.Session`. | `httpx2.AsyncClient`. Requests adapters, hooks, authentication objects, and session customization are not interchangeable. |
| Timeouts | Numbers, `None`, `(connect, read)` tuples, and requests/urllib3 timeout objects. | The same numbers, `None`, and tuples; also native `httpx2.Timeout`, but not requests/urllib3 timeout objects. |
| TLS contexts | Shared options include CA files/directories and client certificates. | Also accepts an `ssl.SSLContext` for `verify`. Load client certificates into that context; combining it with `cert` raises `TypeError`. The context is also used to connect to an HTTPS proxy, which is then offered a client certificate loaded into it. |
| SOCKS proxies | Requires requests' SOCKS dependencies; `socks5://` resolves DNS locally, `socks5h://` at the proxy. | Requires `pip install "httpx2[socks]"` separately. Both schemes resolve DNS at the proxy. Use `socks5h://` for matching behavior. SOCKS4 is unsupported. |
| Connection limits | The default pool cache size is not a hard concurrency limit. | Each pool defaults to at most 100 connections; this is not a global SDK limit. |
| Streaming | `stream` is forwarded to requests, but high-level methods still consume the response before returning results. | `stream` is accepted but ignored. Responses and request bodies are buffered. `upload_image()` reads the file off the event loop; low-level request body preparation is synchronous. |
| Error details | HTTP error responses are `requests.Response` objects. | HTTP error responses are `httpx2.Response` objects. Exception text can differ; blank read/write/pool timeout messages receive a fallback. |

Neither client sets a timeout by default. A numeric or `(connect, read)` timeout is not a total wall-clock deadline, and the async client does not apply those forms to waiting for a free pool connection. Use a native `httpx2.Timeout` if you need a separate pool-wait timeout.

The async client keeps its default pool plus up to 16 cached proxy/TLS/certificate combinations. Further uncached combinations use temporary sessions that close after the request, so they do not reuse connections between requests. Cached entries are not evicted. This bounds the number of cached pools but can reduce performance when rotating through many configurations.

Async `HTTPError` messages omit the `api_key` query parameter. In httpx2 INFO request logs, the SDK redacts `api_key` from the URL it actually sends, including keys supplied by session defaults, authentication, or request hooks. Unrelated httpx2 requests and raw request/response URLs are unchanged; do not log raw URLs containing credentials.

Exceeding the redirect limit raises `requests.exceptions.TooManyRedirects`, invalid compressed content raises `requests.exceptions.ContentDecodingError`, and an unsupported transport protocol raises `requests.exceptions.InvalidSchema`. Other httpx2 HTTP failures can also be caught with `requests.exceptions.RequestException`. This does not cover input validation errors such as a malformed URL.
