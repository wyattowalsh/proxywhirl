"""Core token-bucket rate limiter implementation."""

from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import Callable
from datetime import datetime

from loguru import logger
from pydantic import BaseModel, Field


class RateLimit(BaseModel):
    """Rate limit configuration."""

    max_requests: int = Field(..., ge=1, description="Maximum requests allowed")
    time_window: int = Field(..., ge=1, description="Time window in seconds")
    burst_allowance: int | None = Field(None, ge=0, description="Burst capacity (token bucket)")


class RateLimitEvent(BaseModel):
    """Rate limit event for logging."""

    timestamp: datetime
    proxy_id: str
    event_type: str
    details: dict


class _RateLimitExceededError(Exception):
    """Raised when a token bucket has no immediately available capacity."""


class _TokenBucketLimiter:
    """Thread-safe token bucket with fixed refill rate and optional burst capacity."""

    def __init__(
        self,
        limit: RateLimit,
        *,
        time_fn: Callable[[], float] = time.monotonic,
    ) -> None:
        self._capacity = float(limit.max_requests + (limit.burst_allowance or 0))
        self._refill_rate = float(limit.max_requests) / float(limit.time_window)
        self._tokens = self._capacity
        self._updated_at = time_fn()
        self._time_fn = time_fn
        self._lock = threading.RLock()

    def try_acquire(self, _key: str) -> None:
        """Acquire one token or raise when the bucket is empty."""
        with self._lock:
            now = self._time_fn()
            elapsed = max(0.0, now - self._updated_at)
            self._tokens = min(self._capacity, self._tokens + (elapsed * self._refill_rate))
            self._updated_at = now

            if self._tokens < 1.0:
                raise _RateLimitExceededError

            self._tokens -= 1.0

    def release(self) -> None:
        """Return one token after a multi-bucket acquire fails."""
        with self._lock:
            self._tokens = min(self._capacity, self._tokens + 1.0)


def _make_limiter(
    limit: RateLimit,
    *,
    time_fn: Callable[[], float] = time.monotonic,
) -> _TokenBucketLimiter:
    """Build a token bucket limiter, applying burst as temporary capacity."""
    return _TokenBucketLimiter(limit, time_fn=time_fn)


def _check_token_limits(
    global_limiter: _TokenBucketLimiter | None,
    proxy_limiter: _TokenBucketLimiter | None,
    proxy_id: str,
) -> bool:
    """Acquire proxy and global tokens, refunding proxy quota when global capacity fails."""
    proxy_acquired = False

    if proxy_limiter:
        try:
            proxy_limiter.try_acquire(proxy_id)
            proxy_acquired = True
        except _RateLimitExceededError:
            logger.warning(f"Rate limit exceeded for proxy {proxy_id}")
            return False

    if global_limiter:
        try:
            global_limiter.try_acquire("global")
        except _RateLimitExceededError:
            if proxy_acquired and proxy_limiter:
                proxy_limiter.release()
            logger.warning("Global rate limit exceeded")
            return False

    return True


class RateLimiter:
    """Rate limiter with per-proxy and global token-bucket limits.

    DEPRECATED: Use AsyncRateLimiter for async contexts or SyncRateLimiter for sync contexts.
    This class maintains backwards compatibility by using threading.RLock.
    """

    def __init__(
        self,
        global_limit: RateLimit | None = None,
    ) -> None:
        """Initialize rate limiter."""
        self.global_limit = global_limit
        self._proxy_limiters: dict[str, _TokenBucketLimiter] = {}
        self._global_limiter: _TokenBucketLimiter | None = None
        self._lock = threading.RLock()  # Use threading lock for backwards compatibility

        if global_limit:
            self._global_limiter = _make_limiter(global_limit)

    def set_proxy_limit(self, proxy_id: str, limit: RateLimit) -> None:
        """Set rate limit for a specific proxy."""
        with self._lock:
            self._proxy_limiters[proxy_id] = _make_limiter(limit)
        logger.info(f"Set rate limit for {proxy_id}: {limit.max_requests} req/{limit.time_window}s")

    def check_limit(self, proxy_id: str) -> bool:
        """Check if request is allowed for proxy."""
        with self._lock:
            limiter = self._proxy_limiters.get(proxy_id)

        return _check_token_limits(self._global_limiter, limiter, proxy_id)

    def acquire(self, proxy_id: str) -> bool:
        """Acquire permission to make a request."""
        return self.check_limit(proxy_id)


class AsyncRateLimiter:
    """Async rate limiter for use in async contexts.

    This class provides an async-safe interface using asyncio.Lock.
    Use this class when calling from async functions to avoid blocking the event loop.
    """

    def __init__(
        self,
        global_limit: RateLimit | None = None,
    ) -> None:
        """Initialize async rate limiter."""
        self.global_limit = global_limit
        self._proxy_limiters: dict[str, _TokenBucketLimiter] = {}
        self._global_limiter: _TokenBucketLimiter | None = None
        self._lock: asyncio.Lock | None = None  # Lazy-initialized

        if global_limit:
            self._global_limiter = _make_limiter(global_limit)

    def _get_lock(self) -> asyncio.Lock:
        """Get or create async lock. Lazy initialization to avoid event loop issues."""
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def set_proxy_limit(self, proxy_id: str, limit: RateLimit) -> None:
        """Set rate limit for a specific proxy."""
        async with self._get_lock():
            self._proxy_limiters[proxy_id] = _make_limiter(limit)
        logger.info(f"Set rate limit for {proxy_id}: {limit.max_requests} req/{limit.time_window}s")

    async def check_limit(self, proxy_id: str) -> bool:
        """Check if request is allowed for proxy."""
        async with self._get_lock():
            limiter = self._proxy_limiters.get(proxy_id)

        return _check_token_limits(self._global_limiter, limiter, proxy_id)

    async def acquire(self, proxy_id: str) -> bool:
        """Acquire permission to make a request."""
        return await self.check_limit(proxy_id)


class SyncRateLimiter:
    """Synchronous rate limiter for use in sync contexts.

    This class provides a thread-safe, synchronous interface to rate limiting
    without requiring asyncio.run() calls, which can fail when called from
    an existing event loop or create performance overhead.
    """

    def __init__(
        self,
        global_limit: RateLimit | None = None,
    ) -> None:
        """Initialize synchronous rate limiter."""
        self.global_limit = global_limit
        self._proxy_limiters: dict[str, _TokenBucketLimiter] = {}
        self._global_limiter: _TokenBucketLimiter | None = None
        self._lock = threading.RLock()

        if global_limit:
            self._global_limiter = _make_limiter(global_limit)

    def set_proxy_limit(self, proxy_id: str, limit: RateLimit) -> None:
        """Set rate limit for a specific proxy."""
        with self._lock:
            self._proxy_limiters[proxy_id] = _make_limiter(limit)
        logger.info(f"Set rate limit for {proxy_id}: {limit.max_requests} req/{limit.time_window}s")

    def check_limit(self, proxy_id: str) -> bool:
        """Check if request is allowed for proxy."""
        with self._lock:
            limiter = self._proxy_limiters.get(proxy_id)

        return _check_token_limits(self._global_limiter, limiter, proxy_id)

    def acquire(self, proxy_id: str) -> bool:
        """Acquire permission to make a request."""
        return self.check_limit(proxy_id)
