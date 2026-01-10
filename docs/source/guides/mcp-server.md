---
title: MCP Server Guide
---

# MCP Server Guide

ProxyWhirl provides a Model Context Protocol (MCP) server that enables AI assistants to manage proxies programmatically. This guide covers installation, configuration, the unified tool interface, resources, prompts, and integration patterns.

## Overview

The MCP server exposes ProxyWhirl's proxy management capabilities through a standardized protocol that AI assistants can use. It provides:

- **Unified Tool**: A single `proxywhirl` tool with action-based operations
- **Resources**: Real-time proxy pool health and configuration data
- **Prompts**: Guided workflows for proxy selection and troubleshooting

```{note}
The MCP server requires Python 3.10 or higher due to FastMCP dependencies.
```

## Quick Start

### Installation

```bash
# Install ProxyWhirl with MCP support
pip install "proxywhirl[mcp]"

# Or with uv
uv pip install "proxywhirl[mcp]"
```

### Running the Server

```bash
# Run the MCP server with stdio transport (default)
python -m proxywhirl.mcp.server

# Or use the ProxyWhirlMCPServer class
python -c "from proxywhirl.mcp import ProxyWhirlMCPServer; ProxyWhirlMCPServer().run()"
```

### Auto-Loading Proxies

The MCP server automatically loads proxies from `proxywhirl.db` if it exists in the current directory. Use the CLI to populate the database first:

```bash
# Fetch proxies and save to database
proxywhirl fetch --sources recommended --output proxywhirl.db

# Then run MCP server (proxies load automatically)
python -m proxywhirl.mcp.server
```

## The `proxywhirl` Tool

The MCP server exposes a single unified tool called `proxywhirl` that handles all proxy management operations through an `action` parameter.

### Available Actions

| Action | Description | Required Parameters | Optional Parameters |
|--------|-------------|---------------------|---------------------|
| `list` | List all proxies in the pool | - | `api_key` |
| `rotate` | Get next proxy using rotation strategy | - | `api_key` |
| `status` | Get detailed status for a specific proxy | `proxy_id` | `api_key` |
| `recommend` | Get best proxy based on criteria | - | `criteria`, `api_key` |
| `health` | Get pool health overview | - | - |
| `reset_cb` | Reset circuit breaker for a proxy | `proxy_id` | `api_key` |

### Action Examples

#### List All Proxies

```json
{
  "action": "list"
}
```

**Response:**
```json
{
  "proxies": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "url": "http://proxy1.example.com:8080",
      "status": "healthy",
      "success_rate": 0.95,
      "avg_latency_ms": 120.5,
      "region": "US",
      "total_requests": 150,
      "total_successes": 142,
      "total_failures": 8
    }
  ],
  "total": 1,
  "healthy": 1,
  "degraded": 0,
  "unhealthy": 0,
  "dead": 0,
  "unknown": 0
}
```

#### Rotate to Next Proxy

```json
{
  "action": "rotate"
}
```

**Response:**
```json
{
  "proxy": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "url": "http://proxy1.example.com:8080",
    "status": "healthy",
    "success_rate": 0.95,
    "avg_latency_ms": 120.5,
    "region": "US"
  }
}
```

#### Get Proxy Status

```json
{
  "action": "status",
  "proxy_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
  "proxy_id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "http://proxy1.example.com:8080",
  "status": "healthy",
  "metrics": {
    "success_rate": 0.95,
    "avg_latency_ms": 120.5,
    "total_requests": 150,
    "successful_requests": 142,
    "failed_requests": 8,
    "ema_response_time_ms": 115.3
  },
  "health": {
    "last_check": "2024-01-15T10:30:00Z",
    "last_success": "2024-01-15T10:29:55Z",
    "last_failure": "2024-01-15T09:15:00Z",
    "circuit_breaker": "closed",
    "consecutive_failures": 0,
    "consecutive_successes": 25
  },
  "region": "US",
  "protocol": "http"
}
```

