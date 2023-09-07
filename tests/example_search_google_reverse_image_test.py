# Example: google_reverse_image search engine
import pytest
import os
import serpapi

def test_search_google_reverse_image(client):
  data = client.search({
      'engine': 'google_reverse_image',
      'image_url': 'https://i.imgur.com/5bGzZi7.jpg',
      'max_results': '1',
  })
  assert data.get('error') is None
  assert data['image_sizes']

# os.getenv("API_KEY") is your secret API Key
# copy/paste from [http://serpapi.com/dashboard] to your bash
# ```export API_KEY="your_secure_api_key"```
