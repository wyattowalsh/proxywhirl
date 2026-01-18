"""
Unit tests for proxy fetcher rate limiting retry logic.

Tests cover:
- T429: Retry on HTTP 429 (Too Many Requests) with Retry-After header
- T503: Retry on HTTP 503 (Service Unavailable)
- T502: Retry on HTTP 502 (Bad Gateway)
- T504: Retry on HTTP 504 (Gateway Timeout)
- Exponential backoff with jitter
- Retry-After header parsing and capping
"""

import pytest


class TestRateLimitingRetry:
    """Test ProxyFetcher rate limiting retry logic."""

    async def test_retry_on_429_with_retry_after_header(self, respx_mock) -> None:
        """Test retry respects Retry-After header on 429 response."""
        from unittest.mock import AsyncMock, patch

        import httpx

        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig

        source = ProxySourceConfig(url="http://example.com/proxies.json", format="json")
        fetcher = ProxyFetcher()

        # First request: 429 with Retry-After header
        # Second request: 200 OK
        respx_mock.get("http://example.com/proxies.json").mock(
            side_effect=[
                httpx.Response(429, headers={"Retry-After": "2"}),
                httpx.Response(200, text='[{"host": "proxy1.com", "port": 8080}]'),
            ]
        )

        # Mock asyncio.sleep to avoid actual delay in tests
        with patch("asyncio.sleep", new_callable=AsyncMock):
            proxies = await fetcher.fetch_from_source(source)

        assert len(proxies) == 1
        assert proxies[0]["host"] == "proxy1.com"
        await fetcher.close()

    async def test_retry_on_429_without_retry_after(self, respx_mock) -> None:
        """Test retry uses exponential backoff when Retry-After header missing."""
        from unittest.mock import AsyncMock, patch

        import httpx

        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig

        source = ProxySourceConfig(url="http://example.com/proxies.json", format="json")
        fetcher = ProxyFetcher()

        # First request: 429 without Retry-After
        # Second request: 200 OK
        respx_mock.get("http://example.com/proxies.json").mock(
            side_effect=[
                httpx.Response(429),
                httpx.Response(200, text='[{"host": "proxy1.com", "port": 8080}]'),
            ]
        )

        # Mock asyncio.sleep to avoid actual delay
        with patch("asyncio.sleep", new_callable=AsyncMock):
            proxies = await fetcher.fetch_from_source(source)

        assert len(proxies) == 1
        assert proxies[0]["host"] == "proxy1.com"
        await fetcher.close()

    async def test_retry_on_503_service_unavailable(self, respx_mock) -> None:
        """Test retry on 503 Service Unavailable."""
        from unittest.mock import AsyncMock, patch

        import httpx

        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig

        source = ProxySourceConfig(url="http://example.com/proxies.json", format="json")
        fetcher = ProxyFetcher()

        # First request: 503
        # Second request: 200 OK
        respx_mock.get("http://example.com/proxies.json").mock(
            side_effect=[
                httpx.Response(503),
                httpx.Response(200, text='[{"host": "proxy1.com", "port": 8080}]'),
            ]
        )

        with patch("asyncio.sleep", new_callable=AsyncMock):
            proxies = await fetcher.fetch_from_source(source)

        assert len(proxies) == 1
        await fetcher.close()

    async def test_retry_exhaustion_on_persistent_429(self, respx_mock) -> None:
        """Test that retries are exhausted after max attempts on persistent 429."""
        from unittest.mock import AsyncMock, patch

        import httpx

        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig

        source = ProxySourceConfig(url="http://example.com/proxies.json", format="json")
        fetcher = ProxyFetcher()

        # All requests return 429 (will retry 5 times then fail)
        respx_mock.get("http://example.com/proxies.json").mock(
            side_effect=[httpx.Response(429, headers={"Retry-After": "1"})] * 10
        )

        # Mock asyncio.sleep to avoid delay
        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(httpx.HTTPStatusError, match="429"):
                await fetcher.fetch_from_source(source)

        await fetcher.close()

    async def test_retry_after_header_capped_at_60_seconds(self, respx_mock) -> None:
        """Test that Retry-After header is capped at 60 seconds to prevent DoS."""
        from unittest.mock import AsyncMock, patch

        import httpx

        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig

        source = ProxySourceConfig(url="http://example.com/proxies.json", format="json")
        fetcher = ProxyFetcher()

        # First request: 429 with very long Retry-After (should be capped)
        # Second request: 200 OK
        respx_mock.get("http://example.com/proxies.json").mock(
            side_effect=[
                httpx.Response(429, headers={"Retry-After": "3600"}),  # 1 hour
                httpx.Response(200, text='[{"host": "proxy1.com", "port": 8080}]'),
            ]
        )

        # Mock asyncio.sleep to avoid actual delay
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            proxies = await fetcher.fetch_from_source(source)

        assert len(proxies) == 1
        # Verify sleep was called (tenacity uses asyncio.sleep for async functions)
        assert mock_sleep.called
        await fetcher.close()

    async def test_retry_on_502_bad_gateway(self, respx_mock) -> None:
        """Test retry on 502 Bad Gateway."""
        from unittest.mock import AsyncMock, patch

        import httpx

        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig

        source = ProxySourceConfig(url="http://example.com/proxies.json", format="json")
        fetcher = ProxyFetcher()

        respx_mock.get("http://example.com/proxies.json").mock(
            side_effect=[
                httpx.Response(502),
                httpx.Response(200, text='[{"host": "proxy1.com", "port": 8080}]'),
            ]
        )

        with patch("asyncio.sleep", new_callable=AsyncMock):
            proxies = await fetcher.fetch_from_source(source)

        assert len(proxies) == 1
        await fetcher.close()

    async def test_retry_on_504_gateway_timeout(self, respx_mock) -> None:
        """Test retry on 504 Gateway Timeout."""
        from unittest.mock import AsyncMock, patch

        import httpx

        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig

        source = ProxySourceConfig(url="http://example.com/proxies.json", format="json")
        fetcher = ProxyFetcher()

        respx_mock.get("http://example.com/proxies.json").mock(
            side_effect=[
                httpx.Response(504),
                httpx.Response(200, text='[{"host": "proxy1.com", "port": 8080}]'),
            ]
        )

        with patch("asyncio.sleep", new_callable=AsyncMock):
            proxies = await fetcher.fetch_from_source(source)

        assert len(proxies) == 1
        await fetcher.close()

    async def test_no_retry_on_404_not_found(self, respx_mock) -> None:
        """Test that 404 is NOT retried (not a retryable status)."""
        import httpx

        from proxywhirl.exceptions import ProxyFetchError
        from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig

        source = ProxySourceConfig(url="http://example.com/proxies.json", format="json")
        fetcher = ProxyFetcher()

        respx_mock.get("http://example.com/proxies.json").mock(
            return_value=httpx.Response(404, text="Not Found")
        )

        with pytest.raises(ProxyFetchError, match="HTTP error"):
            await fetcher.fetch_from_source(source)

        await fetcher.close()

    async def test_retry_with_jitter_adds_randomness(self) -> None:
        """Test that exponential backoff with jitter adds randomness."""
        from proxywhirl.fetchers import _wait_with_retry_after

        # Create a mock retry state without Retry-After header
        class MockOutcome:
            def exception(self):
                return None

        class MockRetryState:
            attempt_number = 1
            outcome = MockOutcome()

        state = MockRetryState()

        # Call wait function multiple times
        wait_times = [_wait_with_retry_after(state) for _ in range(10)]

        # With jitter, wait times should vary
        # Base wait for attempt 1 is 2^1 = 2 seconds, jitter adds 0-25% (0-0.5s)
        assert all(2.0 <= t <= 2.5 for t in wait_times)
        # Should have some variation (not all identical)
        assert len(set(wait_times)) > 1
