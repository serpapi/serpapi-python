# Example: google search engine
import unittest
import os
import serpapi

class TestGoogle(unittest.TestCase):

  @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
  def test_search_google(self):
    client = serpapi.Client({
        'engine': 'google',
        'api_key': os.getenv("API_KEY")
      })
    data = client.search({
        'q': 'coffee',
        'engine': 'google',
    })
    self.assertIsNone(data.get('error'))
    self.assertIsNotNone(data['organic_results'])
    # os.getenv("API_KEY") is your secret API Key
    # copy/paste from [http://serpapi.com/dashboard] to your bash
    # ```export API_KEY="your_secure_api_key"```
