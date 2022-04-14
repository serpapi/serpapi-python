import unittest
import os
import serpapi

class TestLocationApi(unittest.TestCase):


    @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
    def test_get_account(self):
        client = serpapi.Client({'api_key': os.getenv('API_KEY')})
        locations = client.location({'q':'Austin', 'limit': 3})
        self.assertGreater(len(locations), 1)
        self.assertTrue('id' in locations[0])


