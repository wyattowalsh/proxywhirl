"""Unit tests for MCP server module."""

import asyncio
import json
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from proxywhirl.async_client import AsyncProxyRotator
from proxywhirl.circuit_breaker import CircuitBreaker
from proxywhirl.mcp.auth import MCPAuth
from proxywhirl.mcp.server import (
    ProxyWhirlMCPServer,
    _proxywhirl_tool,
    cleanup_rotator,
    get_auth,
    get_proxy_config,
    get_proxy_health,
    get_rate_limit_status,
    get_rotator,
    list_proxies,
    proxy_status,
    recommend_proxy,
    rotate_proxy,
    set_auth,
    set_rotator,
)
from proxywhirl.models import HealthStatus, Proxy, ProxyPool, ProxySource


@pytest.fixture
def mock_rotator():
    """Create a mock rotator with test proxies."""
    # Create test proxies with different health statuses
    proxy1 = Proxy(
        id=uuid4(),
        url="http://proxy1.example.com:8080",
        protocol="http",
        health_status=HealthStatus.HEALTHY,
        source=ProxySource.USER,
        total_requests=100,
        total_successes=95,
        total_failures=5,
        consecutive_successes=10,
        consecutive_failures=0,
        average_response_time_ms=100.0,
        country_code="US",
    )

    proxy2 = Proxy(
        id=uuid4(),
        url="http://proxy2.example.com:8080",
        protocol="http",
        health_status=HealthStatus.DEGRADED,
        source=ProxySource.USER,
        total_requests=50,
        total_successes=30,
        total_failures=20,
        consecutive_successes=0,
        consecutive_failures=2,
        average_response_time_ms=500.0,
        country_code="UK",
    )

    proxy3 = Proxy(
        id=uuid4(),
        url="http://proxy3.example.com:8080",
        protocol="http",
        health_status=HealthStatus.UNHEALTHY,
        source=ProxySource.USER,
        total_requests=20,
        total_successes=5,
        total_failures=15,
        consecutive_successes=0,
        consecutive_failures=5,
        average_response_time_ms=1500.0,
        country_code="US",
    )

    proxy4 = Proxy(
        id=uuid4(),
        url="http://proxy4.example.com:8080",
        protocol="http",
        health_status=HealthStatus.DEAD,
        source=ProxySource.USER,
        total_requests=10,
        total_successes=0,
        total_failures=10,
        consecutive_successes=0,
        consecutive_failures=10,
        country_code="FR",
    )

    proxy5 = Proxy(
        id=uuid4(),
        url="http://proxy5.example.com:8080",
        protocol="http",
        health_status=HealthStatus.UNKNOWN,
        source=ProxySource.USER,
        total_requests=0,
        total_successes=0,
        total_failures=0,
    )

    pool = ProxyPool(name="test_pool", proxies=[proxy1, proxy2, proxy3, proxy4, proxy5])

    rotator = AsyncProxyRotator()
    rotator.pool = pool

    # Add circuit breakers for some proxies
    rotator.circuit_breakers[str(proxy1.id)] = CircuitBreaker(
        proxy_id=str(proxy1.id),
        failure_threshold=5,
        window_duration=60.0,
        timeout_duration=30.0,
    )

    return rotator


@pytest.fixture(autouse=True)
async def setup_test_rotator(mock_rotator):
    """Setup mock rotator for all tests."""
    await set_rotator(mock_rotator)
    # Reset auth to default (no authentication required)
    set_auth(MCPAuth())
    yield
    # Reset to None after test
    await set_rotator(None)
    set_auth(None)


class TestProxyWhirlMCPServer:
    """Test ProxyWhirlMCPServer class."""

    def test_init_without_proxy_manager(self) -> None:
        """Test initialization without proxy manager."""
        server = ProxyWhirlMCPServer()
        assert server.proxy_manager is None

    async def test_init_with_proxy_manager(self, mock_rotator) -> None:
        """Test initialization with proxy manager."""
        server = ProxyWhirlMCPServer(proxy_manager=mock_rotator)
        assert server.proxy_manager == mock_rotator
        # Verify set_rotator was called
        assert await get_rotator() is not None

    @patch("proxywhirl.mcp.server.mcp")
    def test_run_with_stdio_transport(self, mock_mcp) -> None:
        """Test running server with stdio transport."""
        server = ProxyWhirlMCPServer()
        server.run(transport="stdio")
        mock_mcp.run.assert_called_once_with(transport="stdio")

    @patch("proxywhirl.mcp.server.mcp")
    def test_run_with_sse_transport(self, mock_mcp) -> None:
        """Test running server with SSE transport."""
        server = ProxyWhirlMCPServer()
        server.run(transport="sse")
        mock_mcp.run.assert_called_once_with(transport="sse")


