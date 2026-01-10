"""MCP Server implementation for ProxyWhirl.

Production-ready MCP server with unified tool interface, auto-loading from database,
proper lifecycle management, and Python version checks.
"""

from __future__ import annotations

import asyncio
import sys
from contextlib import asynccontextmanager
from typing import Any, Literal

from loguru import logger

from proxywhirl.async_client import AsyncProxyRotator
from proxywhirl.mcp.auth import MCPAuth
from proxywhirl.models import HealthStatus


def _check_python_version() -> None:
    """Check that Python version is 3.10+ for MCP server functionality.

    Raises:
        RuntimeError: If Python version is below 3.10
    """
    if sys.version_info < (3, 10):
        raise RuntimeError(
            f"MCP server requires Python 3.10 or higher. "
            f"Current version: {sys.version_info.major}.{sys.version_info.minor}. "
            f"Please upgrade Python or use proxywhirl without MCP functionality."
        )


# Import FastMCP with graceful fallback and Python version check
try:
    _check_python_version()
    from fastmcp import FastMCP

    mcp = FastMCP("ProxyWhirl")
except RuntimeError as e:
    logger.warning(str(e))
    mcp = None  # type: ignore[assignment]
except ImportError:
    logger.warning(
        "FastMCP is not installed. MCP server functionality will be limited. "
        "Install with: pip install fastmcp (Python 3.10+ required)"
    )
    mcp = None  # type: ignore[assignment]

# Global AsyncProxyRotator instance for MCP server
# This will be lazily initialized on first use (thread-safe)
_rotator_lock = asyncio.Lock()
_rotator: AsyncProxyRotator | None = None

# Global MCPAuth instance for authentication
# This can be configured via set_auth() or will use default (no auth)
_auth: MCPAuth | None = None


async def get_rotator() -> AsyncProxyRotator:
    """Get or create the global AsyncProxyRotator instance with auto-loading.

    On first initialization:
    1. If proxywhirl.db exists, loads proxies from it
    2. If pool is still empty, auto-fetches proxies from public sources

    Returns:
        AsyncProxyRotator instance
    """
    global _rotator
    async with _rotator_lock:
        if _rotator is None:
            _rotator = AsyncProxyRotator()

            # Auto-load from database if it exists
            from pathlib import Path

            db_path = Path("proxywhirl.db")
            if db_path.exists():
                try:
                    from proxywhirl.storage import SQLiteStorage

                    storage = SQLiteStorage(str(db_path))
                    await storage.initialize()
                    proxies = await storage.load()
                    for proxy in proxies:
                        await _rotator.add_proxy(proxy)
                    await storage.close()
                    logger.info(f"MCP: Auto-loaded {len(proxies)} proxies from {db_path}")
                except Exception as e:
                    logger.warning(f"MCP: Failed to auto-load proxies from {db_path}: {e}")

            # Auto-fetch if pool is still empty
            if _rotator.pool.size == 0:
                logger.info("MCP: Pool is empty, auto-fetching proxies from public sources...")
                await _auto_fetch_proxies(_rotator)

            logger.info(
                f"Initialized global AsyncProxyRotator for MCP server with {_rotator.pool.size} proxies"
            )

        return _rotator


async def _auto_fetch_proxies(rotator: AsyncProxyRotator, max_proxies: int = 100) -> None:
    """Auto-fetch proxies from public sources for cold start.

    Args:
        rotator: AsyncProxyRotator to populate
        max_proxies: Maximum number of proxies to fetch
    """
    from uuid import uuid4

    import httpx

    from proxywhirl.models import HealthStatus, Proxy, ProxySource

    # Public proxy list sources (reliable, no auth needed)
    sources = [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    ]

    fetched_count = 0
    async with httpx.AsyncClient(timeout=30) as client:
        for source_url in sources:
            if fetched_count >= max_proxies:
                break
            try:
                resp = await client.get(source_url)
                if resp.status_code == 200:
                    lines = resp.text.strip().split("\n")
                    for line in lines:
                        if fetched_count >= max_proxies:
                            break
                        line = line.strip()
                        if ":" in line and line:
                            # Parse IP:PORT format
                            try:
                                proxy = Proxy(
                                    id=uuid4(),
                                    url=f"http://{line}",
                                    protocol="http",
                                    source=ProxySource.FETCHED,
                                    health_status=HealthStatus.UNKNOWN,
                                )
                                await rotator.add_proxy(proxy)
                                fetched_count += 1
                            except Exception:
                                continue
                    logger.info(f"MCP: Fetched proxies from {source_url[:50]}...")
            except Exception as e:
                logger.warning(f"MCP: Failed to fetch from {source_url}: {e}")

    logger.info(f"MCP: Auto-fetched {fetched_count} proxies from public sources")


