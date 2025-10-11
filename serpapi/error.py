"""
SerpApi error handling module.
"""


class SerpApiError(Exception):
    """
    SerpApiError wraps any errors related to the SerpApi client.

    Handles the following types of errors:
    - HTTP response errors from SerpApi.com
    - Missing API key
    - Credit limit exceeded
    - Incorrect query parameters
    - JSON parsing errors
    - Network timeouts
    - And more...
    """

    pass
