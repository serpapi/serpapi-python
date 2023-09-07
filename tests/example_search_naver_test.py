# Example: naver search engine
import pytest
import os
import serpapi

def test_search_naver(client):
  data = client.search({
      'engine': 'naver',
      'query': 'coffee',
  })
  assert data.get('error') is None
  assert data['ads_results']

# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
