# Example: google_images search engine
import pytest
import os
import serpapi

def test_search_google_images(client):
  data = client.search({
      'engine': 'google_images',
      'engine': 'google_images',
      'tbm': 'isch',
      'q': 'coffee',
  })
  assert data.get('error') is None
  assert data['images_results']
