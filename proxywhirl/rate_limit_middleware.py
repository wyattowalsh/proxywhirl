"""
FastAPI middleware for rate limiting enforcement.

Transparently enforces rate limits on all API requests.
Injects rate limit headers and returns HTTP 429 when limits exceeded.
"""

from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from proxywhirl.exceptions import RateLimitExceeded
from proxywhirl.rate_limit_models import RateLimitConfig
from proxywhirl.rate_limiter import RateLimiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting.

    Enforces rate limits on all requests and injects headers.
    """

    def __init__(
        self,
        app: ASGIApp,
        config: RateLimitConfig,
    ) -> None:
        """
        Initialize rate limit middleware.

        Args:
            app: ASGI application
            config: Rate limit configuration
        """
        super().__init__(app)
        self.config = config
        self.limiter = RateLimiter(config)
        logger.info("Rate limit middleware initialized")

    def _extract_identifier(self, request: Request) -> str:
        """
        Extract user identifier from request.

        Priority order for unauthenticated requests:
        1. X-Forwarded-For header (first IP if comma-separated)
        2. X-Real-IP header
        3. request.client.host (direct connection)

        For authenticated requests, extract from JWT/API key.

        Args:
            request: FastAPI request object

        Returns:
            User ID (UUID) or IP address
        """
        # TODO: Extract user ID from JWT token or API key
        # For now, use IP-based identification (unauthenticated)

        # Try X-Forwarded-For (behind proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP in comma-separated list
            return forwarded_for.split(",")[0].strip()

        # Try X-Real-IP (behind Nginx)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # Fallback to direct connection IP
        if request.client and request.client.host:
            return request.client.host

        # Ultimate fallback
        return "unknown"

    def _extract_tier(self, request: Request, identifier: str) -> str:
        """
        Determine user's rate limit tier.

        TODO: Extract tier from authenticated user context.
        For now, use default tier for all users.

        Args:
            request: FastAPI request object
            identifier: User ID or IP address

        Returns:
            Tier name (e.g., "free", "premium", "enterprise")
        """
        # TODO: Implement tier extraction from JWT/API key
        # For now, return default tier
        return self.config.default_tier

    def _extract_endpoint(self, request: Request) -> str:
        """
        Extract endpoint path from request.

        Args:
            request: FastAPI request object

        Returns:
            API endpoint path (e.g., "/api/v1/request")
        """
        return request.url.path

    def _build_rate_limit_headers(
        self, limit: int, remaining: int, reset_at_timestamp: int, tier: str
    ) -> dict[str, str]:
        """
        Build rate limit headers for response.

        Args:
            limit: Maximum requests allowed in window
            remaining: Remaining requests in current window
            reset_at_timestamp: Unix timestamp when limit resets
            tier: User's rate limit tier

        Returns:
            Dictionary of headers
        """
        prefix = self.config.header_prefix
        return {
            f"{prefix}Limit": str(limit),
            f"{prefix}Remaining": str(remaining),
            f"{prefix}Reset": str(reset_at_timestamp),
            f"{prefix}Tier": tier,
        }

    def _build_429_response(self, exc: RateLimitExceeded) -> JSONResponse:
        """
        Build HTTP 429 Too Many Requests response.

        Args:
            exc: RateLimitExceeded exception

        Returns:
            JSONResponse with 429 status and Retry-After header
        """
        reset_at = exc.metadata.get("reset_at")
        reset_at_timestamp = int(reset_at) if isinstance(reset_at, int) else 0

        headers = self._build_rate_limit_headers(
            limit=exc.limit,
            remaining=0,
            reset_at_timestamp=reset_at_timestamp,
            tier=exc.tier,
        )
        headers["Retry-After"] = str(exc.retry_after_seconds)

        body = {
            "error": {
                "code": "rate_limit_exceeded",
                "message": str(exc),
                "details": {
                    "limit": exc.limit,
                    "window_size": exc.window_size_seconds,
                    "reset_at": exc.metadata.get("reset_at_iso"),
                    "retry_after_seconds": exc.retry_after_seconds,
                    "tier": exc.tier,
                    "endpoint": exc.endpoint,
                },
            }
        }

        return JSONResponse(status_code=429, content=body, headers=headers)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        """
        Middleware dispatch: check rate limit and inject headers.

        Args:
            request: FastAPI request object
            call_next: Next middleware in chain

        Returns:
            Response with rate limit headers
        """
        # Skip rate limiting if disabled
        if not self.config.enabled:
            return await call_next(request)

        # Extract identifier, tier, and endpoint
        identifier = self._extract_identifier(request)
        tier = self._extract_tier(request, identifier)
        endpoint = self._extract_endpoint(request)

        # Check if whitelisted (FR-015: no headers for whitelisted)
        if identifier in self.config.whitelist:
            logger.debug(f"Whitelisted identifier bypassing rate limit: {identifier}")
            return await call_next(request)

        try:
            # Check rate limit
            result = await self.limiter.check(identifier, endpoint, tier)

            if not result.allowed:
                # Rate limit exceeded - return 429
                logger.warning(
                    f"Rate limit exceeded: {identifier} ({tier}) on {endpoint} "
                    f"({result.state.current_count}/{result.state.limit})"
                )

                exc = RateLimitExceeded(
                    message=f"Rate limit exceeded. Please retry after {result.state.retry_after_seconds} seconds.",
                    limit=result.state.limit,
                    current_count=result.state.current_count,
                    window_size_seconds=result.state.window_size_seconds,
                    retry_after_seconds=result.state.retry_after_seconds,
                    tier=result.state.tier,
                    endpoint=result.state.endpoint,
                    identifier=identifier,
                    reset_at=int(result.state.reset_at.timestamp()),
                    reset_at_iso=result.state.reset_at.isoformat(),
                )

                return self._build_429_response(exc)

            # Rate limit OK - proceed with request
            logger.debug(
                f"Rate limit OK: {identifier} ({tier}) on {endpoint} "
                f"({result.state.current_count}/{result.state.limit})"
            )

            response = await call_next(request)

            # Inject rate limit headers (FR-009: all responses)
            reset_at_timestamp = int(result.state.reset_at.timestamp())
            headers = self._build_rate_limit_headers(
                limit=result.state.limit,
                remaining=result.state.remaining,
                reset_at_timestamp=reset_at_timestamp,
                tier=result.state.tier,
            )

            for key, value in headers.items():
                response.headers[key] = value

            return response

        except Exception as e:
            logger.error(f"Error during rate limit check: {e}")
            # If fail_open, allow request; otherwise, propagate error
            if self.config.fail_open:
                logger.warning(
                    f"Allowing request due to rate limiter error (fail_open=True): {e}"
                )
                return await call_next(request)
            else:
                # Return 500 Internal Server Error
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": {
                            "code": "rate_limiter_error",
                            "message": "Rate limiting system unavailable",
                        }
                    },
                )
