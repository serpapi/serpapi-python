# Example: google_light search engine
import pytest
import os
import serpapi

def test_search_google_light(client):
  data = client.search({
      'engine': 'google_light',
      'q': 'coffee',
  })
  assert data.get('error') is None
  assert data['organic_results']
