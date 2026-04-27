"""ProxyWhirl API v2 - FastAPI application with advanced features.

Features:
- Structured request/response envelopes
- Per-API-key rate limiting
- Webhook signing
- Streaming responses
- Distributed tracing
- Async-first design
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from loguru import logger

from proxywhirl.api.v2.auth import APIKeyAuth, RateLimitKey, WebhookSigner
from proxywhirl.api.v2.models import (
    APIResponse,
    ErrorCode,
    ErrorDetail,
    PaginatedResponse,
    ProxyResourceV2,
    ResponseMetadata,
)

# In-memory stores (would be moved to database in production)
API_KEYS: dict[str, APIKeyAuth] = {}
RATE_LIMITS: dict[str, RateLimitKey] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app."""
    # Startup
    logger.info("API v2 starting up")
    yield
    # Shutdown
    logger.info("API v2 shutting down")


app = FastAPI(
    title="ProxyWhirl API v2",
    description="Advanced proxy rotation with event-driven architecture",
    version="2.0.0",
    lifespan=lifespan,
)


# =============================================================================
# Authentication & Rate Limiting
# =============================================================================


async def get_api_key(authorization: str | None = Header(None)) -> APIKeyAuth:
    """Extract and validate API key from header.

    Args:
        authorization: Authorization header value

    Returns:
        Valid APIKeyAuth

    Raises:
        HTTPException: If key is invalid or missing
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format",
        )

    key_id = parts[1]
    if key_id not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    api_key = API_KEYS[key_id]

    # Check if key is active and not expired
    if not api_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key is inactive",
        )

    if api_key.expires_at and api_key.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key has expired",
        )

    return api_key


async def check_rate_limit(
    api_key: APIKeyAuth = Depends(get_api_key),
) -> None:
    """Check rate limits for API key.

    Args:
        api_key: The API key being used

    Raises:
        HTTPException: If rate limits exceeded
    """
    now = time.time()
    key_id = api_key.key_id

    if key_id not in RATE_LIMITS:
        RATE_LIMITS[key_id] = RateLimitKey(key_id=key_id)

    limit = RATE_LIMITS[key_id]

    # Reset minute counter
    if now - limit.last_minute_reset >= 60:
        RATE_LIMITS[key_id] = RateLimitKey(
            key_id=key_id,
            hour_requests=limit.hour_requests,
            last_hour_reset=limit.last_hour_reset,
        )
        limit = RATE_LIMITS[key_id]

    # Reset hour counter
    if now - limit.last_hour_reset >= 3600:
        RATE_LIMITS[key_id] = RateLimitKey(
            key_id=key_id,
            minute_requests=limit.minute_requests,
            last_minute_reset=limit.last_minute_reset,
        )
        limit = RATE_LIMITS[key_id]

    # Check limits
    if limit.is_minute_limit_exceeded(api_key.requests_per_minute):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded (per minute)",
        )

    if limit.is_hour_limit_exceeded(api_key.requests_per_hour):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded (per hour)",
        )

    # Increment counters
    RATE_LIMITS[key_id].minute_requests += 1
    RATE_LIMITS[key_id].hour_requests += 1


# =============================================================================
# Middleware for Request/Response Metadata
# =============================================================================


@app.middleware("http")
async def add_metadata(request: Request, call_next):
    """Add request metadata to context."""
    request.state.start_time = time.time()
    request.state.request_id = request.headers.get(
        "X-Request-ID",
        str(UUID(int=int(time.time() * 1000))),
    )
    response = await call_next(request)
    return response


# =============================================================================
# Helper Functions
# =============================================================================


def create_response(
    data: Any,
    request_id: str,
    start_time: float,
) -> APIResponse:
    """Create standard API response.

    Args:
        data: Response data
        request_id: Request ID
        start_time: Request start time

    Returns:
        APIResponse with metadata
    """
    processing_time = (time.time() - start_time) * 1000

    return APIResponse(
        success=True,
        data=data,
        error=None,
        metadata=ResponseMetadata(
            request_id=UUID(request_id),
            processing_time_ms=processing_time,
        ),
    )


def create_error_response(
    code: ErrorCode,
    message: str,
    request_id: str,
    start_time: float,
    details: dict[str, Any] | None = None,
) -> APIResponse:
    """Create error response.

    Args:
        code: Error code
        message: Error message
        request_id: Request ID
        start_time: Request start time
        details: Additional error details

    Returns:
        APIResponse with error
    """
    processing_time = (time.time() - start_time) * 1000

    return APIResponse(
        success=False,
        data=None,
        error=ErrorDetail(
            code=code,
            message=message,
            details=details or {},
        ),
        metadata=ResponseMetadata(
            request_id=UUID(request_id),
            processing_time_ms=processing_time,
        ),
    )


# =============================================================================
# Proxy Endpoints
# =============================================================================


@app.get(
    "/api/v2/proxies",
    response_model=APIResponse[PaginatedResponse[ProxyResourceV2]],
    summary="List proxies",
)
async def list_proxies(
    request: Request,
    page: int = 1,
    page_size: int = 50,
    api_key: APIKeyAuth = Depends(get_api_key),
    _: None = Depends(check_rate_limit),
) -> APIResponse:
    """List all proxies with pagination."""
    start_time = request.state.start_time
    request_id = request.state.request_id

    # Mock implementation - would use actual proxy pool
    proxies = [
        ProxyResourceV2(
            id=f"proxy-{i}",
            protocol="http",
            host=f"{100 + i}.{200 + i}.{50 + i}.{i}",
            port=8080 + i,
            is_active=True,
        )
        for i in range(10)
    ]

    total = len(proxies)
    total_pages = (total + page_size - 1) // page_size
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    paginated = PaginatedResponse(
        items=proxies[start_idx:end_idx],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
    )

    return create_response(paginated, request_id, start_time)


@app.get(
    "/api/v2/proxies/{proxy_id}",
    response_model=APIResponse[ProxyResourceV2],
    summary="Get proxy details",
)
async def get_proxy(
    request: Request,
    proxy_id: str,
    api_key: APIKeyAuth = Depends(get_api_key),
    _: None = Depends(check_rate_limit),
) -> APIResponse:
    """Get details of a specific proxy."""
    start_time = request.state.start_time
    request_id = request.state.request_id

    # Mock implementation
    proxy = ProxyResourceV2(
        id=proxy_id,
        protocol="http",
        host="1.2.3.4",
        port=8080,
        is_active=True,
    )

    return create_response(proxy, request_id, start_time)


# =============================================================================
# Health Check
# =============================================================================


@app.get("/api/v2/health")
async def health_check(request: Request) -> dict[str, Any]:
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# =============================================================================
# Webhook Management
# =============================================================================


@app.post(
    "/api/v2/webhooks/verify",
    summary="Verify webhook signature",
)
async def verify_webhook(
    request: Request,
    signature: str = Header(...),
    timestamp: str = Header(...),
    nonce: str = Header(...),
    api_key: APIKeyAuth = Depends(get_api_key),
) -> dict[str, bool]:
    """Verify a webhook signature.

    Args:
        signature: HMAC-SHA256 signature
        timestamp: Request timestamp
        nonce: One-time nonce

    Returns:
        Verification result
    """
    try:
        body = await request.body()
        signer = WebhookSigner()
        is_valid = signer.verify_signature(body, signature, timestamp, nonce)
        return {"valid": is_valid}
    except Exception as e:
        logger.error("Webhook verification failed", error=e)
        return {"valid": False}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
