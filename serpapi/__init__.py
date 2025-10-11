"""
SerpApi Python Client Library

Official Python client for SerpApi.com - Search Engine Results API.
Integrate search data into your AI workflow, RAG / fine-tuning, or Python application.

Supports Google, Google Maps, Google Shopping, Baidu, Yandex, Yahoo, eBay, App Stores, and more.
"""

from .error import SerpApiError
from .version import __version__

# Import Client only when aiohttp is available
try:
    from .client import Client

    __all__ = ["Client", "SerpApiError", "__version__"]
except ImportError:
    __all__ = ["SerpApiError", "__version__"]
