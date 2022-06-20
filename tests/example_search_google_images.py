# test Google Images search engine
import unittest
import os
import serpapi

class TestGoogleImages(unittest.TestCase):

  @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
  def test_search_google_images(self):
    client = serpapi.Client({
        'engine': 'google',
        'api_key': os.getenv("API_KEY")
      })
    data = client.search({
        'engine': 'google', 
        'tbm': 'isch', 
        'q': 'coffee', 
    })
    self.assertIsNone(data.get('error'))
    self.assertIsNotNone(data['images_results'])
    # os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
  