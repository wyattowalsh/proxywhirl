"""
End-to-end integration tests for rate limiting.

Tests full integration including metrics, monitoring, and configuration.
"""

import pytest

from proxywhirl.rate_limit_models import (
    RateLimitConfig,
    RateLimitTierConfig,
)
from proxywhirl.rate_limiter import RateLimiter


@pytest.fixture
def full_config() -> RateLimitConfig:
    """Create comprehensive test configuration."""
    return RateLimitConfig(
        enabled=True,
        default_tier="free",
        redis_enabled=False,
        whitelist=["550e8400-e29b-41d4-a716-446655440099"],
        tiers=[
            RateLimitTierConfig(
                name="free",
                requests_per_window=10,
                window_size_seconds=60,
                endpoints={"/api/v1/expensive": 3},
            ),
            RateLimitTierConfig(
                name="premium",
                requests_per_window=50,
                window_size_seconds=60,
            ),
        ],
    )


@pytest.fixture
def e2e_limiter(full_config: RateLimitConfig) -> RateLimiter:
    """Create rate limiter for e2e tests."""
    return RateLimiter(full_config)


@pytest.mark.asyncio
async def test_e2e_rate_limiting_workflow(e2e_limiter: RateLimiter) -> None:
    """Test complete rate limiting workflow with metrics."""
    free_user = "192.168.1.100"
    premium_user = "550e8400-e29b-41d4-a716-446655440001"
    whitelisted_user = "550e8400-e29b-41d4-a716-446655440099"

    # Free user: 10 requests allowed
    for i in range(10):
        result = await e2e_limiter.check(free_user, "/api/v1/test", "free")
        assert result.allowed
        assert result.state.tier == "free"

    # 11th request denied
    result = await e2e_limiter.check(free_user, "/api/v1/test", "free")
    assert not result.allowed
    assert result.reason == "rate_limit_exceeded"

    # Premium user still has quota
    result = await e2e_limiter.check(premium_user, "/api/v1/test", "premium")
    assert result.allowed
    assert result.state.limit == 50

    # Whitelisted user bypasses limits
    result = await e2e_limiter.check(whitelisted_user, "/api/v1/test", "free")
    assert result.allowed
    assert result.state.tier == "whitelisted"

    # Check metrics (whitelisted requests not tracked)
    metrics = await e2e_limiter.get_metrics()
    assert metrics.total_requests == 12  # 10 + 1 + 1 (whitelisted not counted)
    assert metrics.throttled_requests == 1
    assert metrics.allowed_requests == 11
    assert "free" in metrics.by_tier
    assert metrics.by_tier["free"] == 1  # One throttled request
    assert metrics.avg_check_latency_ms >= 0
    assert metrics.p95_check_latency_ms >= 0


@pytest.mark.asyncio
async def test_e2e_endpoint_specific_limits(e2e_limiter: RateLimiter) -> None:
    """Test per-endpoint limits with metrics tracking."""
    user = "192.168.1.101"

    # Expensive endpoint: 3 req limit
    for i in range(3):
        result = await e2e_limiter.check(user, "/api/v1/expensive", "free")
        assert result.allowed
        assert result.state.limit == 3

    # 4th request to expensive endpoint denied
    result = await e2e_limiter.check(user, "/api/v1/expensive", "free")
    assert not result.allowed

    # Regular endpoint still has quota (10 req limit)
    result = await e2e_limiter.check(user, "/api/v1/regular", "free")
    assert result.allowed
    assert result.state.limit == 10

    # Check metrics
    metrics = await e2e_limiter.get_metrics()
    assert "/api/v1/expensive" in metrics.by_endpoint
    assert metrics.by_endpoint["/api/v1/expensive"] == 1


@pytest.mark.asyncio
async def test_e2e_status_endpoint(e2e_limiter: RateLimiter) -> None:
    """Test rate limit status retrieval."""
    user = "192.168.1.102"
    whitelisted = "550e8400-e29b-41d4-a716-446655440099"

    # Regular user status
    status = await e2e_limiter.get_status(user)
    assert status["identifier"] == user
    assert status["tier"] == "free"
    assert status["is_whitelisted"] is False

    # Whitelisted user status
    status = await e2e_limiter.get_status(whitelisted)
    assert status["identifier"] == whitelisted
    assert status["tier"] == "whitelisted"
    assert status["is_whitelisted"] is True


@pytest.mark.asyncio
async def test_e2e_metrics_accuracy(e2e_limiter: RateLimiter) -> None:
    """Test metrics accuracy and latency tracking."""
    user = "192.168.1.103"

    # Initial metrics
    metrics_before = await e2e_limiter.get_metrics()
    total_before = metrics_before.total_requests

    # Make 5 successful requests
    for _ in range(5):
        result = await e2e_limiter.check(user, "/api/v1/test", "free")
        assert result.allowed

    # Check metrics updated correctly
    metrics_after = await e2e_limiter.get_metrics()
    assert metrics_after.total_requests == total_before + 5
    assert metrics_after.allowed_requests == metrics_before.allowed_requests + 5
    assert metrics_after.throttled_requests == metrics_before.throttled_requests

    # Verify latency is reasonable
    assert metrics_after.avg_check_latency_ms < 10  # Should be <10ms
    assert metrics_after.p95_check_latency_ms < 10  # Should be <10ms


@pytest.mark.asyncio
async def test_e2e_tier_configuration(e2e_limiter: RateLimiter) -> None:
    """Test tier configuration retrieval."""
    config = e2e_limiter.config

    assert config.enabled is True
    assert config.default_tier == "free"
    assert len(config.tiers) == 2

    # Check free tier
    free_tier = config.get_tier_config("free")
    assert free_tier is not None
    assert free_tier.requests_per_window == 10
    assert free_tier.endpoints["/api/v1/expensive"] == 3

    # Check premium tier
    premium_tier = config.get_tier_config("premium")
    assert premium_tier is not None
    assert premium_tier.requests_per_window == 50


@pytest.mark.asyncio
async def test_e2e_configuration_hot_update(e2e_limiter: RateLimiter) -> None:
    """Test configuration can be updated at runtime."""
    user = "192.168.1.104"

    # Make requests with initial config (limit: 10)
    for _ in range(5):
        result = await e2e_limiter.check(user, "/api/v1/test", "free")
        assert result.allowed

    # Update configuration in memory
    new_config = RateLimitConfig(
        enabled=True,
        default_tier="free",
        redis_enabled=False,
        tiers=[
            RateLimitTierConfig(
                name="free",
                requests_per_window=20,  # Increased limit
                window_size_seconds=60,
            )
        ],
    )
    e2e_limiter.config = new_config

    # Verify new limit is applied for new user
    new_user = "192.168.1.105"
    for i in range(20):
        result = await e2e_limiter.check(new_user, "/api/v1/test", "free")
        assert result.allowed, f"Request {i+1} should be allowed (limit: 20)"
        assert result.state.limit == 20

    # 21st request denied
    result = await e2e_limiter.check(new_user, "/api/v1/test", "free")
    assert not result.allowed, "21st request should be denied (limit: 20)"


@pytest.mark.asyncio
async def test_e2e_cleanup(e2e_limiter: RateLimiter) -> None:
    """Test rate limiter cleanup and resource management."""
    # Should not raise any exceptions
    await e2e_limiter.close()
    assert True
