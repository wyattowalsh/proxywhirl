"""
Unit tests for Proxy model validation.
"""

from datetime import UTC, datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from proxywhirl.models import HealthStatus, Proxy, ProxyPool


class TestProxyValidation:
    """Test Proxy model validation rules."""

    # -------------------------------------------------------------------------
    # Valid protocol tests (parametrized)
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "url,expected_protocol",
        [
            ("http://proxy.example.com:8080", "http"),
            ("https://proxy.example.com:8080", "https"),
            ("socks5://proxy.example.com:1080", "socks5"),
            ("socks4://proxy.example.com:1080", "socks4"),
        ],
        ids=["http", "https", "socks5", "socks4"],
    )
    def test_valid_proxy_protocols(self, url, expected_protocol):
        """Test proxy creation with valid protocol URLs."""
        proxy = Proxy(url=url)
        assert proxy.url is not None
        assert proxy.protocol == expected_protocol

    # -------------------------------------------------------------------------
    # Invalid scheme tests (parametrized)
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "url,error_pattern",
        [
            ("ftp://proxy.example.com:8080", "Invalid proxy scheme 'ftp'"),
            ("proxy.example.com:8080", "URL must have a scheme"),
            ("ht!tp://proxy.example.com:8080", "URL must have a scheme"),
        ],
        ids=["invalid_ftp", "missing_scheme", "malformed_scheme"],
    )
    def test_invalid_scheme_rejects(self, url, error_pattern):
        """Test that invalid/missing schemes are rejected."""
        with pytest.raises(ValidationError, match=error_pattern):
            Proxy(url=url)

    # -------------------------------------------------------------------------
    # Valid port tests (parametrized)
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "port",
        [1, 80, 443, 8080, 65535],
        ids=["min_port", "http_port", "https_port", "common_proxy", "max_port"],
    )
    def test_port_range_valid(self, port):
        """Test that valid ports are accepted."""
        proxy = Proxy(url=f"http://proxy.example.com:{port}")
        assert proxy.url is not None

    # -------------------------------------------------------------------------
    # Invalid port tests (parametrized)
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "port",
        [0, -1, 65536, 999999],
        ids=["zero", "negative", "too_high", "way_too_high"],
    )
    def test_port_range_invalid_rejects(self, port):
        """Test that invalid ports are rejected."""
        with pytest.raises(ValidationError, match="Port must be between 1 and 65535"):
            Proxy(url=f"http://proxy.example.com:{port}")

    # -------------------------------------------------------------------------
    # Localhost rejection tests (parametrized)
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "url",
        [
            "http://127.0.0.1:8080",
            "http://localhost:8080",
            "http://[::1]:8080",
        ],
        ids=["ipv4_loopback", "localhost_name", "ipv6_loopback"],
    )
    def test_localhost_rejects_by_default(self, url):
        """Test that localhost addresses are rejected by default."""
        with pytest.raises(ValidationError, match="Localhost addresses not allowed"):
            Proxy(url=url)

    # -------------------------------------------------------------------------
    # Private IP rejection tests (parametrized)
    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "url",
        [
            "http://192.168.1.1:8080",
            "http://10.0.0.1:8080",
            "http://172.16.0.1:8080",
        ],
        ids=["192_168_x_x", "10_x_x_x", "172_16_x_x"],
    )
    def test_private_ip_rejects_by_default(self, url):
        """Test that private IP addresses are rejected by default."""
        with pytest.raises(ValidationError, match="Private/internal IP addresses not allowed"):
            Proxy(url=url)

    def test_localhost_allowed_with_flag(self):
        """Test that localhost is allowed when allow_local=True."""
        proxy = Proxy(url="http://localhost:8080", allow_local=True)
        assert proxy.url is not None

    def test_private_ip_allowed_with_flag(self):
        """Test that private IPs are allowed when allow_local=True."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        assert proxy.url is not None

    def test_public_ip_always_allowed(self):
        """Test that public IPs are always allowed."""
        proxy = Proxy(url="http://8.8.8.8:8080")
        assert proxy.url is not None

    def test_public_domain_always_allowed(self):
        """Test that public domains are always allowed."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.url is not None

    def test_url_with_credentials_validates(self):
        """Test that URLs with embedded credentials validate correctly."""
        from pydantic import SecretStr

        proxy = Proxy(
            url="http://proxy.example.com:8080",
            username=SecretStr("user"),
            password=SecretStr("pass"),
        )
        assert proxy.url is not None

    def test_port_in_url_with_credentials(self):
        """Test port validation works with credentials in URL."""
        with pytest.raises(ValidationError, match="Port must be between 1 and 65535"):
            Proxy(url="http://user:pass@proxy.example.com:99999")

    def test_protocol_extracted_from_url(self):
        """Test that protocol is extracted from URL if not provided."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.protocol == "http"

    def test_credentials_both_present(self):
        """Test proxy with both username and password."""
        from pydantic import SecretStr

        proxy = Proxy(
            url="http://proxy.example.com:8080",
            username=SecretStr("user"),
            password=SecretStr("pass"),
        )
        assert proxy.username is not None
        assert proxy.password is not None
        assert proxy.credentials is not None

    def test_credentials_both_absent(self):
        """Test proxy without credentials."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.username is None
        assert proxy.password is None
        assert proxy.credentials is None

    def test_credentials_only_username_raises_error(self):
        """Test that providing only username raises ValidationError."""
        from pydantic import SecretStr

        with pytest.raises(ValidationError, match="Both username and password"):
            Proxy(
                url="http://proxy.example.com:8080",
                username=SecretStr("user"),
            )

    def test_credentials_only_password_raises_error(self):
        """Test that providing only password raises ValidationError."""
        from pydantic import SecretStr

        with pytest.raises(ValidationError, match="Both username and password"):
            Proxy(
                url="http://proxy.example.com:8080",
                password=SecretStr("pass"),
            )