async def set_rotator(rotator: AsyncProxyRotator) -> None:
    """Set the global AsyncProxyRotator instance (thread-safe).

    Args:
        rotator: AsyncProxyRotator instance to use
    """
    global _rotator
    async with _rotator_lock:
        _rotator = rotator
        logger.info("Set custom AsyncProxyRotator for MCP server")


async def cleanup_rotator() -> None:
    """Clean up global rotator resources.

    Closes HTTP clients and releases all resources held by the rotator.
    Safe to call multiple times.
    """
    global _rotator
    async with _rotator_lock:
        if _rotator is not None:
            # Close all pooled clients
            await _rotator._close_all_clients()
            # Stop aggregation thread
            _rotator._stop_event.set()
            if _rotator._aggregation_thread and _rotator._aggregation_thread.is_alive():
                _rotator._aggregation_thread.join(timeout=5.0)
            _rotator = None
            logger.info("MCP: Cleaned up AsyncProxyRotator")


@asynccontextmanager
async def mcp_lifespan():
    """Lifespan context manager for MCP server.

    Handles startup and shutdown lifecycle for the MCP server,
    ensuring proper cleanup of resources on shutdown.

    Yields:
        None
    """
    logger.info("MCP server starting")
    try:
        yield
    finally:
        await cleanup_rotator()
        logger.info("MCP server shutdown complete")


def get_auth() -> MCPAuth:
    """Get or create the global MCPAuth instance.

    Returns:
        MCPAuth instance
    """
    global _auth
    if _auth is None:
        _auth = MCPAuth()
        logger.info("Initialized global MCPAuth for MCP server (no auth required)")
    return _auth


def set_auth(auth: MCPAuth | None) -> None:
    """Set the global MCPAuth instance.

    Args:
        auth: MCPAuth instance to use, or None to disable authentication
    """
    global _auth
    _auth = auth
    if auth is None:
        logger.info("Disabled authentication for MCP server")
    else:
        logger.info("Set custom MCPAuth for MCP server")


class ProxyWhirlMCPServer:
    """ProxyWhirl MCP Server using FastMCP.

    This server exposes proxy management functionality to AI assistants
    via the Model Context Protocol using FastMCP's decorator-based API.

    Example:
        ```python
        # Basic usage
        server = ProxyWhirlMCPServer()
        server.run()

        # With custom rotator
        rotator = AsyncProxyRotator()
        server = ProxyWhirlMCPServer(proxy_manager=rotator)
        await server.initialize()  # Must call for async setup
        server.run()
        ```
    """

    def __init__(self, proxy_manager: Any = None) -> None:
        """Initialize ProxyWhirl MCP server.

        Note: If providing a proxy_manager, you must call initialize() to set it up.

        Args:
            proxy_manager: ProxyWhirl proxy manager instance (AsyncProxyRotator)
        """
        self.proxy_manager = proxy_manager
        logger.info("ProxyWhirl MCP Server initialized")

    async def initialize(self) -> None:
        """Initialize the server asynchronously.

        Call this method after construction if you provided a custom proxy_manager.
        This properly sets up the rotator in an async context.
        """
        if self.proxy_manager is not None:
            await set_rotator(self.proxy_manager)
            logger.info("ProxyWhirl MCP Server async initialization complete")

    def run(self, transport: Literal["stdio", "http", "sse", "streamable-http"] = "stdio") -> None:
        """Run the MCP server.

        Args:
            transport: Transport type ('stdio', 'http', 'sse', or 'streamable-http')
        """
        logger.info(f"Starting ProxyWhirl MCP Server with {transport} transport")
        if mcp is None:
            logger.warning(
                "FastMCP is not installed. MCP server cannot run. Install with: pip install fastmcp"
            )
            return
        mcp.run(transport=transport)


