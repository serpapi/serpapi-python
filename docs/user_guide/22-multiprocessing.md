---
title: "Multiprocessing"
description: "Parallelize CPU-heavy or isolated SerpApi workloads with ProcessPoolExecutor."
guide-section: "Advanced Usage"
---

# Multiprocessing

Use multiprocessing when each search has heavy CPU-bound post-processing, when you need process isolation, or when your worker code already runs in a process pool. For simple network-bound searches, threads are usually lighter.

## ProcessPoolExecutor Example

```python
import os
import serpapi

from concurrent.futures import ProcessPoolExecutor, as_completed


def search_country(country):
    client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)
    results = client.search({
        "engine": "google",
        "q": "best coffee beans",
        "gl": country,
        "hl": "en",
    })

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

The `if __name__ == "__main__"` guard is important for multiprocessing, especially on macOS and Windows.

## Practical Guidance

- Create the `serpapi.Client` inside the worker process.
- Return plain serializable data such as dictionaries, lists, strings, and numbers.
- Avoid passing open sessions, response objects, or client instances between processes.
- Set explicit timeouts.
- Prefer threading for simple concurrent HTTP requests unless CPU-heavy work makes multiprocessing worthwhile.

## Combining Pagination and Processes

For Google Search, independent `start` offsets can be distributed across workers:

```python
def search_offset(start):
    client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=20)
    results = client.search({
        "engine": "google",
        "q": "coffee",
        "location": "Austin, Texas",
        "start": start,
    })
    return results.get("organic_results", [])
```

Check the relevant engine docs before parallelizing offsets because pagination parameters vary by engine.