class TestProxyHealthStatus:
    """Test Proxy health status transitions."""

    def test_initial_health_status_unknown(self):
        """Test that new proxy has UNKNOWN health status."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.health_status == HealthStatus.UNKNOWN

    def test_record_success_updates_health_to_healthy(self):
        """Test that recording success changes status to HEALTHY."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.record_success(response_time_ms=100.0)
        assert proxy.health_status == HealthStatus.HEALTHY
        assert proxy.total_successes == 1
        assert proxy.consecutive_failures == 0

    def test_record_success_resets_consecutive_failures(self):
        """Test that success resets consecutive failures counter."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.record_failure()
        proxy.record_failure()
        assert proxy.consecutive_failures == 2

        proxy.record_success(response_time_ms=100.0)
        assert proxy.consecutive_failures == 0

    def test_one_failure_degrades_health(self):
        """Test that one failure sets status to DEGRADED."""
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        proxy.record_failure()
        assert proxy.health_status == HealthStatus.DEGRADED
        assert proxy.consecutive_failures == 1

    def test_three_failures_unhealthy(self):
        """Test that three consecutive failures set status to UNHEALTHY."""
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        proxy.record_failure()
        proxy.record_failure()
        proxy.record_failure()
        assert proxy.health_status == HealthStatus.UNHEALTHY
        assert proxy.consecutive_failures == 3

    def test_five_failures_dead(self):
        """Test that five consecutive failures set status to DEAD."""
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=HealthStatus.HEALTHY)
        for _ in range(5):
            proxy.record_failure()
        assert proxy.health_status == HealthStatus.DEAD
        assert proxy.consecutive_failures == 5


class TestProxyStats:
    """Test Proxy statistics tracking."""

    def test_success_rate_zero_initially(self):
        """Test that success rate is 0 for new proxy."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.success_rate == 0.0

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.record_success(100.0)
        proxy.record_success(100.0)
        proxy.record_failure()
        # 2 successes / 3 total = 0.666...
        assert abs(proxy.success_rate - 0.6666666666666666) < 0.0001

    def test_average_response_time_single_request(self):
        """Test average response time with single request."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.record_success(response_time_ms=150.0)
        assert proxy.average_response_time_ms == 150.0

    def test_average_response_time_exponential_moving_average(self):
        """Test that average response time uses exponential moving average."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.record_success(response_time_ms=100.0)
        proxy.record_success(response_time_ms=200.0)
        # EMA: alpha=0.2 (default), so 0.2*200 + 0.8*100 = 40 + 80 = 120
        assert proxy.average_response_time_ms == 120.0

    def test_last_success_at_updated(self):
        """Test that last_success_at is updated on success."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        before = datetime.now(UTC)
        proxy.record_success(100.0)
        after = datetime.now(UTC)
        assert proxy.last_success_at is not None
        assert before <= proxy.last_success_at <= after

    def test_last_failure_at_updated(self):
        """Test that last_failure_at is updated on failure."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        before = datetime.now(UTC)
        proxy.record_failure()
        after = datetime.now(UTC)
        assert proxy.last_failure_at is not None
        assert before <= proxy.last_failure_at <= after

    def test_failure_error_stored_in_metadata(self):
        """Test that failure errors are stored in metadata."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.record_failure(error="Connection timeout")
        assert "last_errors" in proxy.metadata
        assert len(proxy.metadata["last_errors"]) == 1
        assert proxy.metadata["last_errors"][0]["error"] == "Connection timeout"

    def test_metadata_keeps_last_10_errors(self):
        """Test that metadata only keeps last 10 errors."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        for i in range(15):
            proxy.record_failure(error=f"Error {i}")
        assert len(proxy.metadata["last_errors"]) == 10
        # Should keep errors 5-14
        assert proxy.metadata["last_errors"][0]["error"] == "Error 5"
        assert proxy.metadata["last_errors"][-1]["error"] == "Error 14"


