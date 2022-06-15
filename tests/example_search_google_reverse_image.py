# test Google Reverse Image search engine
import unittest
import os
import serpapi

class TestGoogleReverseImage(unittest.TestCase):

  @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
  def test_search_google_reverse_image(self):
    client = serpapi.Client({
        'engine': 'google_reverse_image',
        'api_key': os.getenv("API_KEY")
      })
    data = client.search({
        'image_url': 'https://i.imgur.com/5bGzZi7.jpg', 
    })
    self.assertIsNone(data.get('error'))
    self.assertIsNotNone(data['image_sizes'])
    # os.getenv("API_KEY") captures the secret user API available from http://serpapi.com
  