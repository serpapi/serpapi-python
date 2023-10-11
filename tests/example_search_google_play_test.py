# Example: google_play search engine
import pytest
import os
import serpapi

def test_search_google_play(client):
  data = client.search({
      'engine': 'google_play',
      'q': 'kite',
      'store': 'apps',
      'max_results': '2',
  })
  assert data.get('error') is None
  assert data['organic_results']