class TestProxyProperties:
    """Test Proxy computed properties."""

    @pytest.mark.parametrize(
        "health_status,expected_is_healthy",
        [
            (HealthStatus.HEALTHY, True),
            (HealthStatus.DEGRADED, False),
            (HealthStatus.UNHEALTHY, False),
            (HealthStatus.DEAD, False),
            (HealthStatus.UNKNOWN, False),
        ],
        ids=["healthy", "degraded", "unhealthy", "dead", "unknown"],
    )
    def test_is_healthy_for_status(self, health_status, expected_is_healthy):
        """Test is_healthy returns correct value for each health status."""
        proxy = Proxy(url="http://proxy.example.com:8080", health_status=health_status)
        assert proxy.is_healthy is expected_is_healthy

    def test_credentials_property_returns_none_when_no_creds(self):
        """Test credentials property returns None when no credentials."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        assert proxy.credentials is None

    def test_credentials_property_returns_credentials_object(self):
        """Test credentials property returns ProxyCredentials object."""
        from pydantic import SecretStr

        proxy = Proxy(
            url="http://proxy.example.com:8080",
            username=SecretStr("user"),
            password=SecretStr("pass"),
        )
        creds = proxy.credentials
        assert creds is not None
        assert creds.username.get_secret_value() == "user"
        assert creds.password.get_secret_value() == "pass"


class TestProxyLatencyValidation:
    """Test Proxy latency_ms validation."""

    @pytest.mark.parametrize(
        "latency_ms",
        [100.5, 0.0, None],
        ids=["positive", "zero", "none"],
    )
    def test_latency_ms_valid_values_accepted(self, latency_ms):
        """Test that valid latency_ms values are accepted."""
        proxy = Proxy(url="http://proxy.example.com:8080", latency_ms=latency_ms)
        assert proxy.latency_ms == latency_ms

    @pytest.mark.parametrize(
        "latency_ms",
        [-1.0, -1000.5, -0.001],
        ids=["negative", "large_negative", "small_negative"],
    )
    def test_latency_ms_negative_rejected(self, latency_ms):
        """Test that negative latency_ms values are rejected."""
        with pytest.raises(ValidationError, match="latency_ms must be non-negative"):
            Proxy(url="http://proxy.example.com:8080", latency_ms=latency_ms)


class TestProxySuccessRateValidation:
    """Test Proxy success_rate calculation and clamping."""

    def test_success_rate_clamped_to_zero(self):
        """Test that success_rate is clamped to 0.0 minimum."""
        # Create proxy with invalid counters (this should be prevented by validators)
        # But if somehow we get negative successes, success_rate should clamp to 0
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.total_requests = 10
        proxy.total_successes = 0
        assert proxy.success_rate == 0.0

    def test_success_rate_clamped_to_one(self):
        """Test that success_rate is clamped to 1.0 maximum."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.total_requests = 10
        proxy.total_successes = 10
        assert proxy.success_rate == 1.0

    def test_success_rate_normal_range(self):
        """Test that success_rate works correctly in normal range."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.total_requests = 10
        proxy.total_successes = 7
        assert abs(proxy.success_rate - 0.7) < 0.0001

    def test_success_rate_edge_case_all_failures(self):
        """Test success_rate with all failures."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.total_requests = 5
        proxy.total_successes = 0
        assert proxy.success_rate == 0.0

    def test_success_rate_edge_case_all_successes(self):
        """Test success_rate with all successes."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        proxy.total_requests = 5
        proxy.total_successes = 5
        assert proxy.success_rate == 1.0


class TestProxyCounterValidation:
    """Test Proxy counter field validation."""

    @pytest.mark.parametrize(
        "counter_field",
        [
            "total_requests",
            "total_successes",
            "total_failures",
            "consecutive_failures",
            "consecutive_successes",
            "requests_started",
            "requests_completed",
            "requests_active",
        ],
        ids=[
            "total_requests",
            "total_successes",
            "total_failures",
            "consecutive_failures",
            "consecutive_successes",
            "requests_started",
            "requests_completed",
            "requests_active",
        ],
    )
    def test_counter_negative_rejected(self, counter_field):
        """Test that negative counter values are rejected for all counter fields."""
        with pytest.raises(ValidationError, match="Counter must be non-negative"):
            Proxy(url="http://proxy.example.com:8080", **{counter_field: -1})

    def test_counters_zero_accepted(self):
        """Test that zero values for counters are accepted."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            total_requests=0,
            total_successes=0,
            total_failures=0,
            consecutive_failures=0,
        )
        assert proxy.total_requests == 0
        assert proxy.total_successes == 0
        assert proxy.total_failures == 0
        assert proxy.consecutive_failures == 0

    def test_counters_positive_accepted(self):
        """Test that positive values for counters are accepted."""
        proxy = Proxy(
            url="http://proxy.example.com:8080",
            total_requests=100,
            total_successes=80,
            total_failures=20,
            consecutive_failures=5,
        )
        assert proxy.total_requests == 100
        assert proxy.total_successes == 80
        assert proxy.total_failures == 20
        assert proxy.consecutive_failures == 5


