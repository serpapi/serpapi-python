# test Baidu search engine
import unittest
import os
import serpapi

class TestBaidu(unittest.TestCase):

  @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
  def test_search_baidu(self):
    client = serpapi.Client({
        'engine': 'baidu',
        'api_key': os.getenv("API_KEY")
      })
    data = client.search({
        'q': 'coffee', 
    })
    self.assertIsNone(data.get('error'))
    self.assertIsNotNone(data['organic_results'])
    # os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
  