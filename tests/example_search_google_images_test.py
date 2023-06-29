# Example: google_images search engine
import unittest
import os
import serpapi


class TestGoogleImages(unittest.TestCase):
    @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
    def test_search_google_images(self):
        client = serpapi.Client(
            {"engine": "google_images", "api_key": os.getenv("API_KEY")}
        )
        data = client.search(
            {
                "engine": "google_images",
                "tbm": "isch",
                "q": "coffee",
            }
        )
        self.assertIsNone(data.get("error"))
        self.assertIsNotNone(data["images_results"])
        # os.getenv("API_KEY") is your secret API Key
        # copy/paste from [http://serpapi.com/dashboard] to your bash
        # ```export API_KEY="your_secure_api_key"```
