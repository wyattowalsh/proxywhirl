"""Model Context Protocol server for ProxyWhirl."""

from __future__ import annotations

from proxywhirl.mcp.server import (
    ProxyWhirlMCPServer,
    cleanup_rotator,
    get_rotator,
    main,
    mcp,
    mcp_lifespan,
    proxywhirl,
    set_rotator,
)

__all__ = [
    "ProxyWhirlMCPServer",
    "cleanup_rotator",
    "get_rotator",
    "main",
    "mcp",
    "mcp_lifespan",
    "proxywhirl",
    "set_rotator",
]
