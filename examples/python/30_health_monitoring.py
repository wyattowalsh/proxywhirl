"""
Health monitoring demo for ProxyWhirl.

The built-in `HealthMonitor` ships with lifecycle management; this example
provides a tiny concrete health-check loop so you can see eviction behavior
without any external dependencies.

Run with:
    uv run python examples/python/30_health_monitoring.py
"""

from __future__ import annotations

import asyncio
from typing import Iterable

from proxywhirl.models import HealthMonitor, Proxy, ProxyPool


class DemoHealthMonitor(HealthMonitor):
    """
    Concrete health monitor used only for examples.

    Each proxy gets a deterministic outcome:
    - "always_ok": always healthy
    - "flaky": first failure, then recovery
    - "dead": keeps failing until evicted
    """

    async def _run_health_checks(self) -> None:  # type: ignore[override]
        for proxy in list(self.pool.proxies):
            label = proxy.metadata.get("profile", "always_ok")
            checks = proxy.metadata.get("checks", 0)
            proxy.metadata["checks"] = checks + 1

            if label == "dead":
                self._record_failure(proxy)
            elif label == "flaky" and checks == 0:
                self._record_failure(proxy)
            else:
                self._record_success(proxy)


def _pretty_pool(pool: ProxyPool) -> None:
    print("Current pool:")
    for proxy in pool.proxies:
        status = proxy.health_status.value
        print(f"  • {proxy.url} [{status}]")
    if not pool.proxies:
        print("  (empty)")


async def run_demo() -> None:
    pool = ProxyPool(
        name="monitored",
        proxies=[
            Proxy(url="http://always-ok.local:8080", metadata={"profile": "always_ok"}),
            Proxy(url="http://flaky.local:8080", metadata={"profile": "flaky"}),
            Proxy(url="http://dead.local:8080", metadata={"profile": "dead"}),
        ],
    )

    monitor = DemoHealthMonitor(pool=pool, check_interval=0.2, failure_threshold=2)

    print("\nStarting health monitor (0.2s interval, evict after 2 failures)")
    _pretty_pool(pool)

    await monitor.start()
    await asyncio.sleep(0.9)  # Allow a few check cycles to run
    await monitor.stop()

    status = monitor.get_status()
    print("\nMonitor status:", {k: v for k, v in status.items() if k != "failure_counts"})
    print("Failure counts:", status["failure_counts"])
    _pretty_pool(pool)

    print("\nResult:")
    print("  - always_ok stayed in the pool")
    print("  - flaky recovered after the first failure")
    print("  - dead was evicted after two failed checks")


def main() -> None:
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
