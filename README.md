# SerpApi Python Library
[![Package](https://img.shields.io/pypi/v/serpapi?color=green)](https://pypi.org/project/serpapi) [![serpapi-python](https://github.com/serpapi/serpapi-python/actions/workflows/ci.yml/badge.svg)](https://github.com/serpapi/serpapi-python/actions/workflows/ci.yml)

Integrate search data into your AI workflow, RAG / fine-tuning, or Python application using this official [SerpApi Python SDK](https://serpapi.com/integrations/python). 

SerpApi supports Google, Google Maps, Google Shopping, Baidu, Yandex, Yahoo, eBay, app stores, and [more](https://serpapi.com).

> See the [full Python SDK documentation](https://serpapi-python.readthedocs.io/en/latest/) for setup, usage guides, and API reference.

## Installation

Python 3.6 or later is required.

To install the `serpapi` package, simply run the following command inside your Python virtual environment:

```bash
pip install serpapi
```

## Quickstart

[Create a SerpApi account](https://serpapi.com/users/sign_up?plan=free) to get your API key, then store it in an environment variable:

```bash
export SERPAPI_KEY="your_api_key"
```

Environment variables keep secrets out of your source code. Read the API key with `os.environ["SERPAPI_KEY"]`. Python raises `KeyError` if the variable is missing.

Run a Google search and access the structured results:

```python
import os

import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])
results = client.search({
    "engine": "google",
    "q": "coffee"
})

print(results)
```

The `results` variable contains a dict-like `SerpResults` object. Read fields with `results["organic_results"]` or `results.get("organic_results", [])`.

This example runs a search for "coffee" on Google. See the [Playground](https://serpapi.com/playground) to generate your own code.

For Windows setup and instructions to save and run the example, see the [getting-started guide](https://serpapi-python.readthedocs.io/en/latest/user_guide/getting-started.html).

### Error handling

HTTP failures raise `serpapi.HTTPError`. Connection failures raise `serpapi.HTTPConnectionError`, and read timeouts raise `serpapi.TimeoutError`. See the [status and error codes documentation](https://serpapi.com/api-status-and-error-codes) for the meaning of each HTTP status.

```python
import os

import serpapi

# A default timeout can be set here.
client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=10)

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

A successful HTTP response can still contain an `error` field, such as when a search returns no results. Check it before reading result fields. See [Errors and timeouts](https://serpapi-python.readthedocs.io/en/latest/user_guide/errors-and-timeouts.html) for more examples.

## Features

- **Asynchronous searches** for submitting jobs and retrieving completed results from the Search Archive API.
- **Persistent connections and connection pooling** for reusing HTTP connections across searches.
- Search results as a dict-like **SerpResults** object by default, token-efficient **Markdown** with `"output": "md"`, or raw **search-engine HTML** with `"output": "html"`.
- SDK methods for the [Image API](https://serpapi.com/image-api), [Location API](https://serpapi.com/locations-api), [Search Archive API](https://serpapi.com/search-archive-api), and [Account API](https://serpapi.com/account-api).
- **Content extraction** with `client.extract()` for reading pages, discovering URLs, and crawling websites.
- **Configurable HTTP timeouts** established by setting `timeout` in the client.

## Migrating from google-search-results

If you use the legacy `google-search-results` package, follow the [migration guide](https://serpapi-python.readthedocs.io/en/latest/user_guide/migrating-from-google-search-results.html) to update your code. Both packages use `import serpapi`, so install only one in your environment.

## Response formats

| Output | Use it for | Returns |
|--------|------------|---------|
| `json` (default) | Reading fields, filtering, or storing results | Dict-like `SerpResults` |
| `md` | Passing content directly to an LLM | Markdown `str` |
| `html` | Inspecting or processing raw HTML | HTML `str` |

Omit `output` or set `output="json"` for JSON:

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

Set `output="md"` for Markdown:

```python
markdown = client.search({
    "engine": "google",
    "q": "coffee",
    "output": "md"
})
```

Set `output="html"` for HTML:

```python
raw_html = client.search({
    "engine": "google",
    "q": "coffee",
    "output": "html"
})
```

Archived results are also available as Markdown with
`client.search_archive(search_id=search_id, output="md")`.

Learn more about [SerpApi Markdown Output](https://serpapi.com/markdown-output).

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `api_key` | `None` | Your SerpApi API key. |
| `timeout` | `None` | Connection and read timeout in seconds. No timeout is set by default. |

### Asynchronous searches

Searches wait for their results by default. Use `{"async": True}` to submit a search job on SerpApi and retrieve its results later from the Search Archive API.

SerpApi's `async` parameter is separate from Python `asyncio`. The SDK methods are synchronous: each call blocks until its HTTP response arrives and cannot be used with `await`.

> **Note:** `async` is a reserved keyword in Python 3.7+, so pass it inside the parameters dictionary (`{"async": True}`) rather than as a keyword argument.

Submit a search and check its status later:

```python
submitted = client.search({
    "engine": "google",
    "q": "coffee",
    "async": True,
})
search_id = submitted["search_metadata"]["id"]

# Retrieve later; the search may still be processing.
results = client.search_archive(search_id=search_id)
print(results["search_metadata"]["status"])
```

If the search is still processing, retrieve it again later. See the [async search guide](https://serpapi-python.readthedocs.io/en/latest/user_guide/async-search-archive.html) for polling with HTTP timeouts and a deadline.

## Examples

Here are some examples of our most popular APIs. You can find the full list of supported engines and parameters in our [documentation](https://serpapi.com/search-engine-apis).

### Google Shopping

Scrape Google Shopping results with product names, prices, ratings, and merchant information.

```python
import os

import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])
results = client.search({
    "engine": "google_shopping",
    "q": "Macbook M4"
})
shopping_results = results["shopping_results"]
print(shopping_results)
```

[See documentation](https://serpapi.com/google-shopping-api)

**Google Shopping Light**

A [light variant](https://serpapi.com/google-shopping-light-api) engine called `google_shopping_light` is also available for faster, lower-cost shopping searches.

### Google Images

Scrape Google Images search results, including image URLs, thumbnails, titles, and source pages.

```python
import os

import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])
results = client.search({
    "engine": "google_images",
    "q": "coffee",
})
print(results)
```

[See documentation](https://serpapi.com/google-images-api)

**Google Images Light**

A [light variant](https://serpapi.com/google-images-light-api) engine called `google_images_light` is also available for faster, lower-cost image searches.

### Extract API

Extract page content from a public URL as Markdown for an LLM:

```python
import os

import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"], timeout=60)
markdown = client.extract(url="https://serpapi.com/", output="md")
print(markdown)
```

Omit `output` or set `output="json"` for a dict-like `SerpResults` object with structured page data and Markdown. Use `output="html"` for HTML as a string.

For URL discovery and crawling, see [Map Mode](https://github.com/serpapi/serpapi-python/blob/master/docs/user_guide/extract.md#discover-urls) and [Crawl Mode](https://github.com/serpapi/serpapi-python/blob/master/docs/user_guide/extract.md#crawl-multiple-pages) in the Python guide.

[See documentation](https://serpapi.com/extract-api)

### Google Lens with image URL or upload

Google Lens accepts either a publicly accessible image URL or an uploaded
image. To search by URL, pass the URL directly:

```python
import os

import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])
results = client.search({
    "engine": "google_lens",
    "url": "https://i.imgur.com/HBrB8p0.png",
})
print(results)
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

import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])
results = client.search({
    "engine": "google_trends",
    "q": "coffee",
    "data_type": "TIMESERIES"
})
interest_over_time = results["interest_over_time"]
print(interest_over_time)
```

[See documentation](https://serpapi.com/google-trends-api)

### Google Flights

Search flight routes, schedules, prices, and booking options.

> Note: The `google_flights` engine does not use `q`.
> Specify route and date parameters such as `departure_id`, `arrival_id`, `outbound_date`, and `return_date`.

```python
import os
from datetime import date, timedelta

import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])
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
print(flights)
```

[See documentation](https://serpapi.com/google-flights-api)

### Google AI Mode API

The Google AI Mode API returns AI-generated answers with structured text blocks, references, images, products, and more.

```python
import os

