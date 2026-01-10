"""Unit tests for circuit breaker memory leak fix.

Tests verify that circuit breakers are properly cleaned up when proxies are removed,
preventing unbounded memory growth.
"""

from proxywhirl.async_client import AsyncProxyRotator
from proxywhirl.models import HealthStatus, Proxy
from proxywhirl.rotator import ProxyRotator


class TestCircuitBreakerCleanup:
    """Test circuit breaker cleanup to prevent memory leaks."""

    async def test_async_remove_proxy_cleans_circuit_breaker(self) -> None:
        """Test that removing a proxy also removes its circuit breaker."""
        proxy = Proxy(url="http://192.168.1.1:8080", allow_local=True)
        rotator = AsyncProxyRotator(proxies=[proxy])

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
        rotator = AsyncProxyRotator(proxies=proxies)

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
        rotator = ProxyRotator(proxies=[proxy])

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
        rotator = ProxyRotator(proxies=proxies)

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

    async def test_async_multiple_removes_prevent_memory_leak(self) -> None:
        """Test that multiple proxy removals don't cause unbounded memory growth."""
        # Add 100 proxies
        proxies = [Proxy(url=f"http://192.168.1.{i}:8080", allow_local=True) for i in range(1, 101)]
        rotator = AsyncProxyRotator(proxies=proxies)

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
        rotator = ProxyRotator(proxies=proxies)

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
