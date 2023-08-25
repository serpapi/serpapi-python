# Example: google_maps search engine
import pytest
import os
import serpapi

@pytest.mark.skipif((os.getenv("API_KEY") == None), reason="no api_key provided")
def test_search_google_maps():
  client = serpapi.Client(api_key=os.getenv("API_KEY"))
  data = client.search({
      'engine': 'google_maps',
      'q': 'pizza',
      'll': '@40.7455096,-74.0083012,15.1z',
      'type': 'search',
  })
  assert data.get('error') is None
  assert data['local_results']

# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```