# ============================================================================
# Internal Implementation Functions
# ============================================================================


async def _list_proxies_impl(api_key: str | None = None) -> dict[str, Any]:
    """List all proxies in the pool.

    Args:
        api_key: Optional API key for authentication

    Returns:
        Dictionary containing proxy list and statistics
    """
    logger.info("Tool called: list_proxies")

    # Authenticate request
    auth = get_auth()
    if not auth.authenticate({"api_key": api_key}):
        logger.warning("Authentication failed for list_proxies")
        return {"error": "Authentication failed: Invalid API key", "code": 401}

    rotator = await get_rotator()

    # Get all proxies from the pool (thread-safe snapshot)
    proxies = []
    for proxy in rotator.pool.get_all_proxies():
        proxies.append(
            {
                "id": str(proxy.id),
                "url": str(proxy.url),
                "status": proxy.health_status.value,
                "success_rate": proxy.success_rate,
                "avg_latency_ms": proxy.average_response_time_ms or 0.0,
                "region": proxy.country_code or "UNKNOWN",
                "total_requests": proxy.total_requests,
                "total_successes": proxy.total_successes,
                "total_failures": proxy.total_failures,
            }
        )

    # Count by status (use same snapshot for consistency)
    proxies_snapshot = rotator.pool.get_all_proxies()
    status_counts = {
        "healthy": sum(1 for p in proxies_snapshot if p.health_status == HealthStatus.HEALTHY),
        "degraded": sum(1 for p in proxies_snapshot if p.health_status == HealthStatus.DEGRADED),
        "unhealthy": sum(1 for p in proxies_snapshot if p.health_status == HealthStatus.UNHEALTHY),
        "dead": sum(1 for p in proxies_snapshot if p.health_status == HealthStatus.DEAD),
        "unknown": sum(1 for p in proxies_snapshot if p.health_status == HealthStatus.UNKNOWN),
    }

    return {
        "proxies": proxies,
        "total": rotator.pool.size,
        **status_counts,
    }


async def _rotate_proxy_impl(api_key: str | None = None) -> dict[str, Any]:
    """Rotate to the next proxy in the pool.

    Args:
        api_key: Optional API key for authentication

    Returns:
        Dictionary containing selected proxy information
    """
    logger.info("Tool called: rotate_proxy")

    # Authenticate request
    auth = get_auth()
    if not auth.authenticate({"api_key": api_key}):
        logger.warning("Authentication failed for rotate_proxy")
        return {"error": "Authentication failed: Invalid API key", "code": 401}

    rotator = await get_rotator()

    try:
        # Select a proxy using the current strategy
        proxy = rotator.strategy.select(rotator.pool)

        return {
            "proxy": {
                "id": str(proxy.id),
                "url": str(proxy.url),
                "status": proxy.health_status.value,
                "success_rate": proxy.success_rate,
                "avg_latency_ms": proxy.average_response_time_ms or 0.0,
                "region": proxy.country_code or "UNKNOWN",
            }
        }
    except Exception as e:
        logger.error(f"Failed to rotate proxy: {e}")
        return {"error": f"Failed to select proxy: {str(e)}", "code": 500}


