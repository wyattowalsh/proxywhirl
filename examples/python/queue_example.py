"""
Example demonstrating request queuing with rate limiting.

This example shows how to:
1. Enable request queuing when rate limited
2. Configure queue size
3. Monitor queue statistics
4. Handle backpressure (queue full errors)
"""

from proxywhirl import (
    Proxy,
    ProxyConfiguration,
    ProxyWhirl,
    RequestQueueFullError,
)
from proxywhirl.rate_limiting import RateLimiter


def main():
    """Demonstrate request queuing functionality."""
    # Configure ProxyWhirl with queuing enabled
    config = ProxyConfiguration(
        queue_enabled=True,  # Enable request queuing
        queue_size=50,       # Max 50 queued requests
    )

    # Create rate limiter (1 request per second per proxy)
    rate_limiter = RateLimiter(
        max_requests=1,
        time_window=1.0,  # 1 second
    )

    # Initialize rotator with queuing and rate limiting
    rotator = ProxyWhirl(
        config=config,
        rate_limiter=rate_limiter,
    )

    # Add some proxies
    rotator.add_proxy("http://proxy1.example.com:8080")
    rotator.add_proxy("http://proxy2.example.com:8080")

    print("Request queuing example")
    print("=" * 50)

    # Check initial queue stats
    stats = rotator.get_queue_stats()
    print(f"\nInitial queue stats:")
    print(f"  Enabled: {stats['enabled']}")
    print(f"  Size: {stats['size']}")
    print(f"  Max Size: {stats['max_size']}")
    print(f"  Is Empty: {stats['is_empty']}")

    # Simulate rapid requests that might trigger rate limiting
    print("\nMaking requests...")
    for i in range(5):
        try:
            # When rate limited, requests will be queued automatically
            response = rotator.get(f"https://httpbin.org/delay/{i}")
            print(f"  Request {i+1}: {response.status_code}")

            # Check queue stats after each request
            stats = rotator.get_queue_stats()
            if stats['size'] > 0:
                print(f"    Queue size: {stats['size']}")

        except RequestQueueFullError as e:
            # Queue is full - backpressure triggered
            print(f"  Request {i+1}: Queue full! {e}")
            break

    # Final queue stats
    stats = rotator.get_queue_stats()
    print(f"\nFinal queue stats:")
    print(f"  Size: {stats['size']}")
    print(f"  Is Full: {stats['is_full']}")
    print(f"  Is Empty: {stats['is_empty']}")

    # Clear any remaining requests
    if not stats['is_empty']:
        cleared = rotator.clear_queue()
        print(f"\nCleared {cleared} requests from queue")


def example_without_queue():
    """Example showing behavior when queue is disabled."""
    print("\nExample without queuing")
    print("=" * 50)

    # Queuing disabled (default)
    config = ProxyConfiguration(queue_enabled=False)
    rate_limiter = RateLimiter(max_requests=1, time_window=1.0)

    rotator = ProxyWhirl(config=config, rate_limiter=rate_limiter)
    rotator.add_proxy("http://proxy1.example.com:8080")

    # When rate limited without queue, requests will raise errors
    try:
        for i in range(5):
            response = rotator.get(f"https://httpbin.org/delay/{i}")
            print(f"  Request {i+1}: {response.status_code}")
    except Exception as e:
        print(f"  Rate limited! {type(e).__name__}: {e}")


if __name__ == "__main__":
    # Note: This example requires actual proxies to run successfully
    print("Note: This example requires actual working proxies")
    print("Modify the proxy URLs before running\n")

    # Uncomment to run examples:
    # main()
    # example_without_queue()
