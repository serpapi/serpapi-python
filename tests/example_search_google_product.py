# test Google Product search engine
import unittest
import os
import serpapi

class TestGoogleProduct(unittest.TestCase):

  @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
  def test_search_google_product(self):
    client = serpapi.Client({
        'engine': 'google_product',
        'api_key': os.getenv("API_KEY")
      })
    data = client.search({
        'q': 'coffee', 
        'product_id': '4172129135583325756', 
    })
    self.assertIsNone(data.get('error'))
    self.assertIsNotNone(data['product_results'])
    # os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
  