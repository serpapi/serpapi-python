"""
Client implementation for SerpApi.com

Powered by aiohttp for async HTTP requests and persistent connections.
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Literal, Optional, Union, overload
from urllib.parse import urlencode

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from .error import SerpApiError
from .version import __version__


class Client:
    """
    Client for SerpApi.com

    Features:
    - Async non-blocking search
    - Persistent HTTP connections
    - Search API
    - Location API
    - Account API
    - Search Archive API
    """

    # Backend service URL
    BACKEND = "serpapi.com"

    def __init__(
        self,
        api_key: Optional[str] = None,
        engine: str = "google",
        persistent: bool = True,
        async_mode: bool = False,
        timeout: int = 120,
        symbolize_names: bool = True,
        **kwargs: Any,
    ):
        """
        Initialize SerpApi client.

        Args:
            api_key: User secret API key. If None, will try to get from SERPAPI_KEY env var.
            engine: Default search engine selection.
            persistent: Keep socket connection open for faster response times (2x faster).
            async_mode: Enable async mode for non-blocking operations.
            timeout: HTTP request timeout in seconds.
            symbolize_names: Convert JSON keys to symbols (not applicable in Python, kept for compatibility).
            **kwargs: Additional parameters to store as default parameters.

        Raises:
            SerpApiError: If parameters are invalid.
        """
        if api_key is None:
            api_key = os.getenv("SERPAPI_KEY")
            if api_key is None:
                raise SerpApiError(
                    "API key is required. Set api_key parameter or SERPAPI_KEY environment variable."
                )

        # Store configuration
        self._timeout = timeout
        self._persistent = persistent
        self._async_mode = async_mode
        self._symbolize_names = symbolize_names

        # Set default query parameters
        self._params = {
            "api_key": api_key,
            "engine": engine,
            "source": f"serpapi-python:{__version__}",
            **kwargs,
        }

        # HTTP client session (will be created when needed)
        self._session: Optional[ClientSession] = None
        self._session_lock = asyncio.Lock()

    @property
    def timeout(self) -> int:
        """Get HTTP timeout in seconds."""
        return self._timeout

    @property
    def persistent(self) -> bool:
        """Check if persistent connections are enabled."""
        return self._persistent

    @property
    def engine(self) -> str:
        """Get default search engine."""
        return str(self._params.get("engine", "google"))

    @property
    def api_key(self) -> str:
        """Get API key."""
        return str(self._params.get("api_key", ""))

    async def _get_session(self) -> ClientSession:
        """Get or create HTTP session."""
        if not self._persistent or self._session is None or self._session.closed:
            async with self._session_lock:
                if (
                    not self._persistent
                    or self._session is None
                    or self._session.closed
                ):
                    timeout = ClientTimeout(total=self._timeout)
                    connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
                    self._session = ClientSession(
                        timeout=timeout,
                        connector=connector,
                        base_url=f"https://{self.BACKEND}",
                    )
        return self._session

    def _merge_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge runtime parameters with default parameters.

        Args:
            params: Runtime parameters to merge.

        Returns:
            Merged parameters after cleanup.

        Raises:
            SerpApiError: If params is not a dictionary.
        """
        if not isinstance(params, dict):
            raise SerpApiError(f"params must be dict, not: {type(params)}")

        # Merge default params with custom params
        merged = self._params.copy()
        merged.update(params)

        # Remove client-specific configuration
        merged.pop("symbolize_names", None)

        # Remove None values
        return {k: v for k, v in merged.items() if v is not None}

    @overload
    async def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any],
        response_format: Literal["json"] = "json",
    ) -> Dict[str, Any]: ...

    @overload
    async def _make_request(
        self, endpoint: str, params: Dict[str, Any], response_format: Literal["html"]
    ) -> str: ...

    async def _make_request(
        self, endpoint: str, params: Dict[str, Any], response_format: str = "json"
    ) -> Union[Dict[str, Any], str]:
        """
        Make HTTP request to SerpApi backend.

        Args:
            endpoint: API endpoint path.
            params: Request parameters.
            response_format: Response format ('json' or 'html').

        Returns:
            Response data as dict (JSON) or str (HTML).

        Raises:
            SerpApiError: If request fails or response is invalid.
        """
        session = await self._get_session()
        query_params = self._merge_params(params)

        try:
            async with session.get(endpoint, params=query_params) as response:
                if response.status != 200:
                    try:
                        data = await response.json()
                        if isinstance(data, dict) and "error" in data:
                            raise SerpApiError(
                                f"SerpApi error: {data['error']}"
                                f" from url: https://{self.BACKEND}{endpoint} with status: {response.status}"
                            )
                    except json.JSONDecodeError:
                        err = await response.text()
                        raise SerpApiError(
                            f"HTTP request failed with error: {err}"
                            f" from url: https://{self.BACKEND}{endpoint} with status: {response.status}"
                        )

                if response_format == "json":
                    try:
                        data = await response.json()
                        if isinstance(data, dict) and "error" in data:
                            raise SerpApiError(f"SerpApi error: {data['error']}")
                        return data  # type: ignore
                    except json.JSONDecodeError:
                        text = await response.text()
                        raise SerpApiError(f"Invalid JSON response: {text}")

                elif response_format == "html":
                    return await response.text()

                else:
                    raise SerpApiError(
                        f"Unsupported response format: {response_format}"
                    )

        except aiohttp.ClientError as e:
            raise SerpApiError(f"HTTP client error: {e}")

    async def search(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform a search using SerpApi.com

        Args:
            params: Search parameters including engine, query, etc.

        Returns:
            Search results as a dictionary.
        """
        if params is None:
            params = {}
        return await self._make_request("/search", params, "json")

    async def html(self, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Perform a search and return raw HTML.

        Useful for training AI models, RAG, debugging, or custom parsing.

        Args:
            params: Search parameters.

        Returns:
            Raw HTML search results directly from the search engine.
        """
        if params is None:
            params = {}
        return await self._make_request("/search", params, "html")

    async def location(
        self, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get location suggestions using Location API.

        Args:
            params: Location parameters including 'q' (query) and 'limit'.

        Returns:
            List of matching locations.
        """
        if params is None:
            params = {}
        result = await self._make_request("/locations.json", params, "json")
        return result  # type: ignore

    async def search_archive(
        self, search_id: Union[str, int], format_type: str = "json"
    ) -> Union[Dict[str, Any], str]:
        """
        Retrieve search result from the Search Archive API.

        Args:
            search_id: Search ID from original search results.
            format_type: Response format ('json' or 'html').

        Returns:
            Archived search results as dict (JSON) or str (HTML).

        Raises:
            SerpApiError: If format_type is invalid.
        """
        if format_type not in ["json", "html"]:
            raise SerpApiError("format_type must be json or html")

        empty_params: Dict[str, Any] = {}
        if format_type == "json":
            json_result: Dict[str, Any] = await self._make_request(
                f"/searches/{search_id}.{format_type}", empty_params, "json"
            )
            return json_result
        elif format_type == "html":
            html_result: str = await self._make_request(
                f"/searches/{search_id}.{format_type}", empty_params, "html"
            )
            return html_result
        else:
            raise SerpApiError("format_type must be json or html")

    async def account(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get account information using Account API.

        Args:
            api_key: API key (optional if already provided to constructor).

        Returns:
            Account information dictionary.
        """
        params = {"api_key": api_key} if api_key else {}
        return await self._make_request("/account", params, "json")

    async def close(self) -> None:
        """Close HTTP session if persistent connections are enabled."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> "Client":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def __del__(self) -> None:
        """Destructor to ensure session is closed."""
        if hasattr(self, "_session") and self._session and not self._session.closed:
            # Schedule the session close in the event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._session.close())
                else:
                    loop.run_until_complete(self._session.close())
            except RuntimeError:
                # No event loop running, can't close session
                pass
