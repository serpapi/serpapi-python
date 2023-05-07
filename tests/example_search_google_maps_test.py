# Example: google_maps search engine
import unittest
import os
import serpapi

class TestGoogleMaps(unittest.TestCase):

  @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
  def test_search_google_maps(self):
    client = serpapi.Client({
        'engine': 'google_maps',
        'api_key': os.getenv("API_KEY")
      })
    data = client.search({
        'q': 'pizza',
        'll': '@40.7455096,-74.0083012,15.1z',
        'type': 'search',
    })
    self.assertIsNone(data.get('error'))
    self.assertIsNotNone(data['local_results'])
    # os.getenv("API_KEY") is your secret API Key
    # copy/paste from [http://serpapi.com/dashboard] to your bash
    # ```export API_KEY="your_secure_api_key"```
