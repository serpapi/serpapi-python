# test yahoo
import unittest
import os
import serpapi

class TestYahoo(unittest.TestCase):

  @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
  def test_search_yahoo(self):
    client = serpapi.Client({
        'engine': 'yahoo',
        'api_key': os.getenv("API_KEY")
      })
    data = client.search({
        'p': 'coffee', 
    })
    self.assertIsNone(data.get('error'))
    self.assertIsNotNone(data['organic_results'])
    # os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
  