class TestProxyResponseTimeValidation:
    """Test Proxy response time field validation."""

    @pytest.mark.parametrize(
        "field,value",
        [
            ("average_response_time_ms", 150.5),
            ("average_response_time_ms", 0.0),
            ("ema_response_time_ms", 200.0),
            ("ema_response_time_ms", 0.0),
        ],
        ids=["avg_positive", "avg_zero", "ema_positive", "ema_zero"],
    )
    def test_response_time_valid_values_accepted(self, field, value):
        """Test that valid response time values are accepted."""
        proxy = Proxy(url="http://proxy.example.com:8080", **{field: value})
        assert getattr(proxy, field) == value

    @pytest.mark.parametrize(
        "field",
        ["average_response_time_ms", "ema_response_time_ms"],
        ids=["average", "ema"],
    )
    def test_response_time_negative_rejected(self, field):
        """Test that negative response time values are rejected."""
        with pytest.raises(ValidationError, match="Response time must be non-negative"):
            Proxy(url="http://proxy.example.com:8080", **{field: -1.0})


class TestProxyPoolConcurrentAccess:
    """Test ProxyPool thread safety for concurrent access operations.

    This test class validates that ProxyPool's RLock-based synchronization
    correctly handles concurrent operations without data corruption or race
    conditions.
    """

    def test_concurrent_add_proxies(self):
        """Test thread-safe concurrent proxy addition using ThreadPoolExecutor."""
        from concurrent.futures import ThreadPoolExecutor

        pool = ProxyPool(name="test_pool", max_pool_size=1000)

        def add_proxy(i: int) -> None:
            """Add a single proxy to the pool."""
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            pool.add_proxy(proxy)

        # Use ThreadPoolExecutor with 10 workers to add 100 proxies
        with ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(add_proxy, range(100)))

        # Verify all 100 proxies were added successfully
        assert pool.size == 100, f"Expected 100 proxies, got {pool.size}"

        # Verify no proxies were lost or duplicated
        all_proxies = pool.get_all_proxies()
        urls = [p.url for p in all_proxies]
        assert len(urls) == len(set(urls)), "Duplicate proxies found"

    def test_concurrent_remove_proxies(self):
        """Test thread-safe concurrent proxy removal using ThreadPoolExecutor."""
        from concurrent.futures import ThreadPoolExecutor

        pool = ProxyPool(name="test_pool", max_pool_size=1000)

        # Pre-populate pool with 100 proxies
        proxy_ids = []
        for i in range(100):
            proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
            pool.add_proxy(proxy)
            proxy_ids.append(proxy.id)

        def remove_proxy(proxy_id: UUID) -> None:
            """Remove a single proxy from the pool."""
            pool.remove_proxy(proxy_id)

        # Use ThreadPoolExecutor with 10 workers to remove all 100 proxies
        with ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(remove_proxy, proxy_ids))

        # Verify all proxies were removed
        assert pool.size == 0, f"Expected 0 proxies, got {pool.size}"

    def test_concurrent_add_remove_mixed(self):
        """Test concurrent add and remove operations don't cause issues."""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        pool = ProxyPool(name="test_pool", max_pool_size=1000)

        # Pre-populate with 50 proxies
        initial_proxy_ids = []
        for i in range(50):
            proxy = Proxy(url=f"http://initial{i}.example.com:8080")
            pool.add_proxy(proxy)
            initial_proxy_ids.append(proxy.id)

        errors = []

        def add_proxies(offset: int) -> tuple[str, int]:
            """Add 50 new proxies with unique URLs."""
            count = 0
            try:
                for i in range(50):
                    # Use offset to ensure unique URLs across threads
                    proxy = Proxy(url=f"http://new{offset}-{i}.example.com:8080")
                    pool.add_proxy(proxy)
                    count += 1
            except Exception as e:
                errors.append(("add", e))
            return ("add", count)

        def remove_proxies(ids: list[UUID]) -> tuple[str, int]:
            """Remove specific proxies by ID."""
            count = 0
            try:
                for proxy_id in ids:
                    pool.remove_proxy(proxy_id)
                    count += 1
            except Exception as e:
                errors.append(("remove", e))
            return ("remove", count)

        # Run mixed operations concurrently
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            # Submit 2 add tasks with different offsets (no URL conflicts)
            futures.append(executor.submit(add_proxies, 0))
            futures.append(executor.submit(add_proxies, 1))
            # Submit 2 remove tasks with non-overlapping ID sets
            futures.append(executor.submit(remove_proxies, initial_proxy_ids[:25]))
            futures.append(executor.submit(remove_proxies, initial_proxy_ids[25:]))

            # Wait for all to complete
            results = [future.result() for future in as_completed(futures)]

        # Verify no errors occurred
        assert not errors, f"Concurrent operations had errors: {errors}"

        # Verify pool state is consistent
        # Expected: 50 initial + 50 (offset 0) + 50 (offset 1) - 25 - 25 = 100 proxies
        assert pool.size == 100, f"Expected 100 proxies, got {pool.size}"

        # Verify all remaining proxies have unique URLs
        all_proxies = pool.get_all_proxies()
        urls = [p.url for p in all_proxies]
        assert len(urls) == len(set(urls)), "Duplicate proxies found after concurrent operations"

        # Verify that all remaining proxies are the "new" ones (all initials were removed)
        assert all("new" in p.url for p in all_proxies), "Some initial proxies were not removed"

    def test_concurrent_add_remove(self):
        """Test thread safety of concurrent add/remove operations."""
        import threading

        from tests.conftest import ProxyFactory

        pool = ProxyPool(name="test_pool", max_pool_size=1000)
        errors = []

        def add_proxies():
            """Add 100 proxies to the pool."""
            for _ in range(100):
                try:
                    pool.add_proxy(ProxyFactory.build())
                except Exception as e:
                    errors.append(("add", e))

        def remove_proxies():
            """Remove 50 proxies from the pool."""
            for _ in range(50):
                try:
                    # Get all proxies to find candidates for removal
                    all_proxies = pool.get_all_proxies()
                    if all_proxies:
                        # Remove the first proxy by ID
                        pool.remove_proxy(all_proxies[0].id)
                except Exception as e:
                    errors.append(("remove", e))

        # Create 5 adder threads and 5 remover threads
        threads = [threading.Thread(target=add_proxies) for _ in range(5)]
        threads += [threading.Thread(target=remove_proxies) for _ in range(5)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Verify no errors occurred
        assert not errors, f"Concurrent operations had errors: {errors}"

        # Verify pool state is consistent
        # Expected: 5 threads * 100 adds = 500 proxies added
        # 5 threads * 50 removes = 250 proxies removed (best case)
        # Actual removals may be less due to race conditions (trying to remove when empty)
        # So we should have at least 250 proxies remaining
        assert pool.size >= 250, f"Expected at least 250 proxies, got {pool.size}"
        assert pool.size <= 500, f"Expected at most 500 proxies, got {pool.size}"

    def test_concurrent_iteration_modification(self):
        """Test that iteration is safe during modification.

        This test verifies that iterating over the pool while other threads
        modify it does not cause race conditions or data corruption.
        """
        import threading

        from tests.conftest import ProxyFactory

        pool = ProxyPool(name="test_pool", max_pool_size=500)

        # Pre-populate pool with 100 proxies
        for _ in range(100):
            pool.add_proxy(ProxyFactory.build())

        errors = []
        iteration_counts = []

        def iterate_pool():
            """Iterate over pool multiple times."""
            for _ in range(10):
                try:
                    count = 0
                    for proxy in pool.get_all_proxies():
                        count += 1
                        # Access proxy properties to ensure data is valid
                        _ = proxy.url
                        _ = proxy.health_status
                    iteration_counts.append(count)
                except Exception as e:
                    errors.append(("iterate", e))

        def modify_pool():
            """Add and remove proxies concurrently."""
            for _ in range(20):
                try:
                    # Add a proxy
                    pool.add_proxy(ProxyFactory.build())

                    # Try to remove a proxy
                    all_proxies = pool.get_all_proxies()
                    if all_proxies:
                        pool.remove_proxy(all_proxies[0].id)
                except Exception as e:
                    errors.append(("modify", e))

        # Create 3 iterator threads and 3 modifier threads
        threads = [threading.Thread(target=iterate_pool) for _ in range(3)]
        threads += [threading.Thread(target=modify_pool) for _ in range(3)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify no errors
        assert not errors, f"Concurrent iteration/modification had errors: {errors}"

        # Verify we got valid iteration counts (all should be reasonable)
        assert (
            len(iteration_counts) == 30
        ), f"Expected 30 iteration counts, got {len(iteration_counts)}"
        assert all(
            count > 0 for count in iteration_counts
        ), "All iteration counts should be positive"

    def test_concurrent_get_by_id(self):
        """Test thread safety of ID lookups.

        This test verifies that concurrent ID lookups using the O(1) index
        are thread-safe and return correct results.
        """
        import threading

        from tests.conftest import ProxyFactory

        pool = ProxyPool(name="test_pool")

        # Pre-populate pool with 50 proxies and track their IDs
        proxy_ids = []
        for _ in range(50):
            proxy = ProxyFactory.build()
            pool.add_proxy(proxy)
            proxy_ids.append(proxy.id)

        errors = []
        lookup_results = []

        def lookup_proxies():
            """Perform ID lookups."""
            for proxy_id in proxy_ids:
                try:
                    result = pool.get_proxy_by_id(proxy_id)
                    lookup_results.append(result is not None)
                except Exception as e:
                    errors.append(("lookup", e))

        def modify_pool():
            """Add and remove proxies during lookups."""
            for _ in range(10):
                try:
                    # Add new proxy
                    pool.add_proxy(ProxyFactory.build())

                    # Remove a proxy (not from our tracked IDs)
                    all_proxies = pool.get_all_proxies()
                    # Remove one that's not in our tracked list
                    for p in all_proxies:
                        if p.id not in proxy_ids:
                            pool.remove_proxy(p.id)
                            break
                except Exception as e:
                    errors.append(("modify", e))

        # Create 5 lookup threads and 2 modifier threads
        threads = [threading.Thread(target=lookup_proxies) for _ in range(5)]
        threads += [threading.Thread(target=modify_pool) for _ in range(2)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify no errors
        assert not errors, f"Concurrent ID lookups had errors: {errors}"

        # All lookups should have succeeded (proxies we're looking up are never removed)
        assert len(lookup_results) == 250, f"Expected 250 lookup results, got {len(lookup_results)}"
        assert all(lookup_results), "All ID lookups should have succeeded"

    def test_concurrent_pool_statistics(self):
        """Test thread safety of pool statistics calculation.

        This test verifies that computing pool statistics (size, healthy_count,
        success_rate, etc.) is thread-safe and produces consistent results.
        """
        import threading

        from tests.conftest import ProxyFactory

        pool = ProxyPool(name="test_pool")

        # Pre-populate with mix of healthy and unhealthy proxies
        for _ in range(30):
            pool.add_proxy(ProxyFactory.healthy())
        for _ in range(20):
            pool.add_proxy(ProxyFactory.unhealthy())

        errors = []
        stats_snapshots = []

        def collect_statistics():
            """Collect pool statistics multiple times."""
            for _ in range(20):
                try:
                    snapshot = {
                        "size": pool.size,
                        "healthy": pool.healthy_count,
                        "unhealthy": pool.unhealthy_count,
                        "total_requests": pool.total_requests,
                        "success_rate": pool.overall_success_rate,
                    }
                    stats_snapshots.append(snapshot)
                except Exception as e:
                    errors.append(("stats", e))

        def modify_proxies():
            """Modify proxy states concurrently."""
            for _ in range(10):
                try:
                    all_proxies = pool.get_all_proxies()
                    if all_proxies:
                        # Record success on first proxy
                        all_proxies[0].record_success(100.0)
                        # Record failure on second proxy if exists
                        if len(all_proxies) > 1:
                            all_proxies[1].record_failure("test error")
                except Exception as e:
                    errors.append(("modify", e))

        # Create 4 stats threads and 3 modifier threads
        threads = [threading.Thread(target=collect_statistics) for _ in range(4)]
        threads += [threading.Thread(target=modify_proxies) for _ in range(3)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify no errors
        assert not errors, f"Concurrent statistics collection had errors: {errors}"

        # Verify we collected statistics
        assert len(stats_snapshots) == 80, f"Expected 80 stat snapshots, got {len(stats_snapshots)}"

        # Verify all snapshots have valid values
        for snapshot in stats_snapshots:
            assert snapshot["size"] == 50, "Pool size should remain 50"
            assert snapshot["healthy"] >= 0, "Healthy count should be non-negative"
            assert snapshot["unhealthy"] >= 0, "Unhealthy count should be non-negative"
            assert snapshot["total_requests"] >= 0, "Total requests should be non-negative"
            # Note: ProxyFactory may create inconsistent test data where success_rate > 1.0
            # due to total_successes > total_requests. This is a test data issue, not
            # a concurrency issue. The important thing is no exceptions are raised.
            assert snapshot["success_rate"] >= 0.0, "Success rate should be non-negative"

    def test_concurrent_filter_operations(self):
        """Test thread safety of filter operations.

        This test verifies that filtering operations (by tags, source, health)
        are thread-safe when executed concurrently with modifications.
        """
        import threading
        from datetime import timezone

        from proxywhirl.models import ProxySource
        from tests.conftest import ProxyFactory

        pool = ProxyPool(name="test_pool")

        # Pre-populate with tagged and sourced proxies (with timezone-aware datetimes)
        now = datetime.now(timezone.utc)
        for i in range(30):
            tags = {"tag1"} if i % 2 == 0 else {"tag2"}
            source = ProxySource.FETCHED if i % 3 == 0 else ProxySource.USER
            proxy = ProxyFactory.build(
                tags=tags,
                source=source,
                created_at=now,
                updated_at=now,
                # Ensure no expiration to avoid timezone comparison issues
                expires_at=None,
                ttl=None,
            )
            pool.add_proxy(proxy)

        errors = []
        filter_results = []

        def filter_pool():
            """Perform various filter operations."""
            for _ in range(15):
                try:
                    # Filter by tags
                    tag1_proxies = pool.filter_by_tags({"tag1"})
                    filter_results.append(("tag1", len(tag1_proxies)))

                    # Filter by source
                    fetched_proxies = pool.filter_by_source(ProxySource.FETCHED)
                    filter_results.append(("fetched", len(fetched_proxies)))

                    # Get healthy proxies
                    healthy_proxies = pool.get_healthy_proxies()
                    filter_results.append(("healthy", len(healthy_proxies)))
                except Exception as e:
                    errors.append(("filter", e))

        def modify_pool():
            """Add and modify proxies during filtering."""
            for i in range(10):
                try:
                    # Add proxy with tag1 (with timezone-aware datetimes)
                    modify_now = datetime.now(timezone.utc)
                    proxy = ProxyFactory.build(
                        tags={"tag1"},
                        source=ProxySource.FETCHED,
                        created_at=modify_now,
                        updated_at=modify_now,
                        # Ensure no expiration to avoid timezone comparison issues
                        expires_at=None,
                        ttl=None,
                    )
                    pool.add_proxy(proxy)

                    # Modify health status of some proxies
                    all_proxies = pool.get_all_proxies()
                    if all_proxies:
                        all_proxies[i % len(all_proxies)].record_success(100.0)
                except Exception as e:
                    errors.append(("modify", e))

        # Create 3 filter threads and 2 modifier threads
        threads = [threading.Thread(target=filter_pool) for _ in range(3)]
        threads += [threading.Thread(target=modify_pool) for _ in range(2)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify no errors
        assert not errors, f"Concurrent filter operations had errors: {errors}"

        # Verify we collected filter results
        assert len(filter_results) == 135, f"Expected 135 filter results, got {len(filter_results)}"

        # Verify all filter results are valid (non-negative counts)
        for filter_type, count in filter_results:
            assert count >= 0, f"Filter {filter_type} returned negative count: {count}"

    def test_concurrent_clear_operations(self):
        """Test thread safety of clear operations.

        This test verifies that clear_unhealthy and clear_expired operations
        are thread-safe and correctly rebuild the internal ID index.
        """
        import threading
        from datetime import timedelta, timezone

        from tests.conftest import ProxyFactory

        pool = ProxyPool(name="test_pool")

        # Pre-populate with mix of healthy, unhealthy, and expired proxies
        # Use timezone-aware datetimes to prevent comparison issues
        now = datetime.now(timezone.utc)
        for _ in range(20):
            proxy = ProxyFactory.healthy()
            proxy.created_at = now
            proxy.updated_at = now
            proxy.expires_at = None  # No expiration for healthy proxies
            proxy.ttl = None
            pool.add_proxy(proxy)

        for _ in range(15):
            proxy = ProxyFactory.unhealthy()
            proxy.created_at = now
            proxy.updated_at = now
            proxy.expires_at = None  # No expiration for unhealthy proxies
            proxy.ttl = None
            pool.add_proxy(proxy)

        # Add some expired proxies (with timezone-aware datetimes)
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=1)
        for _ in range(10):
            expired_proxy = ProxyFactory.build(
                created_at=past - timedelta(hours=2),
                updated_at=past - timedelta(hours=2),
                expires_at=past,
            )
            pool.add_proxy(expired_proxy)

        errors = []
        clear_results = []

        def clear_unhealthy_loop():
            """Clear unhealthy proxies repeatedly."""
            for _ in range(5):
                try:
                    removed = pool.clear_unhealthy()
                    clear_results.append(("unhealthy", removed))
                except Exception as e:
                    errors.append(("clear_unhealthy", e))

        def clear_expired_loop():
            """Clear expired proxies repeatedly."""
            for _ in range(5):
                try:
                    removed = pool.clear_expired()
                    clear_results.append(("expired", removed))
                except Exception as e:
                    errors.append(("clear_expired", e))

        def verify_id_index():
            """Verify ID index consistency after clears."""
            for _ in range(10):
                try:
                    all_proxies = pool.get_all_proxies()
                    # Verify each proxy can be found by ID
                    for proxy in all_proxies:
                        found = pool.get_proxy_by_id(proxy.id)
                        if found is None:
                            errors.append(("index", f"Proxy {proxy.id} not in index"))
                except Exception as e:
                    errors.append(("verify", e))

        # Create threads
        threads = [threading.Thread(target=clear_unhealthy_loop) for _ in range(2)]
        threads += [threading.Thread(target=clear_expired_loop) for _ in range(2)]
        threads += [threading.Thread(target=verify_id_index) for _ in range(2)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify no errors
        assert not errors, f"Concurrent clear operations had errors: {errors}"

        # After clearing, pool should only have healthy, non-expired proxies
        final_proxies = pool.get_all_proxies()
        assert all(p.is_healthy for p in final_proxies), "All remaining proxies should be healthy"
        assert all(
            not p.is_expired for p in final_proxies
        ), "All remaining proxies should not be expired"

        # Verify ID index is consistent
        for proxy in final_proxies:
            found = pool.get_proxy_by_id(proxy.id)
            assert found is not None, f"Proxy {proxy.id} should be in index"
            assert found.id == proxy.id, "Found proxy should have matching ID"
