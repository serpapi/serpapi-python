# SerpApi Python Library & Package
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

## Quickstart

[Create a SerpApi account](https://serpapi.com/users/sign_up?plan=free) to get your API key, then store it in an environment variable:

```bash
export SERPAPI_KEY="your_api_key"
```

Environment variables keep secrets out of your source code.
Python accesses these variables from `os.getenv("SERPAPI_KEY")`.

Run a Google search and access the results as a Python `dict`:

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

The `results` variable now contains a `SerpResults` object, which acts just like a `dict`, with some convenient functions added on top.

This example runs a search for "coffee" on Google. See the [playground](https://serpapi.com/playground) to generate your own code.

### Error handling

Unsuccessful requests raise `serpapi.HTTPError` or `serpapi.TimeoutError` exceptions. The returned status code will reflect the sort of error that occurred, please refer to [Status and Error Codes Documentation](https://serpapi.com/api-status-and-error-codes) for more details.

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
except serpapi.HTTPError as e:
    if e.status_code == 401: # Invalid API key
        print(e.error) # "Invalid API key. Your API key should be here: https://serpapi.com/manage-api-key"
    elif e.status_code == 400: # Missing required parameter
        pass
    elif e.status_code == 429: # Exceeds the hourly throughput limit OR the account has run out of searches
        pass
except serpapi.TimeoutError as e:
    # Handle timeout
    print(f"The request timed out: {e}")
```

## Features

- **Asynchronous searches** for submitting non-blocking jobs and retrieving completed results from the Search Archive API.
- **Persistent connections and connection pooling** for reusing HTTP connections across searches.
- Search results as **Python dict** with `search`, token-efficient **Markdown** with `md`, or raw **search-engine HTML** with `html`.
- SDK methods for the [Image API](https://serpapi.com/image-api), [Location API](https://serpapi.com/locations-api), [Search Archive API](https://serpapi.com/search-archive-api), and [Account API](https://serpapi.com/account-api).
- **Configurable HTTP timeouts** established by setting `timeout` in the client.

## Response formats

Use `search` and default output (none) for structured results decoded into a `dict`:

```python
results = client.search({
    "engine": "google",
    "q": "coffee"
})
```

Use `md` output for a token-efficient Markdown string optimized for LLMs and AI agents:

```python
markdown = client.search({
    "engine": "google",
    "q": "coffee",
    "output": "md"
})
```

Use `html` output when you need the raw search-engine response:

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
| `timeout` | `None` | Timeout in seconds for each HTTP request. By default no timeout is set, so a request can wait indefinitely. |

Everything else is passed with each call:

| Parameter | Where it goes | Example |
|-----------|---------------|---------|
| `engine`, `q`, and other engine-specific parameters | The dictionary passed to `client.search()` | `{"engine": "google", "q": "coffee"}` |
| `async` | The dictionary passed to `client.search()` | `{"engine": "google", "q": "coffee", "async": True}` |
| `output` | The dictionary passed to `client.search()` | `{"engine": "google", "q": "coffee", "output": "md"}` |
| `search_id`, `output` | Keyword arguments to `client.search_archive()` | `client.search_archive(search_id=search_id, output="md")` |

The client has no default `engine` or `async` setting, so include them in every search. 

### Search asynchronously

Use `{"async": True}` to submit searches without waiting for them to complete.

- **Non-blocking** (`{"async": True}`): a single process can submit many searches and collect the results later from the Search Archive API. The code is more complex because you have to track search IDs and check their status.
- **Blocking** (`{"async": False}`, the default): each call waits for its results before returning, which keeps the code simple. 

> **Note:** `async` is a reserved keyword in Python 3.7+, so pass it inside the parameters dictionary (`{"async": True}`) rather than as a keyword argument.

Here is an example of asynchronous searches using Python:

```python
import os
import re
import time
from queue import Queue

import serpapi

company_list = ["meta", "amazon", "apple", "netflix", "google"]
client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"))
schedule_search = Queue()
result = None

for company in company_list:
    result = client.search({"engine": "google", "q": company, "async": True})
    if re.search(r"Cached", result["search_metadata"]["status"]):
        print(f"{company}: search results found in cache for: {company}")

    schedule_search.put(result["search_metadata"]["id"])

print(f"Last search submitted at: {result['search_metadata']['created_at']}")

print("wait 10s for all requests to be completed")
time.sleep(10)

print("wait until all searches are cached or success")
while not schedule_search.empty():
    search_id = schedule_search.get()

    search_archived = client.search_archive(search_id=search_id)

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

## Basic examples in Python

Here are some examples of our most popular APIs. You can find the full list of supported engines and parameters in our [documentation](https://serpapi.com/search-engine-apis).

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
outbounding = date.today()
returning = outbounding + timedelta(weeks=2)

results = client.search({
    "engine": "google_flights",
    "departure_id": "LAX",
    "arrival_id": "AUS",
    "outbound_date": outbounding,
    "return_date": returning
})
best_flights = results["best_flights"]
pprint(best_flights)
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

### Search Bing

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

### Search DuckDuckGo

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

### Search Baidu

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

## License

MIT License.

## Contributing

Contributions are welcome. Make sure to read our [contributing guide](CONTRIBUTING.md).

© 2026 [SerpApi](https://serpapi.com/)