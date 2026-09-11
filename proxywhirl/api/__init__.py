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

    # Local default (loopback). Non-loopback binds require auth or an explicit
    # insecure override; lifespan refuses open binds without authentication.
    uvicorn.run(app, host="127.0.0.1", port=8000)

Environment Variables:
    PROXYWHIRL_STORAGE_PATH: Path to SQLite database
    PROXYWHIRL_STRATEGY: Rotation strategy (default: round-robin)
    PROXYWHIRL_TIMEOUT: Request timeout in seconds (default: 30)
    PROXYWHIRL_MAX_RETRIES: Max retry attempts (default: 3)
    PROXYWHIRL_REQUIRE_AUTH: Require API key auth (default: false for local;
        set true + PROXYWHIRL_API_KEY for non-loopback / production binds)
    PROXYWHIRL_BIND_HOST: Bind address (default: 127.0.0.1)
    PROXYWHIRL_CORS_ORIGINS: Comma-separated CORS origins
"""

from proxywhirl.api.auth import APIKeyAuth, WebhookSignature, WebhookSigner, create_api_key
from proxywhirl.api.core import (
    app,
    get_config,
    get_rotator,
    get_storage,
    lifespan,
)

__all__ = [
    "APIKeyAuth",
    "WebhookSignature",
    "WebhookSigner",
    "app",
    "create_api_key",
    "get_config",
    "get_rotator",
    "get_storage",
    "lifespan",
]
