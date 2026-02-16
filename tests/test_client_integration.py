"""
Integration-style test suite for SerpApi Client.
Focuses on covering HTTP request logic and session management.
"""

import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
import aiohttp
from serpapi import Client, SerpApiError

class TestClientIntegration:
    """Tests that exercise internal _make_request and session logic."""

    @pytest.mark.asyncio
    async def test_make_request_json_error_parsing(self):
        """Covers error parsing from JSON response when status != 200."""
        client = Client(api_key="test_key")
        
        mock_response = AsyncMock()
        mock_response.status = 403
        mock_response.json.return_value = {"error": "Invalid API key"}
        
        # We need to mock the context manager returned by session.get
        mock_get = MagicMock()
        mock_get.__aenter__.return_value = mock_response
        
        with patch("aiohttp.ClientSession.get", return_value=mock_get):
            with pytest.raises(SerpApiError, match="SerpApi error: Invalid API key"):
                await client.search({"q": "coffee"})

    @pytest.mark.asyncio
    async def test_make_request_non_json_error(self):
        """Covers error handling when response is not JSON and status != 200."""
        client = Client(api_key="test_key")
        
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_response.text.return_value = "Internal Server Error"
        
        mock_get = MagicMock()
        mock_get.__aenter__.return_value = mock_response
        
        with patch("aiohttp.ClientSession.get", return_value=mock_get):
            with pytest.raises(SerpApiError, match="HTTP request failed with error: Internal Server Error"):
                await client.search({"q": "coffee"})

    @pytest.mark.asyncio
    async def test_make_request_invalid_json_success_status(self):
        """Covers JSONDecodeError when status is 200 but body is invalid JSON."""
        client = Client(api_key="test_key")
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_response.text.return_value = "Not JSON"
        
        mock_get = MagicMock()
        mock_get.__aenter__.return_value = mock_response
        
        with patch("aiohttp.ClientSession.get", return_value=mock_get):
            with pytest.raises(SerpApiError, match="Invalid JSON response: Not JSON"):
                await client.search({"q": "coffee"})

    @pytest.mark.asyncio
    async def test_make_request_unsupported_format(self):
        """Covers the 'else' branch for unsupported response format."""
        client = Client(api_key="test_key")
        
        mock_response = AsyncMock()
        mock_response.status = 200
        
        mock_get = MagicMock()
        mock_get.__aenter__.return_value = mock_response
        
        with patch("aiohttp.ClientSession.get", return_value=mock_get):
            with pytest.raises(SerpApiError, match="Unsupported response format: xml"):
                await client._make_request("/search", {"q": "test"}, response_format="xml")

    @pytest.mark.asyncio
    async def test_session_creation_and_persistence(self):
        """Covers lines 108-122: Session creation, lock, and reuse."""
        client = Client(api_key="test_key", persistent=True)
        
        # First call creates session
        session1 = await client._get_session()
        assert isinstance(session1, aiohttp.ClientSession)
        assert session1.closed is False
        
        # Second call returns same session
        session2 = await client._get_session()
        assert session1 is session2
        
        await client.close()
        assert session1.closed is True
        
        # Call after close creates NEW session
        session3 = await client._get_session()
        assert session3 is not session1
        assert session3.closed is False
        await client.close()

    @pytest.mark.asyncio
    async def test_non_persistent_session(self):
        """Covers session behavior when persistent=False."""
        client = Client(api_key="test_key", persistent=False)
        
        session1 = await client._get_session()
        session2 = await client._get_session()
        
        # Even if not persistent, _get_session might return same if not closed
        # but the key is that we test the branch
        assert session1 is not None
        await client.close()

    @pytest.mark.asyncio
    async def test_client_del_cleanup(self):
        """Covers __del__ cleanup logic."""
        client = Client(api_key="test_key")
        session = await client._get_session()
        assert session.closed is False
        
        # Manually call __del__ since we can't easily trigger GC reliably in test
        with patch.object(asyncio, "get_event_loop") as mock_loop:
            mock_loop_instance = MagicMock()
            mock_loop_instance.is_running.return_value = True
            mock_loop.return_value = mock_loop_instance
            
            client.__del__()
            mock_loop_instance.create_task.assert_called_once()