async def _proxy_status_impl(proxy_id: str, api_key: str | None = None) -> dict[str, Any]:
    """Get detailed status for a specific proxy.

    Args:
        proxy_id: UUID of the proxy to check
        api_key: Optional API key for authentication

    Returns:
        Dictionary containing proxy status and metrics
    """
    logger.info(f"Tool called: proxy_status for {proxy_id}")

    # Authenticate request
    auth = get_auth()
    if not auth.authenticate({"api_key": api_key}):
        logger.warning("Authentication failed for proxy_status")
        return {"error": "Authentication failed: Invalid API key", "code": 401}

    if not proxy_id:
        return {"error": "proxy_id is required", "code": 400}

    rotator = await get_rotator()

    # Find the proxy by ID
    from uuid import UUID

    try:
        proxy_uuid = UUID(proxy_id)
    except ValueError:
        return {"error": f"Invalid proxy_id format: {proxy_id}", "code": 400}

    # Use thread-safe snapshot to find proxy
    proxy = None
    for p in rotator.pool.get_all_proxies():
        if p.id == proxy_uuid:
            proxy = p
            break

    if proxy is None:
        return {"error": f"Proxy not found: {proxy_id}", "code": 404}

    # Get circuit breaker state
    circuit_breaker = rotator.circuit_breakers.get(proxy_id)
    cb_state = "unknown"
    if circuit_breaker:
        cb_state = circuit_breaker.state.value

    return {
        "proxy_id": proxy_id,
        "url": str(proxy.url),
        "status": proxy.health_status.value,
        "metrics": {
            "success_rate": proxy.success_rate,
            "avg_latency_ms": proxy.average_response_time_ms or 0.0,
            "total_requests": proxy.total_requests,
            "successful_requests": proxy.total_successes,
            "failed_requests": proxy.total_failures,
            "ema_response_time_ms": proxy.ema_response_time_ms or 0.0,
        },
        "health": {
            "last_check": proxy.last_health_check.isoformat() if proxy.last_health_check else None,
            "last_success": proxy.last_success_at.isoformat() if proxy.last_success_at else None,
            "last_failure": proxy.last_failure_at.isoformat() if proxy.last_failure_at else None,
            "circuit_breaker": cb_state,
            "consecutive_failures": proxy.consecutive_failures,
            "consecutive_successes": proxy.consecutive_successes,
        },
        "region": proxy.country_code or "UNKNOWN",
        "protocol": proxy.protocol,
    }


async def _recommend_proxy_impl(
    region: str | None = None,
    performance: str | None = "medium",
    api_key: str | None = None,
) -> dict[str, Any]:
    """Recommend the best proxy based on criteria.

    Args:
        region: Optional region filter (country code)
        performance: Performance tier (high, medium, low)
        api_key: Optional API key for authentication

    Returns:
        Dictionary containing recommendation and alternatives
    """
    logger.info(f"Tool called: recommend_proxy (region={region}, performance={performance})")

    # Authenticate request
    auth = get_auth()
    if not auth.authenticate({"api_key": api_key}):
        logger.warning("Authentication failed for recommend_proxy")
        return {"error": "Authentication failed: Invalid API key", "code": 401}

    if performance and performance not in ["high", "medium", "low"]:
        return {
            "error": "Invalid performance level. Must be one of: high, medium, low",
            "code": 400,
        }

    rotator = await get_rotator()

    # Filter proxies by region if specified (thread-safe snapshot)
    candidates = rotator.pool.get_all_proxies()
    if region:
        region_upper = region.upper()
        candidates = [
            p for p in candidates if p.country_code and p.country_code.upper() == region_upper
        ]
        if not candidates:
            return {"error": f"No proxies found for region: {region}", "code": 404}

    # Sort by performance criteria
    if performance == "high":
        # High performance: prioritize low latency and high success rate
        candidates.sort(
            key=lambda p: (-(p.success_rate or 0.0), p.average_response_time_ms or float("inf"))
        )
    elif performance == "medium":
        # Medium performance: balance between success rate and latency
        candidates.sort(
            key=lambda p: (
                -(p.success_rate or 0.0) * 0.7
                - (1.0 / max(p.average_response_time_ms or 1000, 1)) * 0.3,
            )
        )
    else:  # low
        # Low performance: just ensure it's working
        candidates.sort(key=lambda p: -(p.success_rate or 0.0))

    if not candidates:
        return {"error": "No proxies available", "code": 404}

    best_proxy = candidates[0]

    # Calculate a score (0-1) based on success rate and response time
    score = best_proxy.success_rate or 0.0
    if best_proxy.average_response_time_ms and best_proxy.average_response_time_ms > 0:
        # Penalize high latency (normalize to 0-1, where 100ms = 1.0, 1000ms = 0.1)
        latency_score = max(0.0, 1.0 - (best_proxy.average_response_time_ms / 1000.0))
        score = (score + latency_score) / 2.0

    reason_parts = [f"Best {performance} performance proxy"]
    if region:
        reason_parts.append(f"in {region.upper()} region")
    if best_proxy.success_rate and best_proxy.success_rate > 0.9:
        reason_parts.append("with high reliability")

    # Get alternatives (top 3 excluding the best)
    alternatives = []
    for alt_proxy in candidates[1:4]:
        alt_score = alt_proxy.success_rate or 0.0
        if alt_proxy.average_response_time_ms and alt_proxy.average_response_time_ms > 0:
            alt_latency_score = max(0.0, 1.0 - (alt_proxy.average_response_time_ms / 1000.0))
            alt_score = (alt_score + alt_latency_score) / 2.0

        alternatives.append(
            {
                "id": str(alt_proxy.id),
                "url": str(alt_proxy.url),
                "score": round(alt_score, 2),
                "reason": f"Alternative with {alt_proxy.success_rate:.1%} success rate",
            }
        )

    return {
        "recommendation": {
            "id": str(best_proxy.id),
            "url": str(best_proxy.url),
            "score": round(score, 2),
            "reason": " ".join(reason_parts),
            "metrics": {
                "success_rate": best_proxy.success_rate,
                "avg_latency_ms": best_proxy.average_response_time_ms or 0.0,
                "region": best_proxy.country_code or "UNKNOWN",
                "performance_tier": performance,
                "total_requests": best_proxy.total_requests,
            },
            "alternatives": alternatives,
        }
    }