class TestGetSetRotator:
    """Test get_rotator and set_rotator functions."""

    async def test_get_rotator_creates_new_instance(self) -> None:
        """Test that get_rotator creates a new instance when none exists."""
        # Clear the global rotator
        await set_rotator(None)

        # Get rotator should create a new instance
        rotator = await get_rotator()
        assert rotator is not None
        assert isinstance(rotator, AsyncProxyRotator)

    async def test_get_rotator_returns_existing_instance(self, mock_rotator) -> None:
        """Test that get_rotator returns the existing instance."""
        await set_rotator(mock_rotator)
        rotator = await get_rotator()
        assert rotator is mock_rotator

    async def test_set_rotator_updates_global_instance(self, mock_rotator) -> None:
        """Test that set_rotator updates the global instance."""
        await set_rotator(mock_rotator)
        assert await get_rotator() is mock_rotator


class TestGetSetAuth:
    """Test get_auth and set_auth functions."""

    def test_get_auth_creates_new_instance(self) -> None:
        """Test that get_auth creates a new instance when none exists."""
        # Clear the global auth
        set_auth(None)

        # Get auth should create a new instance
        auth = get_auth()
        assert auth is not None
        assert isinstance(auth, MCPAuth)
        assert auth.api_key is None  # Default: no auth required

    def test_get_auth_returns_existing_instance(self) -> None:
        """Test that get_auth returns the existing instance."""
        test_auth = MCPAuth(api_key="test-key")
        set_auth(test_auth)
        auth = get_auth()
        assert auth is test_auth

    def test_set_auth_updates_global_instance(self) -> None:
        """Test that set_auth updates the global instance."""
        test_auth = MCPAuth(api_key="test-key")
        set_auth(test_auth)
        assert get_auth() is test_auth

    def test_set_auth_to_none(self) -> None:
        """Test that set_auth can disable authentication."""
        set_auth(None)
        # Next get_auth should create a new default instance
        auth = get_auth()
        assert auth.api_key is None


class TestListProxiesTool:
    """Test list_proxies tool."""

    async def test_list_proxies_returns_all_proxies(self, mock_rotator) -> None:
        """Test list_proxies returns all proxies with correct structure."""
        result = await list_proxies()

        assert "proxies" in result
        assert "total" in result
        assert "healthy" in result
        assert "degraded" in result
        assert "unhealthy" in result
        assert "dead" in result
        assert "unknown" in result

        assert isinstance(result["proxies"], list)
        assert len(result["proxies"]) == 5
        assert result["total"] == 5
        assert result["healthy"] == 1
        assert result["degraded"] == 1
        assert result["unhealthy"] == 1
        assert result["dead"] == 1
        assert result["unknown"] == 1

    async def test_list_proxies_proxy_structure(self, mock_rotator) -> None:
        """Test that each proxy in list has correct structure."""
        result = await list_proxies()

        proxy = result["proxies"][0]
        assert "id" in proxy
        assert "url" in proxy
        assert "status" in proxy
        assert "success_rate" in proxy
        assert "avg_latency_ms" in proxy
        assert "region" in proxy
        assert "total_requests" in proxy
        assert "total_successes" in proxy
        assert "total_failures" in proxy

    async def test_list_proxies_empty_pool(self) -> None:
        """Test list_proxies with empty pool."""
        empty_rotator = AsyncProxyRotator()
        empty_rotator.pool = ProxyPool(name="empty_pool", proxies=[])
        await set_rotator(empty_rotator)

        result = await list_proxies()

        assert result["proxies"] == []
        assert result["total"] == 0
        assert result["healthy"] == 0


class TestRotateProxyTool:
    """Test rotate_proxy tool."""

    async def test_rotate_proxy_success(self, mock_rotator) -> None:
        """Test successful proxy rotation."""
        result = await rotate_proxy()

        assert "proxy" in result
        assert "id" in result["proxy"]
        assert "url" in result["proxy"]
        assert "status" in result["proxy"]
        assert "success_rate" in result["proxy"]
        assert "avg_latency_ms" in result["proxy"]
        assert "region" in result["proxy"]

    async def test_rotate_proxy_empty_pool(self) -> None:
        """Test rotate_proxy with empty pool."""
        empty_rotator = AsyncProxyRotator()
        empty_rotator.pool = ProxyPool(name="empty_pool", proxies=[])
        await set_rotator(empty_rotator)

        result = await rotate_proxy()

        assert "error" in result

    async def test_rotate_proxy_exception_handling(self, mock_rotator) -> None:
        """Test rotate_proxy handles exceptions."""
        # Mock strategy to raise an exception
        mock_rotator.strategy.select = MagicMock(side_effect=Exception("Selection failed"))

        result = await rotate_proxy()

        assert "error" in result
        assert "Failed to select proxy" in result["error"]


