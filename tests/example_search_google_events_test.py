# Example: google_events search engine
import pytest
import os
import serpapi

def test_search_google_events(client):
  data = client.search({
      'engine': 'google_events',
      'q': 'coffee',
  })
  assert data.get('error') is None
  assert data['events_results']
