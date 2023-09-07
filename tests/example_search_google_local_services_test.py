# Example: google_local_services search engine
import pytest
import os
import serpapi

def test_search_google_local_services(client):

  data = client.search({
      'engine': 'google_local_services',
      'q': 'electrician',
      'data_cid': '6745062158417646970',
  })
  assert data.get('error') is None
  assert data['local_ads']