class TestProxyStatusTool:
    """Test proxy_status tool."""

    async def test_proxy_status_valid_id(self, mock_rotator) -> None:
        """Test proxy_status with valid proxy ID."""
        proxy_id = str(mock_rotator.pool.proxies[0].id)
        result = await proxy_status(proxy_id)

        assert result["proxy_id"] == proxy_id
        assert "url" in result
        assert "status" in result
        assert "metrics" in result
        assert "health" in result
        assert "region" in result
        assert "protocol" in result

        # Check metrics structure
        metrics = result["metrics"]
        assert "success_rate" in metrics
        assert "avg_latency_ms" in metrics
        assert "total_requests" in metrics
        assert "successful_requests" in metrics
        assert "failed_requests" in metrics

        # Check health structure
        health = result["health"]
        assert "last_check" in health
        assert "last_success" in health
        assert "last_failure" in health
        assert "circuit_breaker" in health
        assert "consecutive_failures" in health
        assert "consecutive_successes" in health

    async def test_proxy_status_empty_id(self) -> None:
        """Test proxy_status with empty ID."""
        result = await proxy_status("")

        assert "error" in result
        assert result["error"] == "proxy_id is required"

    async def test_proxy_status_invalid_uuid_format(self) -> None:
        """Test proxy_status with invalid UUID format."""
        result = await proxy_status("not-a-valid-uuid")

        assert "error" in result
        assert "Invalid proxy_id format" in result["error"]

    async def test_proxy_status_nonexistent_proxy(self, mock_rotator) -> None:
        """Test proxy_status with non-existent proxy ID."""
        fake_id = str(uuid4())
        result = await proxy_status(fake_id)

        assert "error" in result
        assert f"Proxy not found: {fake_id}" in result["error"]

    async def test_proxy_status_with_circuit_breaker(self, mock_rotator) -> None:
        """Test proxy_status includes circuit breaker state."""
        proxy_id = str(mock_rotator.pool.proxies[0].id)
        result = await proxy_status(proxy_id)

        assert result["health"]["circuit_breaker"] in ["closed", "open", "half_open"]

    async def test_proxy_status_without_circuit_breaker(self, mock_rotator) -> None:
        """Test proxy_status when no circuit breaker exists."""
        proxy_id = str(mock_rotator.pool.proxies[1].id)
        result = await proxy_status(proxy_id)

        assert result["health"]["circuit_breaker"] == "unknown"


class TestRecommendProxyTool:
    """Test recommend_proxy tool."""

    async def test_recommend_proxy_no_criteria(self, mock_rotator) -> None:
        """Test recommend_proxy without criteria."""
        result = await recommend_proxy()

        assert "recommendation" in result
        rec = result["recommendation"]
        assert "id" in rec
        assert "url" in rec
        assert "score" in rec
        assert "reason" in rec
        assert "metrics" in rec
        assert "alternatives" in rec

    async def test_recommend_proxy_high_performance(self, mock_rotator) -> None:
        """Test recommend_proxy with high performance."""
        result = await recommend_proxy(performance="high")

        assert "recommendation" in result
        assert "high" in result["recommendation"]["reason"]
        assert result["recommendation"]["metrics"]["performance_tier"] == "high"

    async def test_recommend_proxy_medium_performance(self, mock_rotator) -> None:
        """Test recommend_proxy with medium performance."""
        result = await recommend_proxy(performance="medium")

        assert "recommendation" in result
        assert result["recommendation"]["metrics"]["performance_tier"] == "medium"

    async def test_recommend_proxy_low_performance(self, mock_rotator) -> None:
        """Test recommend_proxy with low performance."""
        result = await recommend_proxy(performance="low")

        assert "recommendation" in result
        assert result["recommendation"]["metrics"]["performance_tier"] == "low"

    async def test_recommend_proxy_invalid_performance(self) -> None:
        """Test recommend_proxy with invalid performance level."""
        result = await recommend_proxy(performance="ultra")

        assert "error" in result
        assert "Invalid performance level" in result["error"]

    async def test_recommend_proxy_with_region(self, mock_rotator) -> None:
        """Test recommend_proxy with region filter."""
        result = await recommend_proxy(region="US")

        assert "recommendation" in result
        # Should recommend proxy1 or proxy3 (both US)
        assert result["recommendation"]["metrics"]["region"] == "US"

    async def test_recommend_proxy_invalid_region(self, mock_rotator) -> None:
        """Test recommend_proxy with region that has no proxies."""
        result = await recommend_proxy(region="INVALID-REGION")

        assert "error" in result
        assert "No proxies found for region" in result["error"]

    async def test_recommend_proxy_empty_pool(self) -> None:
        """Test recommend_proxy with empty pool."""
        empty_rotator = AsyncProxyRotator()
        empty_rotator.pool = ProxyPool(name="empty_pool", proxies=[])
        await set_rotator(empty_rotator)

        result = await recommend_proxy()

        assert "error" in result
        assert "No proxies available" in result["error"]

    async def test_recommend_proxy_includes_alternatives(self, mock_rotator) -> None:
        """Test that recommendations include alternatives."""
        result = await recommend_proxy()

        assert "recommendation" in result
        assert "alternatives" in result["recommendation"]
        alternatives = result["recommendation"]["alternatives"]

        # Should have up to 3 alternatives
        assert isinstance(alternatives, list)
        for alt in alternatives:
            assert "id" in alt
            assert "url" in alt
            assert "score" in alt
            assert "reason" in alt

    async def test_recommend_proxy_score_calculation(self, mock_rotator) -> None:
        """Test that score is calculated and in valid range."""
        result = await recommend_proxy()

        score = result["recommendation"]["score"]
        assert isinstance(score, (int, float))
        assert 0.0 <= score <= 1.0


