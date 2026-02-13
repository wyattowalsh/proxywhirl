"""
Example: Health Monitoring for Proxy Pools

This example demonstrates how to use ProxyWhirl's HealthMonitor
to continuously monitor proxy health and automatically remove
failing proxies from the pool.

Usage:
    python examples/health_monitoring_example.py
"""

import asyncio

from proxywhirl.models import HealthMonitor, Proxy, ProxyPool


async def example_basic_health_monitoring():
    """Basic health monitoring example."""
    print("\n=== Example 1: Basic Health Monitoring ===")

    # Create a proxy pool
    pool = ProxyPool(name="monitored_pool")
    pool.add_proxy(Proxy(url="http://proxy1.example.com:8080"))
    pool.add_proxy(Proxy(url="http://proxy2.example.com:8080"))
    pool.add_proxy(Proxy(url="http://proxy3.example.com:8080"))

    print(f"Initial pool size: {pool.size}")

    # Create health monitor with default settings
    monitor = HealthMonitor(
        pool=pool,
        check_interval=60,  # Check every 60 seconds
        failure_threshold=3,  # Evict after 3 consecutive failures
    )

    # Start monitoring (runs in background)
    await monitor.start()
    status = monitor.get_status()
    print(f"Monitoring started (uptime: {status.get('uptime_seconds', 0):.1f}s)")
    print(f"Check interval: {monitor.check_interval} seconds")
    print(f"Failure threshold: {monitor.failure_threshold} failures")

    # Simulate some activity
    await asyncio.sleep(2)

    # Stop monitoring
    await monitor.stop()
    print("Monitoring stopped")


async def example_custom_thresholds():
    """Health monitoring with custom thresholds."""
    print("\n=== Example 2: Custom Thresholds ===")

    pool = ProxyPool(name="strict_pool")
    pool.add_proxy(Proxy(url="http://proxy1.example.com:8080"))
    pool.add_proxy(Proxy(url="http://proxy2.example.com:8080"))

    # Stricter monitoring settings
    monitor = HealthMonitor(
        pool=pool,
        check_interval=30,  # Check more frequently (every 30 seconds)
        failure_threshold=2,  # Lower tolerance (evict after 2 failures)
    )

    print(f"Pool size: {pool.size}")
    print(f"Stricter settings: check every {monitor.check_interval}s")
    print(f"Evict after {monitor.failure_threshold} consecutive failures")

    await monitor.start()
    print("Monitoring started with strict settings")

    # Simulate some activity
    await asyncio.sleep(1)

    await monitor.stop()
    print("Monitoring stopped")


async def example_long_running_monitoring():
    """Long-running health monitoring simulation."""
    print("\n=== Example 3: Long-Running Monitoring ===")

    pool = ProxyPool(name="production_pool")

    # Add multiple proxies
    for i in range(1, 6):
        proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
        pool.add_proxy(proxy)

    print(f"Starting with {pool.size} proxies")

    # Production-like settings
    monitor = HealthMonitor(
        pool=pool,
        check_interval=60,  # Check every minute
        failure_threshold=3,  # Evict after 3 consecutive failures
    )

    await monitor.start()
    print("Monitoring started for production pool")

    # Simulate long-running application
    print("Running for 10 seconds...")
    for i in range(10):
        await asyncio.sleep(1)
        print(f"  {i + 1}s elapsed, pool size: {pool.size}")

    await monitor.stop()
    print(f"Monitoring stopped, final pool size: {pool.size}")


