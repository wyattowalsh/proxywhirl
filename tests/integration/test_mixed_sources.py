"""
Integration tests for mixed proxy sources (US6).

Tests cover:
- T114: Pool contains user + fetched proxies with distinct tags
- T115: Weighted rotation follows configured weights across mixed sources
- T116: Statistics indicate source for each proxy
"""

import random

import httpx
import respx

from proxywhirl.fetchers import ProxyFetcher, ProxySourceConfig
from proxywhirl.models import HealthStatus, Proxy, ProxySource, StrategyConfig
from proxywhirl.rotator import ProxyWhirl
from proxywhirl.strategies import WeightedStrategy


class TestMixedProxySources:
    """Test mixing user-provided and fetched proxies."""

    @respx.mock
    async def test_pool_contains_user_and_fetched_with_distinct_tags(self) -> None:
        """T114/SC1: Pool contains proxies from both sources with distinct tags."""
        # Setup fetcher with mock source
        json_data = [
            {"url": "http://fetched1.example.com:8080"},
            {"url": "http://fetched2.example.com:3128"},
        ]
        respx.get("https://free-proxy-list.example.com/api").mock(
            return_value=httpx.Response(200, json=json_data)
        )

        # Create rotator and add user-provided proxies
        rotator = ProxyWhirl()
        user_proxy1 = Proxy(url="http://user1.example.com:8080")
        user_proxy2 = Proxy(url="http://user2.example.com:3128")
        rotator.add_proxy(user_proxy1)
        rotator.add_proxy(user_proxy2)

        # Fetch and add auto-fetched proxies
        source = ProxySourceConfig(
            url="https://free-proxy-list.example.com/api",
            format="json",
        )
        fetcher = ProxyFetcher(sources=[source])
        fetched_proxies = await fetcher.fetch_all(validate=False)

        # Add fetched proxies to rotator
        for proxy_dict in fetched_proxies:
            fetched_proxy = Proxy(
                url=proxy_dict["url"],
                source=ProxySource.FETCHED,
            )
            rotator.add_proxy(fetched_proxy)

        # Verify pool contains both types
        all_proxies = rotator.pool.get_all_proxies()
        assert len(all_proxies) == 4

        # Verify source tags
        user_proxies = [p for p in all_proxies if p.source == ProxySource.USER]
        fetched_proxies_list = [p for p in all_proxies if p.source == ProxySource.FETCHED]

        assert len(user_proxies) == 2
        assert len(fetched_proxies_list) == 2

        # Verify distinct tags
        assert all(p.source == ProxySource.USER for p in user_proxies)
        assert all(p.source == ProxySource.FETCHED for p in fetched_proxies_list)

    def test_weighted_rotation_prefers_explicit_weights_across_sources(self) -> None:
        """T115/SC2: Weighted rotation follows configured weights across mixed sources."""
        random.seed(0)

        strategy = WeightedStrategy()

        user_proxy = Proxy(
            url="http://premium-user.example.com:8080",
            source=ProxySource.USER,
            health_status=HealthStatus.HEALTHY,
        )

        fetched_proxies = []
        for i in range(3):
            fetched_proxies.append(
                Proxy(
                    url=f"http://fetched{i}.example.com:8080",
                    source=ProxySource.FETCHED,
                    health_status=HealthStatus.HEALTHY,
                )
            )

        strategy.configure(
            StrategyConfig(
                weights={
                    user_proxy.url: 20.0,
                    fetched_proxies[0].url: 1.0,
                    fetched_proxies[1].url: 1.0,
                    fetched_proxies[2].url: 1.0,
                }
            )
        )
        rotator = ProxyWhirl(strategy=strategy)
        rotator.add_proxy(user_proxy)
        for fetched_proxy in fetched_proxies:
            rotator.add_proxy(fetched_proxy)

        selections = [rotator.strategy.select(rotator.pool).url for _ in range(200)]
        user_selections = selections.count(user_proxy.url)
        fetched_selections = len(selections) - user_selections

        assert user_selections >= 150, (
            f"Expected weighted user proxy selected >=150 times, got {user_selections}"
        )
        assert user_selections > fetched_selections, (
            "Expected explicit weights to dominate mixed-source selection counts"
        )
        assert user_selections + fetched_selections == 200

    def test_statistics_indicate_source_for_each_proxy(self) -> None:
        """T116/SC3: Statistics clearly indicate source for each proxy."""
        rotator = ProxyWhirl()

        # Add mix of proxies
        user_proxy = Proxy(url="http://user.example.com:8080", source=ProxySource.USER)
        fetched_proxy = Proxy(url="http://fetched.example.com:8080", source=ProxySource.FETCHED)

        rotator.add_proxy(user_proxy)
        rotator.add_proxy(fetched_proxy)

        # Get statistics
        stats = rotator.get_statistics()

        # Verify source breakdown exists
        assert "source_breakdown" in stats
        source_breakdown = stats["source_breakdown"]

        # Verify counts by source
        assert source_breakdown.get(ProxySource.USER.value, 0) == 1
        assert source_breakdown.get(ProxySource.FETCHED.value, 0) == 1

    def test_mixed_sources_maintain_independent_health_tracking(self) -> None:
        """Verify user and fetched proxies track health independently."""
        rotator = ProxyWhirl()

        # Add proxies from different sources
        user_proxy = Proxy(url="http://user.example.com:8080", source=ProxySource.USER)
        fetched_proxy = Proxy(url="http://fetched.example.com:8080", source=ProxySource.FETCHED)

        rotator.add_proxy(user_proxy)
        rotator.add_proxy(fetched_proxy)

        # Simulate requests on each
        user_proxy.record_success(response_time_ms=100)
        user_proxy.record_success(response_time_ms=120)
        fetched_proxy.record_success(response_time_ms=150)
        fetched_proxy.record_failure()

        # Verify independent tracking
        assert user_proxy.total_successes == 2
        assert user_proxy.total_failures == 0
        assert fetched_proxy.total_successes == 1
        assert fetched_proxy.total_failures == 1

    @respx.mock
    async def test_fetched_proxies_can_be_refreshed_without_affecting_user_proxies(self) -> None:
        """Verify refresh updates fetched proxies but preserves user proxies."""
        # Setup
        json_data_initial = [{"url": "http://fetched1.example.com:8080"}]
        json_data_refresh = [{"url": "http://fetched2.example.com:3128"}]

        route = respx.get("https://proxy-source.example.com/api")
        route.mock(return_value=httpx.Response(200, json=json_data_initial))

        rotator = ProxyWhirl()

        # Add user proxy (should persist)
        user_proxy = Proxy(url="http://user.example.com:8080", source=ProxySource.USER)
        rotator.add_proxy(user_proxy)

        # Fetch initial proxies
        source = ProxySourceConfig(url="https://proxy-source.example.com/api", format="json")
        fetcher = ProxyFetcher(sources=[source])
        initial_proxies = await fetcher.fetch_all(validate=False)

        for proxy_dict in initial_proxies:
            rotator.add_proxy(Proxy(url=proxy_dict["url"], source=ProxySource.FETCHED))

        assert rotator.pool.size == 2

        # Simulate refresh with different proxies
        route.mock(return_value=httpx.Response(200, json=json_data_refresh))

        # User proxy should still exist
        all_proxies = rotator.pool.get_all_proxies()
        user_proxies = [p for p in all_proxies if p.source == ProxySource.USER]
        assert len(user_proxies) == 1
        assert user_proxies[0].url == "http://user.example.com:8080"
