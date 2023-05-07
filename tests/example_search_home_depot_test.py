# Example: home_depot search engine
import unittest
import os
import serpapi

class TestHomeDepot(unittest.TestCase):

  @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
  def test_search_home_depot(self):
    client = serpapi.Client({
        'engine': 'home_depot',
        'api_key': os.getenv("API_KEY")
      })
    data = client.search({
        'q': 'table',
    })
    self.assertIsNone(data.get('error'))
    self.assertIsNotNone(data['products'])
    # os.getenv("API_KEY") is your secret API Key
    # copy/paste from [http://serpapi.com/dashboard] to your bash
    # ```export API_KEY="your_secure_api_key"```
