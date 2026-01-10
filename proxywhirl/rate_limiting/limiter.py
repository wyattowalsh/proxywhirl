"""Core rate limiter implementation using pyrate-limiter."""

from __future__ import annotations

import asyncio
import threading

from loguru import logger
from pyrate_limiter import Duration, Limiter, Rate
from pyrate_limiter.limiter import BucketFullException

from proxywhirl.rate_limiting.models import RateLimit


class RateLimiter:
    """Rate limiter with per-proxy and global limits using pyrate-limiter.

    DEPRECATED: Use AsyncRateLimiter for async contexts or SyncRateLimiter for sync contexts.
    This class maintains backwards compatibility by using threading.RLock.
    """

    def __init__(
        self,
        global_limit: RateLimit | None = None,
    ) -> None:
        """Initialize rate limiter."""
        self.global_limit = global_limit
        self._proxy_limiters: dict[str, Limiter] = {}
        self._global_limiter: Limiter | None = None
        self._lock = threading.RLock()  # Use threading lock for backwards compatibility

        if global_limit:
            rate = Rate(global_limit.max_requests, Duration.SECOND * global_limit.time_window)
            self._global_limiter = Limiter(rate)

    def set_proxy_limit(self, proxy_id: str, limit: RateLimit) -> None:
        """Set rate limit for a specific proxy."""
        rate = Rate(limit.max_requests, Duration.SECOND * limit.time_window)
        with self._lock:
            self._proxy_limiters[proxy_id] = Limiter(rate)
        logger.info(f"Set rate limit for {proxy_id}: {limit.max_requests} req/{limit.time_window}s")

    def check_limit(self, proxy_id: str) -> bool:
        """Check if request is allowed for proxy."""
        # Check per-proxy limit
        with self._lock:
            limiter = self._proxy_limiters.get(proxy_id)

        if limiter:
            try:
                limiter.try_acquire(proxy_id)
            except BucketFullException:
                logger.warning(f"Rate limit exceeded for proxy {proxy_id}")
                return False

        # Check global limit
        if self._global_limiter:
            try:
                self._global_limiter.try_acquire("global")
            except BucketFullException:
                logger.warning("Global rate limit exceeded")
                return False

        return True

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
        self._proxy_limiters: dict[str, Limiter] = {}
        self._global_limiter: Limiter | None = None
        self._lock: asyncio.Lock | None = None  # Lazy-initialized

        if global_limit:
            rate = Rate(global_limit.max_requests, Duration.SECOND * global_limit.time_window)
            self._global_limiter = Limiter(rate)

    def _get_lock(self) -> asyncio.Lock:
        """Get or create async lock. Lazy initialization to avoid event loop issues."""
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def set_proxy_limit(self, proxy_id: str, limit: RateLimit) -> None:
        """Set rate limit for a specific proxy."""
        rate = Rate(limit.max_requests, Duration.SECOND * limit.time_window)
        async with self._get_lock():
            self._proxy_limiters[proxy_id] = Limiter(rate)
        logger.info(f"Set rate limit for {proxy_id}: {limit.max_requests} req/{limit.time_window}s")

    async def check_limit(self, proxy_id: str) -> bool:
        """Check if request is allowed for proxy."""
        # Check per-proxy limit
        async with self._get_lock():
            limiter = self._proxy_limiters.get(proxy_id)

        if limiter:
            try:
                limiter.try_acquire(proxy_id)
            except BucketFullException:
                logger.warning(f"Rate limit exceeded for proxy {proxy_id}")
                return False

        # Check global limit
        if self._global_limiter:
            try:
                self._global_limiter.try_acquire("global")
            except BucketFullException:
                logger.warning("Global rate limit exceeded")
                return False

        return True

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
        self._proxy_limiters: dict[str, Limiter] = {}
        self._global_limiter: Limiter | None = None
        self._lock = threading.RLock()

        if global_limit:
            rate = Rate(global_limit.max_requests, Duration.SECOND * global_limit.time_window)
            self._global_limiter = Limiter(rate)

    def set_proxy_limit(self, proxy_id: str, limit: RateLimit) -> None:
        """Set rate limit for a specific proxy."""
        rate = Rate(limit.max_requests, Duration.SECOND * limit.time_window)
        with self._lock:
            self._proxy_limiters[proxy_id] = Limiter(rate)
        logger.info(f"Set rate limit for {proxy_id}: {limit.max_requests} req/{limit.time_window}s")

    def check_limit(self, proxy_id: str) -> bool:
        """Check if request is allowed for proxy."""
        # Check per-proxy limit
        with self._lock:
            limiter = self._proxy_limiters.get(proxy_id)

        if limiter:
            try:
                limiter.try_acquire(proxy_id)
            except BucketFullException:
                logger.warning(f"Rate limit exceeded for proxy {proxy_id}")
                return False

        # Check global limit
        if self._global_limiter:
            try:
                self._global_limiter.try_acquire("global")
            except BucketFullException:
                logger.warning("Global rate limit exceeded")
                return False

        return True

    def acquire(self, proxy_id: str) -> bool:
        """Acquire permission to make a request."""
        return self.check_limit(proxy_id)
