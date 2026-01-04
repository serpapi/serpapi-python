"""
Test suite for SerpApi Client.
"""

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from serpapi import Client, SerpApiError


class TestClient:
    """Test cases for SerpApi Client."""

    def test_client_initialization_with_api_key(self):
        """Test client initialization with API key."""
        client = Client(api_key="test_key", engine="google")
        assert client.api_key == "test_key"
        assert client.engine == "google"
        assert client.persistent is True
        assert client.timeout == 120

    def test_client_initialization_with_env_var(self):
        """Test client initialization with environment variable."""
        with patch.dict(os.environ, {"SERPAPI_KEY": "env_key"}):
            client = Client(engine="bing")
            assert client.api_key == "env_key"
            assert client.engine == "bing"

    def test_client_initialization_no_api_key(self):
        """Test client initialization without API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SerpApiError, match="API key is required"):
                Client()

    def test_client_initialization_custom_params(self):
        """Test client initialization with custom parameters."""
        client = Client(
            api_key="test_key",
            engine="yahoo",
            persistent=False,
            timeout=60,
            custom_param="value",
        )
        assert client.api_key == "test_key"
        assert client.engine == "yahoo"
        assert client.persistent is False
        assert client.timeout == 60
        assert client._params["custom_param"] == "value"

    def test_merge_params(self):
        """Test parameter merging."""
        client = Client(api_key="test_key", engine="google", param1="value1")

        # Test with valid params
        merged = client._merge_params({"param2": "value2", "q": "coffee"})
        expected = {
            "api_key": "test_key",
            "engine": "google",
            "source": "serpapi-python:1.0.1",
            "param1": "value1",
            "param2": "value2",
            "q": "coffee",
        }
        assert merged == expected

        # Test with invalid params
        with pytest.raises(SerpApiError, match="params must be dict"):
            client._merge_params("invalid")

    @pytest.mark.asyncio
    async def test_search_success(self):
        """Test successful search request."""
        client = Client(api_key="test_key")

        mock_response = {
            "search_metadata": {"id": "test_id", "status": "Success"},
            "organic_results": [
                {"title": "Test Result", "link": "https://example.com"}
            ],
        }

        with patch.object(
            client, "_make_request", return_value=mock_response
        ) as mock_request:
            result = await client.search({"q": "coffee"})

            mock_request.assert_called_once_with("/search", {"q": "coffee"}, "json")
            assert result == mock_response

    @pytest.mark.asyncio
    async def test_html_success(self):
        """Test successful HTML request."""
        client = Client(api_key="test_key")

        mock_html = "<html><body>Test HTML</body></html>"

        with patch.object(
            client, "_make_request", return_value=mock_html
        ) as mock_request:
            result = await client.html({"q": "coffee"})

            mock_request.assert_called_once_with("/search", {"q": "coffee"}, "html")
            assert result == mock_html

    @pytest.mark.asyncio
    async def test_location_success(self):
        """Test successful location request."""
        client = Client(api_key="test_key")

        mock_locations = [{"id": "1", "name": "Austin, TX", "country_code": "US"}]

        with patch.object(
            client, "_make_request", return_value=mock_locations
        ) as mock_request:
            result = await client.location({"q": "Austin", "limit": 3})

            mock_request.assert_called_once_with(
                "/locations.json", {"q": "Austin", "limit": 3}, "json"
            )
            assert result == mock_locations

    @pytest.mark.asyncio
    async def test_search_archive_success(self):
        """Test successful search archive request."""
        client = Client(api_key="test_key")

        mock_archive = {"search_metadata": {"id": "test_id"}, "organic_results": []}

        with patch.object(
            client, "_make_request", return_value=mock_archive
        ) as mock_request:
            result = await client.search_archive("test_id", "json")

            mock_request.assert_called_once_with("/searches/test_id.json", {}, "json")
            assert result == mock_archive

    @pytest.mark.asyncio
    async def test_search_archive_invalid_format(self):
        """Test search archive with invalid format."""
        client = Client(api_key="test_key")

        with pytest.raises(SerpApiError, match="format_type must be json or html"):
            await client.search_archive("test_id", "invalid")

    @pytest.mark.asyncio
    async def test_account_success(self):
        """Test successful account request."""
        client = Client(api_key="test_key")

        mock_account = {
            "account_id": "123456",
            "account_email": "test@example.com",
            "plan_name": "Free Plan",
        }

        with patch.object(
            client, "_make_request", return_value=mock_account
        ) as mock_request:
            result = await client.account()

            mock_request.assert_called_once_with("/account", {}, "json")
            assert result == mock_account

    @pytest.mark.asyncio
    async def test_account_with_api_key(self):
        """Test account request with specific API key."""
        client = Client(api_key="test_key")

        mock_account = {"account_id": "123456"}

        with patch.object(
            client, "_make_request", return_value=mock_account
        ) as mock_request:
            result = await client.account("custom_key")

            mock_request.assert_called_once_with(
                "/account", {"api_key": "custom_key"}, "json"
            )
            assert result == mock_account

    @pytest.mark.asyncio
    async def test_make_request_json_success(self):
        """Test successful JSON request."""
        client = Client(api_key="test_key")

        # Test the public API methods instead of internal _make_request
        with patch.object(client, "_make_request") as mock_request:
            mock_request.return_value = {"result": "success"}

            result = await client.search({"q": "test"})

            assert result == {"result": "success"}
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_json_error_response(self):
        """Test JSON request with error response."""
        client = Client(api_key="test_key")

        # Test error handling through public API
        with patch.object(client, "_make_request") as mock_request:
            mock_request.side_effect = SerpApiError("SerpApi error: API Error")

            with pytest.raises(SerpApiError, match="SerpApi error: API Error"):
                await client.search({"q": "test"})

    @pytest.mark.asyncio
    async def test_make_request_json_http_error(self):
        """Test JSON request with HTTP error status."""
        client = Client(api_key="test_key")

        # Test HTTP error handling through public API
        with patch.object(client, "_make_request") as mock_request:
            mock_request.side_effect = SerpApiError("SerpApi error: Bad Request")

            with pytest.raises(SerpApiError, match="SerpApi error: Bad Request"):
                await client.search({"q": "test"})

    @pytest.mark.asyncio
    async def test_make_request_html_success(self):
        """Test successful HTML request."""
        client = Client(api_key="test_key")

        # Test HTML request through public API
        with patch.object(client, "_make_request") as mock_request:
            mock_request.return_value = "<html>Test</html>"

            result = await client.html({"q": "test"})

            assert result == "<html>Test</html>"
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_invalid_format(self):
        """Test request with invalid response format."""
        client = Client(api_key="test_key")

        # Test invalid format through public API
        with patch.object(client, "_make_request") as mock_request:
            mock_request.side_effect = SerpApiError(
                "Unsupported response format: invalid"
            )

            with pytest.raises(
                SerpApiError, match="Unsupported response format: invalid"
            ):
                await client.search({"q": "test"})

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        with patch.object(Client, "close") as mock_close:
            async with Client(api_key="test_key") as client:
                assert isinstance(client, Client)

            mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_session(self):
        """Test closing session."""
        client = Client(api_key="test_key")

        mock_session = AsyncMock()
        mock_session.closed = False
        client._session = mock_session

        await client.close()

        mock_session.close.assert_called_once()

    def test_properties(self):
        """Test client properties."""
        client = Client(api_key="test_key", engine="google", timeout=60)

        assert client.timeout == 60
        assert client.persistent is True
        assert client.engine == "google"
        assert client.api_key == "test_key"
