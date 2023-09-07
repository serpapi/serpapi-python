# Example: apple_app_store search engine
import pytest
import os
import serpapi

def test_search_apple_app_store(client):
  data = client.search({
      'engine': 'apple_app_store',
      'term': 'coffee',
  })
  assert data.get('error') is None
  assert data['organic_results']

# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
