"""Integration tests for MCP server."""

from uuid import uuid4

import pytest

from proxywhirl.circuit_breaker import CircuitBreaker
from proxywhirl.mcp.auth import MCPAuth
from proxywhirl.mcp.server import (
    _proxywhirl_tool,
    cleanup_rotator,
    set_auth,
    set_rotator,
)
from proxywhirl.models import HealthStatus, Proxy, ProxyPool, ProxySource
from proxywhirl.rotator import AsyncProxyWhirl

# Use _proxywhirl_tool for testing as the decorated proxywhirl becomes a
# FunctionTool object when FastMCP is available and is not directly callable
proxywhirl = _proxywhirl_tool


@pytest.fixture
async def mcp_rotator():
    """Fixture that provides MCP rotator and cleans up after."""
    # Create a fresh rotator with test proxies
    proxy1 = Proxy(
        id=uuid4(),
        url="http://mcp-proxy1.example.com:8080",
        protocol="http",
        health_status=HealthStatus.HEALTHY,
        source=ProxySource.USER,
        total_requests=100,
        total_successes=95,
        total_failures=5,
        average_response_time_ms=100.0,
        country_code="US",
    )

    proxy2 = Proxy(
        id=uuid4(),
        url="http://mcp-proxy2.example.com:8080",
        protocol="http",
        health_status=HealthStatus.HEALTHY,
        source=ProxySource.USER,
        total_requests=80,
        total_successes=75,
        total_failures=5,
        average_response_time_ms=150.0,
        country_code="UK",
    )

    proxy3 = Proxy(
        id=uuid4(),
        url="http://mcp-proxy3.example.com:8080",
        protocol="http",
        health_status=HealthStatus.DEGRADED,
        source=ProxySource.USER,
        total_requests=50,
        total_successes=35,
        total_failures=15,
        average_response_time_ms=300.0,
        country_code="US",
    )

    pool = ProxyPool(name="mcp_test_pool", proxies=[proxy1, proxy2, proxy3])

    rotator = AsyncProxyWhirl()
    rotator.pool = pool

    # Add circuit breakers
    rotator.circuit_breakers[str(proxy1.id)] = CircuitBreaker(
        proxy_id=str(proxy1.id),
        failure_threshold=5,
        window_duration=60.0,
        timeout_duration=30.0,
    )

    await set_rotator(rotator)
    # Disable auth for integration tests by default
    set_auth(MCPAuth())

    yield rotator

    # Cleanup
    await cleanup_rotator()
    set_auth(None)


@pytest.mark.integration
class TestMCPFullWorkflow:
    """Test complete MCP workflows."""

    async def test_mcp_full_workflow_list_rotate_status_health(self, mcp_rotator) -> None:
        """Test complete MCP workflow: list -> rotate -> status -> health."""
        # Step 1: List all proxies
        list_result = await proxywhirl(action="list")
        assert "proxies" in list_result
        assert "total" in list_result
        assert list_result["total"] == 3

        # Step 2: Rotate to get a proxy
        rotate_result = await proxywhirl(action="rotate")
        assert "proxy" in rotate_result
        proxy_id = rotate_result["proxy"]["id"]
        assert proxy_id is not None

        # Step 3: Get status for the rotated proxy
        status_result = await proxywhirl(action="status", proxy_id=proxy_id)
        assert status_result["proxy_id"] == proxy_id
        assert "metrics" in status_result
        assert "health" in status_result

        # Step 4: Check overall health
        health_result = await proxywhirl(action="health")
        assert "pool_status" in health_result
        assert health_result["total_proxies"] == 3

    async def test_mcp_recommend_workflow(self, mcp_rotator) -> None:
        """Test recommendation workflow with different criteria."""
        # Recommend with high performance
        high_perf_result = await proxywhirl(action="recommend", criteria={"performance": "high"})
        assert "recommendation" in high_perf_result
        assert high_perf_result["recommendation"]["metrics"]["performance_tier"] == "high"

        # Recommend with region filter
        us_result = await proxywhirl(action="recommend", criteria={"region": "US"})
        assert "recommendation" in us_result
        assert us_result["recommendation"]["metrics"]["region"] == "US"

        # Recommend with both criteria
        combined_result = await proxywhirl(
            action="recommend", criteria={"region": "US", "performance": "medium"}
        )
        assert "recommendation" in combined_result
        assert combined_result["recommendation"]["metrics"]["region"] == "US"

    async def test_mcp_circuit_breaker_workflow(self, mcp_rotator) -> None:
        """Test circuit breaker management workflow."""
        proxy_id = str(mcp_rotator.pool.proxies[0].id)

        # Check initial status
        status_result = await proxywhirl(action="status", proxy_id=proxy_id)
        assert status_result["health"]["circuit_breaker"] == "closed"

        # Reset circuit breaker (should work even when already closed)
        reset_result = await proxywhirl(action="reset_cb", proxy_id=proxy_id)
        assert reset_result["success"] is True
        assert reset_result["new_state"] == "closed"

        # Verify status after reset
        status_after = await proxywhirl(action="status", proxy_id=proxy_id)
        assert status_after["health"]["circuit_breaker"] == "closed"