#### Get Proxy Recommendation

```json
{
  "action": "recommend",
  "criteria": {
    "region": "US",
    "performance": "high"
  }
}
```

**Response:**
```json
{
  "recommendation": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "url": "http://proxy1.example.com:8080",
    "score": 0.92,
    "reason": "Best high performance proxy in US region with high reliability",
    "metrics": {
      "success_rate": 0.95,
      "avg_latency_ms": 85.2,
      "region": "US",
      "performance_tier": "high",
      "total_requests": 500
    },
    "alternatives": [
      {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "url": "http://proxy2.example.com:8080",
        "score": 0.88,
        "reason": "Alternative with 92.0% success rate"
      }
    ]
  }
}
```

The `criteria` parameter supports:
- `region`: Country code filter (e.g., "US", "DE", "JP")
- `performance`: Performance tier (`"high"`, `"medium"`, `"low"`)

#### Check Pool Health

```json
{
  "action": "health"
}
```

**Response:**
```json
{
  "pool_status": "healthy",
  "total_proxies": 10,
  "healthy_proxies": 8,
  "degraded_proxies": 1,
  "failed_proxies": 1,
  "average_success_rate": 0.89,
  "average_latency_ms": 145.3,
  "last_update": "2024-01-15T10:30:00Z",
  "total_requests": 5000,
  "total_successes": 4450,
  "total_failures": 550,
  "rate_limit": {
    "enabled": false,
    "message": "Rate limiting not configured"
  }
}
```

Pool status values:
- `empty`: No proxies in pool
- `healthy`: 70%+ proxies are healthy
- `degraded`: 30-70% proxies are healthy
- `critical`: Less than 30% proxies are healthy

#### Reset Circuit Breaker

```json
{
  "action": "reset_cb",
  "proxy_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
  "success": true,
  "proxy_id": "550e8400-e29b-41d4-a716-446655440000",
  "previous_state": "open",
  "new_state": "closed",
  "message": "Circuit breaker reset successfully for proxy 550e8400-e29b-41d4-a716-446655440000"
}
```

## Resources

The MCP server exposes two resources that AI assistants can read for real-time data.

### proxy://health

Returns real-time pool health data as JSON. This resource provides the same data as the `health` action but is accessible as a resource that can be subscribed to.

```json
{
  "pool_status": "healthy",
  "total_proxies": 10,
  "healthy_proxies": 8,
  "degraded_proxies": 1,
  "failed_proxies": 1,
  "average_success_rate": 0.89,
  "average_latency_ms": 145.3,
  "last_update": "2024-01-15T10:30:00Z",
  "total_requests": 5000,
  "total_successes": 4450,
  "total_failures": 550,
  "rate_limit": {
    "enabled": false,
    "message": "Rate limiting not configured"
  }
}
```

### proxy://config

Returns current configuration settings as JSON.

```json
{
  "rotation_strategy": "RoundRobinStrategy",
  "timeout": 30.0,
  "verify_ssl": true,
  "follow_redirects": true,
  "pool_connections": 10,
  "pool_max_keepalive": 5,
  "circuit_breaker": {
    "failure_threshold": 5,
    "timeout_duration": 60,
    "window_duration": 120
  },
  "retry_policy": {
    "max_attempts": 3,
    "backoff_strategy": "exponential",
    "base_delay": 1.0,
    "max_backoff_delay": 60.0,
    "multiplier": 2.0
  },
  "logging": {
    "level": "INFO",
    "format": "json",
    "redact_credentials": true
  }
}
```

## Prompts

The MCP server provides two guided workflow prompts for AI assistants.

### proxy_selection_workflow

A step-by-step workflow for selecting the optimal proxy for a request:

1. **Assess Requirements**: Determine target geography and performance needs
2. **Check Pool Health**: Verify pool status before selection
3. **Get Recommendation**: Use criteria-based recommendation
4. **Verify Selected Proxy**: Check circuit breaker and metrics
5. **Use or Rotate**: Execute request or switch proxies if issues arise