async def example_multiple_monitors():
    """Multiple health monitors for different pools."""
    print("\n=== Example 4: Multiple Monitors ===")

    # Create multiple pools
    pool1 = ProxyPool(name="us_proxies")
    pool2 = ProxyPool(name="eu_proxies")

    # Populate pools
    pool1.add_proxy(Proxy(url="http://us1.example.com:8080"))
    pool1.add_proxy(Proxy(url="http://us2.example.com:8080"))
    pool2.add_proxy(Proxy(url="http://eu1.example.com:8080"))
    pool2.add_proxy(Proxy(url="http://eu2.example.com:8080"))

    # Create separate monitors with different settings
    monitor1 = HealthMonitor(pool=pool1, check_interval=30, failure_threshold=2)
    monitor2 = HealthMonitor(pool=pool2, check_interval=60, failure_threshold=3)

    # Start both monitors
    await monitor1.start()
    await monitor2.start()

    print(f"US pool: {pool1.size} proxies, check every {monitor1.check_interval}s")
    print(f"EU pool: {pool2.size} proxies, check every {monitor2.check_interval}s")

    # Run both monitors concurrently
    await asyncio.sleep(2)

    # Stop both monitors
    await monitor1.stop()
    await monitor2.stop()

    print("Both monitors stopped")


async def example_error_handling():
    """Error handling in health monitoring."""
    print("\n=== Example 5: Error Handling ===")

    pool = ProxyPool(name="test_pool")
    pool.add_proxy(Proxy(url="http://proxy.example.com:8080"))

    # Test invalid configuration
    try:
        monitor = HealthMonitor(
            pool=pool,
            check_interval=0,  # Invalid: must be positive
            failure_threshold=3,
        )
    except ValueError as e:
        print(f"Caught expected error: {e}")

    try:
        monitor = HealthMonitor(
            pool=pool,
            check_interval=60,
            failure_threshold=-1,  # Invalid: must be positive
        )
    except ValueError as e:
        print(f"Caught expected error: {e}")

    # Create valid monitor
    monitor = HealthMonitor(pool=pool, check_interval=60, failure_threshold=3)
    print("Valid monitor created successfully")

    # Test idempotent start/stop
    await monitor.start()
    print("Monitor started")

    await monitor.start()  # Safe to call multiple times
    print("Monitor start called again (no-op)")

    await monitor.stop()
    print("Monitor stopped")

    await monitor.stop()  # Safe to call when not running
    print("Monitor stop called again (no-op)")


async def example_monitoring_with_rotator():
    """Health monitoring integrated with ProxyRotator."""
    print("\n=== Example 6: Monitoring with ProxyRotator ===")

    # Import here to avoid circular dependency issues in examples
    from proxywhirl.rotator import ProxyRotator
    from proxywhirl.strategies import RandomStrategy

    # Create rotator (which creates its own internal pool)
    rotator = ProxyRotator(
        proxies=[
            Proxy(url="http://proxy1.example.com:8080"),
            Proxy(url="http://proxy2.example.com:8080"),
            Proxy(url="http://proxy3.example.com:8080"),
        ],
        strategy=RandomStrategy(),
    )

    # Start health monitoring on the rotator's pool
    monitor = HealthMonitor(pool=rotator.pool, check_interval=60, failure_threshold=3)
    await monitor.start()

    print(f"Rotator pool size: {rotator.pool.size}")
    print("Health monitoring active")

    # Use rotator while monitoring runs in background
    for i in range(5):
        proxy = rotator.strategy.select(rotator.pool)
        print(f"  Request {i + 1}: using {proxy.url}")

    # Stop monitoring
    await monitor.stop()
    print("Monitoring stopped")


async def main():
    """Run all examples."""
    print("ProxyWhirl Health Monitoring Examples")
    print("=" * 50)

    await example_basic_health_monitoring()
    await example_custom_thresholds()
    await example_long_running_monitoring()
    await example_multiple_monitors()
    await example_error_handling()
    await example_monitoring_with_rotator()

    print("\n" + "=" * 50)
    print("Examples complete!")
    print("\nNote: These examples use placeholder proxies.")
    print("In production, HealthMonitor will perform actual health checks")
    print("and automatically evict failing proxies.")


if __name__ == "__main__":
    asyncio.run(main())
