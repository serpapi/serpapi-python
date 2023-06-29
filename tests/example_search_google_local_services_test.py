# Example: google_local_services search engine
import unittest
import os
import serpapi


class TestGoogleLocalServices(unittest.TestCase):
    @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
    def test_search_google_local_services(self):
        client = serpapi.Client(
            {"engine": "google_local_services", "api_key": os.getenv("API_KEY")}
        )
        data = client.search(
            {
                "q": "electrician",
                "data_cid": "6745062158417646970",
            }
        )
        self.assertIsNone(data.get("error"))
        self.assertIsNotNone(data["local_ads"])
        # os.getenv("API_KEY") is your secret API Key
        # copy/paste from [http://serpapi.com/dashboard] to your bash
        # ```export API_KEY="your_secure_api_key"```
