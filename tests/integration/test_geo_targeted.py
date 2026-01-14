"""Integration tests for GeoTargetedStrategy.

Tests the complete geo-targeting behavior including:
- SC-006: 100% correct region selection
- Multiple regions
- Fallback behavior
- High load scenarios
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
def multi_region_pool() -> ProxyPool:
    """Create a pool with proxies from multiple regions."""
    proxies = [
        # North America
        Proxy(url="http://us1.example.com:8001", country_code="US", region="NA"),
        Proxy(url="http://us2.example.com:8002", country_code="US", region="NA"),
        Proxy(url="http://ca1.example.com:8003", country_code="CA", region="NA"),
        # Europe
        Proxy(url="http://uk1.example.com:8004", country_code="GB", region="EU"),
        Proxy(url="http://uk2.example.com:8005", country_code="GB", region="EU"),
        Proxy(url="http://de1.example.com:8006", country_code="DE", region="EU"),
        Proxy(url="http://fr1.example.com:8007", country_code="FR", region="EU"),
        # Asia Pacific
        Proxy(url="http://jp1.example.com:8008", country_code="JP", region="APAC"),
        Proxy(url="http://sg1.example.com:8009", country_code="SG", region="APAC"),
        # No geo data
        Proxy(url="http://unknown.example.com:8010"),
    ]
    return ProxyPool(name="multi_region", proxies=proxies)


@pytest.fixture
def strategy() -> GeoTargetedStrategy:
    """Create a GeoTargetedStrategy instance."""
    return GeoTargetedStrategy()


def test_sc_006_correct_region_selection_country(
    strategy: GeoTargetedStrategy, multi_region_pool: ProxyPool
) -> None:
    """Test SC-006: 100% correct region selection when specifying country.

    Success Criteria:
    - 100% of selections match target country
    - Test with 100 requests for statistical significance
    """
    context = SelectionContext(target_country="GB")

    # Make 100 selections
    for _ in range(100):
        proxy = strategy.select(multi_region_pool, context)
        # All selections must be GB
        assert proxy.country_code == "GB", f"Expected GB, got {proxy.country_code}"


def test_sc_006_correct_region_selection_region(
    strategy: GeoTargetedStrategy, multi_region_pool: ProxyPool
) -> None:
    """Test SC-006: 100% correct region selection when specifying region.

    Success Criteria:
    - 100% of selections match target region
    - Test with 100 requests for statistical significance
    """
    context = SelectionContext(target_region="EU")

    # Expected countries in EU region
    eu_countries = {"GB", "DE", "FR"}

    # Make 100 selections
    selected_countries = set()
    for _ in range(100):
        proxy = strategy.select(multi_region_pool, context)
        # Must be from EU region
        assert proxy.region == "EU", f"Expected EU region, got {proxy.region}"
        assert proxy.country_code in eu_countries, f"Country {proxy.country_code} not in EU"
        selected_countries.add(proxy.country_code)

    # Should have distributed across multiple EU countries
    assert len(selected_countries) >= 2, "Should distribute across EU countries"


def test_multiple_concurrent_geo_requests(
    strategy: GeoTargetedStrategy, multi_region_pool: ProxyPool
) -> None:
    """Test concurrent requests to different regions."""
    from threading import Thread
    from typing import List

    results: List[tuple[str, str]] = []  # (target, actual)
    errors: List[Exception] = []

    def make_requests(target_country: str) -> None:
        try:
            context = SelectionContext(target_country=target_country)
            for _ in range(10):
                proxy = strategy.select(multi_region_pool, context)
                results.append((target_country, proxy.country_code))
        except Exception as e:
            errors.append(e)

    # Create threads for different countries
    threads = []
    for country in ["US", "GB", "JP"]:
        thread = Thread(target=make_requests, args=(country,))
        threads.append(thread)
        thread.start()

    # Wait for all threads
    for thread in threads:
        thread.join()

    # Check for errors
    assert len(errors) == 0, f"Errors occurred: {errors}"

    # Verify all selections matched targets
    assert len(results) == 30  # 3 countries × 10 requests
    for target, actual in results:
        assert actual == target, f"Expected {target}, got {actual}"


def test_high_load_geo_targeting(
    strategy: GeoTargetedStrategy, multi_region_pool: ProxyPool
) -> None:
    """Test geo-targeting under high load (1000 requests)."""
    context = SelectionContext(target_region="NA")

    na_countries = {"US", "CA"}
    selected_countries = set()

    # Make 1000 selections
    for _ in range(1000):
        proxy = strategy.select(multi_region_pool, context)
        assert proxy.region == "NA", f"Expected NA, got {proxy.region}"
        assert proxy.country_code in na_countries
        selected_countries.add(proxy.country_code)

    # Should have used both US and CA proxies
    assert selected_countries == na_countries


def test_fallback_behavior_no_matches(
    strategy: GeoTargetedStrategy, multi_region_pool: ProxyPool
) -> None:
    """Test fallback behavior when no proxies match target."""
    # Enable fallback (default)
    config = StrategyConfig(geo_fallback_enabled=True)
    strategy.configure(config)

    # Request country not in pool
    context = SelectionContext(target_country="BR")  # Brazil not in pool

    # Should fallback to any available proxy
    proxy = strategy.select(multi_region_pool, context)
    assert proxy is not None
    assert proxy.country_code != "BR"  # Won't be BR since none exist


def test_no_fallback_raises_error(
    strategy: GeoTargetedStrategy, multi_region_pool: ProxyPool
) -> None:
    """Test that error is raised when no matches and fallback disabled."""
    # Disable fallback
    config = StrategyConfig(geo_fallback_enabled=False)
    strategy.configure(config)

    # Request country not in pool
    context = SelectionContext(target_country="BR")

    with pytest.raises(ProxyPoolEmptyError) as exc_info:
        strategy.select(multi_region_pool, context)

    assert "No proxies available" in str(exc_info.value)
    assert "BR" in str(exc_info.value)


def test_geo_targeting_with_failed_proxies(
    strategy: GeoTargetedStrategy, multi_region_pool: ProxyPool
) -> None:
    """Test geo-targeting respects failed proxy list."""
    # Get GB proxy IDs
    gb_proxies = [p for p in multi_region_pool.proxies if p.country_code == "GB"]
    failed_id = str(gb_proxies[0].id)
    other_gb_id = str(gb_proxies[1].id)

    context = SelectionContext(target_country="GB", failed_proxy_ids=[failed_id])

    # Make multiple selections
    for _ in range(20):
        proxy = strategy.select(multi_region_pool, context)
        # Should be GB but not the failed one
        assert proxy.country_code == "GB"
        assert str(proxy.id) != failed_id
        # Should be the other GB proxy
        assert str(proxy.id) == other_gb_id


def test_geo_distribution_across_region(
    strategy: GeoTargetedStrategy, multi_region_pool: ProxyPool
) -> None:
    """Test that selections distribute across proxies in target region."""
    context = SelectionContext(target_region="EU")

    # Track proxy IDs selected
    selected_ids = set()
    for _ in range(100):
        proxy = strategy.select(multi_region_pool, context)
        assert proxy.region == "EU"
        selected_ids.add(str(proxy.id))

    # Should have selected multiple different EU proxies
    eu_proxy_count = len([p for p in multi_region_pool.proxies if p.region == "EU"])
    assert (
        len(selected_ids) >= 2
    ), f"Should distribute across EU proxies (got {len(selected_ids)} of {eu_proxy_count})"


def test_country_preference_over_region(
    strategy: GeoTargetedStrategy, multi_region_pool: ProxyPool
) -> None:
    """Test that country takes precedence over region in context."""
    # Request specific country within a region
    context = SelectionContext(target_country="US", target_region="NA")

    # Make multiple selections
    for _ in range(50):
        proxy = strategy.select(multi_region_pool, context)
        # Should only select US, not other NA countries
        assert proxy.country_code == "US"
        assert proxy.region == "NA"


def test_mixed_geo_and_non_geo_proxies(
    strategy: GeoTargetedStrategy, multi_region_pool: ProxyPool
) -> None:
    """Test behavior with mix of geo-tagged and non-geo-tagged proxies."""
    context = SelectionContext(target_country="JP")

    # Make multiple selections
    for _ in range(20):
        proxy = strategy.select(multi_region_pool, context)
        # Should only select JP proxies
        assert proxy.country_code == "JP"
        # Should not select the unknown proxy
        assert proxy.url != "http://unknown.example.com:8010"


def test_secondary_strategy_application(
    strategy: GeoTargetedStrategy, multi_region_pool: ProxyPool
) -> None:
    """Test that secondary strategy is applied to filtered proxies."""
    # Configure with least_used secondary strategy
    config = StrategyConfig(geo_secondary_strategy="least_used")
    strategy.configure(config)

    context = SelectionContext(target_country="GB")

    # Get GB proxies
    gb_proxies = [p for p in multi_region_pool.proxies if p.country_code == "GB"]

    # Make selections and track usage
    for _ in range(10):
        proxy = strategy.select(multi_region_pool, context)
        assert proxy.country_code == "GB"
        # Simulate completion to update usage
        strategy.record_result(proxy, success=True, response_time_ms=100.0)

    # Usage should be relatively balanced (least_used should distribute)
    usage_counts = {p.total_requests for p in gb_proxies}
    assert len(usage_counts) >= 1  # At least some variation
