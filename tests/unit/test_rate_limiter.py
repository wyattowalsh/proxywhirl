"""Unit tests for rate_limiting.limiter module."""

from proxywhirl.rate_limiting.limiter import RateLimiter, SyncRateLimiter
from proxywhirl.rate_limiting.models import RateLimit


class TestRateLimiter:
    """Test RateLimiter class (now synchronous for backwards compatibility)."""

    def test_init_without_global_limit(self) -> None:
        """Test initialization without global limit."""
        limiter = RateLimiter()
        assert limiter.global_limit is None
        assert limiter._global_limiter is None

    def test_init_with_global_limit(self) -> None:
        """Test initialization with global limit."""
        global_limit = RateLimit(max_requests=100, time_window=60)
        limiter = RateLimiter(global_limit=global_limit)
        assert limiter.global_limit == global_limit
        assert limiter._global_limiter is not None

    def test_set_proxy_limit(self) -> None:
        """Test setting per-proxy limit."""
        limiter = RateLimiter()
        limit = RateLimit(max_requests=50, time_window=30)

        limiter.set_proxy_limit("proxy1", limit)

        assert "proxy1" in limiter._proxy_limiters

    def test_check_limit_no_limits(self) -> None:
        """Test check_limit with no limits set."""
        limiter = RateLimiter()
        result = limiter.check_limit("proxy1")
        assert result is True

    def test_check_limit_within_proxy_limit(self) -> None:
        """Test check_limit within proxy limit."""
        limiter = RateLimiter()
        limit = RateLimit(max_requests=10, time_window=1)
        limiter.set_proxy_limit("proxy1", limit)

        # First request should succeed
        result = limiter.check_limit("proxy1")
        assert result is True

    def test_check_limit_exceeds_proxy_limit(self) -> None:
        """Test check_limit when exceeding proxy limit."""
        limiter = RateLimiter()
        limit = RateLimit(max_requests=2, time_window=60)
        limiter.set_proxy_limit("proxy1", limit)

        # First two should succeed
        assert limiter.check_limit("proxy1") is True
        assert limiter.check_limit("proxy1") is True

        # Third should fail (exceeds limit)
        assert limiter.check_limit("proxy1") is False

    def test_check_limit_within_global_limit(self) -> None:
        """Test check_limit within global limit."""
        global_limit = RateLimit(max_requests=10, time_window=1)
        limiter = RateLimiter(global_limit=global_limit)

        # Should succeed
        result = limiter.check_limit("proxy1")
        assert result is True

    def test_check_limit_exceeds_global_limit(self) -> None:
        """Test check_limit when exceeding global limit."""
        global_limit = RateLimit(max_requests=2, time_window=60)
        limiter = RateLimiter(global_limit=global_limit)

        # First two should succeed
        assert limiter.check_limit("proxy1") is True
        assert limiter.check_limit("proxy2") is True

        # Third should fail (exceeds global limit)
        assert limiter.check_limit("proxy3") is False

    def test_acquire_delegates_to_check_limit(self) -> None:
        """Test acquire delegates to check_limit."""
        limiter = RateLimiter()
        limit = RateLimit(max_requests=5, time_window=1)
        limiter.set_proxy_limit("proxy1", limit)

        result = limiter.acquire("proxy1")
        assert result is True

    def test_multiple_proxies_independent_limits(self) -> None:
        """Test that different proxies have independent limits."""
        limiter = RateLimiter()
        limit1 = RateLimit(max_requests=2, time_window=60)
        limit2 = RateLimit(max_requests=3, time_window=60)

        limiter.set_proxy_limit("proxy1", limit1)
        limiter.set_proxy_limit("proxy2", limit2)

        # proxy1: 2 requests OK, 3rd fails
        assert limiter.check_limit("proxy1") is True
        assert limiter.check_limit("proxy1") is True
        assert limiter.check_limit("proxy1") is False

        # proxy2: still has its own quota
        assert limiter.check_limit("proxy2") is True
        assert limiter.check_limit("proxy2") is True
        assert limiter.check_limit("proxy2") is True


