# Example: google_product search engine
import pytest
import os
import serpapi

def test_search_google_product(client):
  data = client.search({
      'engine': 'google_product',
      'q': 'coffee',
      'product_id': '4887235756540435899',
  })
  assert data.get('error') is None
  assert data['product_results']

# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
