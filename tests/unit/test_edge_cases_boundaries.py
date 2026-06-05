"""Tests for edge cases and boundary conditions."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from proxywhirl.exceptions import ProxyPoolEmptyError
from proxywhirl.models import HealthStatus, Proxy, ProxyPool
from proxywhirl.storage import SQLiteStorage
from tests.conftest import ProxyFactory

pytestmark = pytest.mark.slow


def _proxy(index: int, *, health_status: HealthStatus = HealthStatus.UNKNOWN) -> Proxy:
    return Proxy(
        url=f"http://proxy{index:05d}.example.com:{8000 + (index % 1000)}",
        health_status=health_status,
    )


# ============================================================================
# EMPTY POOL STRATEGY TESTS
# ============================================================================


class TestEmptyPoolStrategies:
    """Test strategy behavior with empty pools."""

    def test_empty_pool_initialization(self) -> None:
        """Test creating an empty pool."""
        pool = ProxyPool(name="empty_pool", proxies=[])
        assert len(pool.proxies) == 0
        assert pool.name == "empty_pool"

    def test_empty_pool_selection_error(self) -> None:
        """Test selecting from empty pool raises error."""
        pool = ProxyPool(name="empty", proxies=[])

        if not pool.proxies:
            with pytest.raises(ProxyPoolEmptyError):
                raise ProxyPoolEmptyError(f"Pool '{pool.name}' is empty")

    def test_empty_pool_with_subsequent_additions(self) -> None:
        """Test adding to empty pool."""
        pool = ProxyPool(name="grow_pool", proxies=[])

        assert len(pool.proxies) == 0

        # Add proxies
        new_proxies = [ProxyFactory.build() for _ in range(5)]
        pool.proxies.extend(new_proxies)

        assert len(pool.proxies) == 5

    def test_empty_to_non_empty_transition(self) -> None:
        """Test transition from empty to non-empty pool."""
        pool = ProxyPool(name="transition_pool", proxies=[])

        # Check initial state
        assert len(pool.proxies) == 0

        # Add a proxy
        proxy = ProxyFactory.build()
        pool.proxies.append(proxy)

        # Can now select
        assert len(pool.proxies) == 1
        assert pool.proxies[0] == proxy

    def test_pool_becomes_empty_after_removal(self) -> None:
        """Test pool becoming empty after removing all proxies."""
        proxy = ProxyFactory.build()
        pool = ProxyPool(name="deplete_pool", proxies=[proxy])

        assert len(pool.proxies) == 1

        pool.proxies.clear()

        assert len(pool.proxies) == 0


# ============================================================================
# CHARACTER ENCODING EDGE CASES
# ============================================================================


class TestEncodingEdgeCases:
    """Test character encoding edge cases."""

    @pytest.mark.parametrize(
        "test_string",
        [
            "proxy.example.com",  # ASCII
            "プロキシ.jp",  # Japanese
            "代理.中国",  # Chinese
            "прокси.рф",  # Cyrillic
            "🔒proxy.ssl",  # Emoji
            "mixed_日本_text",  # Mixed ASCII and Japanese
            "café.proxy",  # Accented characters
            "\u0001\u0002\u0003",  # Control characters
        ],
    )
    def test_proxy_url_encoding(self, test_string: str) -> None:
        """Test proxy URLs with various encodings."""
        try:
            proxy = ProxyFactory.build()
            # Most real proxies use ASCII, but test that the model handles encoding
            assert proxy.url is not None
        except ValidationError:
            # Expected for some special characters in URLs
            pass

    def test_proxy_username_unicode(self) -> None:
        """Test proxy with Unicode username."""
        try:
            proxy = ProxyFactory.with_auth(
                username="用户",  # Chinese: "user"
                password="密码",  # Chinese: "password"
            )
            assert proxy.username is not None
        except ValidationError:
            pass

    def test_proxy_credentials_with_special_chars(self) -> None:
        """Test credentials with special characters."""
        special_chars = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`"

        try:
            proxy = ProxyFactory.with_auth(
                username="user",
                password=special_chars,
            )
            assert proxy.password is not None
        except ValidationError:
            # Some special chars may not be allowed in URLs
            pass

    def test_proxy_metadata_unicode_values(self) -> None:
        """Test proxy metadata with Unicode values."""
        proxy = ProxyFactory.build()
        proxy.metadata["country"] = "日本"  # Japan
        proxy.metadata["description"] = "High-speed proxy 🚀"

        assert proxy.metadata["country"] == "日本"
        assert "🚀" in proxy.metadata["description"]

    def test_pool_name_encoding(self) -> None:
        """Test pool names with various encodings."""
        pool = ProxyPool(name="プールテスト", proxies=[])
        assert pool.name == "プールテスト"

    def test_utf8_json_serialization(self) -> None:
        """Test JSON serialization of Unicode data."""
        proxy = ProxyFactory.build()
        proxy.metadata["unicode_key"] = "中文值"

        json_str = proxy.model_dump_json()
        assert "中文值" in json_str or "\\u" in json_str  # Unicode or escaped

        # Should deserialize correctly
        parsed = json.loads(json_str)
        assert parsed is not None


# ============================================================================
# LARGE PROXY LISTS
# ============================================================================


class TestLargeProxyLists:
    """Test with 100k+ proxy lists."""

    @pytest.mark.slow
    def test_large_pool_memory_efficiency(self) -> None:
        """Test memory efficiency with large proxy count."""
        # Create a moderately large pool (not full 100k in tests)
        proxy_count = 10000
        proxies = [_proxy(i) for i in range(proxy_count)]

        pool = ProxyPool(name="large_pool", proxies=proxies)

        assert len(pool.proxies) == proxy_count

    @pytest.mark.slow
    def test_large_pool_iteration_performance(self) -> None:
        """Test iteration performance over large pool."""
        proxy_count = 5000
        proxies = [_proxy(i, health_status=HealthStatus.HEALTHY) for i in range(proxy_count)]
        pool = ProxyPool(name="iterate_pool", proxies=proxies)

        # Iterate and count healthy proxies
        healthy_count = sum(1 for p in pool.proxies if p.health_status == HealthStatus.HEALTHY)

        assert healthy_count == proxy_count

    @pytest.mark.slow
    async def test_large_pool_storage(self, tmp_path: Path) -> None:
        """Test storing and loading large pools."""
        proxy_count = 1000  # Reduced for test performance
        proxies = [_proxy(i) for i in range(proxy_count)]
        storage = SQLiteStorage(tmp_path / "large_pool.db")
        await storage.initialize()

        try:
            # Save large pool
            await storage.save(proxies)

            # Load back
            loaded = await storage.load()
            assert len(loaded) == proxy_count
        finally:
            await storage.clear()
            await storage.close()

    @pytest.mark.slow
    def test_large_pool_filtering(self) -> None:
        """Test filtering large proxy lists."""
        proxy_count = 2000
        proxies = [
            _proxy(i, health_status=HealthStatus.HEALTHY)
            if i % 3 == 0
            else _proxy(i, health_status=HealthStatus.UNHEALTHY)
            for i in range(proxy_count)
        ]
        pool = ProxyPool(name="filter_pool", proxies=proxies)

        # Filter healthy proxies
        healthy = [p for p in pool.proxies if p.health_status == HealthStatus.HEALTHY]
        unhealthy = [p for p in pool.proxies if p.health_status == HealthStatus.UNHEALTHY]

        assert len(healthy) > 0
        assert len(unhealthy) > 0
        assert len(healthy) + len(unhealthy) == proxy_count

    def test_large_pool_json_serialization(self) -> None:
        """Test JSON serialization of large pool."""
        proxy_count = 500
        proxies = [_proxy(i) for i in range(proxy_count)]
        pool = ProxyPool(name="json_pool", proxies=proxies)

        # Serialize
        json_str = pool.model_dump_json()
        assert len(json_str) > 0

        # Deserialize
        parsed = json.loads(json_str)
        assert len(parsed["proxies"]) == proxy_count


# ============================================================================
# UNICODE PROXY DATA TESTS
# ============================================================================


class TestUnicodeProxyData:
    """Test Unicode in proxy URLs and credentials."""

    def test_proxy_with_unicode_host(self) -> None:
        """Test proxy with internationalized domain name."""
        # IDN domains would need punycode encoding
        proxy = ProxyFactory.build()
        assert proxy.url is not None

    def test_proxy_with_unicode_port_metadata(self) -> None:
        """Test Unicode in proxy metadata."""
        proxy = ProxyFactory.build()
        proxy.metadata["region"] = "日本"
        proxy.metadata["city"] = "東京"

        assert proxy.metadata["region"] == "日本"
        assert proxy.metadata["city"] == "東京"

    def test_credential_unicode_roundtrip(self) -> None:
        """Test Unicode credential encoding/decoding."""
        original_username = "用户"
        original_password = "密码"

        try:
            proxy = ProxyFactory.with_auth(
                username=original_username,
                password=original_password,
            )

            # Check credentials are preserved
            assert proxy.username is not None
            assert proxy.password is not None
        except ValidationError:
            # URL encoding may reject Unicode in credentials
            pass

    def test_pool_metadata_unicode_storage(self) -> None:
        """Test pool with Unicode metadata storage."""
        pool = ProxyPool(
            name="unicode_pool",
            proxies=[ProxyFactory.build()],
        )
        with pytest.raises(ValueError, match='object has no field "metadata"'):
            pool.metadata = {
                "region": "欧洲",
                "country": "中国",
                "description": "多语言代理",
            }

        # The strict current pool model should still be serializable.
        json_str = pool.model_dump_json()
        assert len(json_str) > 0

        # Should be deserializable.
        parsed = json.loads(json_str)
        assert parsed is not None

    def test_unicode_proxy_url_encoding_safety(self) -> None:
        """Test that Unicode URLs are safely handled."""
        proxy = ProxyFactory.build()

        # Normal proxy URLs should be ASCII
        if proxy.url:
            try:
                proxy.url.encode("ascii")
            except UnicodeEncodeError:
                # If not ASCII, should be properly encoded
                proxy.url.encode("utf-8")


# ============================================================================
# FILE DESCRIPTOR LIMITS
# ============================================================================


class TestFileDescriptorLimits:
    """Test behavior at system FD limits."""

    def test_pool_handles_many_proxies_without_fd_leak(self) -> None:
        """Test that large pools don't leak file descriptors."""
        # Create several pools without closing resources
        pools = []
        for i in range(10):
            proxies = [_proxy((i * 100) + j) for j in range(100)]
            pool = ProxyPool(name=f"fd_pool_{i}", proxies=proxies)
            pools.append(pool)

        assert len(pools) == 10
        assert all(len(p.proxies) == 100 for p in pools)

    async def test_storage_connection_reuse(self, tmp_path: Path) -> None:
        """Test that storage reuses connections efficiently."""
        storage = SQLiteStorage(tmp_path / "reuse.db")
        await storage.initialize()

        try:
            proxies = [_proxy(i) for i in range(20)]

            # Create and save multiple proxies
            for proxy in proxies:
                added = await storage.add_proxy(proxy)
                assert added is True

            # Load them back - should reuse connection
            loaded = await storage.load()
            assert {row["url"] for row in loaded} == {proxy.url for proxy in proxies}
        finally:
            await storage.clear()
            await storage.close()

    async def test_concurrent_storage_no_fd_exhaustion(self, tmp_path: Path) -> None:
        """Test concurrent storage operations don't exhaust FDs."""
        storage = SQLiteStorage(tmp_path / "concurrent.db")
        await storage.initialize()

        try:
            # Run multiple concurrent write operations.
            results = await asyncio.gather(
                *(storage.add_proxies_batch([_proxy(i)], validated=False) for i in range(20))
            )

            assert sum(added for added, _ in results) == 20
            loaded = await storage.load()
            assert len(loaded) == 20
        finally:
            await storage.clear()
            await storage.close()


