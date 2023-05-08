
<div align="center">
<h1 align="center">SerpApi Python Library</h1>
  <img src="https://user-images.githubusercontent.com/78694043/233921372-bb57c347-9005-4b59-8f09-993698a87eb6.svg" width="600" alt="serpapi python library logo">

  <a href="https://badge.fury.io/py/serpapi-python">![Package](https://badge.fury.io/py/serpapi.svg)</a> 
  <a href="https://pepy.tech/project/serpapi-python">![Downloads](https://static.pepy.tech/personalized-badge/serpapi?period=month&units=international_system&left_color=grey&right_color=brightgreen&left_text=Downloads)</a> 
  [![serpapi-python](https://github.com/serpapi/serpapi-python/actions/workflows/ci.yml/badge.svg)](https://github.com/serpapi/serpapi-python/actions/workflows/ci.yml)
</div>


Integrate search data into your Ruby application. This library is the official wrapper for SerpApi (https://serpapi.com).

SerpApi supports Google, Google Maps, Google Shopping, Baidu, Yandex, Yahoo, eBay, App Stores, and more.

## Installation
Python3 must be installed.

```sh
$ pip install serpapi
```

## Simple usage

```python
import serpapi
client = serpapi.Client({     
  'api_key': "secret_api_key", # set personal API key from serpapi.com/dashboard
  'engine': "google",          # set default search engine
})
results = client.search({
  q: "coffee",          # google query
  location: "Austin,TX" # force the location [optional]
})
print(results['organic_results'])
```

This example runs a search for "coffee" on Google. It then returns the results as a regular Ruby Hash. See the [playground](https://serpapi.com/playground) to generate your own code.

## Advanced Usage
### Search API
```python
# load pip package
import serpapi

# serpapi client created with default parameters
client = serpapi.Client({'api_key': 'secret_key', 'engine': 'google'})

# We recommend that you keep your keys safe.
# At least, don't commit them in plain text.
# More about configuration via environment variables: 
# https://hackernoon.com/all-the-secrets-of-encrypting-api-keys-in-ruby-revealed-5qf3t5l

# search query overview (more fields available depending on search engine)
params = {
  # select the search engine (full list: https://serpapi.com/)
  'engine': "google",
  # actual search query for google
  'q': "Coffee",
  # then adds search engine specific options.
  # for example: google specific parameters: https://serpapi.com/search-api
  'google_domain': "Google Domain",
  'location': "Location Requested", # example: Portland,Oregon,United States [see: Location API](#Location-API)
  'device': "desktop|mobile|tablet",
  'hl': "Google UI Language",
  'gl': "Google Country",
  'safe': "Safe Search Flag",
  'num': "Number of Results",
  'start': "Pagination Offset",
  'tbm': "nws|isch|shop",
  'tbs': "custom to be client criteria",
  # tweak HTTP client behavior
  'async': False, # true when async call enabled.
  'timeout': 60, # HTTP timeout in seconds on the client side only.
}

# formated search results as a Hash
#  serpapi.com converts HTML -> JSON 
results = client.search(params)

# raw search engine html as a String
#  serpapi.com acts a proxy to provive high throughputs, no search limit and more.
raw_html = client.html(params)
```

[Google search documentation](https://serpapi.com/search-api). More hands on examples are available below.

### Documentation
 * [API documentation](https://rubydoc.info/github/serpapi/serpapi-ruby/master)
 * [Full documentation on SerpApi.com](https://serpapi.com)
 * [Library Github page](https://github.com/serpapi/serpapi-ruby)
 * [Library GEM page](https://rubygems.org/gems/serpapi/)
 * [API health status](https://serpapi.com/status)

### Location API

```python
import serpapi
client = serpapi.Client({'api_key': 'secret_api_key'})
locations = client.location({'q':'Austin', 'limit': 3})
print([loc['canonical_name'] for loc in locations])
```

it prints the first 3 locations matching Austin:
```python
['Austin,TX,Texas,United States', 'Austin,Texas,United States', 'Rochester,MN-Mason City,IA-Austin,MN,United States']
```

NOTE: api_key is not required for this endpoint.

### Search Archive API

This API allows retrieving previous search results.
To fetch earlier results from the search_id.

First, you need to run a search and save the search id.
```python
import serpapi
client = serpapi.Client({'api_key': 'secret_api_key', 'engine': 'google'})
results = client.search({'q': "Coffee"})
search_id = results['search_metadata']['id']
print("search_id: " + search_id)
```

Now let's retrieve the previous search results from the archive.

```python
import serpapi
client = serpapi.Client({'api_key': 'secret_api_key'})
results = client.search_archive('search_id')
print(results)
```

This code prints the search results from the archive. :)

### Account API

```python
import serpapi
client = serpapi.Client({'api_key': 'secret_api_key'})
print(client.account())
```

It prints your account information including plan, credit, montly

## Basic example per search engines

### Search bing
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'bing',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'q': 'coffee',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['organic_results'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_bing_test.py]
see: [https://serpapi.com/bing-search-api](https://serpapi.com/bing-search-api)

### Search baidu
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'baidu',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'q': 'coffee',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['organic_results'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_baidu_test.py]
see: [https://serpapi.com/baidu-search-api](https://serpapi.com/baidu-search-api)

### Search yahoo
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'yahoo',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'p': 'coffee',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['organic_results'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_yahoo_test.py]
see: [https://serpapi.com/yahoo-search-api](https://serpapi.com/yahoo-search-api)

### Search youtube
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'youtube',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'search_query': 'coffee',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['video_results'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_youtube_test.py]
see: [https://serpapi.com/youtube-search-api](https://serpapi.com/youtube-search-api)

### Search walmart
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'walmart',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'query': 'coffee',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['organic_results'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_walmart_test.py]
see: [https://serpapi.com/walmart-search-api](https://serpapi.com/walmart-search-api)

### Search ebay
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'ebay',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    '_nkw': 'coffee',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['organic_results'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_ebay_test.py]
see: [https://serpapi.com/ebay-search-api](https://serpapi.com/ebay-search-api)

### Search naver
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'naver',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'query': 'coffee',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['ads_results'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_naver_test.py]
see: [https://serpapi.com/naver-search-api](https://serpapi.com/naver-search-api)

### Search home depot
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'home_depot',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'q': 'table',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['products'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_home_depot_test.py]
see: [https://serpapi.com/home-depot-search-api](https://serpapi.com/home-depot-search-api)

### Search apple app store
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'apple_app_store',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'term': 'coffee',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['organic_results'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_apple_app_store_test.py]
see: [https://serpapi.com/apple-app-store](https://serpapi.com/apple-app-store)

### Search duckduckgo
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'duckduckgo',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'q': 'coffee',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['organic_results'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_duckduckgo_test.py]
see: [https://serpapi.com/duckduckgo-search-api](https://serpapi.com/duckduckgo-search-api)

### Search google
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'google',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'q': 'coffee',
    'engine': 'google',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['organic_results'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_google_test.py]
see: [https://serpapi.com/search-api](https://serpapi.com/search-api)

### Search google scholar
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'google_scholar',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'q': 'coffee',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['organic_results'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_google_scholar_test.py]
see: [https://serpapi.com/google-scholar-api](https://serpapi.com/google-scholar-api)

### Search google autocomplete
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'google_autocomplete',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'q': 'coffee',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['suggestions'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_google_autocomplete_test.py]
see: [https://serpapi.com/google-autocomplete-api](https://serpapi.com/google-autocomplete-api)

### Search google product
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'google_product',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'q': 'coffee',
    'product_id': '4172129135583325756',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['product_results'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_google_product_test.py]
see: [https://serpapi.com/google-product-api](https://serpapi.com/google-product-api)

### Search google reverse image
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'google_reverse_image',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'image_url': 'https://i.imgur.com/5bGzZi7.jpg',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['image_sizes'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_google_reverse_image_test.py]
see: [https://serpapi.com/google-reverse-image](https://serpapi.com/google-reverse-image)

### Search google events
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'google_events',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'q': 'coffee',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['events_results'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_google_events_test.py]
see: [https://serpapi.com/google-events-api](https://serpapi.com/google-events-api)

### Search google local services
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'google_local_services',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'q': 'electrician',
    'data_cid': '6745062158417646970',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['local_ads'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_google_local_services_test.py]
see: [https://serpapi.com/google-local-services-api](https://serpapi.com/google-local-services-api)

### Search google maps
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'google_maps',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'q': 'pizza',
    'll': '@40.7455096,-74.0083012,15.1z',
    'type': 'search',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['local_results'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_google_maps_test.py]
see: [https://serpapi.com/google-maps-api](https://serpapi.com/google-maps-api)

### Search google jobs
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'google_jobs',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'q': 'coffee',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['jobs_results'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_google_jobs_test.py]
see: [https://serpapi.com/google-jobs-api](https://serpapi.com/google-jobs-api)

### Search google play
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'google_play',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'q': 'kite',
    'store': 'apps',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['organic_results'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_google_play_test.py]
see: [https://serpapi.com/google-play-api](https://serpapi.com/google-play-api)

### Search google images
```python
import serpapi
import pprint
import os

client = serpapi.Client({
    'engine': 'google_images',
    'api_key': os.getenv("API_KEY")
  })
data = client.search({
    'engine': 'google_images',
    'tbm': 'isch',
    'q': 'coffee',
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['images_results'])
# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
```
test: [https://github.com/serpapi/serpapi-python/tests/example_search_google_images_test.py]
see: [https://serpapi.com/images-results](https://serpapi.com/images-results)
    

# Developer Guide
TODO update this section
### Key goals
 - High code quality
 - KISS principles (https://en.wikipedia.org/wiki/KISS_principle)
 - Brand centric instead of search engine based
   - No hard coded logic per search engine on the client side.
 - Simple HTTP client (lightweight, reduced dependency)
   - No magic default values
   - Thread safe
   - Leak free
 - Easy to extends
 - Defensive code style (raise custom exception)
 - TDD - Test driven development (lint, ~100% code coverage)
 - Follow best API coding pratice per platform

### Inspiration
The API design was inpired by the most popular Python packages.
 - urllib3 - https://github.com/urllib3/urllib3
 - Boto3 - https://github.com/boto/boto3
 - Numpy - 

### Quality expectation
 - 0 lint issues using pylint `make lint`
 - 99% code coverage running `make test`
 - 100% test passing: `make test`
 
# Developer Guide
## Design : UML diagram
### Client design: Class diagram
```mermaid
classDiagram
  CustomClient *-- Client
  HttpClient <-- Client
  HttpClient *-- urllib3
  HttpClient *-- ObjectDecoder

  class Client {
    'engine': String
    'api_key': String
    parameter: Hash
    search()
    html()
    location()
    search_archive()
    account()
  }

  class HttpClient {
    start()
    decode()
  }

  class urllib3 {
    request()
  }
```

## JSON search() : Sequence diagram
```mermaid
sequenceDiagram
    Client->>SerpApi.com: search() : http request 
    SerpApi.com-->>SerpApi.com: query search engine
    SerpApi.com-->>SerpApi.com: parse HTML into JSON
    SerpApi.com-->>Client: JSON payload
    Client-->>Client: decode JSON into Dict
```

where:
  - The end user implements the application.
  - Client refers to SerpApi:Client.
  - SerpApi.com is the backend HTTP / REST service.
  - Engine refers to Google, Baidu, Bing, and more.

The SerpApi.com service (backend)
 - executes a scalable search on `'engine': "google"` using the search query: `q: "coffee"`.
 - parses the messy HTML responses from Google on the backend.
 - returns a standardized JSON response.
The class SerpApi::Client (client side / ruby):
 - Format the request to SerpApi.com server.
 - Execute HTTP Get request.
 - Parse JSON into Ruby Hash using a standard JSON library.
Et voila!

## Continuous integration
We love "true open source" and "continuous integration", and Test Drive Development (TDD).
 We are using RSpec to test [our infrastructure around the clock]) using Github Action to achieve the best QoS (Quality Of Service).

The directory spec/ includes specification which serves the dual purposes of examples and functional tests.

Set your secret API key in your shell before running a test.
```bash
export API_KEY="your_secret_key"
```
Install testing dependency
```bash
$ make install
```

Check code quality using Lint.
```bash
$ make lint
```

Run regression.
```bash
$ make test
```

To flush the flow.
```bash
$ make
```

Open coverage report generated by `rake test`
```sh
open coverage/index.html
```

Open ./Rakefile for more information.

Contributions are welcome. Feel to submit a pull request!

## Dependencies

HTTP requests are executed using [URL LIB3 documentation](https://urllib3.readthedocs.io/en/stable/user-guide.html). 

## TODO
 - [] Release version 1.0.0
