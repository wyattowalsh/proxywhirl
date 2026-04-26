"""Tests for cache prewarming functionality."""

import asyncio

import pytest

from proxywhirl.cache_prewarmer import (
    CachePrewarmer,
    GeolocationCachePrewarmSource,
    PreheatProgress,
    PreheatStrategy,
    ProxyListPrewarmSource,
    StaticDataPrewarmSource,
)


class TestPreheatProgress:
    """Tests for PreheatProgress."""

    def test_initial_state(self):
        """Test initial progress state."""
        progress = PreheatProgress(total_items=100)

        assert progress.total_items == 100
        assert progress.loaded_items == 0
        assert progress.failed_items == 0
        assert progress.success_rate == 0.0
        assert not progress.is_complete

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        progress = PreheatProgress(total_items=100)
        progress.loaded_items = 80
        progress.failed_items = 20

        assert progress.success_rate == 80.0

    def test_completion(self):
        """Test completion detection."""
        progress = PreheatProgress(total_items=10)
        progress.loaded_items = 8
        progress.failed_items = 2

        assert progress.is_complete

        progress.mark_complete()
        assert progress.end_time is not None

    def test_elapsed_time(self):
        """Test elapsed time calculation."""
        progress = PreheatProgress(total_items=10)

        elapsed1 = progress.elapsed_seconds
        assert elapsed1 >= 0

        progress.mark_complete()
        elapsed2 = progress.elapsed_seconds
        assert elapsed2 >= elapsed1


class TestPreheatStrategy:
    """Tests for PreheatStrategy."""

    def test_strategy_creation(self):
        """Test strategy creation."""
        strategy = PreheatStrategy(
            name="test-strategy",
            description="Test description",
            priority=10,
        )

        assert strategy.name == "test-strategy"
        assert strategy.description == "Test description"
        assert strategy.priority == 10


class TestProxyListPrewarmSource:
    """Tests for ProxyListPrewarmSource."""

    @pytest.mark.asyncio
    async def test_fetch_proxies(self):
        """Test fetching proxies."""

        async def mock_fetcher():
            return [
                {"ip": "1.2.3.4", "port": 8080},
                {"ip": "5.6.7.8", "port": 8080},
            ]

        source = ProxyListPrewarmSource(
            fetcher=mock_fetcher,
            category="http",
        )

        items = []
        async for key, value in source.fetch_items():
            items.append((key, value))

        assert len(items) == 2
        assert items[0][0] == "proxy:http:0"
        assert items[1][0] == "proxy:http:1"

    @pytest.mark.asyncio
    async def test_fetch_error_handling(self):
        """Test error handling when fetching fails."""

        async def mock_fetcher():
            raise RuntimeError("Fetch failed")

        source = ProxyListPrewarmSource(
            fetcher=mock_fetcher,
            category="http",
        )

        items = []
        async for key, value in source.fetch_items():
            items.append((key, value))

        assert len(items) == 0

    def test_strategy_metadata(self):
        """Test strategy metadata."""

        async def mock_fetcher():
            return []

        source = ProxyListPrewarmSource(
            fetcher=mock_fetcher,
            category="socks5",
        )

        strategy = source.strategy

        assert strategy.name == "proxy-list-socks5"
        assert "socks5" in strategy.description
        assert strategy.priority == 10


class TestGeolocationCachePrewarmSource:
    """Tests for GeolocationCachePrewarmSource."""

    @pytest.mark.asyncio
    async def test_fetch_geolocation_data(self):
        """Test fetching geolocation data."""

        async def mock_fetcher(ips):
            return {
                "1.2.3.4": {"country": "US", "city": "NYC"},
                "5.6.7.8": {"country": "UK", "city": "London"},
            }

        source = GeolocationCachePrewarmSource(
            fetcher=mock_fetcher,
            ips=["1.2.3.4", "5.6.7.8"],
        )

        items = []
        async for key, value in source.fetch_items():
            items.append((key, value))

        assert len(items) == 2
        assert items[0][0] == "geo:1.2.3.4"
        assert items[1][0] == "geo:5.6.7.8"

    def test_strategy_metadata(self):
        """Test strategy metadata."""

        async def mock_fetcher(ips):
            return {}

        source = GeolocationCachePrewarmSource(
            fetcher=mock_fetcher,
            ips=[],
        )

        strategy = source.strategy

        assert strategy.name == "geolocation-cache"
        assert strategy.priority == 5


class TestStaticDataPrewarmSource:
    """Tests for StaticDataPrewarmSource."""

    @pytest.mark.asyncio
    async def test_fetch_static_data(self):
        """Test fetching static data."""
        data = {
            "config1": {"key": "value1"},
            "config2": {"key": "value2"},
        }

        source = StaticDataPrewarmSource(
            data=data,
            prefix="config",
        )

        items = []
        async for key, value in source.fetch_items():
            items.append((key, value))

        assert len(items) == 2
        keys = [item[0] for item in items]
        assert "config:config1" in keys
        assert "config:config2" in keys

    def test_strategy_metadata(self):
        """Test strategy metadata."""
        source = StaticDataPrewarmSource(data={})

        strategy = source.strategy

        assert strategy.name == "static-data"
        assert strategy.priority == 20  # Highest


