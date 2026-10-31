# SerpApi Python Library
[![Package](https://img.shields.io/pypi/v/serpapi?color=green)](https://pypi.org/project/serpapi) [![serpapi-python](https://github.com/serpapi/serpapi-python/actions/workflows/ci.yml/badge.svg)](https://github.com/serpapi/serpapi-python/actions/workflows/ci.yml)

Integrate search data into your AI workflow, RAG / fine-tuning, or Python application using this official [SerpApi Python SDK](https://serpapi.com/integrations/python). 

SerpApi supports Google, Google Maps, Google Shopping, Baidu, Yandex, Yahoo, eBay, App Stores, and [more](https://serpapi.com). 

## Installation

Python 3.6 or later is required.

To install the `serpapi` package, simply run the following command inside your Python virtual environment:

```bash
pip install serpapi
```

> Please note that this package is separate from the legacy `serpapi` module, 
> which is available on PyPi as `google-search-results`. 
> This package is maintained by SerpApi, and is the recommended way to access the 
> SerpApi service from Python.

Both packages use `import serpapi`, so install only one in your environment. See the [migration guide](https://serpapi-python.readthedocs.io/en/latest/user_guide/migrating-from-google-search-results.html) when updating code that uses `google-search-results`.

## Quickstart

[Create a SerpApi account](https://serpapi.com/users/sign_up?plan=free) to get your API key, then store it in an environment variable:

```bash
export SERPAPI_KEY="your_api_key"
```

Environment variables keep secrets out of your source code.
Python accesses these variables from `os.getenv("SERPAPI_KEY")`.

Run a Google search and access the structured results:

```python
import os
from pprint import pprint

import serpapi

client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"))
results = client.search({
    "engine": "google",
    "q": "coffee"
})

pprint(results)
```

The `results` variable contains a dict-like `SerpResults` object. Read fields with `results["organic_results"]` or `results.get("organic_results", [])`.

This example runs a search for "coffee" on Google. See the [playground](https://serpapi.com/playground) to generate your own code.

For Windows setup and instructions to save and run the example, see the [getting-started guide](https://serpapi-python.readthedocs.io/en/latest/user_guide/getting-started.html).

### Error handling

HTTP failures raise `serpapi.HTTPError`. Connection failures raise `serpapi.HTTPConnectionError`, and read timeouts raise `serpapi.TimeoutError`. See the [status and error codes documentation](https://serpapi.com/api-status-and-error-codes) for the meaning of each HTTP status.

```python
import os

import serpapi

# A default timeout can be set here.
client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"), timeout=10)

try:
    results = client.search({
        "engine": "google",
        "q": "coffee",
    })
except serpapi.TimeoutError:
    raise RuntimeError("The request timed out.") from None
except serpapi.HTTPConnectionError:
    raise RuntimeError("Could not connect to SerpApi.") from None
except serpapi.HTTPError as e:
    raise RuntimeError(f"HTTP {e.status_code}: {e.error or 'Request failed'}") from None

if "error" in results:
    raise RuntimeError(results["error"])
```

A successful HTTP response can still contain an `error` field, such as when a search returns no results. Check it before reading result fields. See [Errors and Timeouts](https://serpapi-python.readthedocs.io/en/latest/user_guide/errors-and-timeouts.html) for more examples.

## Features

- **Asynchronous searches** for submitting jobs and retrieving completed results from the Search Archive API.
- **Persistent connections and connection pooling** for reusing HTTP connections across searches.
- Search results as a dict-like **SerpResults** object by default, token-efficient **Markdown** with `"output": "md"`, or raw **search-engine HTML** with `"output": "html"`.
- SDK methods for the [Image API](https://serpapi.com/image-api), [Location API](https://serpapi.com/locations-api), [Search Archive API](https://serpapi.com/search-archive-api), and [Account API](https://serpapi.com/account-api).
- **Content extraction** with `client.extract()` for reading pages, discovering URLs, and crawling websites.
- **Configurable HTTP timeouts** established by setting `timeout` in the client.

## Response formats

Use `search` without `output` for structured results returned as a dict-like `SerpResults` object:

```python
results = client.search({
    "engine": "google",
    "q": "coffee"
})
```

Use `results.as_dict()` when another library needs a plain `dict`, including before calling `json.dumps()`:

```python
data = results.as_dict()
```

Use `md` output for a token-efficient Markdown string optimized for LLMs and AI agents:

```python
markdown = client.search({
    "engine": "google",
    "q": "coffee",
    "output": "md"
})
```

Use `html` output when you need the raw search-engine response as a string:

```python
raw_html = client.search({
    "engine": "google",
    "q": "coffee",
    "output": "html"
})
```

Archived results are also available as Markdown with
`client.search_archive(search_id=search_id, output="md")`.

Learn more about [SerpApi Markdown output](https://serpapi.com/markdown-output).

## Configuration

The client is configured with your API key (and an optional timeout parameter) when you create it:

```python
import os

import serpapi

client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"))
```

| Option | Default | Description |
|--------|---------|-------------|
| `api_key` | `None` | Your SerpApi API key. Use an environment variable rather than committing it to source control. |
| `timeout` | `None` | Connection and read timeout in seconds for each HTTP request. By default no timeout is set, so a request can wait indefinitely. |

Everything else is passed with each call:

| Parameter | Where it goes | Example |
|-----------|---------------|---------|
| `engine`, `q`, and other engine-specific parameters | The dictionary passed to `client.search()` | `{"engine": "google", "q": "coffee"}` |
| `async` | The dictionary passed to `client.search()` | `{"engine": "google", "q": "coffee", "async": True}` |
| `output` | The dictionary passed to `client.search()` | `{"engine": "google", "q": "coffee", "output": "md"}` |
| `search_id`, `output` | Keyword arguments to `client.search_archive()` | `client.search_archive(search_id=search_id, output="md")` |
| `url`, `mode`, `output` | A dictionary or keyword arguments to `client.extract()` | `client.extract(url="https://serpapi.com/", output="md")` |

### Asynchronous searches

Searches wait for their results by default (`async` is `false`). Use `{"async": True}` to submit server-side search jobs and collect their results later from the Search Archive API. Each Python SDK call still waits for its HTTP response and cannot be awaited with `asyncio`.

> **Note:** `async` is a reserved keyword in Python 3.7+, so pass it inside the parameters dictionary (`{"async": True}`) rather than as a keyword argument.

Here is an example of asynchronous searches using Python:

```python
import os
import re
import time
from queue import Queue

import serpapi

company_list = ["meta", "amazon", "apple", "netflix", "google"]
client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"), timeout=30)
schedule_search = Queue()
result = None

for company in company_list:
    result = client.search({"engine": "google", "q": company, "async": True})
    if re.search(r"Cached", result["search_metadata"]["status"]):
        print(f"{company}: search results found in cache for: {company}")

    schedule_search.put(result["search_metadata"]["id"])

print(f"Last search submitted at: {result['search_metadata']['created_at']}")

deadline = time.monotonic() + 120
print("wait 10s for all requests to be completed")
time.sleep(10)

print("wait until all searches are cached or success")
while not schedule_search.empty():
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("Polling timed out before all searches completed.")

    search_id = schedule_search.get()
    search_archived = client.search_archive(
        search_id=search_id, timeout=min(30, remaining)
    )

    company = search_archived["search_parameters"]["q"]
    status = search_archived["search_metadata"]["status"]

    if re.search(r"Cached|Success", status):
        print(f"{company}: search results found in archive for: {company}")
        continue

    if status == "Error":
        print(f"{company}: search failed: {search_archived.get('error')}")
        continue

    schedule_search.put(search_id)
    time.sleep(1)

print("done")
```

This code batches searches into a [queue](https://en.wikipedia.org/wiki/Queue_(abstract_data_type)).
Each search can take a few seconds to complete, so by the time the first ID is popped, its results are usually already in the archive. Searches that are still processing are put back in the queue and checked again.

The client uses a 30-second HTTP timeout. A separate 120-second polling deadline, checked between requests, stops retries with a `TimeoutError` if searches remain unfinished.

## Examples

Here are some examples of our most popular APIs. You can find the full list of supported engines and parameters in our [documentation](https://serpapi.com/search-engine-apis).

### Extract API

Read content from a public URL with `client.extract()`. It supports single-page scraping, URL discovery, and crawling, and sets `engine="extract"` automatically.

Set `output="md"` to get the page's main content as a Markdown string for an AI agent or other text processing:

```python
import os

import serpapi

client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"), timeout=60)
markdown = client.extract(url="https://serpapi.com/", output="md")
print(markdown)
```

JSON is the default output format. It returns a dict-like `SerpResults` object with page information, structured data, links, and Markdown:

```python
results = client.extract(url="https://serpapi.com/")
print(results["page_information"]["title"])
print(results["markdown"])
```

Use `output="html"` to get the retrieved HTML as a string:

```python
html = client.extract(url="https://serpapi.com/", output="html")
```

Use `mode="map"` to discover URLs. Map mode includes sitemap URLs by default. This example sets `include_sitemap=False` to use only the page's links:

```python
results = client.extract(url="https://serpapi.com/", mode="map", include_sitemap=False)
for entry in results["urls"]:
    print(entry["url"])
```

Use `mode="crawl"` to follow links and extract multiple pages:

```python
results = client.extract(
    url="https://serpapi.com/", mode="crawl", max_pages=2, max_depth=1, timeout=180
)
for page in results["pages"]:
    print(page["url"])
    print(page["markdown"])
```

Crawl mode can consume one search credit per successfully extracted page, including the starting page. Set `max_pages` to limit the number of pages.

The `timeout` keyword sets the SDK's HTTP timeout in seconds. To set the Extract API's fetch timeout in milliseconds, put it in the parameter dictionary: `client.extract({"url": "https://serpapi.com/", "timeout": 30000}, timeout=60)`.

[See documentation](https://serpapi.com/extract-api) or the [Python Extract API guide](https://github.com/serpapi/serpapi-python/blob/master/docs/user_guide/extract.md) for more options.

### Google Shopping

Scrape Google Shopping results with product names, prices, ratings, and merchant information.

```python
import os
from pprint import pprint

import serpapi

client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"))
results = client.search({
    "engine": "google_shopping",
    "q": "Macbook M4"
})
shopping_results = results["shopping_results"]
pprint(shopping_results)
```

[See documentation](https://serpapi.com/google-shopping-api)

**Google Shopping Light**

A [light variant](https://serpapi.com/google-shopping-light-api) engine called `google_shopping_light` is also available for faster, lower-cost shopping searches.

### Google Images

Scrape Google Images search results, including image URLs, thumbnails, titles, and source pages.

```python
import os
from pprint import pprint

import serpapi

client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"))
results = client.search({
    "engine": "google_images",
    "q": "coffee",
})
pprint(results)
```

[See documentation](https://serpapi.com/google-images-api)

**Google Images Light**

A [light variant](https://serpapi.com/google-images-light-api) engine called `google_images_light` is also available for faster, lower-cost image searches.

### Google Lens with image URL or upload

Google Lens accepts either a publicly accessible image URL or an uploaded
image. To search by URL, pass the URL directly:

```python
import os
from pprint import pprint

import serpapi

client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"))
results = client.search({
    "engine": "google_lens",
    "url": "https://i.imgur.com/HBrB8p0.png",
})
pprint(results)
```

To search a local image, place a file named `image.png` in your working directory, upload it, and pass its temporary `image_id` to Google Lens:

```python
upload = client.upload_image("image.png")
results = client.search({
    "engine": "google_lens",
    "image_id": upload["image_id"],
})
```

Uploaded images can be JPG/JPEG, PNG, or WebP files up to 500 KB. The returned
`image_id` expires after 10 minutes.

[See Image API documentation](https://serpapi.com/image-api) · [See Google Lens image upload documentation](https://serpapi.com/google-lens-upload-an-image)

### Google Trends

Track search interest over time and compare the popularity of search terms.

```python
import os
from pprint import pprint

import serpapi

client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"))
results = client.search({
    "engine": "google_trends",
    "q": "coffee",
    "data_type": "TIMESERIES"
})
interest_over_time = results["interest_over_time"]
pprint(interest_over_time)
```

[See documentation](https://serpapi.com/google-trends-api)

### Google Flights

Search flight routes, schedules, prices, and booking options.

> Note: The `google_flights` engine does not use `q`.
> Specify route and date parameters such as `departure_id`, `arrival_id`, `outbound_date`, and `return_date`.

```python
import os
from datetime import date, timedelta
from pprint import pprint

import serpapi

client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"))
outbounding = date.today() + timedelta(days=30)
returning = outbounding + timedelta(weeks=2)

results = client.search({
    "engine": "google_flights",
    "departure_id": "LAX",
    "arrival_id": "AUS",
    "outbound_date": outbounding.isoformat(),
    "return_date": returning.isoformat()
})
flights = results.get("best_flights") or results.get("other_flights", [])
pprint(flights)
```

[See documentation](https://serpapi.com/google-flights-api)

### Google AI Mode API

The Google AI Mode API returns AI-generated answers with structured text blocks, references, images, products, and more.

```python
import os
from pprint import pprint

import serpapi

client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"))
results = client.search({
    "engine": "google_ai_mode",
    "q": "best coffee maker"
})
text_blocks = results["text_blocks"]
pprint(text_blocks)
```

[See documentation](https://serpapi.com/google-ai-mode-api)

### Bing Search

Scrape Bing web search results, including organic results, ads, related searches, and more.

```python
import os
from pprint import pprint

import serpapi

client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"))
results = client.search({
    "engine": "bing",
    "q": "coffee"
})
pprint(results)
```

[See documentation](https://serpapi.com/bing-search-api)

### DuckDuckGo Search

Scrape DuckDuckGo search results, including organic results, ads, knowledge graphs, and related searches.

```python
import os
from pprint import pprint

import serpapi

client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"))
results = client.search({
    "engine": "duckduckgo",
    "q": "coffee",
})
pprint(results)
```

[See documentation](https://serpapi.com/duckduckgo-search-api)

### Baidu Search

Scrape Baidu search results, including organic results, answer boxes, and related searches.

```python
import os
from pprint import pprint

import serpapi

client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"))
results = client.search({
    "engine": "baidu",
    "q": "coffee",
})
pprint(results)
```

[See documentation](https://serpapi.com/baidu-search-api)

### Amazon Search

Scrape Amazon product search results, including product names, prices, ratings, reviews, and availability.

> Note: The `amazon` engine uses the `k` parameter for a keyword search, not `q`.

```python
import os
from pprint import pprint

import serpapi

client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"))
results = client.search({
    "engine": "amazon",
    "k": "Coffee",
    "amazon_domain": "amazon.com"
})
organic_results = results["organic_results"]
pprint(organic_results)
```

[See documentation](https://serpapi.com/amazon-search-api)

## Documentation

Documentation is [available on Read the Docs](https://serpapi-python.readthedocs.io/en/latest/).

Change history is [available on GitHub](https://github.com/serpapi/serpapi-python/blob/master/HISTORY.md).

Browse the [SerpApi documentation](https://serpapi.com/search-api) to find supported APIs and parameters, or use the [Playground](https://serpapi.com/playground) to build a request and generate Python code.

Additional SDK resources:

- [Python SDK integration page](https://serpapi.com/integrations/python)
- [AI agent guide](https://serpapi-python.readthedocs.io/en/latest/ai-agents.html)
- [SerpApi llms.txt](https://serpapi.com/llms.txt) for links to each API's Markdown parameter reference
- [SerpApi status](https://serpapi.com/api-metrics)

## License

MIT License.

## Contributing

Contributions are welcome. Make sure to read our [contributing guide](CONTRIBUTING.md).

© 2026 [SerpApi](https://serpapi.com/)