class TestGetRateLimitStatusTool:
    """Test get_rate_limit_status tool."""

    async def test_get_rate_limit_status_valid_id(self, mock_rotator) -> None:
        """Test get_rate_limit_status with valid proxy ID."""
        proxy_id = str(mock_rotator.pool.proxies[0].id)
        result = await get_rate_limit_status(proxy_id)

        assert result["proxy_id"] == proxy_id
        assert "rate_limit" in result
        assert "enabled" in result["rate_limit"]
        assert "note" in result

    async def test_get_rate_limit_status_invalid_uuid(self) -> None:
        """Test get_rate_limit_status with invalid UUID format."""
        result = await get_rate_limit_status("not-a-uuid")

        assert "error" in result
        assert "Invalid proxy_id format" in result["error"]

    async def test_get_rate_limit_status_nonexistent_proxy(self, mock_rotator) -> None:
        """Test get_rate_limit_status with non-existent proxy."""
        fake_id = str(uuid4())
        result = await get_rate_limit_status(fake_id)

        assert "error" in result
        assert f"Proxy not found: {fake_id}" in result["error"]

    async def test_get_rate_limit_status_structure(self, mock_rotator) -> None:
        """Test rate limit status response structure."""
        proxy_id = str(mock_rotator.pool.proxies[0].id)
        result = await get_rate_limit_status(proxy_id)

        rate_limit = result["rate_limit"]
        assert "enabled" in rate_limit
        assert "message" in rate_limit
        assert "max_requests" in rate_limit
        assert "time_window_seconds" in rate_limit
        assert "current_usage" in rate_limit
        assert "remaining" in rate_limit


class TestGetProxyHealthResource:
    """Test get_proxy_health resource."""

    async def test_get_proxy_health_structure(self, mock_rotator) -> None:
        """Test get_proxy_health returns valid JSON with correct structure."""
        result = await get_proxy_health()
        data = json.loads(result)

        assert "pool_status" in data
        assert "total_proxies" in data
        assert "healthy_proxies" in data
        assert "degraded_proxies" in data
        assert "failed_proxies" in data
        assert "average_success_rate" in data
        assert "average_latency_ms" in data
        assert "last_update" in data
        assert "total_requests" in data
        assert "total_successes" in data
        assert "total_failures" in data

    async def test_get_proxy_health_pool_status_healthy(self, mock_rotator) -> None:
        """Test pool status is calculated correctly for healthy pool."""
        # Create a mostly healthy pool
        healthy_proxies = [
            Proxy(
                id=uuid4(),
                url=f"http://proxy{i}.example.com:8080",
                protocol="http",
                health_status=HealthStatus.HEALTHY,
                source=ProxySource.USER,
            )
            for i in range(10)
        ]
        mock_rotator.pool = ProxyPool(name="healthy_pool", proxies=healthy_proxies)

        result = await get_proxy_health()
        data = json.loads(result)

        assert data["pool_status"] == "healthy"

    async def test_get_proxy_health_pool_status_degraded(self, mock_rotator) -> None:
        """Test pool status is calculated correctly for degraded pool."""
        # Create a degraded pool (30-70% healthy)
        proxies = [
            Proxy(
                id=uuid4(),
                url=f"http://proxy{i}.example.com:8080",
                protocol="http",
                health_status=HealthStatus.HEALTHY if i < 5 else HealthStatus.UNHEALTHY,
                source=ProxySource.USER,
            )
            for i in range(10)
        ]
        mock_rotator.pool = ProxyPool(name="degraded_pool", proxies=proxies)

        result = await get_proxy_health()
        data = json.loads(result)

        assert data["pool_status"] == "degraded"

    async def test_get_proxy_health_pool_status_critical(self, mock_rotator) -> None:
        """Test pool status is calculated correctly for critical pool."""
        # Create a critical pool (< 30% healthy)
        proxies = [
            Proxy(
                id=uuid4(),
                url=f"http://proxy{i}.example.com:8080",
                protocol="http",
                health_status=HealthStatus.HEALTHY if i < 2 else HealthStatus.UNHEALTHY,
                source=ProxySource.USER,
            )
            for i in range(10)
        ]
        mock_rotator.pool = ProxyPool(name="critical_pool", proxies=proxies)

        result = await get_proxy_health()
        data = json.loads(result)

        assert data["pool_status"] == "critical"

    async def test_get_proxy_health_pool_status_empty(self) -> None:
        """Test pool status is empty when no proxies."""
        empty_rotator = AsyncProxyRotator()
        empty_rotator.pool = ProxyPool(name="empty_pool", proxies=[])
        await set_rotator(empty_rotator)

        result = await get_proxy_health()
        data = json.loads(result)

        assert data["pool_status"] == "empty"

    async def test_get_proxy_health_average_latency(self, mock_rotator) -> None:
        """Test average latency calculation."""
        result = await get_proxy_health()
        data = json.loads(result)

        assert "average_latency_ms" in data
        assert isinstance(data["average_latency_ms"], (int, float))
        assert data["average_latency_ms"] >= 0


