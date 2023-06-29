import random
import unittest
import os
import serpapi


class TestAccountApi(unittest.TestCase):
    @unittest.skipIf((os.getenv("API_KEY") == None), "no api_key provided")
    def test_get_account(self):
        client = serpapi.Client()
        account = client.account(os.getenv("API_KEY"))
        self.assertIsNotNone(account.get("account_id"))
