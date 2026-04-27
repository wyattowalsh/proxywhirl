"""
Regression test suite for ProxyWhirl.

Tests fixed bugs and edge cases to prevent regressions.
"""

from __future__ import annotations

import pytest
from proxywhirl.exceptions import ProxyPoolEmptyError, ProxyValidationError
from proxywhirl.models import Proxy, ProxyPool, HealthStatus
from proxywhirl.validators import is_valid_proxy_url, is_healthy_proxy


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_pool_selection(self):
        """Regression: selecting from empty pool should raise error."""
        pool = ProxyPool()
        with pytest.raises(ProxyPoolEmptyError):
            pool.select()

    def test_invalid_proxy_url_format(self):
        """Regression: invalid proxy URL should fail validation."""
        invalid_urls = [
            "not_a_url",
            "http://",
            "http://host",  # missing port
            "://host:8080",  # missing scheme
            "ftp://host:8080",  # unsupported scheme
        ]
        for url in invalid_urls:
            assert not is_valid_proxy_url(url), f"URL {url} should be invalid"

    def test_proxy_with_none_health_status(self):
        """Regression: proxy with None health status."""
        proxy = Proxy(
            id="test-1",
            url="http://proxy1:8080",
            health_status=None,
            last_checked=None,
        )
        # Should not crash
        assert proxy.id == "test-1"

    def test_zero_timeout_value(self):
        """Regression: zero timeout should be rejected."""
        with pytest.raises(ValueError):
            from proxywhirl.query_builder import ProxyQuery
            ProxyQuery().with_max_latency_ms(0)  # type: ignore


class TestErrorHandling:
    """Tests for error handling and recovery."""

    def test_connection_error_context(self):
        """Regression: connection errors should preserve context."""
        from proxywhirl.exception_helpers import wrap_connection_error

        exc = Exception("Connection refused")
        wrapped = wrap_connection_error(
            exc,
            proxy_url="http://proxy:8080",
            operation="test_op",
            attempt_count=2,
        )

        assert wrapped.proxy_url is not None
        assert wrapped.operation == "test_op"
        assert wrapped.attempt_count == 2

    def test_timeout_error_wrapping(self):
        """Regression: timeout errors should include timeout duration."""
        from proxywhirl.exception_helpers import wrap_timeout_error

        exc = TimeoutError("Request timed out")
        wrapped = wrap_timeout_error(
            exc,
            proxy_url="http://proxy:8080",
            timeout_seconds=5.0,
        )

        assert wrapped.error_code.value == "TIMEOUT"
        assert "5.0s" in str(wrapped)


class TestValidation:
    """Tests for validation logic."""

    def test_proxy_url_with_credentials(self):
        """Regression: proxy URL with credentials should validate."""
        url = "http://user:pass@proxy:8080"
        assert is_valid_proxy_url(url)

    def test_socks_proxy_urls(self):
        """Regression: SOCKS proxy URLs should validate."""
        valid_socks = [
            "socks4://proxy:1080",
            "socks5://proxy:1080",
            "socks5h://proxy:1080",
        ]
        for url in valid_socks:
            assert is_valid_proxy_url(url), f"URL {url} should be valid"

    def test_port_boundary_values(self):
        """Regression: port validation at boundaries."""
        from proxywhirl.validators import is_valid_port

        assert is_valid_port(1)
        assert is_valid_port(65535)
        assert not is_valid_port(0)
        assert not is_valid_port(65536)
        assert not is_valid_port(-1)


