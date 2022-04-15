# test google play
import unittest
import os
import serpapi

class TestGooglePlay(unittest.TestCase):

  @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
  def test_search_google_play(self):
    client = serpapi.Client({
        'engine': 'google_play',
        'api_key': os.getenv("API_KEY")
      })
    data = client.search({
        'q': 'coffee', 
        'store': 'apps', 
    })
    self.assertIsNone(data.get('error'))
    self.assertIsNotNone(data['organic_results'])
    # os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
  