import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])
results = client.search({
    "engine": "google_ai_mode",
    "q": "best coffee maker"
})
text_blocks = results["text_blocks"]
print(text_blocks)
```

[See documentation](https://serpapi.com/google-ai-mode-api)

### Bing Search

Scrape Bing web search results, including organic results, ads, related searches, and more.

```python
import os

import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])
results = client.search({
    "engine": "bing",
    "q": "coffee"
})
print(results)
```

[See documentation](https://serpapi.com/bing-search-api)

### DuckDuckGo Search

Scrape DuckDuckGo search results, including organic results, ads, knowledge graphs, and related searches.

```python
import os

import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])
results = client.search({
    "engine": "duckduckgo",
    "q": "coffee",
})
print(results)
```

[See documentation](https://serpapi.com/duckduckgo-search-api)

### Baidu Search

Scrape Baidu search results, including organic results, answer boxes, and related searches.

```python
import os

import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])
results = client.search({
    "engine": "baidu",
    "q": "coffee",
})
print(results)
```

[See documentation](https://serpapi.com/baidu-search-api)

### Amazon Search

Scrape Amazon product search results, including product names, prices, ratings, reviews, and availability.

> Note: The `amazon` engine uses the `k` parameter for a keyword search, not `q`.

```python
import os

import serpapi

client = serpapi.Client(api_key=os.environ["SERPAPI_KEY"])
results = client.search({
    "engine": "amazon",
    "k": "Coffee",
    "amazon_domain": "amazon.com"
})
organic_results = results["organic_results"]
print(organic_results)
```

[See documentation](https://serpapi.com/amazon-search-api)

## More resources

- [Python SDK documentation](https://serpapi-python.readthedocs.io/en/latest/) for setup, usage, and examples
- [SerpApi documentation](https://serpapi.com/search-api) for supported APIs and parameters
- [SerpApi status](https://serpapi.com/api-metrics) for API success rates and response times

### Playground

Build and test your request in the **[Playground](https://serpapi.com/playground)**, then generate Python code.

### For agents

- [AI agent guide](https://serpapi-python.readthedocs.io/en/latest/ai-agents.html) for using the Python SDK with AI agents
- [SerpApi llms.txt](https://serpapi.com/llms.txt) for links to each API's Markdown parameter reference

## License

MIT License.

## Contributing

Contributions are welcome. Make sure to read our [contributing guide](CONTRIBUTING.md).

© 2026 [SerpApi](https://serpapi.com/)