async def _get_health_impl() -> dict[str, Any]:
    """Get health status of the proxy pool.

    Returns:
        Dictionary containing health metrics and status
    """
    from datetime import datetime, timezone

    logger.info("Tool called: health")
    rotator = await get_rotator()

    # Get pool statistics
    stats = rotator.get_pool_stats()

    # Calculate average latency (thread-safe snapshot)
    proxies_snapshot = rotator.pool.get_all_proxies()
    latencies = [
        p.average_response_time_ms
        for p in proxies_snapshot
        if p.average_response_time_ms is not None and p.average_response_time_ms > 0
    ]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

    # Determine overall pool status
    if stats["total_proxies"] == 0:
        pool_status = "empty"
    elif stats["healthy_proxies"] >= stats["total_proxies"] * 0.7:
        pool_status = "healthy"
    elif stats["healthy_proxies"] >= stats["total_proxies"] * 0.3:
        pool_status = "degraded"
    else:
        pool_status = "critical"

    # Check rate limiter if configured
    rate_limit_info = {"enabled": False, "message": "Rate limiting not configured"}
    if hasattr(rotator, "rate_limiter") and rotator.rate_limiter is not None:
        try:
            rate_limit_info = {
                "enabled": True,
                "max_requests": getattr(rotator.rate_limiter, "max_requests", None),
                "time_window_seconds": getattr(rotator.rate_limiter, "time_window", None),
            }
        except Exception:
            pass

    return {
        "pool_status": pool_status,
        "total_proxies": stats["total_proxies"],
        "healthy_proxies": stats["healthy_proxies"],
        "degraded_proxies": stats.get("unhealthy_proxies", 0),
        "failed_proxies": stats.get("dead_proxies", 0),
        "average_success_rate": stats["average_success_rate"],
        "average_latency_ms": round(avg_latency, 2),
        "last_update": datetime.now(timezone.utc).isoformat(),
        "total_requests": stats["total_requests"],
        "total_successes": stats["total_successes"],
        "total_failures": stats["total_failures"],
        "rate_limit": rate_limit_info,
    }


