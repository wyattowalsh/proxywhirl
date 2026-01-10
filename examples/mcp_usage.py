"""
Example: Using ProxyWhirl MCP Server programmatically.

This example demonstrates how to use the MCP server's unified `proxywhirl` tool
directly in Python code, outside of the MCP protocol context.

Requirements:
    - Python 3.10+ (MCP server requirement)
    - pip install "proxywhirl[mcp]"

Usage:
    python examples/mcp_usage.py
"""

import asyncio

from proxywhirl.mcp.server import (
    cleanup_rotator,
    proxywhirl,
    set_rotator,
)


async def basic_usage():
    """Demonstrate basic MCP tool usage."""
    print("=== Basic MCP Usage ===\n")

    # List all proxies in the pool
    print("1. Listing proxies...")
    result = await proxywhirl(action="list")
    total = result.get("total", 0)
    print(f"   Total proxies: {total}")
    print(f"   Healthy: {result.get('healthy', 0)}")
    print(f"   Degraded: {result.get('degraded', 0)}")
    print(f"   Unhealthy: {result.get('unhealthy', 0)}")

    # Check pool health
    print("\n2. Checking pool health...")
    result = await proxywhirl(action="health")
    print(f"   Pool status: {result.get('pool_status', 'unknown')}")
    print(f"   Average success rate: {result.get('average_success_rate', 0):.2%}")
    print(f"   Average latency: {result.get('average_latency_ms', 0):.2f}ms")

    # Rotate to next proxy (if any exist)
    if total > 0:
        print("\n3. Rotating to next proxy...")
        result = await proxywhirl(action="rotate")
        if "proxy" in result:
            proxy = result["proxy"]
            print(f"   Selected: {proxy['url']}")
            print(f"   Status: {proxy['status']}")
            print(f"   Success rate: {proxy.get('success_rate', 0):.2%}")
    else:
        print("\n3. Skipping rotation (no proxies in pool)")

    print()


async def recommendation_example():
    """Demonstrate proxy recommendations with criteria."""
    print("=== Proxy Recommendation ===\n")

    # Get recommendation without criteria
    print("1. General recommendation (no criteria)...")
    result = await proxywhirl(action="recommend")
    if "recommendation" in result:
        rec = result["recommendation"]
        print(f"   Recommended: {rec['url']}")
        print(f"   Score: {rec['score']:.2f}")
        print(f"   Reason: {rec['reason']}")
    elif "error" in result:
        print(f"   No recommendation: {result['error']}")

    # Get high-performance recommendation
    print("\n2. High-performance recommendation...")
    result = await proxywhirl(
        action="recommend",
        criteria={"performance": "high"},
    )
    if "recommendation" in result:
        rec = result["recommendation"]
        print(f"   Recommended: {rec['url']}")
        print(f"   Score: {rec['score']:.2f}")
        metrics = rec.get("metrics", {})
        print(f"   Latency: {metrics.get('avg_latency_ms', 0):.2f}ms")
    elif "error" in result:
        print(f"   No recommendation: {result['error']}")

    # Get region-specific recommendation
    print("\n3. Region-specific recommendation (US)...")
    result = await proxywhirl(
        action="recommend",
        criteria={"region": "US", "performance": "medium"},
    )
    if "recommendation" in result:
        rec = result["recommendation"]
        print(f"   Recommended: {rec['url']}")
        print(f"   Region: {rec['metrics'].get('region', 'unknown')}")
    elif "error" in result:
        print(f"   No recommendation: {result['error']}")

    print()


async def proxy_management_example():
    """Demonstrate proxy status and circuit breaker management."""
    print("=== Proxy Management ===\n")

    # First, get a proxy to work with
    result = await proxywhirl(action="list")
    proxies = result.get("proxies", [])

    if not proxies:
        print("No proxies available for management demo.")
        print("Run 'proxywhirl fetch --output proxywhirl.db' to populate proxies.\n")
        return

    proxy = proxies[0]
    proxy_id = proxy["id"]

    # Get detailed status
    print(f"1. Getting status for proxy {proxy_id[:8]}...")
    result = await proxywhirl(action="status", proxy_id=proxy_id)
    if "error" not in result:
        print(f"   URL: {result['url']}")
        print(f"   Status: {result['status']}")
        metrics = result.get("metrics", {})
        print(f"   Total requests: {metrics.get('total_requests', 0)}")
        print(f"   Success rate: {metrics.get('success_rate', 0):.2%}")
        health = result.get("health", {})
        print(f"   Circuit breaker: {health.get('circuit_breaker', 'unknown')}")
    else:
        print(f"   Error: {result['error']}")

    # Reset circuit breaker
    print(f"\n2. Resetting circuit breaker for proxy {proxy_id[:8]}...")
    result = await proxywhirl(action="reset_cb", proxy_id=proxy_id)
    if result.get("success"):
        print(f"   Previous state: {result['previous_state']}")
        print(f"   New state: {result['new_state']}")
    elif "error" in result:
        print(f"   {result['error']}")

    print()


async def custom_rotator_example():
    """Demonstrate using a custom rotator with MCP."""
    print("=== Custom Rotator ===\n")

    from proxywhirl import AsyncProxyRotator, ProxyConfiguration

    # Create custom configuration
    config = ProxyConfiguration(
        timeout=45.0,
        verify_ssl=False,
        pool_connections=25,
    )

    # Create custom rotator with performance-based strategy
    rotator = AsyncProxyRotator(
        strategy="performance-based",
        config=config,
    )

    # Set as global MCP rotator
    await set_rotator(rotator)
    print("1. Set custom rotator (performance-based strategy)")

    # Add some example proxies
    await rotator.add_proxy("http://proxy1.example.com:8080")
    await rotator.add_proxy("http://proxy2.example.com:8080")
    await rotator.add_proxy("http://proxy3.example.com:8080")
    print("2. Added 3 example proxies")

    # Verify via MCP tool
    result = await proxywhirl(action="list")
    print(f"3. MCP tool shows {result.get('total', 0)} proxies")

    # Check health
    result = await proxywhirl(action="health")
    print(f"4. Pool status: {result.get('pool_status', 'unknown')}")

    print()


async def error_handling_example():
    """Demonstrate error handling."""
    print("=== Error Handling ===\n")

    # Try to get status for invalid proxy ID
    print("1. Requesting status for invalid proxy ID...")
    result = await proxywhirl(action="status", proxy_id="invalid-uuid")
    if "error" in result:
        print(f"   Error code: {result.get('code')}")
        print(f"   Message: {result['error']}")

    # Try status without proxy_id
    print("\n2. Requesting status without proxy_id...")
    result = await proxywhirl(action="status", proxy_id=None)
    if "error" in result:
        print(f"   Error code: {result.get('code')}")
        print(f"   Message: {result['error']}")

    # Try invalid action
    print("\n3. Requesting invalid action...")
    # Note: Type checker would catch this, but demonstrating runtime behavior
    result = await proxywhirl(action="invalid_action")  # type: ignore[arg-type]
    if "error" in result:
        print(f"   Error code: {result.get('code')}")
        print(f"   Message: {result['error']}")

    print()


async def main():
    """Run all MCP usage examples."""
    print("=" * 60)
    print("ProxyWhirl MCP Server Usage Examples")
    print("=" * 60)
    print()

    try:
        await basic_usage()
        await recommendation_example()
        await proxy_management_example()
        await custom_rotator_example()
        await error_handling_example()

    finally:
        # Always clean up
        print("=== Cleanup ===\n")
        await cleanup_rotator()
        print("Cleaned up MCP rotator resources.")

    print()
    print("=" * 60)
    print("Examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
