"""Tests for proxywhirl.utils module.

Unit tests for utility functions including fetch operations with retries.
"""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from tenacity import RetryError

from proxywhirl.utils import fetch, fetch_json, fetch_text


@pytest.mark.asyncio
class TestFetchUtils:
    """Test utility fetch functions."""

    @patch("proxywhirl.utils.httpx.AsyncClient")
    async def test_fetch_success(self, mock_async_client):
        """Test successful fetch operation."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.raise_for_status.return_value = None
        mock_async_client.return_value.__aenter__.return_value.get.return_value = mock_response

        result = await fetch("http://example.com")

        assert result == mock_response
        mock_async_client.return_value.__aenter__.return_value.get.assert_called_once_with(
            "http://example.com"
        )
        mock_response.raise_for_status.assert_called_once()

    @patch("proxywhirl.utils.httpx.AsyncClient")
    async def test_fetch_with_custom_timeout(self, mock_async_client):
        """Test fetch with custom timeout."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.raise_for_status.return_value = None
        mock_async_client.return_value.__aenter__.return_value.get.return_value = mock_response

        result = await fetch("http://example.com", timeout=10.0)

        assert result == mock_response
        mock_async_client.assert_called_once_with(timeout=10.0)

    @patch("proxywhirl.utils.httpx.AsyncClient")
    async def test_fetch_retry_on_failure(self, mock_async_client):
        """Test fetch retry behavior on failure."""
        mock_async_client.return_value.__aenter__.return_value.get.side_effect = httpx.HTTPError(
            "Connection failed"
        )

        with pytest.raises(RetryError):
            await fetch("http://example.com")

        assert mock_async_client.return_value.__aenter__.return_value.get.call_count == 3

    @patch("proxywhirl.utils.httpx.AsyncClient")
    async def test_fetch_http_error(self, mock_async_client):
        """Test fetch with HTTP error status."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=Mock(), response=Mock()
        )
        mock_async_client.return_value.__aenter__.return_value.get.return_value = mock_response

        with pytest.raises(RetryError):
            await fetch("http://example.com")

    @patch("proxywhirl.utils.fetch", new_callable=AsyncMock)
    async def test_fetch_text_success(self, mock_fetch):
        """Test successful fetch_text operation."""
        mock_response = Mock()
        mock_response.text = "Hello, World!"
        mock_fetch.return_value = mock_response

        result = await fetch_text("http://example.com")

        assert result == "Hello, World!"
        mock_fetch.assert_called_once_with("http://example.com", timeout=30.0)

    @patch("proxywhirl.utils.fetch", new_callable=AsyncMock)
    async def test_fetch_text_with_timeout(self, mock_fetch):
        """Test fetch_text with custom timeout."""
        mock_response = Mock()
        mock_response.text = "Hello, World!"
        mock_fetch.return_value = mock_response

        result = await fetch_text("http://example.com", timeout=15.0)

        assert result == "Hello, World!"
        mock_fetch.assert_called_once_with("http://example.com", timeout=15.0)

    @patch("proxywhirl.utils.fetch", new_callable=AsyncMock)
    async def test_fetch_text_failure(self, mock_fetch):
        """Test fetch_text failure."""
        mock_fetch.side_effect = httpx.HTTPError("Connection failed")

        with pytest.raises(RetryError):
            await fetch_text("http://example.com")

    @patch("proxywhirl.utils.fetch", new_callable=AsyncMock)
    async def test_fetch_json_success(self, mock_fetch):
        """Test successful fetch_json operation."""
        mock_response = Mock()
        mock_response.json.return_value = {"key": "value", "number": 42}
        mock_fetch.return_value = mock_response

        result = await fetch_json("http://example.com/api")

        assert result == {"key": "value", "number": 42}
        mock_fetch.assert_called_once_with("http://example.com/api", timeout=30.0)
        mock_response.json.assert_called_once()

    @patch("proxywhirl.utils.fetch", new_callable=AsyncMock)
    async def test_fetch_json_with_timeout(self, mock_fetch):
        """Test fetch_json with custom timeout."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": [1, 2, 3]}
        mock_fetch.return_value = mock_response

        result = await fetch_json("http://example.com/api", timeout=20.0)

        assert result == {"data": [1, 2, 3]}
        mock_fetch.assert_called_once_with("http://example.com/api", timeout=20.0)

    @patch("proxywhirl.utils.fetch", new_callable=AsyncMock)
    async def test_fetch_json_parse_error(self, mock_fetch):
        """Test fetch_json with JSON parse error."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_fetch.return_value = mock_response

        with pytest.raises(RetryError):
            await fetch_json("http://example.com/api")

    @patch("proxywhirl.utils.fetch", new_callable=AsyncMock)
    async def test_fetch_json_failure(self, mock_fetch):
        """Test fetch_json failure."""
        mock_fetch.side_effect = httpx.HTTPError("Connection failed")

        with pytest.raises(RetryError):
            await fetch_json("http://example.com/api")

    def test_fetch_functions_have_retry_decorators(self):
        """Test that fetch functions have retry decorators configured."""
        assert hasattr(fetch, "retry")
        assert hasattr(fetch_text, "retry")
        assert hasattr(fetch_json, "retry")

    @patch("proxywhirl.utils.httpx.AsyncClient")
    async def test_fetch_context_manager_cleanup(self, mock_async_client):
        """Test that httpx.AsyncClient context manager is properly cleaned up."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.raise_for_status.return_value = None
        mock_async_client.return_value.__aenter__.return_value.get.return_value = mock_response

        await fetch("http://example.com")

        mock_async_client.return_value.__aenter__.assert_called_once()
        mock_async_client.return_value.__aexit__.assert_called_once()

    @patch("proxywhirl.utils.httpx.AsyncClient")
    async def test_fetch_exception_during_cleanup(self, mock_async_client):
        """Test fetch behavior when exception occurs during cleanup."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.raise_for_status.return_value = None
        mock_async_client.return_value.__aenter__.return_value.get.return_value = mock_response
        mock_async_client.return_value.__aexit__.side_effect = Exception("Cleanup failed")

        with pytest.raises(Exception, match="Cleanup failed"):
            await fetch("http://example.com")
