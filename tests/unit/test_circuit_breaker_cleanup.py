"""Unit tests for circuit breaker memory leak fix.

Tests verify that circuit breakers are properly cleaned up when proxies are removed,
preventing unbounded memory growth.
"""

from unittest.mock import MagicMock, patch

from proxywhirl.models import HealthStatus, Proxy
from proxywhirl.rotator import AsyncProxyWhirl, ProxyWhirl


class TestCircuitBreakerCleanup:
    """Test circuit breaker cleanup to prevent memory leaks."""

    async def test_async_remove_proxy_cleans_circuit_breaker(self) -> None:
        """Test that removing a proxy also removes its circuit breaker."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyWhirl(proxies=[proxy])

        # Verify circuit breaker exists
        assert str(proxy.id) in rotator.circuit_breakers
        initial_cb_count = len(rotator.circuit_breakers)

        # Remove proxy
        await rotator.remove_proxy(str(proxy.id))

        # Verify circuit breaker was removed
        assert str(proxy.id) not in rotator.circuit_breakers
        assert len(rotator.circuit_breakers) == initial_cb_count - 1

    async def test_async_clear_unhealthy_cleans_circuit_breakers(self) -> None:
        """Test that clearing unhealthy proxies removes their circuit breakers."""
        proxies = [
            Proxy(
                url="http://192.168.1.1:8080", health_status=HealthStatus.HEALTHY, allow_local=True
            ),
            Proxy(
                url="http://192.168.1.2:8080",
                health_status=HealthStatus.UNHEALTHY,
                allow_local=True,
            ),
            Proxy(url="http://192.168.1.3:8080", health_status=HealthStatus.DEAD, allow_local=True),
        ]
        rotator = AsyncProxyWhirl(proxies=proxies)

        # Verify all circuit breakers exist
        assert len(rotator.circuit_breakers) == 3

        # Capture IDs of unhealthy proxies
        unhealthy_ids = [
            str(p.id)
            for p in proxies
            if p.health_status in (HealthStatus.DEAD, HealthStatus.UNHEALTHY)
        ]

        # Clear unhealthy proxies
        removed_count = await rotator.clear_unhealthy_proxies()

        # Verify circuit breakers for unhealthy proxies were removed
        assert removed_count == 2
        assert len(rotator.circuit_breakers) == 1

        for unhealthy_id in unhealthy_ids:
            assert unhealthy_id not in rotator.circuit_breakers

    def test_sync_remove_proxy_cleans_circuit_breaker(self) -> None:
        """Test that removing a proxy also removes its circuit breaker (sync)."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = ProxyWhirl(proxies=[proxy])

        # Verify circuit breaker exists
        assert str(proxy.id) in rotator.circuit_breakers
        initial_cb_count = len(rotator.circuit_breakers)

        # Remove proxy
        rotator.remove_proxy(str(proxy.id))

        # Verify circuit breaker was removed
        assert str(proxy.id) not in rotator.circuit_breakers
        assert len(rotator.circuit_breakers) == initial_cb_count - 1

    def test_sync_clear_unhealthy_cleans_circuit_breakers(self) -> None:
        """Test that clearing unhealthy proxies removes their circuit breakers (sync)."""
        proxies = [
            Proxy(
                url="http://192.168.1.1:8080", health_status=HealthStatus.HEALTHY, allow_local=True
            ),
            Proxy(
                url="http://192.168.1.2:8080",
                health_status=HealthStatus.UNHEALTHY,
                allow_local=True,
            ),
            Proxy(url="http://192.168.1.3:8080", health_status=HealthStatus.DEAD, allow_local=True),
        ]
        rotator = ProxyWhirl(proxies=proxies)

        # Verify all circuit breakers exist
        assert len(rotator.circuit_breakers) == 3

        # Capture IDs of unhealthy proxies
        unhealthy_ids = [
            str(p.id)
            for p in proxies
            if p.health_status in (HealthStatus.DEAD, HealthStatus.UNHEALTHY)
        ]

        # Clear unhealthy proxies
        removed_count = rotator.clear_unhealthy_proxies()

        # Verify circuit breakers for unhealthy proxies were removed
        assert removed_count == 2
        assert len(rotator.circuit_breakers) == 1

        for unhealthy_id in unhealthy_ids:
            assert unhealthy_id not in rotator.circuit_breakers

    @patch("httpx.Client")
    def test_sync_clear_unhealthy_closes_pooled_clients(self, mock_client_class: MagicMock) -> None:
        """Sync clear_unhealthy_proxies should close LRU client pool entries (P-R-03)."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        dead = Proxy(
            url="http://192.168.1.9:8080",
            health_status=HealthStatus.DEAD,
            allow_local=True,
        )
        rotator = ProxyWhirl(proxies=[dead])
        rotator._get_or_create_client(dead, rotator._get_proxy_dict(dead))
        proxy_id = str(dead.id)
        assert proxy_id in rotator._client_pool

        removed = rotator.clear_unhealthy_proxies()

        assert removed == 1
        assert proxy_id not in rotator._client_pool
        mock_client.close.assert_called()

    async def test_async_multiple_removes_prevent_memory_leak(self) -> None:
        """Test that multiple proxy removals don't cause unbounded memory growth."""
        # Add 100 proxies
        proxies = [Proxy(url=f"http://192.168.1.{i}:8080", allow_local=True) for i in range(1, 101)]
        rotator = AsyncProxyWhirl(proxies=proxies)

        # Verify 100 circuit breakers exist
        assert len(rotator.circuit_breakers) == 100

        # Remove all proxies one by one
        for proxy in proxies[:50]:
            await rotator.remove_proxy(str(proxy.id))

        # Verify circuit breakers were cleaned up
        assert len(rotator.circuit_breakers) == 50

        # Remove remaining proxies
        for proxy in proxies[50:]:
            await rotator.remove_proxy(str(proxy.id))

        # Verify all circuit breakers were cleaned up
        assert len(rotator.circuit_breakers) == 0

    def test_sync_multiple_removes_prevent_memory_leak(self) -> None:
        """Test that multiple proxy removals don't cause unbounded memory growth (sync)."""
        # Add 100 proxies
        proxies = [Proxy(url=f"http://192.168.1.{i}:8080", allow_local=True) for i in range(1, 101)]
        rotator = ProxyWhirl(proxies=proxies)

        # Verify 100 circuit breakers exist
        assert len(rotator.circuit_breakers) == 100

        # Remove all proxies one by one
        for proxy in proxies[:50]:
            rotator.remove_proxy(str(proxy.id))

        # Verify circuit breakers were cleaned up
        assert len(rotator.circuit_breakers) == 50

        # Remove remaining proxies
        for proxy in proxies[50:]:
            rotator.remove_proxy(str(proxy.id))

        # Verify all circuit breakers were cleaned up
        assert len(rotator.circuit_breakers) == 0
