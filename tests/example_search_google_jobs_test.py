# Example: google_jobs search engine
import pytest
import os
import serpapi

def test_search_google_jobs(client):
  data = client.search({
      'engine': 'google_jobs',
      'q': 'coffee',
  })
  assert data.get('error') is None
  assert data['jobs_results']
