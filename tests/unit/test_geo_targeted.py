"""Unit tests for GeoTargetedStrategy.

Tests the geo-targeted proxy selection including:
- Filtering by country code
- Filtering by region
- Fallback behavior when no matches
- Secondary strategy application
- Error handling for missing geo data
"""

import pytest

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import (
    Proxy,
    ProxyPool,
    SelectionContext,
    StrategyConfig,
)
from proxywhirl.strategies import GeoTargetedStrategy


@pytest.fixture
def geo_pool() -> ProxyPool:
    """Create a pool with proxies from different countries."""
    proxies = [
        Proxy(url="http://us1.example.com:8001", country_code="US"),
        Proxy(url="http://us2.example.com:8002", country_code="US"),
        Proxy(url="http://uk1.example.com:8003", country_code="GB"),
        Proxy(url="http://uk2.example.com:8004", country_code="GB"),
        Proxy(url="http://de1.example.com:8005", country_code="DE"),
        Proxy(url="http://jp1.example.com:8006", country_code="JP"),
        Proxy(url="http://no-geo.example.com:8007"),  # No country code
    ]
    return ProxyPool(name="geo_pool", proxies=proxies)


@pytest.fixture
def strategy() -> GeoTargetedStrategy:
    """Create a GeoTargetedStrategy instance."""
    return GeoTargetedStrategy()


def test_select_filters_by_country_code(strategy: GeoTargetedStrategy, geo_pool: ProxyPool) -> None:
    """Test that proxies are filtered by target country code."""
    context = SelectionContext(target_country="US")

    # Select multiple times to verify only US proxies returned
    selected_countries = set()
    for _ in range(10):
        proxy = strategy.select(geo_pool, context)
        selected_countries.add(proxy.country_code)

    # Should only select US proxies
    assert selected_countries == {"US"}


def test_select_filters_by_region(strategy: GeoTargetedStrategy, geo_pool: ProxyPool) -> None:
    """Test that proxies are filtered by target region."""
    # Add region info to proxies
    for proxy in geo_pool.proxies:
        if proxy.country_code in ("GB", "DE"):
            proxy.region = "EU"
        elif proxy.country_code == "US":
            proxy.region = "NA"
        elif proxy.country_code == "JP":
            proxy.region = "APAC"

    context = SelectionContext(target_region="EU")

    # Select multiple times
    selected_countries = set()
    for _ in range(10):
        proxy = strategy.select(geo_pool, context)
        selected_countries.add(proxy.country_code)

    # Should only select EU proxies (GB and DE)
    assert selected_countries.issubset({"GB", "DE"})


def test_select_prefers_country_over_region(
    strategy: GeoTargetedStrategy, geo_pool: ProxyPool
) -> None:
    """Test that country code takes precedence over region."""
    # Add region info
    for proxy in geo_pool.proxies:
        if proxy.country_code in ("GB", "DE"):
            proxy.region = "EU"

    # Request specific country within region
    context = SelectionContext(target_country="GB", target_region="EU")

    # Select multiple times
    selected_countries = set()
    for _ in range(10):
        proxy = strategy.select(geo_pool, context)
        selected_countries.add(proxy.country_code)

    # Should only select GB proxies (not all EU)
    assert selected_countries == {"GB"}


def test_select_raises_when_no_matches_and_no_fallback(
    strategy: GeoTargetedStrategy, geo_pool: ProxyPool
) -> None:
    """Test that error is raised when no proxies match and fallback disabled."""
    # Configure no fallback
    config = StrategyConfig(geo_fallback_enabled=False)
    strategy.configure(config)

    # Request country not in pool
    context = SelectionContext(target_country="FR")

    with pytest.raises(ProxyPoolEmptyError) as exc_info:
        strategy.select(geo_pool, context)

    assert "No proxies available for target location" in str(exc_info.value)
    assert "FR" in str(exc_info.value)


def test_select_falls_back_when_no_matches_and_fallback_enabled(
    strategy: GeoTargetedStrategy, geo_pool: ProxyPool
) -> None:
    """Test fallback to any proxy when no matches found."""
    # Configure with fallback enabled (default)
    config = StrategyConfig(geo_fallback_enabled=True)
    strategy.configure(config)

    # Request country not in pool
    context = SelectionContext(target_country="FR")

    # Should not raise, should select from any available proxy
    proxy = strategy.select(geo_pool, context)
    assert proxy is not None
    assert proxy.country_code != "FR"  # Won't be FR since none exist


