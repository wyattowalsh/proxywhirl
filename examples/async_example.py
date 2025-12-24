"""
Example demonstrating AsyncProxyRotator usage.

This example shows how to use the async API client for proxywhirl.
"""

import asyncio

from proxywhirl import AsyncProxyRotator


async def main():
    """Demonstrate basic async proxy rotation."""
    print("=== AsyncProxyRotator Example ===\n")

    # Create async rotator with round-robin strategy
    async with AsyncProxyRotator(strategy="round-robin") as rotator:
        # Add some example proxies (replace with real proxies for actual use)
        await rotator.add_proxy("http://proxy1.example.com:8080")
        await rotator.add_proxy("http://proxy2.example.com:8080")
        await rotator.add_proxy("http://proxy3.example.com:8080")

        print(f"Added {rotator.pool.size} proxies to the pool\n")

        # Get pool statistics
        stats = rotator.get_pool_stats()
        print("Pool Statistics:")
        print(f"  Total proxies: {stats['total_proxies']}")
        print(f"  Healthy proxies: {stats['healthy_proxies']}")
        print("  Strategy: round-robin\n")

        # Get next proxy from pool
        proxy = await rotator.get_proxy()
        print(f"Selected proxy: {proxy.url}\n")

        # Make async HTTP requests (commented out as example proxies won't work)
        # try:
        #     response = await rotator.get("https://httpbin.org/ip")
        #     print(f"Response status: {response.status_code}")
        #     print(f"Response data: {response.json()}")
        # except Exception as e:
        #     print(f"Request failed: {e}")

        # Hot-swap strategy
        print("Hot-swapping to random strategy...")
        rotator.set_strategy("random")
        print("Strategy changed successfully!\n")

        # Clear unhealthy proxies
        removed = await rotator.clear_unhealthy_proxies()
        print(f"Removed {removed} unhealthy proxies")

        print("\n=== Example completed ===")


if __name__ == "__main__":
    asyncio.run(main())
