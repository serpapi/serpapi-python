# test ebay
import unittest
import os
import serpapi

class TestEbay(unittest.TestCase):

  @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
  def test_search_ebay(self):
    client = serpapi.Client({
        'engine': 'ebay',
        'api_key': os.getenv("API_KEY")
      })
    data = client.search({
        '_nkw': 'coffee', 
    })
    self.assertIsNone(data.get('error'))
    self.assertIsNotNone(data['organic_results'])
    # os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
  