"""
Property-based tests for GeoTargetedStrategy.

Tests invariants and properties that should hold for all valid inputs.
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from proxywhirl import GeoTargetedStrategy, ProxyPool
from proxywhirl.models import HealthStatus, Proxy, SelectionContext, StrategyConfig


# Hypothesis strategies for generating test data
@st.composite
def proxy_with_geo(draw):
    """Generate a proxy with optional geo metadata."""
    proxy_num = draw(st.integers(min_value=1, max_value=1000))
    port = draw(st.integers(min_value=1024, max_value=65535))
    protocol = draw(st.sampled_from(["http", "https", "socks5"]))
    country_code = draw(
        st.one_of(
            st.none(),
            st.sampled_from(["US", "GB", "DE", "FR", "JP", "CN", "BR", "IN", "AU", "CA"]),
        )
    )
    region = draw(
        st.one_of(
            st.none(),
            st.sampled_from(["NA", "EU", "APAC", "LATAM", "AFRICA", "ME"]),
        )
    )

    proxy = Proxy(
        url=f"{protocol}://proxy{proxy_num}.example.com:{port}",
        country_code=country_code,
        region=region,
        health_status=HealthStatus.HEALTHY,
    )
    return proxy


@st.composite
def pool_with_geo_proxies(draw, min_size=1, max_size=20):
    """Generate a proxy pool with geo metadata."""
    pool = ProxyPool(name="test_pool")
    num_proxies = draw(st.integers(min_value=min_size, max_value=max_size))
    for _ in range(num_proxies):
        proxy = draw(proxy_with_geo())
        pool.add_proxy(proxy)
    return pool


@st.composite
def selection_context_with_geo(draw):
    """Generate a SelectionContext with optional geo targeting."""
    target_country = draw(
        st.one_of(
            st.none(),
            st.sampled_from(["US", "GB", "DE", "FR", "JP", "CN", "BR", "IN", "AU", "CA"]),
        )
    )
    target_region = draw(
        st.one_of(
            st.none(),
            st.sampled_from(["NA", "EU", "APAC", "LATAM", "AFRICA", "ME"]),
        )
    )

    return SelectionContext(
        target_country=target_country,
        target_region=target_region,
    )


class TestGeoTargetedProperties:
    """Property-based tests for GeoTargetedStrategy."""

    @given(pool=pool_with_geo_proxies(min_size=1, max_size=10))
    @settings(max_examples=50, deadline=5000)
    def test_property_always_returns_proxy_from_pool(self, pool: ProxyPool):
        """Property: Selected proxy is always from the pool."""
        strategy = GeoTargetedStrategy()
        context = SelectionContext()

        selected = strategy.select(pool, context)
        assert selected in pool.proxies

    @given(
        pool=pool_with_geo_proxies(min_size=3, max_size=10),
        context=selection_context_with_geo(),
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_country_filtering_correct(self, pool: ProxyPool, context: SelectionContext):
        """Property: When country is specified, only matching proxies are selected."""
        strategy = GeoTargetedStrategy()

        # Get matching proxies
        matching = [
            p
            for p in pool.proxies
            if p.country_code == context.target_country and p.health_status == HealthStatus.HEALTHY
        ]

        if context.target_country and matching:
            selected = strategy.select(pool, context)
            assert selected.country_code == context.target_country

    @given(
        pool=pool_with_geo_proxies(min_size=3, max_size=10),
        context=selection_context_with_geo(),
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_region_filtering_correct(self, pool: ProxyPool, context: SelectionContext):
        """Property: When region is specified (no country), only matching proxies selected."""
        strategy = GeoTargetedStrategy()

        # Only test region filtering if no country specified
        if context.target_country:
            return

        # Get matching proxies
        matching = [
            p
            for p in pool.proxies
            if p.region == context.target_region and p.health_status == HealthStatus.HEALTHY
        ]

        if context.target_region and matching:
            selected = strategy.select(pool, context)
            assert selected.region == context.target_region

    @given(pool=pool_with_geo_proxies(min_size=5, max_size=15))
    @settings(max_examples=30, deadline=5000)
    def test_property_fallback_uses_any_proxy(self, pool: ProxyPool):
        """Property: With fallback enabled, any healthy proxy can be selected."""
        strategy = GeoTargetedStrategy()
        config = StrategyConfig(geo_fallback_enabled=True)
        strategy.configure(config)

        # Request non-existent country
        context = SelectionContext(target_country="ZZ")

        # Should fall back to any healthy proxy
        selected = strategy.select(pool, context)
        assert selected in pool.proxies
        assert selected.health_status == HealthStatus.HEALTHY

    @given(
        pool=pool_with_geo_proxies(min_size=5, max_size=15),
        secondary=st.sampled_from(["round_robin", "random", "least_used"]),
    )
    @settings(max_examples=30, deadline=5000)
    def test_property_secondary_strategy_applied(self, pool: ProxyPool, secondary: str):
        """Property: Secondary strategy is applied to filtered proxies."""
        strategy = GeoTargetedStrategy()
        config = StrategyConfig(geo_secondary_strategy=secondary)
        strategy.configure(config)

        context = SelectionContext()

        # Should not raise (any healthy proxy acceptable)
        selected = strategy.select(pool, context)
        assert selected in pool.proxies
        assert selected.health_status == HealthStatus.HEALTHY

    @given(
        pool=pool_with_geo_proxies(min_size=5, max_size=15),
        num_selections=st.integers(min_value=10, max_value=50),
    )
    @settings(max_examples=20, deadline=10000)
    def test_property_idempotent_metadata_validation(self, pool: ProxyPool, num_selections: int):
        """Property: validate_metadata result doesn't change over multiple calls."""
        strategy = GeoTargetedStrategy()

        first_result = strategy.validate_metadata(pool)

        # Call validate_metadata multiple times
        for _ in range(num_selections):
            assert strategy.validate_metadata(pool) == first_result

    @given(
        pool=pool_with_geo_proxies(min_size=3, max_size=10),
        target_country=st.sampled_from(["US", "GB", "DE", "FR", "JP"]),
    )
    @settings(max_examples=30, deadline=5000)
    def test_property_country_precedence_over_region(self, pool: ProxyPool, target_country: str):
        """Property: Country takes precedence over region when both specified."""
        strategy = GeoTargetedStrategy()

        # Ensure at least one proxy matches country
        pool.proxies[0].country_code = target_country
        pool.proxies[0].region = "EU"  # Different region
        pool.proxies[0].health_status = HealthStatus.HEALTHY

        # Request with both country and region (different region)
        context = SelectionContext(
            target_country=target_country,
            target_region="APAC",  # Different from proxy's region
        )

        selected = strategy.select(pool, context)

        # Should match by country, ignoring region mismatch
        assert selected.country_code == target_country

    @given(
        pool=pool_with_geo_proxies(min_size=5, max_size=15),
        num_selections=st.integers(min_value=10, max_value=50),
    )
    @settings(max_examples=20, deadline=10000)
    def test_property_selection_consistency_with_same_context(
        self, pool: ProxyPool, num_selections: int
    ):
        """Property: With round_robin secondary, selections are consistent."""
        strategy = GeoTargetedStrategy()
        config = StrategyConfig(geo_secondary_strategy="round_robin")
        strategy.configure(config)

        # Ensure at least one healthy proxy
        pool.proxies[0].health_status = HealthStatus.HEALTHY

        context = SelectionContext()

        # All selections should be valid
        for _ in range(min(num_selections, len(pool.proxies))):
            selected = strategy.select(pool, context)
            assert selected in pool.proxies
            assert selected.health_status == HealthStatus.HEALTHY

    @given(
        pool=pool_with_geo_proxies(min_size=3, max_size=10),
        success=st.booleans(),
        response_time=st.integers(min_value=10, max_value=5000),
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_record_result_updates_stats(
        self, pool: ProxyPool, success: bool, response_time: int
    ):
        """Property: record_result updates proxy statistics."""
        strategy = GeoTargetedStrategy()
        context = SelectionContext()

        proxy = strategy.select(pool, context)
        initial_total = proxy.total_requests
        initial_success = proxy.total_successes

        strategy.record_result(proxy, success, response_time)

        # Stats should be updated
        assert proxy.total_requests == initial_total + 1
        if success:
            assert proxy.total_successes == initial_success + 1
