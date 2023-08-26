
<div align="center">
<h1 align="center">SerpApi Python Library & Package</h1>
  <img src="https://user-images.githubusercontent.com/78694043/233921372-bb57c347-9005-4b59-8f09-993698a87eb6.svg" width="600" alt="serpapi python library logo">

  <!-- <a href="https://badge.fury.io/py/serpapi-python">![Package](https://badge.fury.io/py/serpapi.svg)</a>
  <a href="https://pepy.tech/project/serpapi-python">![Downloads](https://static.pepy.tech/personalized-badge/serpapi?period=month&units=international_system&left_color=grey&right_color=brightgreen&left_text=Downloads)</a>  -->
  [![serpapi-python](https://github.com/serpapi/serpapi-python/actions/workflows/ci.yml/badge.svg)](https://github.com/serpapi/serpapi-python/actions/workflows/ci.yml)
</div>

This repository is the home of the *soon–to–be* official Python API wrapper for [SerpApi](https://serpapi.com). This `serpapi` module allows you to access search data in your Python application.

[SerpApi](https://serpapi.com) supports Google, Google Maps, Google Shopping, Bing, Baidu, Yandex, Yahoo, eBay, App Stores, and more. Check out the [documentation](https://serpapi.com/search-api) for a full list.

## Current Status

This project is under development, and will be released to the public on PyPi soon.

## Installation

To install the `serpapi` package, simply run the following command:

```bash
$ pip install serpapi
```

Please note that this package is separate from the *soon–to–be* legacy `serpapi` module, which is currently available on PyPi as `google-search-results`.

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

## Examples in python
Here is how to calls the APIs.

### Search bing
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'bing',
    'q': 'coffee',
})
```
test: [tests/example_search_bing_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_bing_test.py)
see: [serpapi.com/bing-search-api](https://serpapi.com/bing-search-api)

### Search baidu
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'baidu',
    'q': 'coffee',
})
```
test: [tests/example_search_baidu_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_baidu_test.py)
see: [serpapi.com/baidu-search-api](https://serpapi.com/baidu-search-api)

### Search yahoo
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'yahoo',
    'p': 'coffee',
})
```
test: [tests/example_search_yahoo_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_yahoo_test.py)
see: [serpapi.com/yahoo-search-api](https://serpapi.com/yahoo-search-api)

### Search youtube
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'youtube',
    'search_query': 'coffee',
})
```
test: [tests/example_search_youtube_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_youtube_test.py)
see: [serpapi.com/youtube-search-api](https://serpapi.com/youtube-search-api)

### Search walmart
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'walmart',
    'query': 'coffee',
})
```
test: [tests/example_search_walmart_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_walmart_test.py)
see: [serpapi.com/walmart-search-api](https://serpapi.com/walmart-search-api)

### Search ebay
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'ebay',
    '_nkw': 'coffee',
})
```
test: [tests/example_search_ebay_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_ebay_test.py)
see: [serpapi.com/ebay-search-api](https://serpapi.com/ebay-search-api)

### Search naver
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'naver',
    'query': 'coffee',
})
```
test: [tests/example_search_naver_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_naver_test.py)
see: [serpapi.com/naver-search-api](https://serpapi.com/naver-search-api)

### Search home depot
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'home_depot',
    'q': 'table',
})
```
test: [tests/example_search_home_depot_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_home_depot_test.py)
see: [serpapi.com/home-depot-search-api](https://serpapi.com/home-depot-search-api)

### Search apple app store
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'apple_app_store',
    'term': 'coffee',
})
```
test: [tests/example_search_apple_app_store_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_apple_app_store_test.py)
see: [serpapi.com/apple-app-store](https://serpapi.com/apple-app-store)

### Search duckduckgo
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'duckduckgo',
    'q': 'coffee',
})
```
test: [tests/example_search_duckduckgo_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_duckduckgo_test.py)
see: [serpapi.com/duckduckgo-search-api](https://serpapi.com/duckduckgo-search-api)

### Search google
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'google',
    'q': 'coffee',
    'engine': 'google',
})
```
test: [tests/example_search_google_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_google_test.py)
see: [serpapi.com/search-api](https://serpapi.com/search-api)

### Search google scholar
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'google_scholar',
    'q': 'coffee',
})
```
test: [tests/example_search_google_scholar_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_google_scholar_test.py)
see: [serpapi.com/google-scholar-api](https://serpapi.com/google-scholar-api)

### Search google autocomplete
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'google_autocomplete',
    'q': 'coffee',
})
```
test: [tests/example_search_google_autocomplete_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_google_autocomplete_test.py)
see: [serpapi.com/google-autocomplete-api](https://serpapi.com/google-autocomplete-api)

### Search google product
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'google_product',
    'q': 'coffee',
    'product_id': '4887235756540435899',
})
```
test: [tests/example_search_google_product_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_google_product_test.py)
see: [serpapi.com/google-product-api](https://serpapi.com/google-product-api)

### Search google reverse image
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'google_reverse_image',
    'image_url': 'https://i.imgur.com/5bGzZi7.jpg',
    'max_results': '1',
})
```
test: [tests/example_search_google_reverse_image_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_google_reverse_image_test.py)
see: [serpapi.com/google-reverse-image](https://serpapi.com/google-reverse-image)

### Search google events
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'google_events',
    'q': 'coffee',
})
```
test: [tests/example_search_google_events_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_google_events_test.py)
see: [serpapi.com/google-events-api](https://serpapi.com/google-events-api)

### Search google local services
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'google_local_services',
    'q': 'electrician',
    'data_cid': '6745062158417646970',
})
```
test: [tests/example_search_google_local_services_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_google_local_services_test.py)
see: [serpapi.com/google-local-services-api](https://serpapi.com/google-local-services-api)

### Search google maps
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'google_maps',
    'q': 'pizza',
    'll': '@40.7455096,-74.0083012,15.1z',
    'type': 'search',
})
```
test: [tests/example_search_google_maps_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_google_maps_test.py)
see: [serpapi.com/google-maps-api](https://serpapi.com/google-maps-api)

### Search google jobs
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'google_jobs',
    'q': 'coffee',
})
```
test: [tests/example_search_google_jobs_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_google_jobs_test.py)
see: [serpapi.com/google-jobs-api](https://serpapi.com/google-jobs-api)

### Search google play
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'google_play',
    'q': 'kite',
    'store': 'apps',
    'max_results': '2',
})
```
test: [tests/example_search_google_play_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_google_play_test.py)
see: [serpapi.com/google-play-api](https://serpapi.com/google-play-api)

### Search google images
```python
import serpapi
import pprint
import os

client = serpapi.Client(api_key=os.getenv("API_KEY"))
data = client.search({
    'engine': 'google_images',
    'engine': 'google_images',
    'tbm': 'isch',
    'q': 'coffee',
})
```
test: [tests/example_search_google_images_test.py](https://github.com/serpapi/serpapi-python/blob/master/tests/example_search_google_images_test.py)
see: [serpapi.com/images-results](https://serpapi.com/images-results)


## License

MIT License.

## Contributing

Bug reports and pull requests are welcome on GitHub. Once dependencies are installed, you can run the tests with `pytest`.