async def _reset_circuit_breaker_impl(proxy_id: str, api_key: str | None = None) -> dict[str, Any]:
    """Reset the circuit breaker for a specific proxy.

    Args:
        proxy_id: UUID of the proxy whose circuit breaker to reset
        api_key: Optional API key for authentication

    Returns:
        Dictionary containing reset confirmation or error
    """
    logger.info(f"Tool called: reset_circuit_breaker for {proxy_id}")

    # Authenticate request
    auth = get_auth()
    if not auth.authenticate({"api_key": api_key}):
        logger.warning("Authentication failed for reset_circuit_breaker")
        return {"error": "Authentication failed: Invalid API key", "code": 401}

    if not proxy_id:
        return {"error": "proxy_id is required", "code": 400}

    rotator = await get_rotator()

    # Check if circuit breaker exists for this proxy
    circuit_breaker = rotator.circuit_breakers.get(proxy_id)
    if circuit_breaker is None:
        return {"error": f"No circuit breaker found for proxy: {proxy_id}", "code": 404}

    # Get state before reset for logging
    old_state = circuit_breaker.state.value

    # Reset the circuit breaker
    try:
        circuit_breaker.reset()
        logger.info(
            f"Circuit breaker reset for proxy {proxy_id}: {old_state} -> closed",
            proxy_id=proxy_id,
            old_state=old_state,
        )
        return {
            "success": True,
            "proxy_id": proxy_id,
            "previous_state": old_state,
            "new_state": "closed",
            "message": f"Circuit breaker reset successfully for proxy {proxy_id}",
        }
    except Exception as e:
        logger.error(f"Failed to reset circuit breaker for {proxy_id}: {e}")
        return {"error": f"Failed to reset circuit breaker: {str(e)}", "code": 500}


# ============================================================================
# Unified MCP Tool
# ============================================================================

# Type alias for action parameter
ProxywhirlAction = Literal["list", "rotate", "status", "recommend", "health", "reset_cb"]