class TestGetProxyConfigResource:
    """Test get_proxy_config resource."""

    async def test_get_proxy_config_structure(self, mock_rotator) -> None:
        """Test get_proxy_config returns valid JSON with correct structure."""
        result = await get_proxy_config()
        data = json.loads(result)

        assert "rotation_strategy" in data
        assert "timeout" in data
        assert "verify_ssl" in data
        assert "follow_redirects" in data
        assert "pool_connections" in data
        assert "pool_max_keepalive" in data
        assert "circuit_breaker" in data
        assert "retry_policy" in data
        assert "logging" in data

    async def test_get_proxy_config_circuit_breaker(self, mock_rotator) -> None:
        """Test circuit breaker config is included."""
        result = await get_proxy_config()
        data = json.loads(result)

        cb_config = data["circuit_breaker"]
        assert "failure_threshold" in cb_config
        assert "timeout_duration" in cb_config
        assert "window_duration" in cb_config

    async def test_get_proxy_config_retry_policy(self, mock_rotator) -> None:
        """Test retry policy config is included."""
        result = await get_proxy_config()
        data = json.loads(result)

        retry_config = data["retry_policy"]
        assert "max_attempts" in retry_config
        assert "backoff_strategy" in retry_config
        assert "base_delay" in retry_config
        assert "max_backoff_delay" in retry_config
        assert "multiplier" in retry_config

    async def test_get_proxy_config_logging(self, mock_rotator) -> None:
        """Test logging config is included."""
        result = await get_proxy_config()
        data = json.loads(result)

        logging_config = data["logging"]
        assert "level" in logging_config
        assert "format" in logging_config
        assert "redact_credentials" in logging_config

    async def test_get_proxy_config_no_circuit_breakers(self) -> None:
        """Test config when no circuit breakers exist."""
        rotator = AsyncProxyRotator()
        rotator.circuit_breakers = {}
        await set_rotator(rotator)

        result = await get_proxy_config()
        data = json.loads(result)

        # Should still have circuit_breaker field but it should be empty
        assert "circuit_breaker" in data
        assert data["circuit_breaker"] == {}


class TestToolAuthentication:
    """Test authentication for MCP tools."""

    async def test_list_proxies_with_valid_auth(self, mock_rotator) -> None:
        """Test list_proxies succeeds with valid API key."""
        # Set up authentication
        set_auth(MCPAuth(api_key="valid-key"))

        result = await list_proxies(api_key="valid-key")

        assert "proxies" in result
        assert "error" not in result

    async def test_list_proxies_with_invalid_auth(self, mock_rotator) -> None:
        """Test list_proxies fails with invalid API key."""
        # Set up authentication
        set_auth(MCPAuth(api_key="valid-key"))

        result = await list_proxies(api_key="invalid-key")

        assert "error" in result
        assert "Authentication failed" in result["error"]

    async def test_list_proxies_without_auth_when_required(self, mock_rotator) -> None:
        """Test list_proxies fails when auth is required but not provided."""
        # Set up authentication
        set_auth(MCPAuth(api_key="valid-key"))

        result = await list_proxies()

        assert "error" in result
        assert "Authentication failed" in result["error"]

    async def test_list_proxies_without_auth_when_not_required(self, mock_rotator) -> None:
        """Test list_proxies succeeds when no auth is required."""
        # Set up no authentication
        set_auth(MCPAuth())

        result = await list_proxies()

        assert "proxies" in result
        assert "error" not in result

    async def test_rotate_proxy_with_valid_auth(self, mock_rotator) -> None:
        """Test rotate_proxy succeeds with valid API key."""
        set_auth(MCPAuth(api_key="valid-key"))

        result = await rotate_proxy(api_key="valid-key")

        assert "proxy" in result
        assert "error" not in result

    async def test_rotate_proxy_with_invalid_auth(self, mock_rotator) -> None:
        """Test rotate_proxy fails with invalid API key."""
        set_auth(MCPAuth(api_key="valid-key"))

        result = await rotate_proxy(api_key="invalid-key")

        assert "error" in result
        assert "Authentication failed" in result["error"]

    async def test_proxy_status_with_valid_auth(self, mock_rotator) -> None:
        """Test proxy_status succeeds with valid API key."""
        set_auth(MCPAuth(api_key="valid-key"))
        proxy_id = str(mock_rotator.pool.proxies[0].id)

        result = await proxy_status(proxy_id, api_key="valid-key")

        assert "proxy_id" in result
        assert "error" not in result or "Authentication" not in result.get("error", "")

    async def test_proxy_status_with_invalid_auth(self, mock_rotator) -> None:
        """Test proxy_status fails with invalid API key."""
        set_auth(MCPAuth(api_key="valid-key"))
        proxy_id = str(mock_rotator.pool.proxies[0].id)

        result = await proxy_status(proxy_id, api_key="invalid-key")

        assert "error" in result
        assert "Authentication failed" in result["error"]

    async def test_recommend_proxy_with_valid_auth(self, mock_rotator) -> None:
        """Test recommend_proxy succeeds with valid API key."""
        set_auth(MCPAuth(api_key="valid-key"))

        result = await recommend_proxy(api_key="valid-key")

        assert "recommendation" in result
        assert "error" not in result

    async def test_recommend_proxy_with_invalid_auth(self, mock_rotator) -> None:
        """Test recommend_proxy fails with invalid API key."""
        set_auth(MCPAuth(api_key="valid-key"))

        result = await recommend_proxy(api_key="invalid-key")

        assert "error" in result
        assert "Authentication failed" in result["error"]

    async def test_get_rate_limit_status_with_valid_auth(self, mock_rotator) -> None:
        """Test get_rate_limit_status succeeds with valid API key."""
        set_auth(MCPAuth(api_key="valid-key"))
        proxy_id = str(mock_rotator.pool.proxies[0].id)

        result = await get_rate_limit_status(proxy_id, api_key="valid-key")

        assert "proxy_id" in result
        assert "error" not in result or "Authentication" not in result.get("error", "")

    async def test_get_rate_limit_status_with_invalid_auth(self, mock_rotator) -> None:
        """Test get_rate_limit_status fails with invalid API key."""
        set_auth(MCPAuth(api_key="valid-key"))
        proxy_id = str(mock_rotator.pool.proxies[0].id)

        result = await get_rate_limit_status(proxy_id, api_key="invalid-key")

        assert "error" in result
        assert "Authentication failed" in result["error"]

    async def test_auth_bypass_with_no_api_key_configured(self, mock_rotator) -> None:
        """Test that when no API key is configured, all requests pass."""
        set_auth(MCPAuth())  # No API key

        # All these should succeed
        result1 = await list_proxies()
        result2 = await rotate_proxy()
        result3 = await recommend_proxy()

        assert "error" not in result1
        assert "error" not in result2
        assert "error" not in result3


