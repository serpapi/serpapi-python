# Example: youtube search engine
import pytest
import os
import serpapi

def test_search_youtube(client):

  data = client.search({
      'engine': 'youtube',
      'search_query': 'coffee',
  })
  assert data.get('error') is None
  assert data['video_results']
