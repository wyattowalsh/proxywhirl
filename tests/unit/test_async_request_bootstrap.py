"""Tests for lazy async request bootstrap behavior."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import Proxy
from proxywhirl.rotator.async_ import AsyncProxyWhirl


class TestAsyncRequestBootstrap:
    """Test lazy bootstrap behavior in async request execution."""

    async def test_bootstrap_failure_is_clear_and_only_attempted_once(self) -> None:
        """Empty bootstrap should raise clear error and avoid repeated fetch attempts."""
        rotator = AsyncProxyWhirl()
        message = "Lazy auto-fetch bootstrap yielded zero proxies from built-in public sources"

        with patch.object(
            rotator, "_bootstrap_pool_if_empty", side_effect=ProxyPoolEmptyError(message)
        ) as bootstrap_mock:
            async with rotator:
                with pytest.raises(
                    ProxyPoolEmptyError, match="Lazy auto-fetch bootstrap yielded zero"
                ):
                    await rotator.get("https://httpbin.org/get")
                with pytest.raises(
                    ProxyPoolEmptyError, match="Lazy auto-fetch bootstrap yielded zero"
                ):
                    await rotator.get("https://httpbin.org/get")

        assert bootstrap_mock.call_count == 1

    async def test_empty_pool_bootstraps_once_then_request_flow_continues(self) -> None:
        """Request flow should continue normally after lazy bootstrap populates the pool."""
        rotator = AsyncProxyWhirl()
        bootstrap_proxy = Proxy(url="http://bootstrap.example.com:8080")

        async def bootstrap_once() -> int:
            await rotator.add_proxy(bootstrap_proxy)
            return 1

        with patch.object(
            rotator, "_bootstrap_pool_if_empty", side_effect=bootstrap_once
        ) as mock_boot:
            with patch("httpx.AsyncClient") as mock_client_class:
                mock_response = AsyncMock(spec=httpx.Response)
                mock_response.status_code = 200
                mock_client = AsyncMock()
                mock_client.request.return_value = mock_response
                mock_client_class.return_value = mock_client

                async with rotator:
                    response = await rotator.get("https://httpbin.org/get")
                    assert response.status_code == 200
                    await rotator.get("https://httpbin.org/get")

        assert mock_boot.call_count == 1

    async def test_bootstrap_guard_is_async_safe_and_one_time(self) -> None:
        """Concurrent request-time bootstrap checks should trigger one bootstrap call."""
        rotator = AsyncProxyWhirl()
        call_count = 0

        async def bootstrap_once() -> int:
            nonlocal call_count
            await asyncio.sleep(0.05)  # Simulate delay
            call_count += 1
            await rotator.add_proxy(Proxy(url="http://async-safe-bootstrap.example.com:8080"))
            return 1

        with patch.object(rotator, "_bootstrap_pool_if_empty", side_effect=bootstrap_once):
            # Run multiple concurrent bootstrap attempts
            tasks = [rotator._ensure_request_bootstrap() for _ in range(5)]
            await asyncio.gather(*tasks, return_exceptions=True)

        assert call_count == 1

    async def test_successful_bootstrap_populates_pool_with_proxies(self) -> None:
        """Successful bootstrap should populate pool with fetched proxies."""
        rotator = AsyncProxyWhirl()
        bootstrap_proxies = [Proxy(url=f"http://bootstrap{i}.example.com:8080") for i in range(3)]

        async def mock_bootstrap() -> int:
            for proxy in bootstrap_proxies:
                await rotator.add_proxy(proxy)
            return len(bootstrap_proxies)

        with patch.object(rotator, "_bootstrap_pool_if_empty", side_effect=mock_bootstrap):
            async with rotator:
                # Bootstrap should be triggered on first request
                with patch("httpx.AsyncClient") as mock_client_class:
                    mock_response = AsyncMock(spec=httpx.Response)
                    mock_response.status_code = 200
                    mock_client = AsyncMock()
                    mock_client.request.return_value = mock_response
                    mock_client_class.return_value = mock_client

                    await rotator.get("https://httpbin.org/get")

        assert rotator.pool.size == 3

    async def test_bootstrap_skipped_when_pool_not_empty(self) -> None:
        """Bootstrap should be skipped when pool already has proxies."""
        initial_proxy = Proxy(url="http://initial.example.com:8080")
        rotator = AsyncProxyWhirl(proxies=[initial_proxy])

        with patch.object(rotator, "_bootstrap_pool_if_empty", return_value=0) as bootstrap_mock:
            async with rotator:
                with patch("httpx.AsyncClient") as mock_client_class:
                    mock_response = AsyncMock(spec=httpx.Response)
                    mock_response.status_code = 200
                    mock_client = AsyncMock()
                    mock_client.request.return_value = mock_response
                    mock_client_class.return_value = mock_client

                    await rotator.get("https://httpbin.org/get")

        # Bootstrap should never be called since pool was not empty
        bootstrap_mock.assert_not_called()

    async def test_bootstrap_error_cached_for_subsequent_requests(self) -> None:
        """Bootstrap failure error should be cached and re-raised without re-attempting."""
        rotator = AsyncProxyWhirl()
        error_message = "Lazy auto-fetch bootstrap yielded zero proxies"

        call_count = 0

        async def failing_bootstrap() -> int:
            nonlocal call_count
            call_count += 1
            raise ProxyPoolEmptyError(error_message)

        with patch.object(rotator, "_bootstrap_pool_if_empty", side_effect=failing_bootstrap):
            async with rotator:
                # First request triggers bootstrap
                with pytest.raises(ProxyPoolEmptyError, match=error_message):
                    await rotator._make_request("GET", "https://httpbin.org/get")

                # Second request should raise cached error without calling bootstrap again
                with pytest.raises(ProxyPoolEmptyError, match=error_message):
                    await rotator._make_request("GET", "https://httpbin.org/get")

        # Bootstrap should only be attempted once
        assert call_count == 1
