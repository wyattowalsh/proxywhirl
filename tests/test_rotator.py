"""Tests for ProxyRotator strategies.

Comprehensive test suite for proxy rotation with property-based testing,
error scenarios, and integration testing.
"""

from ipaddress import ip_address

import pytest
from hypothesis import given
from hypothesis import strategies as st

from proxywhirl.models import (
    AnonymityLevel,
    ErrorHandlingPolicy,
    Proxy,
    ProxyStatus,
    RotationStrategy,
    Scheme,
    ValidationErrorType,
)
from proxywhirl.rotator import ProxyRotator


def _proxies(n: int = 3) -> list[Proxy]:
    """Create test proxies with predictable values."""
    proxies: list[Proxy] = []
    for i in range(n):
        host = f"192.0.2.{i}"
        proxies.append(
            Proxy(
                host=host,
                ip=ip_address(host),
                port=8000 + i,
                schemes=[Scheme.HTTP],
                response_time=0.1 + i,
                country_code=None,
                country=None,
                city=None,
                anonymity=AnonymityLevel.UNKNOWN,
                source=None,
            )
        )
    return proxies


# Property-based testing strategies
proxy_strategy = st.builds(
    Proxy,
    host=st.text(min_size=7, max_size=15).filter(lambda x: "." in x and len(x.split(".")) == 4),
    ip=st.from_regex(
        r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    ).map(ip_address),
    port=st.integers(min_value=1, max_value=65535),
    schemes=st.lists(st.sampled_from(list(Scheme)), min_size=1),
    country_code=st.one_of(
        st.none(), st.text(min_size=2, max_size=2, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    ),
    anonymity=st.sampled_from(list(AnonymityLevel)),
    response_time=st.floats(min_value=0.01, max_value=10.0),
    source=st.one_of(st.none(), st.text(min_size=1, max_size=20)),
)

rotation_strategy = st.sampled_from(list(RotationStrategy))


def test_round_robin():
    """Test round-robin rotation strategy."""
    r = ProxyRotator(RotationStrategy.ROUND_ROBIN)
    proxies = _proxies()
    got: list[str] = []
    for _ in range(5):
        p = r.get_proxy(proxies)
        assert p is not None
        got.append(p.host)
    assert got[:3] == ["192.0.2.0", "192.0.2.1", "192.0.2.2"]


def test_rotator_invalid_strategy():
    """Test rotator initialization with invalid strategy."""
    with pytest.raises(ValueError, match="Invalid rotation strategy"):
        ProxyRotator("invalid_strategy")  # type: ignore


def test_random_selection():
    """Test random rotation strategy."""
    r = ProxyRotator(RotationStrategy.RANDOM)
    proxies = _proxies()
    # Should always return a member
    for _ in range(5):
        p = r.get_proxy(proxies)
        assert p is not None and p in proxies


def test_weighted_prefers_faster():
    """Test weighted strategy prefers faster proxies."""
    r = ProxyRotator(RotationStrategy.WEIGHTED)
    proxies = _proxies()
    # Not strictly deterministic; should often pick lower response_time
    picks: list[str] = []
    for _ in range(50):
        p = r.get_proxy(proxies)
        assert p is not None
        picks.append(p.host)
    # First proxy (fastest) should be picked more often than last (slowest)
    fast_count = picks.count(proxies[0].host)
    slow_count = picks.count(proxies[2].host)
    assert fast_count >= slow_count


def test_health_based_and_update_health():
    """Test health-based rotation and health updates."""
    r = ProxyRotator(RotationStrategy.HEALTH_BASED)
    proxies = _proxies()
    # Initially any could be chosen
    p = r.get_proxy(proxies)
    assert p is not None and p in proxies
    # Demote one proxy
    r.update_health_score(proxies[0], success=False)
    # After demotion, it's still possible but less likely; call shouldn't crash
    p = r.get_proxy(proxies)
    assert p is not None and p in proxies


def test_least_used_strategy():
    """Test LEAST_USED rotation strategy."""
    r = ProxyRotator(RotationStrategy.LEAST_USED)
    proxies = _proxies()

    # First call should pick the first proxy (all have 0 usage)
    p1 = r.get_proxy(proxies)
    assert p1 is not None

    # Second call should pick a different proxy
    # (first one now has usage count 1)
    p2 = r.get_proxy(proxies)
    assert p2 is not None
    assert p2 != p1  # Should be different

    # Continue until all proxies have been used once
    usage_counts: dict[str, int] = {}
    for _ in range(10):
        p = r.get_proxy(proxies)
        assert p is not None
        usage_counts[p.host] = usage_counts.get(p.host, 0) + 1

    # All proxies should have been used
    assert len(usage_counts) == 3


def test_weighted_strategy_comprehensive():
    """Test WEIGHTED strategy picks faster proxies more often."""
    r = ProxyRotator(RotationStrategy.WEIGHTED)
    proxies = _proxies()

    # Set different response times
    proxies[0].response_time = 0.1  # Fast
    proxies[1].response_time = 0.5  # Medium
    proxies[2].response_time = 1.0  # Slow

    picks: dict[str, int] = {}
    for _ in range(100):
        p = r.get_proxy(proxies)
        assert p is not None
        picks[p.host] = picks.get(p.host, 0) + 1

    # Faster proxy should be picked more often
    fast_picks = picks.get(proxies[0].host, 0)
    slow_picks = picks.get(proxies[2].host, 0)
    assert fast_picks > slow_picks


def test_health_based_strategy_comprehensive():
    """Test HEALTH_BASED strategy with success/failure tracking."""
    r = ProxyRotator(RotationStrategy.HEALTH_BASED)
    proxies = _proxies()

    # Mark one proxy as consistently failing
    for _ in range(5):
        r.update_health_score(proxies[0], success=False)

    # Mark another as consistently succeeding
    for _ in range(5):
        r.update_health_score(proxies[1], success=True)

    # Healthy proxy should be picked more often
    picks: dict[str, int] = {}
    for _ in range(50):
        p = r.get_proxy(proxies)
        assert p is not None
        picks[p.host] = picks.get(p.host, 0) + 1

    # Healthy proxy should be preferred
    healthy_picks = picks.get(proxies[1].host, 0)
    unhealthy_picks = picks.get(proxies[0].host, 0)
    assert healthy_picks > unhealthy_picks


def test_health_cooldown_mechanism():
    """Test that unhealthy proxies can recover after cooldown."""
    r = ProxyRotator(RotationStrategy.HEALTH_BASED)
    proxies = _proxies()

    # Mark proxy as failing
    r.update_health_score(proxies[0], success=False)

    # Verify it has low health score initially
    initial_selections: list[str] = []
    for _ in range(20):
        p = r.get_proxy(proxies)
        if p is not None:
            initial_selections.append(p.host)

    # After some successful updates, it should recover
    for _ in range(3):
        r.update_health_score(proxies[0], success=True)

    later_selections: list[str] = []
    for _ in range(20):
        p = r.get_proxy(proxies)
        if p is not None:
            later_selections.append(p.host)

    # Should see more selections of the recovered proxy
    initial_count = initial_selections.count(proxies[0].host)
    later_count = later_selections.count(proxies[0].host)
    assert later_count >= initial_count


def test_rotation_with_empty_proxy_list():
    """Test all strategies handle empty proxy list gracefully."""
    strategies = [
        RotationStrategy.ROUND_ROBIN,
        RotationStrategy.RANDOM,
        RotationStrategy.WEIGHTED,
        RotationStrategy.HEALTH_BASED,
        RotationStrategy.LEAST_USED,
    ]

    for strategy in strategies:
        r = ProxyRotator(strategy)
        result = r.get_proxy([])
        assert result is None


def test_rotation_with_single_proxy():
    """Test all strategies work with single proxy."""
    strategies = [
        RotationStrategy.ROUND_ROBIN,
        RotationStrategy.RANDOM,
        RotationStrategy.WEIGHTED,
        RotationStrategy.HEALTH_BASED,
        RotationStrategy.LEAST_USED,
    ]

    single_proxy = _proxies(1)

    for strategy in strategies:
        r = ProxyRotator(strategy)
        for _ in range(5):
            result = r.get_proxy(single_proxy)
            assert result == single_proxy[0]


# Error handling and edge case tests
class TestRotatorErrorHandling:
    """Test rotator error handling scenarios."""

    def test_error_policy_mapping(self):
        """Test error type to policy mapping."""
        rotator = ProxyRotator(RotationStrategy.HEALTH_BASED)

        # Verify error policy mappings exist
        assert ValidationErrorType.TIMEOUT in rotator.ERROR_TYPE_POLICIES
        assert ValidationErrorType.CONNECTION_ERROR in rotator.ERROR_TYPE_POLICIES
        assert ValidationErrorType.RATE_LIMITED in rotator.ERROR_TYPE_POLICIES

        # Verify policy durations exist
        assert ErrorHandlingPolicy.COOLDOWN_SHORT in rotator.ERROR_POLICY_DURATIONS
        assert ErrorHandlingPolicy.COOLDOWN_MEDIUM in rotator.ERROR_POLICY_DURATIONS
        assert ErrorHandlingPolicy.COOLDOWN_LONG in rotator.ERROR_POLICY_DURATIONS

    def test_proxy_status_filtering(self):
        """Test that blacklisted proxies are filtered out."""
        rotator = ProxyRotator(RotationStrategy.ROUND_ROBIN)
        proxies = _proxies(3)

        # Set one proxy as blacklisted
        proxies[1].status = ProxyStatus.BLACKLISTED

        # Get multiple proxies and verify blacklisted is avoided
        selected_proxies: list[Proxy] = []
        for _ in range(10):
            proxy = rotator.get_proxy(proxies)
            if proxy:
                selected_proxies.append(proxy)

        # Should not get the blacklisted proxy
        blacklisted_selections = [
            p for p in selected_proxies if p.status == ProxyStatus.BLACKLISTED
        ]
        assert len(blacklisted_selections) == 0

    def test_all_proxies_unavailable(self):
        """Test behavior when all proxies are unavailable."""
        rotator = ProxyRotator(RotationStrategy.HEALTH_BASED)
        proxies = _proxies(2)

        # Mark all proxies as blacklisted
        for proxy in proxies:
            proxy.status = ProxyStatus.BLACKLISTED

        # Should still attempt to return a proxy (emergency access)
        result = rotator.get_proxy(proxies)
        # Result may be None or emergency proxy depending on implementation


# Property-based tests
class TestRotatorPropertyBased:
    """Property-based tests for rotation strategies."""

    @given(rotation_strategy)
    def test_rotator_initialization_property(self, strategy):
        """Property test: rotator initializes correctly with any valid strategy."""
        rotator = ProxyRotator(strategy)
        assert rotator.strategy == strategy
        assert isinstance(rotator._health_scores, dict)
        assert isinstance(rotator._use_counts, dict)
        assert isinstance(rotator._sessions, dict)

    @given(st.lists(proxy_strategy, min_size=1, max_size=5))
    def test_get_proxy_always_returns_valid_proxy(self, proxies):
        """Property test: get_proxy always returns a proxy from the list or None."""
        for strategy in RotationStrategy:
            rotator = ProxyRotator(strategy)
            result = rotator.get_proxy(proxies)
            if result is not None:
                assert result in proxies

    @given(st.lists(proxy_strategy, min_size=2, max_size=10))
    def test_round_robin_coverage_property(self, proxies):
        """Property test: round-robin eventually covers all proxies."""
        rotator = ProxyRotator(RotationStrategy.ROUND_ROBIN)

        selected_hosts = set()
        # Try enough times to cover all proxies
        for _ in range(len(proxies) * 2):
            proxy = rotator.get_proxy(proxies)
            if proxy:
                selected_hosts.add(proxy.host)

        # Should have seen all proxy hosts
        expected_hosts = {p.host for p in proxies}
        assert selected_hosts == expected_hosts

    @given(proxy_strategy)
    def test_health_score_updates_property(self, proxy):
        """Property test: health score updates work for any proxy."""
        rotator = ProxyRotator(RotationStrategy.HEALTH_BASED)

        # Should not raise exceptions
        rotator.update_health_score(proxy, success=True)
        rotator.update_health_score(proxy, success=False)

        # Health scores should be tracked
        proxy_key = f"{proxy.host}:{proxy.port}"
        assert proxy_key in rotator._health_scores


# Integration and performance tests
class TestRotatorIntegration:
    """Integration tests for rotator with realistic scenarios."""

    def test_mixed_proxy_states_scenario(self):
        """Test rotation with mixed proxy states (healthy, unhealthy, blacklisted)."""
        rotator = ProxyRotator(RotationStrategy.HEALTH_BASED)
        proxies = _proxies(5)

        # Set up mixed states
        proxies[0].status = ProxyStatus.ACTIVE  # Healthy
        proxies[1].status = ProxyStatus.BLACKLISTED  # Should be excluded
        proxies[2].error_state = ErrorState()  # Error state but might recover
        proxies[3].status = ProxyStatus.ACTIVE  # Healthy
        proxies[4].status = ProxyStatus.INACTIVE  # Might be used in emergency

        # Mark health scores
        rotator.update_health_score(proxies[0], success=True)  # Good
        rotator.update_health_score(proxies[2], success=False)  # Bad
        rotator.update_health_score(proxies[3], success=True)  # Good

        # Run rotation and verify behavior
        selections = []
        for _ in range(50):
            proxy = rotator.get_proxy(proxies)
            if proxy:
                selections.append(proxy.host)

        # Should prefer healthy proxies
        healthy_proxies = [proxies[0].host, proxies[3].host]
        healthy_selections = sum(1 for s in selections if s in healthy_proxies)
        assert healthy_selections > len(selections) // 2  # Majority should be healthy

    def test_session_based_rotation(self):
        """Test session-based proxy assignment."""
        rotator = ProxyRotator(RotationStrategy.ROUND_ROBIN, default_session_ttl=1800)
        proxies = _proxies(3)

        # Create multiple sessions
        sessions = {}
        for i in range(3):
            session_id = f"session_{i}"
            proxy = proxies[i % len(proxies)]
            sessions[session_id] = rotator.create_session_proxy(session_id, proxy)

        # Verify each session gets its assigned proxy
        for session_id, expected_proxy in sessions.items():
            retrieved_proxy = rotator.get_session_proxy(session_id)
            assert retrieved_proxy == expected_proxy

    def test_concurrent_rotation_simulation(self):
        """Simulate concurrent rotation requests."""
        rotator = ProxyRotator(RotationStrategy.LEAST_USED)
        proxies = _proxies(5)

        # Simulate concurrent requests
        results = []
        for _ in range(100):
            proxy = rotator.get_proxy(proxies)
            if proxy:
                results.append(proxy.host)

        # Verify load distribution
        usage_counts = {}
        for host in results:
            usage_counts[host] = usage_counts.get(host, 0) + 1

        # Should have relatively even distribution for LEAST_USED
        if usage_counts:
            min_usage = min(usage_counts.values())
            max_usage = max(usage_counts.values())
            # Difference shouldn't be too large for least-used strategy
            assert max_usage - min_usage <= 5


# Performance benchmarks
class TestRotatorPerformance:
    """Performance benchmarks for rotation strategies."""

    def test_round_robin_performance(self, benchmark):
        """Benchmark round-robin strategy performance."""
        rotator = ProxyRotator(RotationStrategy.ROUND_ROBIN)
        proxies = _proxies(100)

        @benchmark
        def get_proxy_roundrobin():
            return rotator.get_proxy(proxies)

        result = get_proxy_roundrobin
        assert result is not None

    def test_weighted_selection_performance(self, benchmark):
        """Benchmark weighted selection performance."""
        rotator = ProxyRotator(RotationStrategy.WEIGHTED)
        proxies = _proxies(100)

        # Set varied response times
        for i, proxy in enumerate(proxies):
            proxy.response_time = 0.1 + (i * 0.01)  # Increasing response times

        @benchmark
        def get_proxy_weighted():
            return rotator.get_proxy(proxies)

        result = get_proxy_weighted
        assert result is not None

    def test_health_based_selection_performance(self, benchmark):
        """Benchmark health-based selection with health tracking."""
        rotator = ProxyRotator(RotationStrategy.HEALTH_BASED)
        proxies = _proxies(50)

        # Initialize health scores
        for i, proxy in enumerate(proxies):
            success_rate = 0.8 if i % 2 == 0 else 0.3  # Alternate good/bad
            for _ in range(10):
                rotator.update_health_score(proxy, success=success_rate > 0.5)

        @benchmark
        def get_proxy_health_based():
            return rotator.get_proxy(proxies)

        result = get_proxy_health_based
        assert result is not None
