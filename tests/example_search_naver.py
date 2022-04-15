# test naver
import unittest
import os
import serpapi

class TestNaver(unittest.TestCase):

  @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
  def test_search_naver(self):
    client = serpapi.Client({
        'engine': 'naver',
        'api_key': os.getenv("API_KEY")
      })
    data = client.search({
        'query': 'coffee', 
    })
    self.assertIsNone(data.get('error'))
    self.assertIsNotNone(data['ads_results'])
    # os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
  