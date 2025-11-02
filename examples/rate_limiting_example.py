"""
Rate Limiting Example

Demonstrates how to use ProxyWhirl's rate limiting features.
"""

import asyncio
from pathlib import Path

from proxywhirl.rate_limit_models import RateLimitConfig, RateLimitTierConfig
from proxywhirl.rate_limiter import RateLimiter


async def example_basic_rate_limiting() -> None:
    """Example 1: Basic rate limiting with in-memory storage."""
    print("=== Example 1: Basic Rate Limiting ===")

    # Create configuration
    config = RateLimitConfig(
        enabled=True,
        default_tier="free",
        redis_enabled=False,  # Use in-memory for this example
        tiers=[
            RateLimitTierConfig(
                name="free",
                requests_per_window=10,
                window_size_seconds=60,
                description="Free tier: 10 requests per minute",
            )
        ],
    )

    # Create rate limiter
    limiter = RateLimiter(config)

    # Simulate requests from a user
    user_id = "550e8400-e29b-41d4-a716-446655440000"
    endpoint = "/api/v1/request"

    print(f"Making requests from user {user_id[:8]}...")

    # Make 12 requests (limit is 10)
    for i in range(12):
        result = await limiter.check(user_id, endpoint, "free")

        if result.allowed:
            print(
                f"✓ Request {i+1}: ALLOWED "
                f"({result.state.current_count}/{result.state.limit}, "
                f"{result.state.remaining} remaining)"
            )
        else:
            print(
                f"✗ Request {i+1}: RATE LIMITED "
                f"(retry after {result.state.retry_after_seconds}s)"
            )

    await limiter.close()
    print()


async def example_tiered_rate_limiting() -> None:
    """Example 2: Different rate limits for different tiers."""
    print("=== Example 2: Tiered Rate Limiting ===")

    # Create configuration with multiple tiers
    config = RateLimitConfig(
        enabled=True,
        default_tier="free",
        redis_enabled=False,
        tiers=[
            RateLimitTierConfig(
                name="free",
                requests_per_window=5,
                window_size_seconds=60,
                description="Free tier: 5 requests per minute",
            ),
            RateLimitTierConfig(
                name="premium",
                requests_per_window=20,
                window_size_seconds=60,
                description="Premium tier: 20 requests per minute",
            ),
        ],
    )

    limiter = RateLimiter(config)

    # Free user
    free_user = "550e8400-e29b-41d4-a716-446655440001"
    # Premium user
    premium_user = "550e8400-e29b-41d4-a716-446655440002"

    endpoint = "/api/v1/request"

    print(f"Free user ({free_user[:8]}) - limit: 5 req/min")
    for i in range(7):
        result = await limiter.check(free_user, endpoint, "free")
        status = "ALLOWED" if result.allowed else "RATE LIMITED"
        print(f"  Request {i+1}: {status} ({result.state.remaining} remaining)")

    print(f"\nPremium user ({premium_user[:8]}) - limit: 20 req/min")
    for i in range(7):
        result = await limiter.check(premium_user, endpoint, "premium")
        status = "ALLOWED" if result.allowed else "RATE LIMITED"
        print(f"  Request {i+1}: {status} ({result.state.remaining} remaining)")

    await limiter.close()
    print()


async def example_per_endpoint_limits() -> None:
    """Example 3: Different limits for different endpoints."""
    print("=== Example 3: Per-Endpoint Rate Limiting ===")

    # Create configuration with endpoint-specific overrides
    config = RateLimitConfig(
        enabled=True,
        default_tier="free",
        redis_enabled=False,
        tiers=[
            RateLimitTierConfig(
                name="free",
                requests_per_window=100,  # Global limit
                window_size_seconds=60,
                endpoints={
                    "/api/v1/request": 5,  # Expensive endpoint: stricter limit
                    "/api/v1/health": 100,  # Health checks: no additional restriction
                },
                description="Free tier with per-endpoint limits",
            )
        ],
    )

    limiter = RateLimiter(config)
    user_id = "192.168.1.100"  # Using IP address

    # Test expensive endpoint
    print("Expensive endpoint (/api/v1/request) - limit: 5 req/min")
    for i in range(7):
        result = await limiter.check(user_id, "/api/v1/request", "free")
        status = "✓" if result.allowed else "✗"
        print(
            f"  {status} Request {i+1}: "
            f"{result.state.current_count}/{result.state.limit}"
        )

    # Test health endpoint (independent limit)
    print("\nHealth endpoint (/api/v1/health) - limit: 100 req/min")
    for i in range(3):
        result = await limiter.check(user_id, "/api/v1/health", "free")
        print(
            f"  ✓ Request {i+1}: "
            f"{result.state.current_count}/{result.state.limit}"
        )

    await limiter.close()
    print()


async def example_whitelist() -> None:
    """Example 4: Whitelisted users bypass rate limiting."""
    print("=== Example 4: Whitelist Bypass ===")

    admin_user = "550e8400-e29b-41d4-a716-446655440099"

    # Create configuration with whitelist
    config = RateLimitConfig(
        enabled=True,
        default_tier="free",
        redis_enabled=False,
        whitelist=[admin_user],  # Admin bypasses rate limits
        tiers=[
            RateLimitTierConfig(
                name="free",
                requests_per_window=5,
                window_size_seconds=60,
            )
        ],
    )

    limiter = RateLimiter(config)
    endpoint = "/api/v1/request"

    print(f"Whitelisted user ({admin_user[:8]}) - no limits")
    # Make 10 requests (would exceed limit of 5 for normal users)
    for i in range(10):
        result = await limiter.check(admin_user, endpoint, "free")
        print(f"  ✓ Request {i+1}: ALLOWED (whitelisted, tier={result.state.tier})")

    await limiter.close()
    print()


async def example_load_from_yaml() -> None:
    """Example 5: Load configuration from YAML file."""
    print("=== Example 5: Load Configuration from YAML ===")

    # Load from YAML file
    config_path = Path(__file__).parent.parent / "rate_limit_config.yaml"

    if config_path.exists():
        print(f"Loading configuration from: {config_path}")
        config = RateLimitConfig.from_yaml(config_path)

        print(f"  Enabled: {config.enabled}")
        print(f"  Default tier: {config.default_tier}")
        print(f"  Redis enabled: {config.redis_enabled}")
        print(f"  Number of tiers: {len(config.tiers)}")

        for tier in config.tiers:
            print(
                f"    - {tier.name}: {tier.requests_per_window} req/"
                f"{tier.window_size_seconds}s"
            )
            if tier.endpoints:
                print(f"      Endpoint overrides: {len(tier.endpoints)}")
                for ep, limit in tier.endpoints.items():
                    print(f"        {ep}: {limit} req/min")
    else:
        print(f"Config file not found: {config_path}")

    print()


async def main() -> None:
    """Run all examples."""
    print("ProxyWhirl Rate Limiting Examples")
    print("=" * 50)
    print()

    await example_basic_rate_limiting()
    await example_tiered_rate_limiting()
    await example_per_endpoint_limits()
    await example_whitelist()
    await example_load_from_yaml()

    print("=" * 50)
    print("All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
