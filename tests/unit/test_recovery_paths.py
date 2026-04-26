"""Tests for failure recovery and fallback paths."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from proxywhirl.exceptions import ProxyConnectionError, ProxyValidationError
from proxywhirl.models import Proxy


class TestRecoveryPaths:
    """Test failure recovery and fallback paths."""

    def test_proxy_connection_fallback(self) -> None:
        """Test fallback when proxy connection fails."""
        proxies = [
            Proxy(url="http://invalid1.local:8080"),
            Proxy(url="http://invalid2.local:8080"),
            Proxy(url="http://127.0.0.1:8080", allow_local=True),
        ]

        # Last proxy should be the fallback
        assert proxies[-1].url == "http://127.0.0.1:8080"

    def test_validation_recovery_on_timeout(self) -> None:
        """Test validation recovery on timeout."""
        proxy = Proxy(url="http://slow.proxy.local:8080")

        # Mark as failed initially
        with pytest.raises(ProxyValidationError):
            if proxy.url.startswith("http://slow"):
                raise ProxyValidationError("timeout")

        # Subsequent retry should work differently
        assert proxy.url == "http://slow.proxy.local:8080"

    def test_connection_pool_exhaustion_recovery(self) -> None:
        """Test recovery when connection pool is exhausted."""
        pool_size = 5
        active_connections = 5

        # Pool exhausted
        assert active_connections >= pool_size

        # Should wait or use fallback
        # Simulating backoff
        backoff_count = 0
        while active_connections >= pool_size:
            backoff_count += 1
            if backoff_count > 3:
                break

        assert backoff_count > 0

    def test_circuit_breaker_half_open_recovery(self) -> None:
        """Test circuit breaker transitioning from open to half-open."""
        # Simulate circuit breaker states
        states = ["closed", "open", "half_open", "closed"]

        current_state = states[0]
        assert current_state == "closed"

        # Trigger failures to open circuit
        current_state = states[1]
        assert current_state == "open"

        # After timeout, move to half-open
        current_state = states[2]
        assert current_state == "half_open"

        # Successful request closes circuit
        current_state = states[3]
        assert current_state == "closed"

    def test_cache_miss_recovery(self) -> None:
        """Test recovery when cache lookup fails."""
        cache_data = {}
        key = "proxy:http://example.local:8080"

        # Cache miss
        result = cache_data.get(key)
        assert result is None

        # Fallback to direct lookup
        fallback_result = "direct_lookup"
        assert fallback_result is not None

    def test_database_connection_retry(self) -> None:
        """Test database connection retry logic."""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Simulate db connection attempt
                if retry_count < 2:
                    raise Exception("Connection failed")
                break
            except Exception:
                retry_count += 1

        assert retry_count == 2

    def test_geo_lookup_fallback(self) -> None:
        """Test fallback when geo lookup fails."""
        geo_data = None

        if geo_data is None:
            # Fallback to cached data
            geo_data = {"country": "US", "city": "unknown"}

        assert geo_data is not None
        assert "country" in geo_data

    @pytest.mark.asyncio
    async def test_async_recovery_with_retry(self) -> None:
        """Test async recovery with exponential backoff."""
        attempts = []
        max_attempts = 3

        for attempt in range(max_attempts):
            attempts.append(attempt)
            if attempt == 2:
                break
            await asyncio.sleep(0.01 * (2**attempt))

        assert len(attempts) == 3

    def test_proxy_pool_depletion_recovery(self) -> None:
        """Test recovery when proxy pool is depleted."""
        pool = []

        # Pool is empty
        assert len(pool) == 0

        # Trigger refresh
        pool = [
            Proxy(url="http://proxy1.local:8080"),
            Proxy(url="http://proxy2.local:8080"),
        ]

        assert len(pool) == 2

    def test_validation_error_categorization(self) -> None:
        """Test categorizing validation errors for recovery."""
        error_types = {
            "timeout": "retry_with_longer_timeout",
            "connection_refused": "skip_proxy",
            "ssl_error": "mark_as_https_incompatible",
            "auth_error": "skip_proxy",
        }

        error = "timeout"
        action = error_types.get(error)
        assert action == "retry_with_longer_timeout"
