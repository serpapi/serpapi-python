# test Youtube search engine
import unittest
import os
import serpapi

class TestYoutube(unittest.TestCase):

  @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
  def test_search_youtube(self):
    client = serpapi.Client({
        'engine': 'youtube',
        'api_key': os.getenv("API_KEY")
      })
    data = client.search({
        'search_query': 'coffee', 
    })
    self.assertIsNone(data.get('error'))
    self.assertIsNotNone(data['video_results'])
    # os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
  