# SerpApi Python Library

Official Python client for SerpApi.com - Search Engine Results API.

## Features

- Async/await support for non-blocking HTTP requests
- Persistent connections for 2x faster response times
- Multiple search engines (Google, Bing, Yahoo, Baidu, Yandex, etc.)
- Comprehensive API coverage (Search, Location, Account, Search Archive)
- Type hints and extensive documentation

## Installation

```bash
# Using pip
pip install serpapi

# Using uv (recommended)
uv add serpapi
```

## Quick Start

```python
import asyncio
from serpapi import Client

async def main():
    client = Client(api_key="your_api_key", engine="google")
    results = await client.search({"q": "coffee"})
    
    for result in results.get("organic_results", []):
        print(f"Title: {result.get('title')}")
        print(f"Link: {result.get('link')}")
    
    await client.close()

asyncio.run(main())
```

 → [SerpApi documentation](https://serpapi.com/search-api).

## API Key

Get your API key from [serpapi.com/signup](https://serpapi.com/users/sign_up?plan=free).

Set environment variable:
```bash
export SERPAPI_KEY="your_secret_key"
```

#### Documentations
This library is well documented, and you can find the following resources:
 * [Full documentation on SerpApi.com](https://serpapi.com)
 * [Library Github page](https://github.com/serpapi/serpapi-ruby)
 * [Library GEM page](https://rubygems.org/gems/serpapi/)
 * [Library API documentation](https://rubydoc.info/github/serpapi/serpapi-ruby/master)
 * [API health status](https://serpapi.com/status)

## Usage Examples

### Basic Search
```python
results = await client.search({"q": "coffee"})
print(f"Found {len(results.get('organic_results', []))} organic results")
```

### HTML Search
```python
html_content = await client.html({"q": "coffee"})
print(f"HTML content length: {len(html_content)} characters")
```

### Location API
```python
locations = await client.location({"q": "Austin", "limit": 3})
print(f"Found {len(locations)} locations")
```

### Search Archive
```python
archived = await client.search_archive(search_id)
print(f"Retrieved archived search: {archived.get('search_metadata', {}).get('id')}")
```

### Account Info
```python
account = await client.account()
print(f"Account plan: {account.get('plan')}")
```

## Async Batch Processing

```python
import asyncio

async def search_company(client, company):
    results = await client.search({"q": company})
    return {"company": company, "count": len(results.get("organic_results", []))}

async def main():
    client = Client(api_key="your_api_key", persistent=True)
    companies = ["meta", "amazon", "apple", "netflix", "google"]
    
    tasks = [search_company(client, company) for company in companies]
    results = await asyncio.gather(*tasks)
    
    for result in results:
        print(f"{result['company']}: {result['count']} results")
    
    await client.close()

asyncio.run(main())
```

## Context Manager

```python
async with Client(api_key="your_api_key") as client:
    results = await client.search({"q": "coffee"})
    # Client automatically closed
```

## Error Handling

```python
from serpapi import SerpApiError

try:
    results = await client.search({"q": "coffee"})
except SerpApiError as e:
    print(f"SerpApi error: {e}")
```

## Developer guide
 
The UV Package Manager must be installed. See [uv installation instructions](https://docs.astral.sh/uv/getting-started/installation).

The library also includes a `Rakefile` for developers coming from the Ruby ecosystem, providing a familiar interface for common tasks:

```bash
# Run tests with coverage
rake coverage

# Run all quality checks (lint, test, coverage)
rake default

# Build and test local package
rake oobt
```

The following commands are also available via `uv`:

```bash
# Install dependencies (including formatting tools)
uv sync --dev
# Run tests
uv run pytest

# Run test with coverage
uv run pytest --cov=serpapi tests/

# Type checking with mypy
uv run mypy serpapi/

# Format code with black
uv run black serpapi/

# Sort imports with isort  
uv run isort serpapi/

# Check formatting without making changes
uv run black --check .
uv run isort --check-only .
```

### UV Benefits

- **Fast**: 10-100x faster than pip
- **Reliable**: Lock file ensures reproducible builds
- **Simple**: Single command for most operations
- **Modern**: Built for Python 3.11+ with async support

### Project Structure with UV

```
serpapi-python/
├── .python-version          # Python version (3.11)
├── uv.lock                  # Dependency lock file
├── .venv/                   # Virtual environment (auto-created)
├── pyproject.toml           # Project configuration
├── serpapi/                 # Package source code
├── tests/                   # Test suite
├── examples/                # Usage examples
└── README.md               # This file
```

## License

MIT License - see LICENSE file for details.
