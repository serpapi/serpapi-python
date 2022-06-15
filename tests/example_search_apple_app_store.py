# test Apple App Store search engine
import unittest
import os
import serpapi

class TestAppleAppStore(unittest.TestCase):

  @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
  def test_search_apple_app_store(self):
    client = serpapi.Client({
        'engine': 'apple_app_store',
        'api_key': os.getenv("API_KEY")
      })
    data = client.search({
        'term': 'coffee', 
    })
    self.assertIsNone(data.get('error'))
    self.assertIsNotNone(data['organic_results'])
    # os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
  