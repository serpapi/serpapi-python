---
title: "Multiprocessing"
description: "Run searches in separate Python processes with ProcessPoolExecutor."
---

# Multiprocessing

Multiprocessing runs work in separate Python processes. Use it when you do substantial computation on each search response, need separate process memory, or already use a process pool in your application. [Threads](threading.md) have less startup overhead for searches that mainly wait for network responses.

## ProcessPoolExecutor Example

After [setting your API key](getting-started.md#installation), save this example in a Python file and run it from your terminal. `max_workers=4` allows up to four worker processes. Each worker creates its own client and returns a dictionary with selected results.

```python
import os
import serpapi

from concurrent.futures import ProcessPoolExecutor, as_completed


def search_country(country):
    client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)
    results = client.search(
        engine="google",
        q="best coffee beans",
        gl=country,
        hl="en",
    )

    organic_results = results.get("organic_results", [])
    return {
        "country": country,
        "count": len(organic_results),
        "first_title": organic_results[0].get("title") if organic_results else None,
    }


if __name__ == "__main__":
    countries = ["us", "gb", "ca", "au", "in"]

    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(search_country, country) for country in countries]

        for future in as_completed(futures):
            print(future.result())
```

Keep `if __name__ == "__main__":` around the code that starts the pool. When a new worker imports the file, this guard prevents it from starting another pool. It is required when workers start this way, as they do by default on macOS and Windows.

## Practical Guidance

- Create the `serpapi.Client` inside the worker process.
- Return data that Python can copy between processes, such as dictionaries, lists, strings, and numbers.
- Avoid passing open sessions, response objects, or client instances between processes.
- Set a timeout on each client so a stalled request does not wait indefinitely.
- Use threads if your workers only make searches and read a few fields from the response.

## Combining Pagination and Processes

You can submit a different Google `start` offset to each worker. Here is a worker function that fetches one range of results:

```python
def search_offset(start):
    client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)
    results = client.search(
        engine="google",
        q="coffee",
        location="Austin, Texas",
        start=start,
    )
    return results.get("organic_results", [])
```

Use the [pagination parameters](pagination.md#pagination-parameters-vary-by-engine) for the engine you are searching. Other engines may require a token from the previous page to request the next one.