class TestConcurrency:
    """Tests for concurrent access patterns."""

    @pytest.mark.asyncio
    async def test_concurrent_pool_access(self):
        """Regression: concurrent pool access should be safe."""
        import asyncio

        pool = ProxyPool()
        for i in range(5):
            proxy = Proxy(id=f"proxy-{i}", url=f"http://proxy{i}:8080")
            pool.add_proxy(proxy)

        async def select_proxy():
            return pool.select()

        tasks = [select_proxy() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        # All should succeed (no crashes)
        assert len(results) == 10


class TestDataIntegrity:
    """Tests for data integrity and persistence."""

    def test_proxy_immutability(self):
        """Regression: Proxy model should be immutable."""
        proxy = Proxy(id="test", url="http://proxy:8080")
        with pytest.raises(Exception):  # Pydantic will raise validation error
            proxy.id = "modified"

    def test_pool_size_tracking(self):
        """Regression: pool size should accurately reflect proxies."""
        pool = ProxyPool()
        for i in range(10):
            proxy = Proxy(id=f"proxy-{i}", url=f"http://proxy{i}:8080")
            pool.add_proxy(proxy)

        assert pool.size() == 10


class TestFiltering:
    """Tests for filtering and selection."""

    def test_query_builder_empty_result(self):
        """Regression: query with no matches should return empty list."""
        from proxywhirl.query_builder import ProxyQuery

        pool = ProxyPool()
        pool.add_proxy(Proxy(id="test", url="http://proxy:8080", country="US"))

        query = ProxyQuery(pool).by_country("GB")
        results = query.build()

        assert len(results) == 0

    def test_query_builder_limit(self):
        """Regression: query limit should be respected."""
        from proxywhirl.query_builder import ProxyQuery

        pool = ProxyPool()
        for i in range(20):
            pool.add_proxy(Proxy(id=f"proxy-{i}", url=f"http://proxy{i}:8080"))

        query = ProxyQuery(pool).limit(5)
        results = query.build()

        assert len(results) == 5

    def test_query_builder_offset(self):
        """Regression: query offset should skip correctly."""
        from proxywhirl.query_builder import ProxyQuery

        pool = ProxyPool()
        for i in range(10):
            pool.add_proxy(Proxy(id=f"proxy-{i}", url=f"http://proxy{i}:8080"))

        query = ProxyQuery(pool).offset(5).limit(3)
        results = query.build()

        assert len(results) == 3


class TestResourceManagement:
    """Tests for resource management."""

    def test_resource_limiter_memory_check(self):
        """Regression: resource limiter should check memory."""
        from proxywhirl.resource_limits import ResourceLimiter

        limiter = ResourceLimiter()
        is_ok, msg = limiter.check_memory_limit()

        # Should not crash and should return tuple
        assert isinstance(is_ok, bool)
        assert isinstance(msg, str)

    def test_connection_tracking(self):
        """Regression: connection tracking should be accurate."""
        from proxywhirl.resource_limits import ResourceLimiter

        limiter = ResourceLimiter()
        assert limiter.record_connection_open() is True
        assert limiter.open_connections == 1
        limiter.record_connection_close()
        assert limiter.open_connections == 0


class TestQuotaManagement:
    """Tests for quota enforcement."""

    def test_quota_request_tracking(self):
        """Regression: quota should track requests correctly."""
        from proxywhirl.quota import QuotaManager

        manager = QuotaManager()
        assert manager.check_request_quota("client1") is True

        manager.record_request(client_id="client1")
        stats = manager.get_stats("client1")
        assert stats.total_requests == 1

    def test_session_quota_enforcement(self):
        """Regression: session quota should be enforced."""
        from proxywhirl.quota import QuotaConfig, QuotaManager

        config = QuotaConfig(max_concurrent_sessions=2)
        manager = QuotaManager(config)

        assert manager.create_session("client1") is True
        assert manager.create_session("client1") is True
        assert manager.create_session("client1") is False

        manager.close_session("client1")
        assert manager.create_session("client1") is True


class TestRetryBudget:
    """Tests for retry budget."""

    def test_retry_budget_enforcement(self):
        """Regression: retry budget should be enforced."""
        from proxywhirl.retry_budget import RetryBudget

        budget = RetryBudget(total_budget_per_minute=5)

        # Should allow retries within budget
        for _ in range(5):
            is_allowed, msg = budget.check_retry_allowed(1)
            assert is_allowed
            budget.consume_retry()

        # Should reject after budget exhausted
        is_allowed, msg = budget.check_retry_allowed(1)
        assert not is_allowed

    def test_retry_limit_per_request(self):
        """Regression: per-request retry limit should be enforced."""
        from proxywhirl.retry_budget import RetryBudget

        budget = RetryBudget(max_retries_per_request=3)

        assert budget.check_retry_allowed(1)[0] is True
        assert budget.check_retry_allowed(2)[0] is True
        assert budget.check_retry_allowed(3)[0] is True
        assert budget.check_retry_allowed(4)[0] is False
