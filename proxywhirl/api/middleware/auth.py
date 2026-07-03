"""API key authentication middleware for ProxyWhirl API.

Provides middleware-based API key validation as an additional
layer to the existing dependency-based authentication.
"""

from __future__ import annotations

import secrets

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from proxywhirl.api.models import APIResponse, ErrorCode
from proxywhirl.settings import APISettings


def _api_error(status_code: int, code: ErrorCode, message: str) -> JSONResponse:
    response: APIResponse[None] = APIResponse.error_response(code=code, message=message)
    return JSONResponse(status_code=status_code, content=response.model_dump(mode="json"))


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce API key authentication on protected routes.

    Skips authentication for public paths (health, readiness, docs, root).
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
        }
    )
    PUBLIC_METRICS_PATHS: frozenset[str] = frozenset({"/api/metrics"})

    async def dispatch(self, request: Request, call_next):
        """Validate API key for protected requests."""
        api_settings = APISettings()

        if not api_settings.require_auth:
            return await call_next(request)

        path = request.url.path

        # Skip public paths. Prometheus exposition is public only by explicit opt-in.
        if path in self.PUBLIC_PATHS or (
            api_settings.public_metrics and path in self.PUBLIC_METRICS_PATHS
        ):
            return await call_next(request)

        expected_key = api_settings.api_key.get_secret_value() if api_settings.api_key else None
        if not expected_key:
            return _api_error(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                ErrorCode.SERVICE_UNAVAILABLE,
                "API authentication not configured",
            )

        api_key = request.headers.get("X-API-Key")
        if not api_key or not secrets.compare_digest(api_key, expected_key):
            return _api_error(
                status.HTTP_401_UNAUTHORIZED,
                ErrorCode.VALIDATION_ERROR,
                "Invalid or missing API key",
            )

        return await call_next(request)
