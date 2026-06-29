"""Integration tests for storage dict hydration."""

from proxywhirl.models import HealthStatus, Proxy, ProxySource
from proxywhirl.storage import dict_to_proxy
from proxywhirl.utils import proxy_to_dict


def test_dict_to_proxy_round_trip() -> None:
    """dict_to_proxy should reconstruct proxies produced by proxy_to_dict."""
    original = Proxy(
        url="http://hydration-proxy.example.com:8080",
        health_status=HealthStatus.HEALTHY,
        source=ProxySource.USER,
        tags={"test", "hydration"},
    )
    original.total_requests = 12
    original.total_successes = 10

    serialized = proxy_to_dict(original, include_stats=True)
    row = {
        "url": serialized["url"],
        "protocol": serialized["protocol"],
        "health_status": serialized["health_status"],
        "source": serialized["source"],
        "total_successes": serialized["stats"]["total_successes"],
        "total_checks": serialized["stats"]["total_requests"],
    }

    restored = dict_to_proxy(row)
    round_trip = proxy_to_dict(restored, include_stats=True)

    assert str(restored.url) == serialized["url"]
    assert restored.health_status == original.health_status
    assert restored.source == original.source
    assert restored.total_successes == original.total_successes
    assert round_trip["url"] == serialized["url"]
    assert round_trip["health_status"] == serialized["health_status"]
