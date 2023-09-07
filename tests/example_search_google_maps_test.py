# Example: google_maps search engine
import pytest
import os
import serpapi

def test_search_google_maps(client):
  data = client.search({
      'engine': 'google_maps',
      'q': 'pizza',
      'll': '@40.7455096,-74.0083012,15.1z',
      'type': 'search',
  })
  assert data.get('error') is None
  assert data['local_results']
