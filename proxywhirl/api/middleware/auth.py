"""API key authentication middleware for ProxyWhirl API.

Provides middleware-based API key validation as an additional
layer to the existing dependency-based authentication.
"""

from __future__ import annotations

import os
import secrets

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce API key authentication on protected routes.

    Skips authentication for public paths (health, docs, root, Prometheus metrics).
    When PROXYWHIRL_REQUIRE_AUTH is enabled, validates the X-API-Key header
    against the PROXYWHIRL_API_KEY environment variable.
    """

    # Paths that never require authentication
    PUBLIC_PATHS: frozenset[str] = frozenset(
        {
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/health",
            "/api/ready",
            "/api/status",
            "/api/stats",
            "/api/metrics",
        }
    )

    async def dispatch(self, request: Request, call_next):
        """Validate API key for protected requests."""
        require_auth = os.getenv("PROXYWHIRL_REQUIRE_AUTH", "false").lower() == "true"

        if not require_auth:
            return await call_next(request)

        path = request.url.path

        # Skip public paths
        if path in self.PUBLIC_PATHS:
            return await call_next(request)

        expected_key = os.getenv("PROXYWHIRL_API_KEY")
        if not expected_key:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"detail": "API authentication not configured"},
            )

        api_key = request.headers.get("X-API-Key")
        if not api_key or not secrets.compare_digest(api_key, expected_key):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or missing API key"},
            )

        return await call_next(request)
