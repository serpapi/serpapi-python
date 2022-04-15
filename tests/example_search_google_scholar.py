# test google scholar
import unittest
import os
import serpapi

class TestGoogleScholar(unittest.TestCase):

  @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
  def test_search_google_scholar(self):
    client = serpapi.Client({
        'engine': 'google_scholar',
        'api_key': os.getenv("API_KEY")
      })
    data = client.search({
        'q': 'coffee', 
    })
    self.assertIsNone(data.get('error'))
    self.assertIsNotNone(data['organic_results'])
    # os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
  