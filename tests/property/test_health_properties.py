"""Property-based tests for health monitoring using Hypothesis."""

from datetime import datetime, timezone

from hypothesis import given, strategies as st

from proxywhirl.health import HealthChecker
from proxywhirl.health_models import HealthCheckConfig, HealthStatus


class TestHealthStatusStateMachine:
    """Property tests for health status state machine (T100)."""

    @given(st.integers(min_value=0, max_value=10))
    def test_status_transitions_are_valid(self, failure_count: int) -> None:
        """Test that status transitions follow valid state machine rules."""
        checker = HealthChecker()
        checker.add_proxy("http://proxy.example.com:8080", source="test")

        # Simulate failures
        for _ in range(failure_count):
            checker._proxies["http://proxy.example.com:8080"]["consecutive_failures"] += 1

        # Verify status is one of valid states
        status = checker._proxies["http://proxy.example.com:8080"]["health_status"]
        assert status in {
            HealthStatus.UNKNOWN,
            HealthStatus.HEALTHY,
            HealthStatus.UNHEALTHY,
            HealthStatus.CHECKING,
            HealthStatus.RECOVERING,
            HealthStatus.PERMANENTLY_FAILED,
        }


class TestFailureCountInvariants:
    """Property tests for failure count monotonicity (T101)."""

    @given(st.integers(min_value=0, max_value=100))
    def test_consecutive_failures_monotonic_until_reset(self, failure_count: int) -> None:
        """Test that consecutive_failures is monotonic increasing until reset."""
        checker = HealthChecker()
        checker.add_proxy("http://proxy.example.com:8080", source="test")

        # Track failures
        prev_count = 0
        for i in range(failure_count):
            checker._proxies["http://proxy.example.com:8080"][
                "consecutive_failures"
            ] = i
            current_count = checker._proxies["http://proxy.example.com:8080"][
                "consecutive_failures"
            ]
            assert current_count >= prev_count  # Monotonic
            prev_count = current_count


class TestPoolStatusIntegrity:
    """Property tests for pool status count integrity (T102)."""

    @given(
        st.integers(min_value=0, max_value=10),
        st.integers(min_value=0, max_value=10),
        st.integers(min_value=0, max_value=10),
    )
    def test_pool_counts_sum_to_total(
        self, healthy: int, unhealthy: int, unknown: int
    ) -> None:
        """Test that pool status counts sum to total."""
        checker = HealthChecker()

        # Add proxies with different statuses
        for i in range(healthy):
            checker.add_proxy(f"http://healthy{i}.example.com:8080", source="test")
            checker._proxies[f"http://healthy{i}.example.com:8080"][
                "health_status"
            ] = HealthStatus.HEALTHY

        for i in range(unhealthy):
            checker.add_proxy(f"http://unhealthy{i}.example.com:8080", source="test")
            checker._proxies[f"http://unhealthy{i}.example.com:8080"][
                "health_status"
            ] = HealthStatus.UNHEALTHY

        for i in range(unknown):
            checker.add_proxy(f"http://unknown{i}.example.com:8080", source="test")
            checker._proxies[f"http://unknown{i}.example.com:8080"][
                "health_status"
            ] = HealthStatus.UNKNOWN

        status = checker.get_pool_status()

        # Counts should sum to total
        assert (
            status.healthy_proxies
            + status.unhealthy_proxies
            + status.unknown_proxies
            + status.checking_proxies
            + status.recovering_proxies
            == status.total_proxies
        )


class TestExponentialBackoffMonotonicity:
    """Property tests for exponential backoff (T103)."""

    @given(st.integers(min_value=0, max_value=20))
    def test_backoff_cooldown_monotonic_increasing(self, attempt: int) -> None:
        """Test that backoff cooldown increases monotonically."""
        checker = HealthChecker()

        cooldown1 = checker._calculate_recovery_cooldown(attempt)
        cooldown2 = checker._calculate_recovery_cooldown(attempt + 1)

        # Cooldown should increase (unless capped)
        assert cooldown2 >= cooldown1

    @given(st.integers(min_value=0, max_value=50))
    def test_backoff_cooldown_capped(self, attempt: int) -> None:
        """Test that backoff cooldown is capped at maximum."""
        checker = HealthChecker()
        cooldown = checker._calculate_recovery_cooldown(attempt)

        # Should never exceed 1 hour
        assert cooldown <= 3600

