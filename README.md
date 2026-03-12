# SerpApi Python Library & Package
[![Package](https://badge.fury.io/py/serpapi.svg)](https://pypi.org/project/serpapi) [![serpapi-python](https://github.com/serpapi/serpapi-python/actions/workflows/ci.yml/badge.svg)](https://github.com/serpapi/serpapi-python/actions/workflows/ci.yml)

Integrate search data into your AI workflow, RAG / fine-tuning, or Python application using this official wrapper for [SerpApi](https://serpapi.com). 

SerpApi supports Google, Google Maps, Google Shopping, Baidu, Yandex, Yahoo, eBay, App Stores, and [more](https://serpapi.com). 

Query a vast range of data at scale, including web search results, flight schedules, stock market data, news headlines, and [more](https://serpapi.com).

## Installation

To install the `serpapi` package, simply run the following command:

```bash
$ pip install serpapi
```

Please note that this package is separate from the legacy `serpapi` module, which is available on PyPi as `google-search-results`. This package is maintained by SerpApi, and is the recommended way to access the SerpApi service from Python.

## Simple Usage

Let's start by searching for Coffee on Google:

```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"))
results = client.search({
  "engine": "google",
  "q": "coffee"
})

print(results)
```

The `results` variable now contains a `SerpResults` object, which acts just like a standard dictionary, with some convenient functions added on top.

This example runs a search for "coffee" on Google. It then returns the results as a regular Python Hash.
 See the [playground](https://serpapi.com/playground) to generate your own code.

The SerpApi key can be obtained from [serpapi.com/signup](https://serpapi.com/users/sign_up?plan=free).

Environment variables are a secure, safe, and easy way to manage secrets.
 Set `export SERPAPI_KEY=<secret_serpapi_key>` in your shell.
 Python accesses these variables from `os.environ["SERPAPI_KEY"]`.

### Error handling

Unsuccessful requests raise `serpapi.HTTPError` or `serpapi.TimeoutError` exceptions. The returned status code will reflect the sort of error that occurred, please refer to [Status and Error Codes Documentation](https://serpapi.com/api-status-and-error-codes) for more details.

```python
import os
import serpapi

# A default timeout can be set here.
client = serpapi.Client(api_key=os.getenv("API_KEY"), timeout=10)

try:
    results = client.search({
        'engine': 'google',
        'q': 'coffee',
    })
except serpapi.HTTPError as e:
    if e.status_code == 401: # Invalid API key
        print(e.error) # "Invalid API key. Your API key should be here: https://serpapi.com/manage-api-key"
    elif e.status_code == 400: # Missing required parameter
        pass
    elif e.status_code == 429: # Exceeds the hourly throughput limit OR account run out of searches
        pass
except serpapi.TimeoutError as e:
    # Handle timeout
    print(f"The request timed out: {e}")
```

## Documentation

Documentation is [available on Read the Docs](https://serpapi-python.readthedocs.io/en/latest/).

Change history is [available on GitHub](https://github.com/serpapi/serpapi-python/blob/master/HISTORY.md).

## Basic Examples in Python

### Search Bing
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'bing',
    'q': 'coffee'
})
```
- API Documentation: [serpapi.com/bing-search-api](https://serpapi.com/bing-search-api)

### Search Baidu
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'baidu',
    'q': 'coffee',
})
```
- API Documentation: [serpapi.com/baidu-search-api](https://serpapi.com/baidu-search-api)

### Search Yahoo
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'yahoo',
    'p': 'coffee',
})
```
- API Documentation: [serpapi.com/yahoo-search-api](https://serpapi.com/yahoo-search-api)

### Search YouTube
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'youtube',
    'search_query': 'coffee',
})
```
- API Documentation: [serpapi.com/youtube-search-api](https://serpapi.com/youtube-search-api)

### Search Walmart
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'walmart',
    'query': 'coffee',
})
```
- API Documentation: [serpapi.com/walmart-search-api](https://serpapi.com/walmart-search-api)

### Search eBay
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'ebay',
    '_nkw': 'coffee',
})
```
- API Documentation: [serpapi.com/ebay-search-api](https://serpapi.com/ebay-search-api)

### Search Naver
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'naver',
    'query': 'coffee',
})
```
- API Documentation: [serpapi.com/naver-search-api](https://serpapi.com/naver-search-api)

### Search Home Depot
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'home_depot',
    'q': 'table',
})
```
- API Documentation: [serpapi.com/home-depot-search-api](https://serpapi.com/home-depot-search-api)

### Search Apple App Store
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'apple_app_store',
    'term': 'coffee',
})
```
- API Documentation: [serpapi.com/apple-app-store](https://serpapi.com/apple-app-store)

### Search DuckDuckGo
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'duckduckgo',
    'q': 'coffee',
})
```
- API Documentation: [serpapi.com/duckduckgo-search-api](https://serpapi.com/duckduckgo-search-api)

### Search Google
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'google',
    'q': 'coffee'
})
```
- API Documentation: [serpapi.com/search-api](https://serpapi.com/search-api)

### Search Google Scholar
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'google_scholar',
    'q': 'coffee',
})
```
- API Documentation: [serpapi.com/google-scholar-api](https://serpapi.com/google-scholar-api)

### Search Google Autocomplete
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'google_autocomplete',
    'q': 'coffee',
})
```
- API Documentation: [serpapi.com/google-autocomplete-api](https://serpapi.com/google-autocomplete-api)

### Search Google Immersive Product
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'google_immersive_product',
    'page_token': 'eyJlaSI6Im5ZVmxaOXVVTDY2X3A4NFBqTnZELUFjIiwicHJvZHVjdGlkIjoiIiwiY2F0YWxvZ2lkIjoiNTE1NDU2NTc1NTc5MzcxMDY3NSIsImhlYWRsaW5lT2ZmZXJEb2NpZCI6IjI1MDkyMjcwMDUzMjk2NzQwODMiLCJpbWFnZURvY2lkIjoiMTYzOTg5MjU0MDcwMDU4MDA1NTQiLCJyZHMiOiJQQ18zNDg4MDE0MTg3ODgxNzc5NjU0fFBST0RfUENfMzQ4ODAxNDE4Nzg4MTc3OTY1NCIsInF1ZXJ5IjoibGcrdHYiLCJncGNpZCI6IjM0ODgwMTQxODc4ODE3Nzk2NTQiLCJtaWQiOiI1NzY0NjI3ODM3Nzc5MTUzMTMiLCJwdnQiOiJoZyIsInV1bGUiOm51bGx9=',
})
```
- API Documentation: [serpapi.com/google-immersive-product-api](https://serpapi.com/google-immersive-product-api)

### Search Google Reverse Image
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'google_reverse_image',
    'image_url': 'https://i.imgur.com/5bGzZi7.jpg',
    'max_results': '1',
})
```
- API Documentation: [serpapi.com/google-reverse-image](https://serpapi.com/google-reverse-image)

### Search Google Events
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'google_events',
    'q': 'Events in Austin',
})
```
- API Documentation: [serpapi.com/google-events-api](https://serpapi.com/google-events-api)

### Search Google Local Services
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'google_local_services',
    'q': 'electrician',
    'data_cid': '6745062158417646970',
})
```
- API Documentation: [serpapi.com/google-local-services-api](https://serpapi.com/google-local-services-api)

### Search Google Maps
```python
import os
import serpapi


client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'google_maps',
    'q': 'pizza',
    'll': '@40.7455096,-74.0083012,15.1z',
    'type': 'search',
})
```
- API Documentation: [serpapi.com/google-maps-api](https://serpapi.com/google-maps-api)

### Search Google Jobs
```python
import os
import serpapi


client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'google_jobs',
    'q': 'coffee',
})
```
- API Documentation: [serpapi.com/google-jobs-api](https://serpapi.com/google-jobs-api)

### Search Google Play
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'google_play',
    'q': 'kite',
    'store': 'apps',
})
```
- API Documentation: [serpapi.com/google-play-api](https://serpapi.com/google-play-api)

### Search Google Images
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'google_images',
    'tbm': 'isch',
    'q': 'coffee',
})
```
- API Documentation: [serpapi.com/google-images-api](https://serpapi.com/google-images-api)

## License

MIT License.

## Contributing

Bug reports and pull requests are welcome on GitHub. Once dependencies are installed, you can run the tests with `pytest`.
