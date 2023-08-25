# Example: ebay search engine
import pytest
import os
import serpapi

@pytest.mark.skipif((os.getenv("API_KEY") == None), reason="no api_key provided")
def test_search_ebay():
  client = serpapi.Client(api_key=os.getenv("API_KEY"))
  data = client.search({
      'engine': 'ebay',
      '_nkw': 'coffee',
  })
  assert data.get('error') is None
  assert data['organic_results']

# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```