class TestCachePrewarmer:
    """Tests for CachePrewarmer."""

    @pytest.mark.asyncio
    async def test_preheat_single_source(self):
        """Test prewarming with single source."""
        cache = {}

        async def cache_set(key, value):
            cache[key] = value

        prewarmer = CachePrewarmer(cache_set=cache_set)

        # Add source
        data = {"key1": "value1", "key2": "value2"}
        source = StaticDataPrewarmSource(data=data, prefix="test")
        prewarmer.add_source(source)

        # Preheat
        progress = await prewarmer.preheat()

        assert progress.total_items == 2
        assert progress.loaded_items == 2
        assert progress.failed_items == 0
        assert progress.success_rate == 100.0
        assert cache["test:key1"] == "value1"
        assert cache["test:key2"] == "value2"

    @pytest.mark.asyncio
    async def test_preheat_multiple_sources(self):
        """Test prewarming with multiple sources."""
        cache = {}

        async def cache_set(key, value):
            cache[key] = value

        prewarmer = CachePrewarmer(cache_set=cache_set)

        # Add multiple sources
        static_data = {"config": "data"}
        static_source = StaticDataPrewarmSource(data=static_data, prefix="static")
        prewarmer.add_source(static_source)

        async def proxy_fetcher():
            return [{"ip": "1.2.3.4"}]

        proxy_source = ProxyListPrewarmSource(fetcher=proxy_fetcher, category="http")
        prewarmer.add_source(proxy_source)

        # Preheat
        progress = await prewarmer.preheat()

        assert progress.total_items == 2
        assert progress.loaded_items == 2
        assert "static:config" in cache
        assert "proxy:http:0" in cache

    @pytest.mark.asyncio
    async def test_preheat_with_progress_callback(self):
        """Test prewarming with progress callback."""
        cache = {}

        async def cache_set(key, value):
            cache[key] = value

        prewarmer = CachePrewarmer(cache_set=cache_set)

        data = {"k1": "v1", "k2": "v2"}
        source = StaticDataPrewarmSource(data=data)
        prewarmer.add_source(source)

        progress_updates = []

        def on_progress(progress):
            progress_updates.append(progress.loaded_items)

        await prewarmer.preheat(on_progress=on_progress)

        assert len(progress_updates) >= 2
        assert progress_updates[-1] == 2

    @pytest.mark.asyncio
    async def test_preheat_error_handling(self):
        """Test error handling during prewarming."""

        async def failing_cache_set(key, value):
            if "fail" in key:
                raise RuntimeError("Set failed")

        prewarmer = CachePrewarmer(cache_set=failing_cache_set)

        data = {"fail": "value", "success": "value"}
        source = StaticDataPrewarmSource(data=data)
        prewarmer.add_source(source)

        progress = await prewarmer.preheat()

        assert progress.total_items == 2
        assert progress.loaded_items == 1
        assert progress.failed_items == 1
        assert progress.success_rate == 50.0

    @pytest.mark.asyncio
    async def test_preheat_background(self):
        """Test background prewarming."""
        cache = {}

        async def cache_set(key, value):
            await asyncio.sleep(0.01)  # Simulate async operation
            cache[key] = value

        prewarmer = CachePrewarmer(cache_set=cache_set)

        data = {"key": "value"}
        source = StaticDataPrewarmSource(data=data)
        prewarmer.add_source(source)

        # Start background task
        task = await prewarmer.preheat_background()

        # Task should be running
        assert isinstance(task, asyncio.Task)

        # Wait for completion
        progress = await task

        assert progress.loaded_items == 1

    @pytest.mark.asyncio
    async def test_get_progress(self):
        """Test getting progress."""
        cache = {}

        async def cache_set(key, value):
            cache[key] = value

        prewarmer = CachePrewarmer(cache_set=cache_set)

        # No progress before preheating
        assert prewarmer.get_progress() is None

        data = {"key": "value"}
        source = StaticDataPrewarmSource(data=data)
        prewarmer.add_source(source)

        await prewarmer.preheat()

        # Progress available after preheating
        progress = prewarmer.get_progress()
        assert progress is not None
        assert progress.loaded_items == 1

    def test_get_sources_summary(self):
        """Test getting sources summary."""
        prewarmer = CachePrewarmer(cache_set=lambda k, v: None)

        source1 = StaticDataPrewarmSource(data={})
        source2 = ProxyListPrewarmSource(
            fetcher=lambda: [],
            category="http",
        )

        prewarmer.add_source(source1)
        prewarmer.add_source(source2)

        summary = prewarmer.get_sources_summary()

        assert summary["count"] == 2
        assert len(summary["sources"]) == 2

    @pytest.mark.asyncio
    async def test_source_priority_ordering(self):
        """Test sources are ordered by priority."""
        call_order = []

        async def cache_set(key, value):
            pass

        prewarmer = CachePrewarmer(cache_set=cache_set)

        # Add sources in non-priority order
        low_priority = StaticDataPrewarmSource(data={"low": "value"})
        low_priority.strategy.priority = 1

        high_priority = ProxyListPrewarmSource(
            fetcher=lambda: [],
            category="http",
        )

        prewarmer.add_source(low_priority)
        prewarmer.add_source(high_priority)

        # Verify ordering
        sources = prewarmer.sources
        assert sources[0].strategy.priority >= sources[1].strategy.priority

    @pytest.mark.asyncio
    async def test_concurrent_cache_operations(self):
        """Test concurrent cache set operations."""
        operations = []

        async def cache_set(key, value):
            operations.append(key)
            await asyncio.sleep(0.01)

        prewarmer = CachePrewarmer(
            cache_set=cache_set,
            max_concurrent=3,
        )

        data = {f"key{i}": f"value{i}" for i in range(10)}
        source = StaticDataPrewarmSource(data=data)
        prewarmer.add_source(source)

        progress = await prewarmer.preheat()

        assert progress.loaded_items == 10
        assert len(operations) == 10
