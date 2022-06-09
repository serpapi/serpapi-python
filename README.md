# User guide
Scrape Google and other search engines from our fast, easy, and complete API using SerpApi.com
This python library is meant to scrape and parse results from all major search engines available world wide including Google, Bing, Baidu, Yandex, Yahoo, Ebay, Home depot, Apple and more using [SerpApi](https://serpapi.com).
This is an open source project hosted under https://github.com/serpapi/serpapi-python.

SerpApi.com provides a [script builder](https://serpapi.com/demo) to get you started quickly.

## Installation
serpapi can be installed with pip.

```sh
$ python -m pip install serpapi
```

## Quick start
First things first, import the serpapi module:

```python
>>> import serpapi
```
You'll need a client instance to make a search. This object handles all of the details of connection pooling and thread safety so that you don't have to:

```python
>>> client = serpapi.Client()
```
To make a search using SerpApi.com client.

```python
>>> parameter = {
      api_key: "secret_api_key", # from serpapi.com
      engine: "google",     # search engine
      q: "coffee",          # search topic
      location: "Austin,TX" # location
    }
    results = searpapi.search(parameter)
```
Putting everything together.
```python
import serpapi

parameter = {
  api_key: "secret_api_key", # from serpapi.com
  engine: "google",     # search engine
  q: "coffee",          # search topic
  location: "Austin,TX" # location
}
results = searpapi.search(parameter)
print(results)
```

### Advanced settings
SerpApi Client uses urllib3 under the hood.
The HTTP connection be tuned by setting the following client specific setting.
  - retries : attempt to reconnect if the connection failed by default: False 
  - timeout : connection timeout by default 60s

  ```python
parameter = {
   retries: 5,
   timeout: 4.0
   # regular parameters
}
```

for more details: [URL LIB3 documentation](https://urllib3.readthedocs.io/en/stable/user-guide.html)


## Basic example per search engine
### Search bing
```python
import 'serpapi'
import 'pprint'
import 'os'

client = serpapi.Client({
'engine': 'bing',
'api_key': os.getenv("API_KEY")
})
data = client.search({
'q': 'coffee', 
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['organic_results'])
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_bing.py
[see https://serpapi.com/bing](https://serpapi.com/bing)

### Search baidu
```python
import 'serpapi'
import 'pprint'
import 'os'

client = serpapi.Client({
'engine': 'baidu',
'api_key': os.getenv("API_KEY")
})
data = client.search({
'q': 'coffee', 
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['organic_results'])
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_baidu.py
[see https://serpapi.com/baidu](https://serpapi.com/baidu)

### Search yahoo
```python
import 'serpapi'
import 'pprint'
import 'os'

client = serpapi.Client({
'engine': 'yahoo',
'api_key': os.getenv("API_KEY")
})
data = client.search({
'p': 'coffee', 
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['organic_results'])
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_yahoo.py
[see https://serpapi.com/yahoo](https://serpapi.com/yahoo)

### Search youtube
```python
import 'serpapi'
import 'pprint'
import 'os'

client = serpapi.Client({
'engine': 'youtube',
'api_key': os.getenv("API_KEY")
})
data = client.search({
'search_query': 'coffee', 
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['video_results'])
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_youtube.py
[see https://serpapi.com/youtube](https://serpapi.com/youtube)

### Search walmart
```python
import 'serpapi'
import 'pprint'
import 'os'

client = serpapi.Client({
'engine': 'walmart',
'api_key': os.getenv("API_KEY")
})
data = client.search({
'query': 'coffee', 
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['organic_results'])
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_walmart.py
[see https://serpapi.com/walmart](https://serpapi.com/walmart)

### Search ebay
```python
import 'serpapi'
import 'pprint'
import 'os'

client = serpapi.Client({
'engine': 'ebay',
'api_key': os.getenv("API_KEY")
})
data = client.search({
'_nkw': 'coffee', 
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['organic_results'])
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_ebay.py
[see https://serpapi.com/ebay](https://serpapi.com/ebay)

### Search naver
```python
import 'serpapi'
import 'pprint'
import 'os'

client = serpapi.Client({
'engine': 'naver',
'api_key': os.getenv("API_KEY")
})
data = client.search({
'query': 'coffee', 
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['ads_results'])
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_naver.py
[see https://serpapi.com/naver](https://serpapi.com/naver)

### Search home depot
```python
import 'serpapi'
import 'pprint'
import 'os'

client = serpapi.Client({
'engine': 'home_depot',
'api_key': os.getenv("API_KEY")
})
data = client.search({
'q': 'table', 
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['products'])
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_home_depot.py
[see https://serpapi.com/home_depot](https://serpapi.com/home_depot)

### Search apple app store
```python
import 'serpapi'
import 'pprint'
import 'os'

client = serpapi.Client({
'engine': 'apple_app_store',
'api_key': os.getenv("API_KEY")
})
data = client.search({
'term': 'coffee', 
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['organic_results'])
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_apple_app_store.py
[see https://serpapi.com/apple_app_store](https://serpapi.com/apple_app_store)

### Search duckduckgo
```python
import 'serpapi'
import 'pprint'
import 'os'

client = serpapi.Client({
'engine': 'duckduckgo',
'api_key': os.getenv("API_KEY")
})
data = client.search({
'q': 'coffee', 
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['organic_results'])
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_duckduckgo.py
[see https://serpapi.com/duckduckgo](https://serpapi.com/duckduckgo)

### Search google scholar
```python
import 'serpapi'
import 'pprint'
import 'os'

client = serpapi.Client({
'engine': 'google_scholar',
'api_key': os.getenv("API_KEY")
})
data = client.search({
'q': 'coffee', 
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['organic_results'])
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_google_scholar.py
[see https://serpapi.com/google_scholar](https://serpapi.com/google_scholar)

### Search google autocomplete
```ruby
import 'serpapi'
import 'pprint'
import 'os'

'engine': 'google_autocomplete',
'api_key': os.getenv("API_KEY")
})
data = client.search({
'q': 'coffee', 
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['suggestions'])
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_google_autocomplete.py
[see https://serpapi.com/google_autocomplete](https://serpapi.com/google_autocomplete)

### Search google product
```python
import 'serpapi'
import 'pprint'
import 'os'

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
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_google_product.py
[see https://serpapi.com/google_product](https://serpapi.com/google_product)

### Search google reverse image
```python
import 'serpapi'
import 'pprint'
import 'os'

client = serpapi.Client({
'engine': 'google_reverse_image',
'api_key': os.getenv("API_KEY")
})
data = client.search({
'image_url': 'https://i.imgur.com/5bGzZi7.jpg', 
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['image_sizes'])
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_google_reverse_image.py
[see https://serpapi.com/google_reverse_image](https://serpapi.com/google_reverse_image)

### Search google events
```python
import 'serpapi'
import 'pprint'
import 'os'

client = serpapi.Client({
'engine': 'google_events',
'api_key': os.getenv("API_KEY")
})
data = client.search({
'q': 'coffee', 
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['events_results'])
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_google_events.py
[see https://serpapi.com/google_events](https://serpapi.com/google_events)

### Search google local services
```python
import 'serpapi'
import 'pprint'
import 'os'

client = serpapi.Client({
'engine': 'google_local_services',
'api_key': os.getenv("API_KEY")
})
data = client.search({
'q': 'Electrician', 
'place_id': 'ChIJOwg_06VPwokRYv534QaPC8g', 
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['local_ads'])
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_google_local_services.py
[see https://serpapi.com/google_local_services](https://serpapi.com/google_local_services)

### Search google maps
```python
import 'serpapi'
import 'pprint'
import 'os'

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
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_google_maps.py
[see https://serpapi.com/google_maps](https://serpapi.com/google_maps)

### Search google jobs
```python
import 'serpapi'
import 'pprint'
import 'os'

client = serpapi.Client({
'engine': 'google_jobs',
'api_key': os.getenv("API_KEY")
})
data = client.search({
'q': 'coffee', 
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['jobs_results'])
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_google_jobs.py
[see https://serpapi.com/google_jobs](https://serpapi.com/google_jobs)

### Search google play
```python
import 'serpapi'
import 'pprint'
import 'os'

client = serpapi.Client({
'engine': 'google_play',
'api_key': os.getenv("API_KEY")
})
data = client.search({
"engine": "google_play",
"q": "maps",
"hl": "en",
"gl": "us",
"store": "apps"
})
# pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['organic_results'])
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_google_play.py
[see https://serpapi.com/google_play](https://serpapi.com/google_play)

### Search google images
```python
import 'serpapi'
import 'pprint'
import 'os'

client = serpapi.Client({
'engine': 'google_images',
'api_key': os.getenv("API_KEY")
})
data = client.search({
'engine': 'google', 
'tbm': 'isch', 
'q': 'coffee', 
})
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(data['images_results'])
# os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
```
 test: tests/example_search_google_images.py
[see https://serpapi.com/google_images](https://serpapi.com/google_images)

## Developer's note
### Key goals
 - Brand centric instead of search engine based
   - No hard coded logic per search engine
 - Simple HTTP client (lightweight, reduced dependency)
   - No magic default values
   - Thread safe
 - Easy to extends
 - Defensive code style (raise cutsom exception)
 - TDD
 - Best API coding pratice per platform

### Design
The API design was inpired by the most popular Python packages.
 - urllib3 - https://github.com/urllib3/urllib3
 - Boto3 - https://github.com/boto/boto3

### Quality expectation
 - 0 lint issues using pylint `make lint`
 - 99% code coverage running `make test`