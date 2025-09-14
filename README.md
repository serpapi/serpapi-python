# SerpApi Python Library

Official Python client for SerpApi.com - Search Engine Results API.

## Features

- Async/await support for non-blocking HTTP requests
- Persistent connections for 2x faster response times
- Multiple search engines (Google, Bing, Yahoo, Baidu, Yandex, etc.)
- Comprehensive API coverage (Search, Location, Account, Search Archive)
- Type hints and extensive documentation

## Installation

### Using pip

```bash
pip install serpapi
```

### Using uv (recommended)

```bash
# Install with uv
uv add serpapi

# Or clone and install locally
git clone https://github.com/serpapi/serpapi-python.git
cd serpapi-python
uv sync
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/serpapi/serpapi-python.git
cd serpapi-python

# Install with uv (recommended)
uv sync --dev

# Or with pip
pip install -e ".[dev]"
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

## API Key

Get your API key from [serpapi.com/signup](https://serpapi.com/users/sign_up?plan=free).

Set environment variable:
```bash
export SERPAPI_KEY="your_secret_key"
```

## Usage Examples

### Basic Search
```python
results = await client.search({"q": "coffee"})
```

### HTML Search
```python
html_content = await client.html({"q": "coffee"})
```

### Location API
```python
locations = await client.location({"q": "Austin", "limit": 3})
```

### Search Archive
```python
archived = await client.search_archive(search_id)
```

### Account Info
```python
account = await client.account()
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

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy serpapi/
```

## UV Package Manager

This project is fully configured for [uv](https://docs.astral.sh/uv/), a fast Python package manager.

### UV Commands

```bash
# Install all dependencies
uv sync

# Install with development dependencies
uv sync --dev

# Run Python scripts
uv run python script.py

# Run tests
uv run pytest

# Add new dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Show installed packages
uv pip list

# Update dependencies
uv sync --upgrade
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
