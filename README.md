
<div align="center">
<h1 align="center">SerpApi Python Library & Package</h1>
  <img src="https://user-images.githubusercontent.com/78694043/233921372-bb57c347-9005-4b59-8f09-993698a87eb6.svg" width="600" alt="serpapi python library logo">

  <a href="https://badge.fury.io/py/serpapi-python">![Package](https://badge.fury.io/py/serpapi.svg)</a>
  
  [![serpapi-python](https://github.com/serpapi/serpapi-python/actions/workflows/ci.yml/badge.svg)](https://github.com/serpapi/serpapi-python/actions/workflows/ci.yml)
</div>

This repository is the home of the *soon–to–be* official Python API wrapper for [SerpApi](https://serpapi.com). This `serpapi` module allows you to access search data in your Python application.

[SerpApi](https://serpapi.com) supports Google, Google Maps, Google Shopping, Bing, Baidu, Yandex, Yahoo, eBay, App Stores, and more. Check out the [documentation](https://serpapi.com/search-api) for a full list.


## Installation

To install the `serpapi` package, simply run the following command:

```bash
$ pip install serpapi
```

Please note that this package is separate from the legacy `serpapi` module, which is available on PyPi as `google-search-results`. This package is maintained by SerpApi, and is the recommended way to access the SerpApi service from Python.

## Usage

Let's start by searching for Coffee on Google:

```pycon
>>> import serpapi
>>> s = serpapi.search(q="Coffee", engine="google", location="Austin, Texas", hl="en", gl="us")
```

The `s` variable now contains a `SerpResults` object, which acts just like a standard dictionary, with some convenient functions added on top.

Let's print the first result:

```pycon
>>> s["organic_results"][0]["link"]
'https://en.wikipedia.org/wiki/Coffee'
```

Let's print the title of the first result, but in a more Pythonic way:

```pycon
>>> s["organic_results"][0].get("title")
'Coffee - Wikipedia'
```

The [SerpApi.com API Documentation](https://serpapi.com/search-api) contains a list of all the possible parameters that can be passed to the API.

## Documentation

Documentation is [available on Read the Docs](https://serpapi-python.readthedocs.io/en/latest/).

## Basic Examples in Python

### Search Bing
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'bing',
    'q': 'coffee',
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
    'q': 'coffee',
    'engine': 'google',
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

### Search Google Product
```python
import os
import serpapi

client = serpapi.Client(api_key=os.getenv("API_KEY"))
results = client.search({
    'engine': 'google_product',
    'q': 'coffee',
    'product_id': '4887235756540435899',
})
```
- API Documentation: [serpapi.com/google-product-api](https://serpapi.com/google-product-api)

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
    'q': 'coffee',
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
    'max_results': '2',
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
- API Documentation: [serpapi.com/images-results](https://serpapi.com/images-results)


## License

MIT License.

## Contributing

Bug reports and pull requests are welcome on GitHub. Once dependencies are installed, you can run the tests with `pytest`.
