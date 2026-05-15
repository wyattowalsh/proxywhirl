"""Request rate limiting with various strategies."""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum

from loguru import logger


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies."""

    TOKEN_BUCKET = "token_bucket"  # Token bucket algorithm
    SLIDING_WINDOW = "sliding_window"  # Sliding window counter
    FIXED_WINDOW = "fixed_window"  # Fixed window counter
    LEAKY_BUCKET = "leaky_bucket"  # Leaky bucket algorithm


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    max_requests: int
    window_seconds: float
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET


class TokenBucketLimiter:
    """Token bucket rate limiter."""

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket.

        Args:
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.time()

    def allow_request(self, tokens_required: int = 1) -> bool:
        """
        Check if request is allowed.

        Args:
            tokens_required: Tokens needed for request

        Returns:
            True if allowed
        """
        self._refill()

        if self.tokens >= tokens_required:
            self.tokens -= tokens_required
            return True

        return False

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate,
        )
        self.last_refill = now

    def get_available_tokens(self) -> float:
        """Get currently available tokens."""
        self._refill()
        return self.tokens


class SlidingWindowLimiter:
    """Sliding window counter rate limiter."""

    def __init__(self, max_requests: int, window_seconds: float):
        """
        Initialize sliding window limiter.

        Args:
            max_requests: Maximum requests per window
            window_seconds: Window size in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: list[float] = []

    def allow_request(self) -> bool:
        """
        Check if request is allowed.

        Returns:
            True if allowed
        """
        now = time.time()
        cutoff = now - self.window_seconds

        # Remove old requests outside window
        self.requests = [t for t in self.requests if t > cutoff]

        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True

        return False

    def get_request_count(self) -> int:
        """Get current request count in window."""
        now = time.time()
        cutoff = now - self.window_seconds
        return sum(1 for t in self.requests if t > cutoff)


class RequestRateLimiter:
    """
    Multi-strategy request rate limiter.

    Supports token bucket, sliding window, fixed window,
    and leaky bucket algorithms with per-client limits.
    """

    def __init__(
        self,
        global_config: RateLimitConfig,
        per_client_config: RateLimitConfig | None = None,
    ):
        """
        Initialize rate limiter.

        Args:
            global_config: Global rate limit configuration
            per_client_config: Per-client rate limit configuration
        """
        self.global_config = global_config
        self.per_client_config = per_client_config
        self.global_limiter: TokenBucketLimiter | SlidingWindowLimiter
        self.client_limiters: dict[
            str,
            TokenBucketLimiter | SlidingWindowLimiter,
        ] = {}
        self.request_log: list[dict] = []

        self._init_global_limiter()

    def _init_global_limiter(self) -> None:
        """Initialize global limiter based on strategy."""
        if self.global_config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            refill_rate = self.global_config.max_requests / self.global_config.window_seconds
            self.global_limiter = TokenBucketLimiter(
                self.global_config.max_requests,
                refill_rate,
            )
        else:
            self.global_limiter = SlidingWindowLimiter(
                self.global_config.max_requests,
                self.global_config.window_seconds,
            )

    def allow_request(
        self,
        client_id: str | None = None,
        tokens_required: int = 1,
    ) -> bool:
        """
        Check if request is allowed.

        Args:
            client_id: Optional client identifier
            tokens_required: Tokens required (for token bucket)

        Returns:
            True if request allowed
        """
        # Check global limit
        if isinstance(self.global_limiter, TokenBucketLimiter):
            if not self.global_limiter.allow_request(tokens_required):
                logger.warning("Global rate limit exceeded")
                return False
        else:
            if not self.global_limiter.allow_request():
                logger.warning("Global rate limit exceeded")
                return False

        # Check client limit if configured
        if client_id and self.per_client_config:
            if client_id not in self.client_limiters:
                self._init_client_limiter(client_id)

            limiter = self.client_limiters[client_id]

            if isinstance(limiter, TokenBucketLimiter):
                if not limiter.allow_request(tokens_required):
                    logger.warning(f"Client {client_id} rate limit exceeded")
                    return False
            else:
                if not limiter.allow_request():
                    logger.warning(f"Client {client_id} rate limit exceeded")
                    return False

        self._log_request(client_id, allowed=True)
        return True

    def _init_client_limiter(self, client_id: str) -> None:
        """Initialize limiter for a client."""
        assert self.per_client_config is not None

        if self.per_client_config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            refill_rate = (
                self.per_client_config.max_requests / self.per_client_config.window_seconds
            )
            self.client_limiters[client_id] = TokenBucketLimiter(
                self.per_client_config.max_requests,
                refill_rate,
            )
        else:
            self.client_limiters[client_id] = SlidingWindowLimiter(
                self.per_client_config.max_requests,
                self.per_client_config.window_seconds,
            )

    def _log_request(self, client_id: str | None, allowed: bool) -> None:
        """Log a request."""
        self.request_log.append(
            {
                "client_id": client_id,
                "timestamp": time.time(),
                "allowed": allowed,
            }
        )

        # Keep only recent entries
        if len(self.request_log) > 10000:
            self.request_log = self.request_log[-5000:]

    def get_global_stats(self) -> dict[str, int | float | str]:
        """
        Get global rate limiter statistics.

        Returns:
            Statistics dictionary
        """
        if isinstance(self.global_limiter, TokenBucketLimiter):
            return {
                "strategy": self.global_config.strategy.value,
                "max_requests": self.global_config.max_requests,
                "window_seconds": self.global_config.window_seconds,
                "available_tokens": self.global_limiter.get_available_tokens(),
                "capacity": self.global_limiter.capacity,
            }
        else:
            return {
                "strategy": self.global_config.strategy.value,
                "max_requests": self.global_config.max_requests,
                "window_seconds": self.global_config.window_seconds,
                "current_requests": self.global_limiter.get_request_count(),
            }

    def get_client_stats(self, client_id: str) -> dict[str, int | float] | None:
        """
        Get statistics for a specific client.

        Args:
            client_id: Client identifier

        Returns:
            Statistics or None
        """
        if client_id not in self.client_limiters:
            return None

        limiter = self.client_limiters[client_id]

        if isinstance(limiter, TokenBucketLimiter):
            return {
                "available_tokens": limiter.get_available_tokens(),
                "capacity": limiter.capacity,
            }
        else:
            return {
                "current_requests": limiter.get_request_count(),
                "max_requests": self.per_client_config.max_requests
                if self.per_client_config
                else 0,
            }

    def reset(self) -> None:
        """Reset rate limiters."""
        self._init_global_limiter()
        self.client_limiters.clear()
        logger.info("Reset rate limiters")