### troubleshooting_workflow

A diagnostic workflow for debugging proxy issues:

1. **Diagnose Pool Health**: Check overall pool status
2. **Check Specific Proxy**: Examine individual proxy metrics
3. **Circuit Breaker Issues**: Reset breakers if needed
4. **Find Alternative**: Get fresh recommendations
5. **Rotate Away**: Switch to different proxy

## Authentication

Authentication is optional. When not configured, all requests are allowed.

### Enabling Authentication

```python
from proxywhirl.mcp.server import set_auth
from proxywhirl.mcp.auth import MCPAuth

# Enable authentication with API key
auth = MCPAuth(api_key="your-secret-api-key")
set_auth(auth)
```

### Authenticated Tool Calls

When authentication is enabled, include `api_key` in tool calls:

```json
{
  "action": "list",
  "api_key": "your-secret-api-key"
}
```

### Disabling Authentication

```python
from proxywhirl.mcp.server import set_auth

# Disable authentication
set_auth(None)
```

```{warning}
Store API keys securely using environment variables or a secrets manager. Never hardcode keys in source code.
```

## Transport Options

The MCP server supports multiple transport protocols:

```python
from proxywhirl.mcp import ProxyWhirlMCPServer

server = ProxyWhirlMCPServer()

# stdio transport (default) - for CLI integration
server.run(transport="stdio")

# HTTP transport - for REST-like access
server.run(transport="http")

# SSE transport - for server-sent events
server.run(transport="sse")

# Streamable HTTP - for streaming responses
server.run(transport="streamable-http")
```

## Integration with Claude Desktop

Add ProxyWhirl to your Claude Desktop configuration:

### macOS

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "proxywhirl": {
      "command": "python",
      "args": ["-m", "proxywhirl.mcp.server"]
    }
  }
}
```

### Windows

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "proxywhirl": {
      "command": "python",
      "args": ["-m", "proxywhirl.mcp.server"]
    }
  }
}
```

### With uv

If using uv for Python management:

```json
{
  "mcpServers": {
    "proxywhirl": {
      "command": "uv",
      "args": ["run", "python", "-m", "proxywhirl.mcp.server"],
      "cwd": "/path/to/your/proxywhirl/project"
    }
  }
}
```

## Programmatic Usage

Use the MCP server functions directly in Python code:

```python
import asyncio
from proxywhirl.mcp.server import (
    proxywhirl,
    get_rotator,
    set_rotator,
    cleanup_rotator,
)
from proxywhirl import AsyncProxyRotator

async def main():
    # List all proxies
    result = await proxywhirl(action="list")
    print(f"Total proxies: {result.get('total', 0)}")

    # Check pool health
    result = await proxywhirl(action="health")
    print(f"Pool status: {result.get('pool_status', 'unknown')}")

    # Get recommendation with criteria
    result = await proxywhirl(
        action="recommend",
        criteria={"region": "US", "performance": "high"}
    )
    if "recommendation" in result:
        print(f"Recommended: {result['recommendation']['url']}")

    # Rotate to next proxy
    result = await proxywhirl(action="rotate")
    if "proxy" in result:
        print(f"Selected: {result['proxy']['url']}")

    # Clean up
    await cleanup_rotator()

asyncio.run(main())
```

### Custom Rotator Configuration

```python
import asyncio
from proxywhirl.mcp.server import set_rotator, proxywhirl, cleanup_rotator
from proxywhirl import AsyncProxyRotator, ProxyConfiguration

async def main():
    # Create custom rotator
    config = ProxyConfiguration(
        timeout=60.0,
        pool_connections=50,
    )
    rotator = AsyncProxyRotator(
        strategy="performance-based",
        config=config
    )

    # Set as global MCP rotator
    await set_rotator(rotator)

    # Add proxies
    await rotator.add_proxy("http://proxy1.example.com:8080")
    await rotator.add_proxy("http://proxy2.example.com:8080")

    # Now MCP tool calls use this rotator
    result = await proxywhirl(action="list")
    print(f"Proxies: {result['total']}")

    # Cleanup
    await cleanup_rotator()

asyncio.run(main())
```