class TestConcurrentRotatorAccess:
    """Test thread-safe concurrent access to global rotator."""

    async def test_concurrent_get_rotator_initialization(self) -> None:
        """Test that concurrent calls to get_rotator are thread-safe."""
        # Reset rotator to force initialization
        await set_rotator(None)

        # Create multiple concurrent tasks trying to initialize the rotator
        tasks = [get_rotator() for _ in range(20)]
        rotators = await asyncio.gather(*tasks)

        # All tasks should get the same instance (no race condition)
        first_rotator = rotators[0]
        for rotator in rotators:
            assert (
                rotator is first_rotator
            ), "Race condition detected: multiple rotator instances created"

    async def test_concurrent_set_get_rotator(self, mock_rotator) -> None:
        """Test concurrent set and get operations are properly synchronized."""
        # Reset to None first
        await set_rotator(None)

        # Set the mock rotator
        await set_rotator(mock_rotator)

        # Multiple concurrent gets should all return the same instance
        tasks = [get_rotator() for _ in range(10)]
        rotators = await asyncio.gather(*tasks)

        for rotator in rotators:
            assert rotator is mock_rotator

    async def test_set_rotator_is_thread_safe(self) -> None:
        """Test that set_rotator properly synchronizes writes."""
        rotator1 = AsyncProxyRotator()
        rotator2 = AsyncProxyRotator()

        # Try to set different rotators concurrently
        # The last one should win, but no corruption should occur
        await asyncio.gather(
            set_rotator(rotator1),
            set_rotator(rotator2),
        )

        # Should get one of them consistently (no mixed state)
        result = await get_rotator()
        assert result in (rotator1, rotator2)


