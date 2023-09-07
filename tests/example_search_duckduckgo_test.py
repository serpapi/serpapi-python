# Example: duckduckgo search engine
import pytest
import os
import serpapi

def test_search_duckduckgo(client):
  data = client.search({
      'engine': 'duckduckgo',
      'q': 'coffee',
  })
  assert data.get('error') is None
  assert data['organic_results']

# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
