"""
Basic integration tests for rate limiting.

Tests core rate limiting functionality with in-memory storage.
"""

import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from proxywhirl.rate_limit_models import (
    RateLimitConfig,
    RateLimitTierConfig,
)
from proxywhirl.rate_limiter import RateLimiter


@pytest.fixture
def rate_limit_config() -> RateLimitConfig:
    """Create test rate limit configuration."""
    return RateLimitConfig(
        enabled=True,
        default_tier="test",
        redis_enabled=False,  # Use in-memory for tests
        tiers=[
            RateLimitTierConfig(
                name="test",
                requests_per_window=10,
                window_size_seconds=60,
            )
        ],
    )


@pytest.fixture
def limiter(rate_limit_config: RateLimitConfig) -> RateLimiter:
    """Create rate limiter instance."""
    return RateLimiter(rate_limit_config)


@pytest.mark.asyncio
async def test_rate_limit_basic_enforcement(limiter: RateLimiter) -> None:
    """Test basic rate limiting enforcement."""
    identifier = "550e8400-e29b-41d4-a716-446655440000"  # Valid UUID
    endpoint = "/api/v1/test"
    tier = "test"

    # Make 10 requests (should all succeed)
    for i in range(10):
        result = await limiter.check(identifier, endpoint, tier)
        assert result.allowed, f"Request {i+1} should be allowed"
        assert result.state.current_count == i + 1
        assert result.state.remaining == 10 - (i + 1)

    # 11th request should be rate limited
    result = await limiter.check(identifier, endpoint, tier)
    assert not result.allowed
    assert result.state.current_count == 10
    assert result.state.remaining == 0
    assert result.reason == "rate_limit_exceeded"


@pytest.mark.asyncio
async def test_rate_limit_independent_users(limiter: RateLimiter) -> None:
    """Test that different users have independent rate limits."""
    user1 = "550e8400-e29b-41d4-a716-446655440001"  # Valid UUID
    user2 = "550e8400-e29b-41d4-a716-446655440002"  # Valid UUID
    endpoint = "/api/v1/test"
    tier = "test"

    # User 1 makes 10 requests
    for _ in range(10):
        result = await limiter.check(user1, endpoint, tier)
        assert result.allowed

    # User 1's 11th request is rate limited
    result = await limiter.check(user1, endpoint, tier)
    assert not result.allowed

    # User 2 can still make requests
    result = await limiter.check(user2, endpoint, tier)
    assert result.allowed
    assert result.state.current_count == 1


@pytest.mark.asyncio
async def test_rate_limit_independent_endpoints(limiter: RateLimiter) -> None:
    """Test that different endpoints have independent rate limits."""
    identifier = "192.168.1.100"  # Valid IP address
    endpoint1 = "/api/v1/endpoint1"
    endpoint2 = "/api/v1/endpoint2"
    tier = "test"

    # Make 10 requests to endpoint1
    for _ in range(10):
        result = await limiter.check(identifier, endpoint1, tier)
        assert result.allowed

    # Endpoint1 is now rate limited
    result = await limiter.check(identifier, endpoint1, tier)
    assert not result.allowed

    # Endpoint2 still has full quota
    result = await limiter.check(identifier, endpoint2, tier)
    assert result.allowed
    assert result.state.current_count == 1


@pytest.mark.asyncio
async def test_rate_limit_whitelist(rate_limit_config: RateLimitConfig) -> None:
    """Test that whitelisted identifiers bypass rate limiting."""
    whitelisted_user = "550e8400-e29b-41d4-a716-446655440000"
    rate_limit_config.whitelist = [whitelisted_user]
    limiter = RateLimiter(rate_limit_config)

    endpoint = "/api/v1/test"
    tier = "test"

    # Make 20 requests (more than limit of 10)
    for _ in range(20):
        result = await limiter.check(whitelisted_user, endpoint, tier)
        assert result.allowed
        assert result.state.tier == "whitelisted"


@pytest.mark.asyncio
async def test_rate_limit_computed_fields(limiter: RateLimiter) -> None:
    """Test computed fields in RateLimitState."""
    identifier = "10.0.0.1"  # Valid IP address
    endpoint = "/api/v1/test"
    tier = "test"

    # Make 5 requests
    for _ in range(5):
        await limiter.check(identifier, endpoint, tier)

    result = await limiter.check(identifier, endpoint, tier)
    assert result.allowed
    assert result.state.current_count == 6
    assert result.state.remaining == 4  # 10 - 6
    assert not result.state.is_exceeded  # Not exceeded yet
    assert result.state.retry_after_seconds >= 0


@pytest.mark.asyncio
async def test_rate_limit_tier_not_found(limiter: RateLimiter) -> None:
    """Test that invalid tier raises ValueError."""
    identifier = "::1"  # Valid IPv6 address
    endpoint = "/api/v1/test"
    tier = "nonexistent"

    with pytest.raises(ValueError, match="Tier 'nonexistent' not found"):
        await limiter.check(identifier, endpoint, tier)


@pytest.mark.asyncio
async def test_rate_limit_per_endpoint_override() -> None:
    """Test per-endpoint rate limit overrides."""
    config = RateLimitConfig(
        enabled=True,
        default_tier="test",
        redis_enabled=False,
        tiers=[
            RateLimitTierConfig(
                name="test",
                requests_per_window=100,
                window_size_seconds=60,
                endpoints={
                    "/api/v1/expensive": 5,  # Stricter limit for expensive endpoint
                },
            )
        ],
    )
    limiter = RateLimiter(config)

    identifier = "192.168.1.50"  # Valid IP address
    expensive_endpoint = "/api/v1/expensive"
    cheap_endpoint = "/api/v1/cheap"
    tier = "test"

    # Expensive endpoint limited to 5
    for i in range(5):
        result = await limiter.check(identifier, expensive_endpoint, tier)
        assert result.allowed, f"Request {i+1} should be allowed"

    # 6th request to expensive endpoint is rate limited
    result = await limiter.check(identifier, expensive_endpoint, tier)
    assert not result.allowed
    assert result.state.limit == 5

    # Cheap endpoint still has full 100 req quota (independent)
    result = await limiter.check(identifier, cheap_endpoint, tier)
    assert result.allowed
    assert result.state.limit == 100


@pytest.mark.asyncio
async def test_rate_limit_config_validation() -> None:
    """Test rate limit configuration validation."""
    # Invalid: default_tier not in tiers
    with pytest.raises(ValueError, match="not found in tiers"):
        RateLimitConfig(
            default_tier="nonexistent",
            tiers=[
                RateLimitTierConfig(
                    name="test", requests_per_window=100, window_size_seconds=60
                )
            ],
        )

    # Invalid: whitelist entry not UUID or IP
    with pytest.raises(ValueError, match="Invalid whitelist entry"):
        RateLimitConfig(
            tiers=[
                RateLimitTierConfig(
                    name="test", requests_per_window=100, window_size_seconds=60
                )
            ],
            whitelist=["not-valid"],
        )


@pytest.mark.asyncio
async def test_rate_limit_close(limiter: RateLimiter) -> None:
    """Test rate limiter cleanup."""
    await limiter.close()
    # Should not raise exception
    assert True
