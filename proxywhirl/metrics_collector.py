"""Prometheus metrics collector for ProxyWhirl.

This module provides centralized Prometheus metrics collection for monitoring
proxy pool health, request performance, and circuit breaker states.

Metrics exposed:
- proxywhirl_requests_total: Counter for total requests
- proxywhirl_request_duration_seconds: Histogram for request latency
- proxywhirl_proxy_health_status: Gauge for proxy health (1=healthy, 0=unhealthy)
- proxywhirl_active_proxies: Gauge for number of active proxies
- proxywhirl_circuit_breaker_state: Gauge for circuit breaker states

Usage:
    from proxywhirl.metrics_collector import MetricsCollector

    collector = MetricsCollector()
    collector.record_request("success", duration=1.5, proxy_id="proxy-1")
    collector.update_proxy_health("proxy-1", is_healthy=True)
"""

from __future__ import annotations

from typing import Literal

from prometheus_client import REGISTRY, CollectorRegistry, Counter, Gauge, Histogram


class MetricsCollector:
    """Centralized Prometheus metrics collector for ProxyWhirl.

    This class provides a clean API for recording metrics throughout the application.
    All metrics follow Prometheus naming conventions and best practices.
    """

    def __init__(self, registry: CollectorRegistry | None = None) -> None:
        """Initialize Prometheus metrics collectors.

        Args:
            registry: Optional custom registry. If None, uses the default REGISTRY.
                     This allows for isolated testing without metric collisions.
        """
        self._registry = registry or REGISTRY

        # Counter: Total requests made through proxies
        self.requests_total = Counter(
            "proxywhirl_requests_total",
            "Total number of requests made through proxies",
            ["status", "proxy_id"],
            registry=self._registry,
        )

        # Histogram: Request latency distribution
        self.request_duration_seconds = Histogram(
            "proxywhirl_request_duration_seconds",
            "Request duration in seconds",
            ["proxy_id"],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0),
            registry=self._registry,
        )

        # Gauge: Proxy health status (1=healthy, 0=unhealthy)
        self.proxy_health_status = Gauge(
            "proxywhirl_proxy_health_status",
            "Current proxy health status (1=healthy, 0=unhealthy)",
            ["proxy_id"],
            registry=self._registry,
        )

        # Gauge: Number of active proxies in the pool
        self.active_proxies = Gauge(
            "proxywhirl_active_proxies",
            "Number of active proxies in the pool",
            registry=self._registry,
        )

        # Gauge: Circuit breaker state (0=closed, 1=open, 2=half-open)
        self.circuit_breaker_state = Gauge(
            "proxywhirl_circuit_breaker_state",
            "Circuit breaker state (0=closed, 1=open, 2=half-open)",
            ["proxy_id"],
            registry=self._registry,
        )

    def record_request(
        self,
        status: Literal["success", "error", "timeout"],
        duration: float,
        proxy_id: str,
    ) -> None:
        """Record a request made through a proxy.

        Args:
            status: Request status (success, error, timeout)
            duration: Request duration in seconds
            proxy_id: Identifier of the proxy used
        """
        # Increment request counter
        self.requests_total.labels(status=status, proxy_id=proxy_id).inc()

        # Record request duration
        self.request_duration_seconds.labels(proxy_id=proxy_id).observe(duration)

    def update_proxy_health(self, proxy_id: str, is_healthy: bool) -> None:
        """Update health status for a specific proxy.

        Args:
            proxy_id: Identifier of the proxy
            is_healthy: True if proxy is healthy, False otherwise
        """
        self.proxy_health_status.labels(proxy_id=proxy_id).set(1 if is_healthy else 0)

    def update_active_proxies(self, count: int) -> None:
        """Update the count of active proxies in the pool.

        Args:
            count: Number of active proxies
        """
        self.active_proxies.set(count)

    def update_circuit_breaker_state(
        self,
        proxy_id: str,
        state: Literal["closed", "open", "half-open"],
    ) -> None:
        """Update circuit breaker state for a specific proxy.

        Args:
            proxy_id: Identifier of the proxy
            state: Circuit breaker state (closed=0, open=1, half-open=2)
        """
        state_value = {"closed": 0, "open": 1, "half-open": 2}[state]
        self.circuit_breaker_state.labels(proxy_id=proxy_id).set(state_value)

    def clear_proxy_metrics(self, proxy_id: str) -> None:
        """Clear all metrics for a specific proxy.

        This should be called when a proxy is removed from the pool to prevent
        stale metrics from persisting.

        Args:
            proxy_id: Identifier of the proxy to clear
        """
        # Note: Prometheus client doesn't support removing specific label combinations
        # Set health to 0 and circuit breaker to closed as a workaround
        self.proxy_health_status.labels(proxy_id=proxy_id).set(0)
        self.circuit_breaker_state.labels(proxy_id=proxy_id).set(0)


# Global singleton instance for convenient access
_collector: MetricsCollector | None = None
_singleton_registry: CollectorRegistry | None = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global MetricsCollector singleton.

    Returns:
        MetricsCollector: The global metrics collector instance
    """
    global _collector, _singleton_registry
    if _collector is None:
        # Use a dedicated registry for the singleton to avoid
        # conflicts with the default REGISTRY during testing
        if _singleton_registry is None:
            _singleton_registry = CollectorRegistry()
        _collector = MetricsCollector(registry=_singleton_registry)
    return _collector


def reset_metrics_collector() -> None:
    """Reset the global MetricsCollector singleton.

    This is primarily used for testing to ensure test isolation.
    Calling this function clears the global collector reference,
    allowing a new instance to be created on next access.
    """
    global _collector, _singleton_registry
    _collector = None
    _singleton_registry = None


# Convenience functions for direct metric access
def record_request(
    status: Literal["success", "error", "timeout"],
    duration: float,
    proxy_id: str,
) -> None:
    """Record a request made through a proxy.

    Convenience function that uses the global collector.

    Args:
        status: Request status (success, error, timeout)
        duration: Request duration in seconds
        proxy_id: Identifier of the proxy used
    """
    get_metrics_collector().record_request(status, duration, proxy_id)


def update_proxy_health(proxy_id: str, is_healthy: bool) -> None:
    """Update health status for a specific proxy.

    Convenience function that uses the global collector.

    Args:
        proxy_id: Identifier of the proxy
        is_healthy: True if proxy is healthy, False otherwise
    """
    get_metrics_collector().update_proxy_health(proxy_id, is_healthy)


def update_active_proxies(count: int) -> None:
    """Update the count of active proxies in the pool.

    Convenience function that uses the global collector.

    Args:
        count: Number of active proxies
    """
    get_metrics_collector().update_active_proxies(count)


def update_circuit_breaker_state(
    proxy_id: str,
    state: Literal["closed", "open", "half-open"],
) -> None:
    """Update circuit breaker state for a specific proxy.

    Convenience function that uses the global collector.

    Args:
        proxy_id: Identifier of the proxy
        state: Circuit breaker state (closed=0, open=1, half-open=2)
    """
    get_metrics_collector().update_circuit_breaker_state(proxy_id, state)


def clear_proxy_metrics(proxy_id: str) -> None:
    """Clear all metrics for a specific proxy.

    Convenience function that uses the global collector.

    Args:
        proxy_id: Identifier of the proxy to clear
    """
    get_metrics_collector().clear_proxy_metrics(proxy_id)