@pytest.mark.integration
class TestMCPRecommendWithCriteria:
    """Test recommend action with various criteria combinations."""

    async def test_mcp_recommend_with_criteria(self, mcp_rotator) -> None:
        """Test recommend with various criteria."""
        # Test with performance only
        result = await proxywhirl(action="recommend", criteria={"performance": "high"})
        assert "recommendation" in result
        assert "alternatives" in result["recommendation"]

    async def test_mcp_recommend_no_criteria(self, mcp_rotator) -> None:
        """Test recommend with no criteria uses defaults."""
        result = await proxywhirl(action="recommend")

        assert "recommendation" in result
        # Default performance is "medium"
        assert result["recommendation"]["metrics"]["performance_tier"] == "medium"

    async def test_mcp_recommend_invalid_region(self, mcp_rotator) -> None:
        """Test recommend with region that has no proxies."""
        result = await proxywhirl(action="recommend", criteria={"region": "INVALID"})

        assert "error" in result
        assert "No proxies found for region" in result["error"]

    async def test_mcp_recommend_low_performance(self, mcp_rotator) -> None:
        """Test recommend with low performance tier."""
        result = await proxywhirl(action="recommend", criteria={"performance": "low"})

        assert "recommendation" in result
        assert result["recommendation"]["metrics"]["performance_tier"] == "low"


@pytest.mark.integration
class TestMCPAuthWhenConfigured:
    """Test authentication when API key is configured."""

    async def test_mcp_auth_rejects_without_key(self, mcp_rotator) -> None:
        """Test authentication rejects requests without API key."""
        # Configure auth
        set_auth(MCPAuth(api_key="test-integration-key"))

        try:
            # Without key should fail
            result = await proxywhirl(action="list")
            assert "error" in result
            assert "Authentication" in result["error"]
        finally:
            # Reset auth
            set_auth(MCPAuth())

    async def test_mcp_auth_accepts_valid_key(self, mcp_rotator) -> None:
        """Test authentication accepts requests with valid API key."""
        # Configure auth
        set_auth(MCPAuth(api_key="test-integration-key"))

        try:
            # With key should succeed
            result = await proxywhirl(action="list", api_key="test-integration-key")
            assert "proxies" in result
            assert "error" not in result
        finally:
            # Reset auth
            set_auth(MCPAuth())

    async def test_mcp_auth_rejects_invalid_key(self, mcp_rotator) -> None:
        """Test authentication rejects requests with invalid API key."""
        # Configure auth
        set_auth(MCPAuth(api_key="correct-key"))

        try:
            # Wrong key should fail
            result = await proxywhirl(action="list", api_key="wrong-key")
            assert "error" in result
            assert "Authentication" in result["error"]
        finally:
            # Reset auth
            set_auth(MCPAuth())

    async def test_mcp_auth_all_actions(self, mcp_rotator) -> None:
        """Test that all actions respect authentication."""
        set_auth(MCPAuth(api_key="auth-test-key"))

        try:
            # Test each action without key - should all fail
            actions_without_proxy_id = ["list", "rotate", "recommend", "health"]
            for action in actions_without_proxy_id:
                result = await proxywhirl(action=action)  # type: ignore[arg-type]
                # health doesn't require auth
                if action != "health":
                    assert "error" in result, f"Action {action} should require auth"

            # Test each action with key - should all succeed
            for action in actions_without_proxy_id:
                result = await proxywhirl(action=action, api_key="auth-test-key")  # type: ignore[arg-type]
                assert "error" not in result, f"Action {action} should succeed with valid key"
        finally:
            set_auth(MCPAuth())


