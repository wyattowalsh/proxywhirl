"""
ProxyWhirl REST API package.

This package provides the FastAPI-based REST API for ProxyWhirl, including:
- Proxy management endpoints (CRUD operations)
- Proxied request handling
- Health and readiness checks
- Configuration management
- Metrics and statistics

Usage:
    from proxywhirl.api import app

    # Run with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

Environment Variables:
    PROXYWHIRL_STORAGE_PATH: Path to SQLite database
    PROXYWHIRL_STRATEGY: Rotation strategy (default: round-robin)
    PROXYWHIRL_TIMEOUT: Request timeout in seconds (default: 30)
    PROXYWHIRL_MAX_RETRIES: Max retry attempts (default: 3)
    PROXYWHIRL_REQUIRE_AUTH: Require API key auth (default: false)
    PROXYWHIRL_CORS_ORIGINS: Comma-separated CORS origins
"""

from proxywhirl.api.core import (
    app,
    get_config,
    get_rotator,
    get_storage,
    lifespan,
)

__all__ = [
    "app",
    "get_rotator",
    "get_storage",
    "get_config",
    "lifespan",
]