## Lifecycle Management

The MCP server provides proper lifecycle management:

```python
from proxywhirl.mcp.server import mcp_lifespan

async def run_server():
    async with mcp_lifespan():
        # Server is running
        # Rotator is initialized
        # Resources are available
        pass
    # Cleanup is automatic on exit
```

### Server Class Usage

```python
from proxywhirl.mcp import ProxyWhirlMCPServer
from proxywhirl import AsyncProxyRotator

async def main():
    # With custom rotator
    rotator = AsyncProxyRotator(strategy="weighted")

    server = ProxyWhirlMCPServer(proxy_manager=rotator)
    await server.initialize()  # Required for async setup

    server.run()  # Starts the server

# Without custom rotator (uses defaults)
server = ProxyWhirlMCPServer()
server.run()  # Auto-initializes rotator on first use
```

## Error Handling

The MCP server returns errors in a consistent format:

```json
{
  "error": "Error message description",
  "code": 400
}
```

### Common Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 400 | Bad Request | Missing required parameter |
| 401 | Unauthorized | Invalid API key |
| 404 | Not Found | Proxy ID not found |
| 500 | Internal Error | Server-side failure |

### Example Error Responses

```json
// Missing proxy_id
{
  "error": "proxy_id required for status action",
  "code": 400
}

// Authentication failed
{
  "error": "Authentication failed: Invalid API key",
  "code": 401
}

// Proxy not found
{
  "error": "Proxy not found: invalid-uuid",
  "code": 404
}
```

## Best Practices

### 1. Always Check Pool Health First

Before making proxy selections, verify the pool is healthy:

```json
{"action": "health"}
```

If `pool_status` is `"critical"` or `"empty"`, fetch new proxies before proceeding.

### 2. Use Recommendations for Critical Requests

For important requests, use the `recommend` action instead of `rotate`:

```json
{
  "action": "recommend",
  "criteria": {"performance": "high"}
}
```

### 3. Monitor Circuit Breaker States

Check proxy status before use to avoid open circuit breakers:

```json
{
  "action": "status",
  "proxy_id": "your-proxy-id"
}
```

If `circuit_breaker` is `"open"`, either wait or reset it.

### 4. Handle Errors Gracefully

Always check for error responses:

```python
result = await proxywhirl(action="status", proxy_id="invalid")
if "error" in result:
    print(f"Error {result['code']}: {result['error']}")
else:
    print(f"Status: {result['status']}")
```

### 5. Clean Up Resources

Always clean up when done:

```python
from proxywhirl.mcp.server import cleanup_rotator

await cleanup_rotator()
```

## Troubleshooting

### Server Won't Start

**Python version too low:**
```
RuntimeError: MCP server requires Python 3.10 or higher
```
Solution: Upgrade to Python 3.10+.

**FastMCP not installed:**
```
FastMCP is not installed. MCP server cannot run.
```
Solution: `pip install fastmcp` or `pip install "proxywhirl[mcp]"`

### No Proxies Available

**Database not found:**
```
MCP: No database at proxywhirl.db, starting with empty pool
```
Solution: Run `proxywhirl fetch --output proxywhirl.db` first.

### Authentication Failures

**Invalid API key:**
```json
{"error": "Authentication failed: Invalid API key", "code": 401}
```
Solution: Verify the API key matches what was configured with `set_auth()`.

## See Also

- {doc}`async-client` - Async client usage patterns
- {doc}`retry-failover` - Circuit breaker and retry configuration
- {doc}`cli-reference` - CLI commands for proxy management
- {doc}`/reference/python-api` - Full Python API reference
