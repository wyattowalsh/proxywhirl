"""Tests for ProxyRotator strategies."""

# mypy: ignore-errors
from ipaddress import ip_address

from proxywhirl.models import (
    AnonymityLevel,
    Proxy,
    RotationStrategy,
    Scheme,
)
from proxywhirl.rotator import ProxyRotator


def _proxies(n: int = 3) -> list[Proxy]:
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


def test_round_robin():
    r = ProxyRotator(RotationStrategy.ROUND_ROBIN)
    proxies = _proxies()
    got: list[str] = []
    for _ in range(5):
        p = r.get_proxy(proxies)
        assert p is not None
        got.append(p.host)
    assert got[:3] == ["192.0.2.0", "192.0.2.1", "192.0.2.2"]


def test_random_selection():
    r = ProxyRotator(RotationStrategy.RANDOM)
    proxies = _proxies()
    # Should always return a member
    for _ in range(5):
        p = r.get_proxy(proxies)
        assert p is not None and p in proxies


def test_weighted_prefers_faster():
    r = ProxyRotator(RotationStrategy.WEIGHTED)
    proxies = _proxies()
    # Not strictly deterministic; should often pick lower response_time
    picks: list[str] = []
    for _ in range(50):
        p = r.get_proxy(proxies)
        assert p is not None
        picks.append(p.host)
    assert picks.count("h0") >= picks.count("h2")


def test_health_based_and_update_health():
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
    usage_counts = {}
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

    picks = {}
    for _ in range(100):
        p = r.get_proxy(proxies)
        assert p is not None
        picks[p.host] = picks.get(p.host, 0) + 1

    # Faster proxy should be picked more often
    assert picks.get(proxies[0].host, 0) > picks.get(proxies[2].host, 0)


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
    picks = {}
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
    initial_selections = []
    for _ in range(20):
        p = r.get_proxy(proxies)
        initial_selections.append(p.host)

    # After some successful updates, it should recover
    for _ in range(3):
        r.update_health_score(proxies[0], success=True)

    later_selections = []
    for _ in range(20):
        p = r.get_proxy(proxies)
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