async def _proxywhirl_tool(
    action: ProxywhirlAction,
    proxy_id: str | None = None,
    criteria: dict[str, Any] | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Unified proxywhirl management tool.

    Args:
        action: Operation to perform (list|rotate|status|recommend|health|reset_cb)
        proxy_id: Proxy ID (required for: status, reset_cb)
        criteria: Filter criteria dict with 'region' and 'performance' keys (for: recommend)
        api_key: API key for authentication (if required)

    Returns:
        Operation result as dictionary
    """
    if action == "list":
        return await _list_proxies_impl(api_key=api_key)
    elif action == "rotate":
        return await _rotate_proxy_impl(api_key=api_key)
    elif action == "status":
        if not proxy_id:
            return {"error": "proxy_id required for status action", "code": 400}
        return await _proxy_status_impl(proxy_id, api_key=api_key)
    elif action == "recommend":
        region = criteria.get("region") if criteria else None
        performance = criteria.get("performance", "medium") if criteria else "medium"
        return await _recommend_proxy_impl(region=region, performance=performance, api_key=api_key)
    elif action == "health":
        return await _get_health_impl()
    elif action == "reset_cb":
        if not proxy_id:
            return {"error": "proxy_id required for reset_cb action", "code": 400}
        return await _reset_circuit_breaker_impl(proxy_id, api_key=api_key)
    else:
        return {"error": f"Unknown action: {action}", "code": 400}


# Register unified tool with FastMCP when available
# Use conditional to wrap with FastMCP decorator or provide standalone function for testing
proxywhirl = mcp.tool()(_proxywhirl_tool) if mcp is not None else _proxywhirl_tool


# ============================================================================
# MCP Resources
# ============================================================================


async def _get_proxy_health_impl() -> str:
    """Get proxy pool health as JSON resource."""
    import json

    health_data = await _get_health_impl()
    return json.dumps(health_data, indent=2)


async def _get_proxy_config_impl() -> str:
    """Get proxy configuration as JSON resource."""
    import json

    logger.info("Resource accessed: proxy://config")
    rotator = await get_rotator()

    # Get circuit breaker config from the first circuit breaker (they all share the same config)
    cb_config = {}
    if rotator.circuit_breakers:
        first_cb = next(iter(rotator.circuit_breakers.values()))
        cb_config = {
            "failure_threshold": first_cb.failure_threshold,
            "timeout_duration": first_cb.timeout_duration,
            "window_duration": first_cb.window_duration,
        }

    config_data = {
        "rotation_strategy": rotator.strategy.__class__.__name__,
        "timeout": rotator.config.timeout,
        "verify_ssl": rotator.config.verify_ssl,
        "follow_redirects": rotator.config.follow_redirects,
        "pool_connections": rotator.config.pool_connections,
        "pool_max_keepalive": rotator.config.pool_max_keepalive,
        "circuit_breaker": cb_config,
        "retry_policy": {
            "max_attempts": rotator.retry_policy.max_attempts,
            "backoff_strategy": rotator.retry_policy.backoff_strategy.value,
            "base_delay": rotator.retry_policy.base_delay,
            "max_backoff_delay": rotator.retry_policy.max_backoff_delay,
            "multiplier": rotator.retry_policy.multiplier,
        },
        "logging": {
            "level": rotator.config.log_level,
            "format": rotator.config.log_format,
            "redact_credentials": rotator.config.log_redact_credentials,
        },
    }
    return json.dumps(config_data, indent=2)


# Register FastMCP resources when available
if mcp is not None:
    proxy_health_resource = mcp.resource("proxy://health")(_get_proxy_health_impl)
    proxy_config_resource = mcp.resource("proxy://config")(_get_proxy_config_impl)


# ============================================================================
# MCP Prompts
# ============================================================================


async def _proxy_selection_workflow_prompt() -> str:
    """Workflow prompt for guiding proxy selection decisions."""
    return """# Proxy Selection Workflow

Use this workflow to select the optimal proxy for your request:

## Step 1: Assess Requirements
- What is the target geography? (Use 'recommend' with region criteria)
- What performance tier do you need? (high/medium/low)
- Is this a one-time request or part of a session?

## Step 2: Check Pool Health
- Call proxywhirl(action="health") to assess overall pool status
- If pool_status is "critical" or "empty", consider fetching new proxies

## Step 3: Get Recommendation
- Call proxywhirl(action="recommend", criteria={"region": "US", "performance": "high"})
- Review the recommendation and alternatives

## Step 4: Verify Selected Proxy
- Call proxywhirl(action="status", proxy_id="<selected_id>")
- Check circuit_breaker state (should be "closed")
- Review success_rate and avg_latency_ms

## Step 5: Use or Rotate
- If proxy looks good, use it for your request
- If issues arise, call proxywhirl(action="rotate") for next proxy
- If circuit breaker is open, call proxywhirl(action="reset_cb", proxy_id="<id>")

## Common Issues
- All proxies failing: Check if target site is blocking proxies
- High latency: Try "high" performance tier recommendation
- Authentication errors: Verify proxy credentials
"""


async def _troubleshooting_workflow_prompt() -> str:
    """Workflow prompt for debugging proxy issues."""
    return """# Proxy Troubleshooting Workflow

Use this workflow when experiencing proxy issues:

## Step 1: Diagnose Pool Health
```
proxywhirl(action="health")
```
- Check pool_status: "healthy", "degraded", "critical", or "empty"
- Review healthy_proxies vs total_proxies ratio
- Check average_success_rate (should be > 0.8)

## Step 2: Check Specific Proxy
```
proxywhirl(action="status", proxy_id="<proxy_id>")
```
- Is circuit_breaker "open"? -> Proxy is failing repeatedly
- Is consecutive_failures high? -> Proxy may be blocked
- Is success_rate low? -> Proxy may be unreliable

## Step 3: Circuit Breaker Issues
If a proxy's circuit breaker is open but you believe it should work:
```
proxywhirl(action="reset_cb", proxy_id="<proxy_id>")
```
This resets the circuit breaker to "closed" state for retry.

## Step 4: Find Alternative
```
proxywhirl(action="recommend", criteria={"performance": "high"})
```
Get a fresh recommendation for a reliable proxy.

## Step 5: Rotate Away from Problem Proxy
```
proxywhirl(action="rotate")
```
Get the next available proxy in rotation.

## Common Patterns

### All Circuit Breakers Open
- Indicates widespread blocking or network issues
- Wait for timeout or reset individual breakers
- Consider if target site is blocking all your proxies

### Low Success Rates Across Pool
- Proxies may be stale (re-fetch from sources)
- Target site may have changed blocking rules
- Consider using different proxy sources

### Single Proxy Issues
- Reset circuit breaker and retry
- If persists, proxy may be permanently blocked
- Rotate to different proxy
"""


# Register FastMCP prompts when available
if mcp is not None:

    @mcp.prompt()
    async def proxy_selection_workflow() -> str:
        """Workflow prompt for guiding proxy selection decisions."""
        return await _proxy_selection_workflow_prompt()

    @mcp.prompt()
    async def troubleshooting_workflow() -> str:
        """Workflow prompt for debugging proxy issues."""
        return await _troubleshooting_workflow_prompt()


# ============================================================================
# Public API Wrappers (for backward compatibility and testing)
# ============================================================================


async def list_proxies(api_key: str | None = None) -> dict[str, Any]:
    """Wrapper to call shared list_proxies implementation."""
    return await _list_proxies_impl(api_key=api_key)


async def rotate_proxy(api_key: str | None = None) -> dict[str, Any]:
    """Wrapper to call shared rotate_proxy implementation."""
    return await _rotate_proxy_impl(api_key=api_key)


async def proxy_status(proxy_id: str, api_key: str | None = None) -> dict[str, Any]:
    """Wrapper to call shared proxy_status implementation."""
    return await _proxy_status_impl(proxy_id, api_key=api_key)


async def recommend_proxy(
    region: str | None = None,
    performance: str | None = "medium",
    api_key: str | None = None,
) -> dict[str, Any]:
    """Wrapper to call shared recommend_proxy implementation."""
    return await _recommend_proxy_impl(region=region, performance=performance, api_key=api_key)


async def get_proxy_health() -> str:
    """Wrapper to call shared get_proxy_health implementation."""
    return await _get_proxy_health_impl()


async def get_proxy_config() -> str:
    """Wrapper to call shared get_proxy_config implementation."""
    return await _get_proxy_config_impl()


async def get_rate_limit_status(proxy_id: str, api_key: str | None = None) -> dict[str, Any]:
    """Get rate limiting status for a specific proxy (backward compatibility wrapper).

    Note: Rate limiting info is now included in the health action response.
    This wrapper is kept for backward compatibility.

    Args:
        proxy_id: UUID of the proxy to check
        api_key: Optional API key for authentication

    Returns:
        Dictionary containing rate limit information
    """
    from uuid import UUID

    logger.info(f"Tool called: get_rate_limit_status for {proxy_id}")

    # Authenticate request
    auth = get_auth()
    if not auth.authenticate({"api_key": api_key}):
        logger.warning("Authentication failed for get_rate_limit_status")
        return {"error": "Authentication failed: Invalid API key", "code": 401}

    rotator = await get_rotator()

    # Check if the proxy exists
    try:
        proxy_uuid = UUID(proxy_id)
    except ValueError:
        return {"error": f"Invalid proxy_id format: {proxy_id}", "code": 400}

    # Use thread-safe snapshot to find proxy
    proxy = None
    for p in rotator.pool.get_all_proxies():
        if p.id == proxy_uuid:
            proxy = p
            break

    if proxy is None:
        return {"error": f"Proxy not found: {proxy_id}", "code": 404}

    # Check if rate limiter is configured
    if hasattr(rotator, "rate_limiter") and rotator.rate_limiter is not None:
        try:
            return {
                "proxy_id": proxy_id,
                "rate_limit": {
                    "enabled": True,
                    "message": "Rate limiting is configured",
                    "max_requests": getattr(rotator.rate_limiter, "max_requests", None),
                    "time_window_seconds": getattr(rotator.rate_limiter, "time_window", None),
                    "current_usage": 0,  # Would need actual tracking
                    "remaining": None,
                },
            }
        except Exception:
            pass

    # Rate limiting not configured (placeholder implementation)
    return {
        "proxy_id": proxy_id,
        "rate_limit": {
            "enabled": False,
            "message": "Rate limiting is not configured for this proxy",
            "max_requests": None,
            "time_window_seconds": None,
            "current_usage": 0,
            "remaining": None,
        },
        "note": "Rate limiting can be configured via the RateLimiter class",
    }