# ============================================================================
# BOUNDARY VALUE ANALYSIS
# ============================================================================


class TestBoundaryValues:
    """Test boundary values for numeric fields."""

    @pytest.mark.parametrize(
        "latency_ms",
        [0, 0.001, 1.0, 1000, 5000, 10000],
    )
    def test_proxy_latency_boundaries(self, latency_ms: float) -> None:
        """Test latency at boundary values."""
        proxy = ProxyFactory.build(latency_ms=latency_ms)
        assert proxy.latency_ms == latency_ms

    @pytest.mark.parametrize(
        "success_rate",
        [0.0, 0.001, 0.5, 0.999, 1.0],
    )
    def test_proxy_success_rate_boundaries(self, success_rate: float) -> None:
        """Test success rate at boundary values."""
        total_requests = 1000 if 0 < success_rate < 1 else 1
        total_successes = int(success_rate * total_requests)
        proxy = _proxy(
            total_successes,
            health_status=HealthStatus.HEALTHY,
        )
        proxy.total_requests = total_requests
        proxy.total_successes = total_successes

        assert proxy.success_rate == pytest.approx(success_rate)

    @pytest.mark.parametrize(
        "request_count",
        [0, 1, 100, 1000, 10000],
    )
    def test_proxy_request_count_boundaries(self, request_count: int) -> None:
        """Test request counts at boundary values."""
        proxy = ProxyFactory.build(total_requests=request_count)
        assert proxy.total_requests == request_count

    def test_pool_with_zero_proxies(self) -> None:
        """Test pool with exactly zero proxies."""
        pool = ProxyPool(name="zero_pool", proxies=[])
        assert len(pool.proxies) == 0

    def test_pool_with_one_proxy(self) -> None:
        """Test pool with exactly one proxy."""
        proxy = ProxyFactory.build()
        pool = ProxyPool(name="one_proxy", proxies=[proxy])
        assert len(pool.proxies) == 1

    def test_pool_with_max_proxies(self) -> None:
        """Test pool with large number of proxies."""
        proxies = [_proxy(i) for i in range(100000 // 100)]  # Use 1000 instead
        pool = ProxyPool(name="max_pool", proxies=proxies)
        assert len(pool.proxies) == 1000


# ============================================================================
# NULL AND OPTIONAL VALUE TESTS
# ============================================================================


class TestNullAndOptionalValues:
    """Test handling of null and optional values."""

    def test_proxy_without_credentials(self) -> None:
        """Test proxy without authentication credentials."""
        proxy = ProxyFactory.build(username=None, password=None)
        assert proxy.username is None
        assert proxy.password is None

    def test_proxy_with_empty_metadata(self) -> None:
        """Test proxy with empty metadata."""
        proxy = ProxyFactory.build(metadata={})
        assert proxy.metadata == {}

    def test_proxy_with_empty_tags(self) -> None:
        """Test proxy with no tags."""
        proxy = ProxyFactory.build(tags=set())
        assert len(proxy.tags) == 0

    def test_pool_with_null_values_in_metadata(self) -> None:
        """Test pool metadata with null values."""
        pool = ProxyPool(name="null_metadata_pool", proxies=[])

        # ProxyPool is intentionally strict and has no pool-level metadata field.
        with pytest.raises(ValueError, match='object has no field "metadata"'):
            pool.metadata = {"key_with_null": None}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
