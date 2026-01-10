#!/usr/bin/env python3
"""
Demonstration of ProxyValidator's shared client pool functionality.

This example shows how ProxyValidator efficiently reuses HTTP connections
through a shared client pool, reducing overhead when validating multiple proxies.
"""

import asyncio

from proxywhirl.fetchers import ProxyValidator


async def demo_basic_usage():
    """Basic usage with automatic client management."""
    print("=== Basic Usage ===")

    # Create validator - client pool is created lazily on first use
    validator = ProxyValidator(timeout=5.0, concurrency=10)

    proxies = [
        {"url": "http://proxy1.example.com:8080"},
        {"url": "http://proxy2.example.com:8080"},
        {"url": "http://proxy3.example.com:8080"},
    ]

    print(f"Validating {len(proxies)} proxies...")
    print("Note: All validations use the same HTTP client (connection pool)")

    # Client is created on first validation and reused for all subsequent ones
    valid_proxies = await validator.validate_batch(proxies)

    print(f"Found {len(valid_proxies)} valid proxies")

    # Don't forget to close the client when done
    await validator.close()
    print("Client pool closed\n")


async def demo_context_manager():
    """Recommended usage with context manager for automatic cleanup."""
    print("=== Context Manager (Recommended) ===")

    # Context manager ensures client is properly closed even on exceptions
    async with ProxyValidator(timeout=5.0, concurrency=20) as validator:
        proxies = [
            {"url": "http://proxy1.example.com:8080"},
            {"url": "http://proxy2.example.com:8080"},
            {"url": "socks5://proxy3.example.com:1080"},  # SOCKS uses separate pool
        ]

        print(f"Validating {len(proxies)} proxies with context manager...")

        # Individual validations
        for i, proxy in enumerate(proxies, 1):
            result = await validator.validate(proxy)
            proxy_type = "SOCKS" if proxy["url"].startswith("socks") else "HTTP"
            print(f"  {i}. {proxy_type} proxy: {'valid' if result else 'invalid'}")

    # Client is automatically closed when exiting the context
    print("Client pool automatically closed by context manager\n")


async def demo_batch_validation():
    """Batch validation with concurrency control."""
    print("=== Batch Validation with Concurrency Control ===")

    # Concurrency controls how many validations run in parallel
    async with ProxyValidator(concurrency=50) as validator:
        # Simulate a large batch of proxies
        proxies = [
            {"url": f"http://proxy{i}.example.com:8080"}
            for i in range(100)
        ]

        print(f"Validating {len(proxies)} proxies with concurrency limit of 50...")
        print("All validations share the same client pool (max 100 connections)")

        valid_proxies = await validator.validate_batch(proxies)

        print(f"Validated {len(proxies)} proxies")
        print(f"Found {len(valid_proxies)} valid proxies")
        print(f"Connection pool reused across all validations\n")


async def demo_anonymity_check():
    """Check proxy anonymity level using the shared client."""
    print("=== Anonymity Checking ===")

    async with ProxyValidator() as validator:
        proxy_url = "http://proxy.example.com:8080"

        print(f"Checking anonymity level for {proxy_url}...")

        # Anonymity check also uses the shared client pool
        anonymity = await validator.check_anonymity(proxy_url)

        print(f"Anonymity level: {anonymity}")
        print("Possible values: elite, anonymous, transparent, unknown\n")


async def demo_separate_socks_pool():
    """Demonstrate separate client pool for SOCKS proxies."""
    print("=== Separate SOCKS Client Pool ===")

    async with ProxyValidator() as validator:
        http_proxy = {"url": "http://proxy.example.com:8080"}
        socks_proxy = {"url": "socks5://proxy.example.com:1080"}

        print("ProxyValidator maintains two separate client pools:")
        print("  1. HTTP/HTTPS client (for HTTP proxies)")
        print("  2. SOCKS client (for SOCKS4/SOCKS5 proxies)")
        print()

        print("Validating HTTP proxy...")
        http_result = await validator.validate(http_proxy)
        print(f"HTTP proxy: {'valid' if http_result else 'invalid'}")

        print("Validating SOCKS proxy...")
        socks_result = await validator.validate(socks_proxy)
        print(f"SOCKS proxy: {'valid' if socks_result else 'invalid'}")

        print()
        print("Both clients are automatically managed and closed together\n")


async def demo_client_pool_benefits():
    """Demonstrate the benefits of connection pooling."""
    print("=== Client Pool Benefits ===")
    print()
    print("1. Connection Reuse:")
    print("   - TCP connections are reused across validations")
    print("   - Reduces connection setup overhead")
    print("   - Faster validation for multiple proxies")
    print()
    print("2. Resource Efficiency:")
    print("   - Single client instance per validator")
    print("   - Up to 100 concurrent connections")
    print("   - 20 keep-alive connections maintained")
    print()
    print("3. Memory Efficiency:")
    print("   - No client creation per request")
    print("   - Controlled resource usage")
    print("   - Proper cleanup with context manager")
    print()
    print("4. Concurrency Control:")
    print("   - Configurable via 'concurrency' parameter")
    print("   - Prevents resource exhaustion")
    print("   - Optimal for large-scale validation")
    print()


async def main():
    """Run all demonstrations."""
    print("ProxyValidator Client Pool Demonstration")
    print("=" * 60)
    print()

    await demo_basic_usage()
    await demo_context_manager()
    await demo_batch_validation()
    await demo_anonymity_check()
    await demo_separate_socks_pool()
    await demo_client_pool_benefits()

    print("=" * 60)
    print("Demonstration complete!")
    print()
    print("Key Takeaways:")
    print("- Always use context manager (async with) for automatic cleanup")
    print("- Client pool is created lazily on first use")
    print("- All validations share the same client pool")
    print("- SOCKS proxies use a separate, dedicated client pool")
    print("- Connection pooling significantly improves performance")


if __name__ == "__main__":
    # Note: In real usage, you would configure actual proxy URLs
    # This demo uses example.com URLs for illustration purposes
    print("Note: This is a demonstration with mock proxy URLs")
    print("In production, replace with actual working proxy addresses")
    print()

    # Uncomment to run the demo:
    # asyncio.run(main())

    print("Demo code is ready to run!")
    print("Uncomment 'asyncio.run(main())' in the script to execute.")
