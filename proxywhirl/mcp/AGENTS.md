# MCP Server Subsystem Agent Guidelines

> Extends: [../../AGENTS.md](../../AGENTS.md)

Agent guidelines for the Model Context Protocol (MCP) server integration.

## Overview

The MCP subsystem exposes proxywhirl functionality as an MCP server, allowing AI assistants to interact with proxy rotation capabilities.

**Note:** Requires Python 3.10+ and the `[mcp]` optional dependency.

## Module Structure

| File | Purpose | Key Classes |
|------|---------|-------------|
| `__init__.py` | Public exports | `MCPServer` |
| `server.py` | MCP server implementation | `MCPServer`, tool definitions |
| `auth.py` | Authentication | API key validation |

## Quick Reference

```bash
# Install MCP dependencies
uv pip install -e ".[mcp]"

# Run MCP server tests
uv run pytest tests/unit/test_mcp_server.py -v
uv run pytest tests/unit/test_mcp_auth.py -v
```

## Key Patterns

### MCP Server Tools

The MCP server exposes these tools:

| Tool | Description |
|------|-------------|
| `get_proxy` | Get a proxy with optional filters |
| `validate_proxy` | Validate a specific proxy |
| `list_proxies` | List available proxies |
| `get_statistics` | Get proxy pool statistics |
| `refresh_proxies` | Refresh proxy list from sources |

### Server Configuration

```python
from proxywhirl.mcp import MCPServer

server = MCPServer(
    name="proxywhirl",
    api_key="your-api-key",  # Optional
)

# Start the server
await server.start()
```

## Boundaries

### Always Do

- Validate API keys when authentication is enabled
- Return structured responses for all tools
- Handle errors gracefully with informative messages

### Ask First

- Adding new MCP tools
- Changing authentication mechanisms
- Modifying response schemas

### Never Touch

- Exposing sensitive proxy credentials in tool responses
- Bypassing authentication

## Test Coverage

```bash
# Unit tests
uv run pytest tests/unit/test_mcp_server.py -v
uv run pytest tests/unit/test_mcp_auth.py -v
```

## Python Version Note

MCP requires Python 3.10+. Tests should be skipped on earlier versions:

```python
import sys
import pytest

@pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="MCP requires Python 3.10+"
)
def test_mcp_feature():
    ...
```