class TestUnifiedProxywhirlTool:
    """Test the unified proxywhirl(action=...) tool.

    Note: We use _proxywhirl_tool (the internal async function) for testing
    because when FastMCP is available, `proxywhirl` is wrapped as a FunctionTool
    that is not directly callable in tests.
    """

    async def test_proxywhirl_list_action(self, mock_rotator) -> None:
        """Test proxywhirl(action='list') returns all proxies."""
        result = await _proxywhirl_tool(action="list")

        assert "proxies" in result
        assert "total" in result
        assert isinstance(result["proxies"], list)
        assert len(result["proxies"]) == 5
        assert result["total"] == 5

    async def test_proxywhirl_rotate_action(self, mock_rotator) -> None:
        """Test proxywhirl(action='rotate') returns a proxy."""
        result = await _proxywhirl_tool(action="rotate")

        assert "proxy" in result
        assert "id" in result["proxy"]
        assert "url" in result["proxy"]
        assert "status" in result["proxy"]

    async def test_proxywhirl_status_action(self, mock_rotator) -> None:
        """Test proxywhirl(action='status', proxy_id=...) returns proxy details."""
        proxy_id = str(mock_rotator.pool.proxies[0].id)
        result = await _proxywhirl_tool(action="status", proxy_id=proxy_id)

        assert result["proxy_id"] == proxy_id
        assert "url" in result
        assert "status" in result
        assert "metrics" in result
        assert "health" in result

    async def test_proxywhirl_status_requires_proxy_id(self) -> None:
        """Test that status action requires proxy_id."""
        result = await _proxywhirl_tool(action="status")

        assert "error" in result
        assert "proxy_id required" in result["error"]
        assert result["code"] == 400

    async def test_proxywhirl_recommend_action(self, mock_rotator) -> None:
        """Test proxywhirl(action='recommend') returns a recommendation."""
        result = await _proxywhirl_tool(action="recommend")

        assert "recommendation" in result
        assert "id" in result["recommendation"]
        assert "url" in result["recommendation"]
        assert "score" in result["recommendation"]

    async def test_proxywhirl_recommend_with_criteria(self, mock_rotator) -> None:
        """Test proxywhirl(action='recommend', criteria={...}) filters correctly."""
        result = await _proxywhirl_tool(
            action="recommend", criteria={"region": "US", "performance": "high"}
        )

        assert "recommendation" in result
        assert result["recommendation"]["metrics"]["region"] == "US"
        assert result["recommendation"]["metrics"]["performance_tier"] == "high"

    async def test_proxywhirl_health_action(self, mock_rotator) -> None:
        """Test proxywhirl(action='health') returns pool health."""
        result = await _proxywhirl_tool(action="health")

        assert "pool_status" in result
        assert "total_proxies" in result
        assert "healthy_proxies" in result
        assert "average_success_rate" in result

    async def test_proxywhirl_reset_cb_action(self, mock_rotator) -> None:
        """Test proxywhirl(action='reset_cb', proxy_id=...) resets circuit breaker."""
        proxy_id = str(mock_rotator.pool.proxies[0].id)
        result = await _proxywhirl_tool(action="reset_cb", proxy_id=proxy_id)

        assert result["success"] is True
        assert result["proxy_id"] == proxy_id
        assert result["new_state"] == "closed"

    async def test_proxywhirl_reset_cb_requires_proxy_id(self) -> None:
        """Test that reset_cb action requires proxy_id."""
        result = await _proxywhirl_tool(action="reset_cb")

        assert "error" in result
        assert "proxy_id required" in result["error"]
        assert result["code"] == 400

    async def test_proxywhirl_unknown_action(self) -> None:
        """Test that unknown action returns error."""
        # Note: Due to Literal type, we need to use the internal function
        # to test with an invalid action
        result = await _proxywhirl_tool(action="invalid")  # type: ignore[arg-type]

        assert "error" in result
        assert "Unknown action" in result["error"]
        assert result["code"] == 400

    async def test_proxywhirl_with_api_key(self, mock_rotator) -> None:
        """Test proxywhirl passes api_key correctly to underlying implementations."""
        set_auth(MCPAuth(api_key="test-key"))

        # Without API key should fail
        result = await _proxywhirl_tool(action="list")
        assert "error" in result
        assert "Authentication failed" in result["error"]

        # With correct API key should succeed
        result = await _proxywhirl_tool(action="list", api_key="test-key")
        assert "proxies" in result
        assert "error" not in result

    async def test_proxywhirl_reset_cb_no_circuit_breaker(self, mock_rotator) -> None:
        """Test reset_cb when no circuit breaker exists for proxy."""
        # proxy2 does not have a circuit breaker
        proxy_id = str(mock_rotator.pool.proxies[1].id)
        result = await _proxywhirl_tool(action="reset_cb", proxy_id=proxy_id)

        assert "error" in result
        assert "No circuit breaker found" in result["error"]


class TestCleanupRotator:
    """Test cleanup_rotator function."""

    async def test_cleanup_rotator_clears_global(self, mock_rotator) -> None:
        """Test cleanup_rotator clears the global rotator."""
        # Verify rotator exists
        rotator = await get_rotator()
        assert rotator is not None

        # Clean it up
        await cleanup_rotator()

        # Import module to check global state directly
        from proxywhirl.mcp import server as mcp_server

        assert mcp_server._rotator is None

    async def test_cleanup_rotator_safe_when_none(self) -> None:
        """Test cleanup_rotator is safe to call when no rotator exists."""
        # Set rotator to None first
        await set_rotator(None)

        # This should not raise
        await cleanup_rotator()

        from proxywhirl.mcp import server as mcp_server

        assert mcp_server._rotator is None

    async def test_cleanup_rotator_multiple_calls(self, mock_rotator) -> None:
        """Test cleanup_rotator can be called multiple times safely."""
        await cleanup_rotator()
        await cleanup_rotator()
        await cleanup_rotator()

        from proxywhirl.mcp import server as mcp_server

        assert mcp_server._rotator is None

    async def test_get_rotator_after_cleanup(self) -> None:
        """Test get_rotator creates new instance after cleanup."""
        # Clean up first
        await cleanup_rotator()

        # Get rotator should create a new instance
        rotator = await get_rotator()
        assert rotator is not None
        assert isinstance(rotator, AsyncProxyRotator)