@pytest.mark.integration
class TestMCPEmptyPool:
    """Test MCP behavior with empty proxy pool."""

    async def test_mcp_list_empty_pool(self) -> None:
        """Test list action with empty pool."""
        # Create empty rotator
        empty_rotator = AsyncProxyWhirl()
        empty_rotator.pool = ProxyPool(name="empty_pool", proxies=[])
        await set_rotator(empty_rotator)
        set_auth(MCPAuth())

        try:
            result = await proxywhirl(action="list")
            assert result["proxies"] == []
            assert result["total"] == 0
        finally:
            await cleanup_rotator()

    async def test_mcp_rotate_empty_pool(self) -> None:
        """Test rotate action with empty pool returns error."""
        empty_rotator = AsyncProxyWhirl()
        empty_rotator.pool = ProxyPool(name="empty_pool", proxies=[])
        await set_rotator(empty_rotator)
        set_auth(MCPAuth())

        try:
            result = await proxywhirl(action="rotate")
            assert "error" in result
        finally:
            await cleanup_rotator()

    async def test_mcp_recommend_empty_pool(self) -> None:
        """Test recommend action with empty pool returns error."""
        empty_rotator = AsyncProxyWhirl()
        empty_rotator.pool = ProxyPool(name="empty_pool", proxies=[])
        await set_rotator(empty_rotator)
        set_auth(MCPAuth())

        try:
            result = await proxywhirl(action="recommend")
            assert "error" in result
            assert "No proxies available" in result["error"]
        finally:
            await cleanup_rotator()

    async def test_mcp_health_empty_pool(self) -> None:
        """Test health action with empty pool returns empty status."""
        empty_rotator = AsyncProxyWhirl()
        empty_rotator.pool = ProxyPool(name="empty_pool", proxies=[])
        await set_rotator(empty_rotator)
        set_auth(MCPAuth())

        try:
            result = await proxywhirl(action="health")
            assert result["pool_status"] == "empty"
            assert result["total_proxies"] == 0
        finally:
            await cleanup_rotator()


@pytest.mark.integration
class TestMCPErrorHandling:
    """Test MCP error handling scenarios."""

    async def test_mcp_status_nonexistent_proxy(self, mcp_rotator) -> None:
        """Test status action with non-existent proxy ID."""
        fake_id = str(uuid4())
        result = await proxywhirl(action="status", proxy_id=fake_id)

        assert "error" in result
        assert "Proxy not found" in result["error"]
        assert result["code"] == 404

    async def test_mcp_status_invalid_uuid(self, mcp_rotator) -> None:
        """Test status action with invalid UUID format."""
        result = await proxywhirl(action="status", proxy_id="not-a-uuid")

        assert "error" in result
        assert "Invalid proxy_id format" in result["error"]
        assert result["code"] == 400

    async def test_mcp_reset_cb_nonexistent_proxy(self, mcp_rotator) -> None:
        """Test reset_cb action with proxy that has no circuit breaker."""
        # proxy3 (index 2) doesn't have a circuit breaker
        proxy_id = str(mcp_rotator.pool.proxies[2].id)
        result = await proxywhirl(action="reset_cb", proxy_id=proxy_id)

        assert "error" in result
        assert "No circuit breaker found" in result["error"]

    async def test_mcp_recommend_invalid_performance(self, mcp_rotator) -> None:
        """Test recommend action with invalid performance level."""
        result = await proxywhirl(action="recommend", criteria={"performance": "ultra-mega"})

        assert "error" in result
        assert "Invalid performance level" in result["error"]


@pytest.mark.integration
class TestMCPConcurrentAccess:
    """Test MCP with concurrent access patterns."""

    async def test_mcp_concurrent_list_operations(self, mcp_rotator) -> None:
        """Test multiple concurrent list operations."""
        import asyncio

        tasks = [proxywhirl(action="list") for _ in range(10)]
        results = await asyncio.gather(*tasks)

        # All results should be consistent
        for result in results:
            assert "proxies" in result
            assert result["total"] == 3

    async def test_mcp_concurrent_rotate_operations(self, mcp_rotator) -> None:
        """Test multiple concurrent rotate operations."""
        import asyncio

        tasks = [proxywhirl(action="rotate") for _ in range(10)]
        results = await asyncio.gather(*tasks)

        # All results should return a proxy (no corruption)
        for result in results:
            assert "proxy" in result
            assert "id" in result["proxy"]

    async def test_mcp_mixed_concurrent_operations(self, mcp_rotator) -> None:
        """Test mixed concurrent operations."""
        import asyncio

        proxy_id = str(mcp_rotator.pool.proxies[0].id)

        tasks = [
            proxywhirl(action="list"),
            proxywhirl(action="rotate"),
            proxywhirl(action="health"),
            proxywhirl(action="status", proxy_id=proxy_id),
            proxywhirl(action="recommend"),
        ]

        results = await asyncio.gather(*tasks)

        # Verify each result type
        assert "proxies" in results[0]  # list
        assert "proxy" in results[1]  # rotate
        assert "pool_status" in results[2]  # health
        assert "proxy_id" in results[3]  # status
        assert "recommendation" in results[4]  # recommend