def test_select_with_no_target_uses_any_proxy(
    strategy: GeoTargetedStrategy, geo_pool: ProxyPool
) -> None:
    """Test that missing target location selects from any proxy."""
    context = SelectionContext()  # No target specified

    # Should select from any proxy
    selected_countries = set()
    for _ in range(20):
        proxy = strategy.select(geo_pool, context)
        selected_countries.add(proxy.country_code)

    # Should have variety (at least 2 different countries)
    assert len(selected_countries) >= 2


def test_configure_accepts_fallback_setting(
    strategy: GeoTargetedStrategy, geo_pool: ProxyPool
) -> None:
    """Test configuration of fallback behavior."""
    # Disable fallback
    config = StrategyConfig(geo_fallback_enabled=False)
    strategy.configure(config)

    # Verify fallback is disabled
    context = SelectionContext(target_country="FR")
    with pytest.raises(ProxyPoolEmptyError):
        strategy.select(geo_pool, context)


def test_configure_accepts_secondary_strategy(
    strategy: GeoTargetedStrategy, geo_pool: ProxyPool
) -> None:
    """Test configuration of secondary selection strategy."""
    # This is a placeholder - secondary strategy config will be string-based
    config = StrategyConfig(geo_secondary_strategy="round_robin")
    strategy.configure(config)

    # Should still work with configured secondary strategy
    context = SelectionContext(target_country="US")
    proxy = strategy.select(geo_pool, context)
    assert proxy.country_code == "US"


def test_validate_metadata_returns_true_with_country_codes(
    strategy: GeoTargetedStrategy, geo_pool: ProxyPool
) -> None:
    """Test metadata validation passes when proxies have country codes."""
    result = strategy.validate_metadata(geo_pool)
    assert result is True


def test_validate_metadata_returns_true_with_no_country_codes(
    strategy: GeoTargetedStrategy,
) -> None:
    """Test metadata validation passes even without country codes."""
    # Pool with no country codes
    proxies = [
        Proxy(url="http://proxy1.example.com:8001"),
        Proxy(url="http://proxy2.example.com:8002"),
    ]
    pool = ProxyPool(name="no_geo", proxies=proxies)

    # Should still return True (geo-targeting is optional)
    result = strategy.validate_metadata(pool)
    assert result is True


def test_record_result_updates_proxy_metadata(
    strategy: GeoTargetedStrategy, geo_pool: ProxyPool
) -> None:
    """Test that proxy metadata is updated after requests."""
    context = SelectionContext(target_country="US")
    proxy = strategy.select(geo_pool, context)

    initial_requests = proxy.total_requests

    # Record result
    strategy.record_result(proxy, success=True, response_time_ms=150.0)

    # Verify metadata updated
    assert proxy.total_requests == initial_requests + 1
    assert proxy.total_successes == 1


def test_select_respects_context_failed_proxies(
    strategy: GeoTargetedStrategy, geo_pool: ProxyPool
) -> None:
    """Test that previously failed proxies are excluded."""
    # Get US proxy IDs
    us_proxies = [p for p in geo_pool.proxies if p.country_code == "US"]
    failed_id = str(us_proxies[0].id)

    context = SelectionContext(target_country="US", failed_proxy_ids=[failed_id])

    # Select multiple times
    for _ in range(10):
        proxy = strategy.select(geo_pool, context)
        # Should never select the failed proxy
        assert str(proxy.id) != failed_id
        assert proxy.country_code == "US"


def test_select_with_all_target_proxies_failed(
    strategy: GeoTargetedStrategy, geo_pool: ProxyPool
) -> None:
    """Test behavior when all proxies in target region have failed."""
    # Mark all US proxies as failed
    us_proxies = [p for p in geo_pool.proxies if p.country_code == "US"]
    failed_ids = [str(p.id) for p in us_proxies]

    # With fallback enabled
    config = StrategyConfig(geo_fallback_enabled=True)
    strategy.configure(config)

    context = SelectionContext(target_country="US", failed_proxy_ids=failed_ids)

    # Should fall back to other countries
    proxy = strategy.select(geo_pool, context)
    assert proxy.country_code != "US"


def test_select_applies_secondary_strategy_to_filtered_list(
    strategy: GeoTargetedStrategy, geo_pool: ProxyPool
) -> None:
    """Test that secondary strategy is applied to filtered proxies."""
    context = SelectionContext(target_country="US")

    # Select multiple times - should distribute across US proxies
    selected_ids = set()
    for _ in range(20):
        proxy = strategy.select(geo_pool, context)
        selected_ids.add(str(proxy.id))

    # Should have selected both US proxies
    us_proxy_ids = {str(p.id) for p in geo_pool.proxies if p.country_code == "US"}
    assert selected_ids == us_proxy_ids