class TestMCPLifespan:
    """Test mcp_lifespan context manager."""

    async def test_mcp_lifespan_cleans_up(self, mock_rotator) -> None:
        """Test that mcp_lifespan cleans up rotator on exit."""
        from proxywhirl.mcp.server import mcp_lifespan

        async with mcp_lifespan():
            # Rotator should be accessible during lifespan
            rotator = await get_rotator()
            assert rotator is not None

        # After context exit, rotator should be cleaned up
        from proxywhirl.mcp import server as mcp_server

        assert mcp_server._rotator is None


class TestAutoLoadFromDatabase:
    """Test auto-load from database functionality."""

    async def test_get_rotator_creates_instance_without_db(self, tmp_path, monkeypatch) -> None:
        """Test get_rotator creates instance when no database exists."""
        import os
        from unittest.mock import AsyncMock, patch

        # Clear the global rotator first
        await cleanup_rotator()

        # Change to a temporary directory where no proxywhirl.db exists
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            # Mock auto-fetch to prevent network calls during test
            with patch("proxywhirl.mcp.server._auto_fetch_proxies", new_callable=AsyncMock):
                rotator = await get_rotator()

                assert rotator is not None
                assert isinstance(rotator, AsyncProxyRotator)
                # Pool should be empty since no DB exists and auto-fetch is mocked
                assert rotator.pool.size == 0
        finally:
            os.chdir(original_cwd)
            await cleanup_rotator()

    async def test_get_rotator_auto_loads_when_db_exists(self, tmp_path, monkeypatch) -> None:
        """Test get_rotator auto-loads proxies when proxywhirl.db exists."""
        import os

        # Clear the global rotator first
        await cleanup_rotator()

        # Create a test database in tmp_path
        db_path = tmp_path / "proxywhirl.db"

        # Create a real SQLiteStorage and add a proxy
        from proxywhirl.storage import SQLiteStorage

        storage = SQLiteStorage(str(db_path))
        await storage.initialize()

        test_proxy = Proxy(
            id=uuid4(),
            url="http://test-db-proxy.example.com:8080",
            protocol="http",
            health_status=HealthStatus.HEALTHY,
            source=ProxySource.USER,
            country_code="US",
        )
        await storage.save([test_proxy])
        await storage.close()

        # Change to tmp_path where our test DB exists
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            rotator = await get_rotator()

            assert rotator is not None
            assert isinstance(rotator, AsyncProxyRotator)
            # Pool should have the proxy we saved
            assert rotator.pool.size == 1
            loaded_proxies = rotator.pool.get_all_proxies()
            assert len(loaded_proxies) == 1
            assert str(loaded_proxies[0].url) == "http://test-db-proxy.example.com:8080"
        finally:
            os.chdir(original_cwd)
            await cleanup_rotator()

    async def test_get_rotator_handles_db_error_gracefully(self, tmp_path, monkeypatch) -> None:
        """Test get_rotator handles database errors gracefully."""
        import os

        # Clear the global rotator first
        await cleanup_rotator()

        # Create an invalid/corrupted database file
        db_path = tmp_path / "proxywhirl.db"
        db_path.write_text("this is not a valid sqlite database")

        # Change to tmp_path where our corrupted DB exists
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            # Should not raise, should handle gracefully and return empty pool
            rotator = await get_rotator()

            assert rotator is not None
            assert isinstance(rotator, AsyncProxyRotator)
        finally:
            os.chdir(original_cwd)
            await cleanup_rotator()


class TestPythonVersionCheck:
    """Test Python version checking for MCP server."""

    def test_check_python_version_passes_on_310_plus(self) -> None:
        """Test that _check_python_version passes on Python 3.10+."""
        import sys

        from proxywhirl.mcp.server import _check_python_version

        # Only run this test if we're actually on Python 3.10+
        if sys.version_info >= (3, 10):
            # Should not raise
            _check_python_version()

    def test_check_python_version_raises_on_older(self) -> None:
        """Test that _check_python_version raises on Python < 3.10."""
        import sys
        from collections import namedtuple

        from proxywhirl.mcp.server import _check_python_version

        # Create a proper version_info-like named tuple
        VersionInfo = namedtuple(
            "version_info", ["major", "minor", "micro", "releaselevel", "serial"]
        )
        mock_version = VersionInfo(3, 9, 0, "final", 0)

        # Mock version_info to be 3.9
        with (
            patch.object(sys, "version_info", mock_version),
            pytest.raises(RuntimeError) as exc_info,
        ):
            _check_python_version()

        assert "Python 3.10 or higher" in str(exc_info.value)
        assert "3.9" in str(exc_info.value)
