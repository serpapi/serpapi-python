---
title: "Asyncio Client"
description: "Run concurrent SerpApi requests with AsyncClient and asyncio."
---

# Asyncio Client

`serpapi.AsyncClient` provides non-blocking versions of the SDK methods for
applications that use Python's `asyncio` event loop. This is separate from the
[Async Search Archive](async-search-archive.md), which is a SerpApi API feature
for retrieving a search after the server finishes processing it.

## Create and Close a Client

Use an async context manager so the connection pool is always closed:

```python
import asyncio
import os

import serpapi


async def main():
    async with serpapi.AsyncClient(
        api_key=os.environ["SERPAPI_KEY"],
        timeout=20,
    ) as client:
        results = await client.search(engine="google", q="coffee")
        print(results["search_metadata"]["id"])


asyncio.run(main())
```

When a context manager does not fit the application lifecycle, call
`await client.aclose()` during shutdown. Create one client per event loop and
reuse it instead of constructing a client for every request.

## Run Independent Searches Concurrently

`asyncio.gather()` lets other requests make progress while one request waits
for network I/O:

```python
async def search_many(client):
    return await asyncio.gather(
        client.search(engine="google", q="coffee"),
        client.search(engine="google", q="tea"),
        client.search(engine="google", q="pizza"),
    )
```

Concurrency improves throughput for independent I/O-bound requests. It does
not make one search finish faster, and each call still consumes a search from
the account.

## Other Async Methods

The async client supports the same endpoint parameters and response formats as
the synchronous client:

```python
async def inspect_account(client):
    account = await client.account()
    locations = await client.locations(q="Austin", limit=3)
    archived = await client.search_archive(search_id="search-id")
    upload = await client.upload_image("image.png")
    return account, locations, archived, upload
```

The example above is an illustrative fragment and assumes it runs inside the
same async function and client context as the first example.

## Async Pagination

JSON search responses are `AsyncSerpResults` objects. Fetch one more page with
`await`, or iterate through several pages with `async for`:

```python
async def read_pages(results):
    next_page = await results.next_page()

    async for page in results.yield_pages(max_pages=5):
        for item in page.get("organic_results", []):
            print(item.get("title"))

    return next_page
```

## Error Handling

Async methods raise the same SerpApi exceptions as synchronous methods:

```python
async def safe_search(client):
    try:
        return await client.search(engine="google", q="coffee")
    except serpapi.TimeoutError:
        print("The request timed out.")
    except serpapi.HTTPConnectionError:
        print("Could not connect to SerpApi.")
    except serpapi.HTTPError as exc:
        print(exc.status_code, exc.error)
```

See [Errors and Timeouts](errors-and-timeouts.md) and
[Request Options](request-options.md) for shared configuration details.