class TestSyncRateLimiter:
    """Test SyncRateLimiter class (synchronous version)."""

    def test_init_without_global_limit(self) -> None:
        """Test initialization without global limit."""
        limiter = SyncRateLimiter()
        assert limiter.global_limit is None
        assert limiter._global_limiter is None

    def test_init_with_global_limit(self) -> None:
        """Test initialization with global limit."""
        global_limit = RateLimit(max_requests=100, time_window=60)
        limiter = SyncRateLimiter(global_limit=global_limit)
        assert limiter.global_limit == global_limit
        assert limiter._global_limiter is not None

    def test_set_proxy_limit(self) -> None:
        """Test setting per-proxy limit (synchronous)."""
        limiter = SyncRateLimiter()
        limit = RateLimit(max_requests=50, time_window=30)

        limiter.set_proxy_limit("proxy1", limit)

        assert "proxy1" in limiter._proxy_limiters

    def test_check_limit_no_limits(self) -> None:
        """Test check_limit with no limits set."""
        limiter = SyncRateLimiter()
        result = limiter.check_limit("proxy1")
        assert result is True

    def test_check_limit_within_proxy_limit(self) -> None:
        """Test check_limit within proxy limit."""
        limiter = SyncRateLimiter()
        limit = RateLimit(max_requests=10, time_window=1)
        limiter.set_proxy_limit("proxy1", limit)

        # First request should succeed
        result = limiter.check_limit("proxy1")
        assert result is True

    def test_check_limit_exceeds_proxy_limit(self) -> None:
        """Test check_limit when exceeding proxy limit."""
        limiter = SyncRateLimiter()
        limit = RateLimit(max_requests=2, time_window=60)
        limiter.set_proxy_limit("proxy1", limit)

        # First two should succeed
        assert limiter.check_limit("proxy1") is True
        assert limiter.check_limit("proxy1") is True

        # Third should fail (exceeds limit)
        assert limiter.check_limit("proxy1") is False

    def test_check_limit_within_global_limit(self) -> None:
        """Test check_limit within global limit."""
        global_limit = RateLimit(max_requests=10, time_window=1)
        limiter = SyncRateLimiter(global_limit=global_limit)

        # Should succeed
        result = limiter.check_limit("proxy1")
        assert result is True

    def test_check_limit_exceeds_global_limit(self) -> None:
        """Test check_limit when exceeding global limit."""
        global_limit = RateLimit(max_requests=2, time_window=60)
        limiter = SyncRateLimiter(global_limit=global_limit)

        # First two should succeed
        assert limiter.check_limit("proxy1") is True
        assert limiter.check_limit("proxy2") is True

        # Third should fail (exceeds global limit)
        assert limiter.check_limit("proxy3") is False

    def test_acquire_delegates_to_check_limit(self) -> None:
        """Test acquire delegates to check_limit."""
        limiter = SyncRateLimiter()
        limit = RateLimit(max_requests=5, time_window=1)
        limiter.set_proxy_limit("proxy1", limit)

        result = limiter.acquire("proxy1")
        assert result is True

    def test_multiple_proxies_independent_limits(self) -> None:
        """Test that different proxies have independent limits."""
        limiter = SyncRateLimiter()
        limit1 = RateLimit(max_requests=2, time_window=60)
        limit2 = RateLimit(max_requests=3, time_window=60)

        limiter.set_proxy_limit("proxy1", limit1)
        limiter.set_proxy_limit("proxy2", limit2)

        # proxy1: 2 requests OK, 3rd fails
        assert limiter.check_limit("proxy1") is True
        assert limiter.check_limit("proxy1") is True
        assert limiter.check_limit("proxy1") is False

        # proxy2: still has its own quota
        assert limiter.check_limit("proxy2") is True
        assert limiter.check_limit("proxy2") is True
        assert limiter.check_limit("proxy2") is True

    def test_sync_limiter_no_asyncio_run(self) -> None:
        """Test that SyncRateLimiter works without asyncio.run()."""
        # This test ensures that SyncRateLimiter can be used in
        # synchronous contexts without creating event loops
        limiter = SyncRateLimiter()
        limit = RateLimit(max_requests=5, time_window=1)
        limiter.set_proxy_limit("proxy1", limit)

        # Should work in a regular synchronous function
        result = limiter.check_limit("proxy1")
        assert result is True

    def test_thread_safety(self) -> None:
        """Test that SyncRateLimiter is thread-safe."""
        import threading

        limiter = SyncRateLimiter()
        limit = RateLimit(max_requests=100, time_window=1)
        limiter.set_proxy_limit("proxy1", limit)

        results = []
        errors = []

        def worker():
            try:
                result = limiter.check_limit("proxy1")
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Create 10 threads
        threads = [threading.Thread(target=worker) for _ in range(10)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Should have no errors
        assert len(errors) == 0
        # All threads should have gotten results
        assert len(results) == 10
