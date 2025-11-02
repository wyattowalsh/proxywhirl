"""
Rate limiting core logic with sliding window counter algorithm.

Implements atomic rate limit checks using Redis Lua scripts for
distributed enforcement across multiple API instances.
"""

import asyncio
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import DefaultDict, Dict, Optional, Tuple
from uuid import uuid4

from loguru import logger
from redis import Redis
from redis.asyncio import Redis as AsyncRedis
from redis.asyncio import ConnectionPool as AsyncConnectionPool
from redis.exceptions import RedisError
from tenacity import retry, stop_after_attempt, wait_exponential

from proxywhirl.rate_limit_models import (
    RateLimitConfig,
    RateLimitResult,
    RateLimitState,
)


# Lua script for atomic sliding window counter check-and-increment
# This script runs atomically in Redis to prevent race conditions
SLIDING_WINDOW_LUA = """
local key = KEYS[1]
local now_ms = tonumber(ARGV[1])
local window_size_ms = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local req_id = ARGV[4]

-- Calculate window start time
local window_start_ms = now_ms - window_size_ms

-- Remove expired entries (outside current window)
redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start_ms)

-- Count requests in current window
local current_count = redis.call('ZCARD', key)

-- Check if limit exceeded
if current_count >= limit then
    -- Set TTL to 2x window size for cleanup
    redis.call('EXPIRE', key, math.ceil(window_size_ms / 500))
    return {0, current_count, window_start_ms}
end

-- Add current request to sorted set
redis.call('ZADD', key, now_ms, req_id)

-- Set TTL to 2x window size for cleanup
redis.call('EXPIRE', key, math.ceil(window_size_ms / 500))

-- Return success with updated count
return {1, current_count + 1, window_start_ms}
"""


class InMemoryRateLimitStore:
    """
    In-memory rate limit store for testing/single-instance mode.

    Uses sorted lists to simulate Redis sorted sets.
    Thread-safe with asyncio locks.
    """

    def __init__(self) -> None:
        """Initialize in-memory store with thread-safe locks."""
        self._store: DefaultDict[str, list[Tuple[int, str]]] = defaultdict(list)
        self._locks: DefaultDict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def check_and_increment(
        self,
        key: str,
        now_ms: int,
        window_size_ms: int,
        limit: int,
        req_id: str,
    ) -> Tuple[bool, int, int]:
        """
        Check rate limit and increment counter atomically.

        Args:
            key: Rate limit key
            now_ms: Current timestamp (milliseconds)
            window_size_ms: Window size (milliseconds)
            limit: Maximum requests allowed
            req_id: Unique request ID

        Returns:
            Tuple of (allowed, current_count, window_start_ms)
        """
        async with self._locks[key]:
            window_start_ms = now_ms - window_size_ms

            # Remove expired entries
            self._store[key] = [
                (ts, rid) for ts, rid in self._store[key] if ts > window_start_ms
            ]

            current_count = len(self._store[key])

            # Check if limit exceeded
            if current_count >= limit:
                return (False, current_count, window_start_ms)

            # Add current request
            self._store[key].append((now_ms, req_id))
            return (True, current_count + 1, window_start_ms)


class RateLimiter:
    """
    Rate limiter with sliding window counter algorithm.

    Supports Redis for distributed state and in-memory fallback.
    Implements atomic rate limit checks with Lua scripts.
    """

    def __init__(self, config: RateLimitConfig) -> None:
        """
        Initialize rate limiter.

        Args:
            config: Rate limit configuration
        """
        self.config = config
        self._redis: Optional[AsyncRedis] = None
        self._redis_pool: Optional[AsyncConnectionPool] = None
        self._script_sha: Optional[str] = None
        self._memory_store = InMemoryRateLimitStore()
        self._use_redis = config.redis_enabled

        # Initialize Redis connection if enabled
        if self._use_redis:
            self._setup_redis()

    def _setup_redis(self) -> None:
        """Setup Redis connection pool and load Lua script."""
        try:
            # Create async Redis connection pool
            self._redis_pool = AsyncConnectionPool.from_url(
                self.config.redis_url.get_secret_value(),
                max_connections=50,
                decode_responses=False,
            )
            self._redis = AsyncRedis(connection_pool=self._redis_pool)
            logger.info("Redis connection pool initialized for rate limiting")
        except Exception as e:
            logger.error(f"Failed to setup Redis for rate limiting: {e}")
            if not self.config.fail_open:
                raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True,
    )
    async def _load_lua_script(self) -> str:
        """
        Load Lua script into Redis.

        Returns:
            SHA1 hash of loaded script

        Raises:
            RedisError: If Redis is unavailable and fail_open=False
        """
        if not self._redis:
            raise RedisError("Redis not initialized")

        script_sha = await self._redis.script_load(SLIDING_WINDOW_LUA)
        logger.debug(f"Loaded rate limit Lua script: {script_sha}")
        return str(script_sha)

    async def _ensure_script_loaded(self) -> str:
        """Ensure Lua script is loaded in Redis."""
        if not self._script_sha:
            self._script_sha = await self._load_lua_script()
        return self._script_sha

    def _build_key(self, identifier: str, endpoint: str) -> str:
        """
        Build Redis key for rate limit state.

        Args:
            identifier: User ID or IP address
            endpoint: API endpoint path

        Returns:
            Redis key (format: ratelimit:{identifier}:{endpoint})
        """
        return f"ratelimit:{identifier}:{endpoint}"

    def _get_effective_limit(
        self, tier_name: str, endpoint: str
    ) -> Tuple[int, int]:
        """
        Calculate effective rate limit for tier + endpoint.

        Applies most restrictive limit (FR-008).

        Args:
            tier_name: Rate limit tier name
            endpoint: API endpoint path

        Returns:
            Tuple of (requests_per_window, window_size_seconds)

        Raises:
            ValueError: If tier not found
        """
        tier_config = self.config.get_tier_config(tier_name)
        if not tier_config:
            raise ValueError(f"Tier '{tier_name}' not found in configuration")

        # Start with tier-level limit
        limit = tier_config.requests_per_window
        window_size = tier_config.window_size_seconds

        # Check for endpoint-specific override
        if endpoint in tier_config.endpoints:
            endpoint_limit = tier_config.endpoints[endpoint]
            # Apply most restrictive limit (FR-008)
            limit = min(limit, endpoint_limit)

        return (limit, window_size)

    async def _check_redis(
        self,
        key: str,
        identifier: str,
        endpoint: str,
        tier: str,
        limit: int,
        window_size_seconds: int,
    ) -> RateLimitResult:
        """
        Check rate limit using Redis.

        Args:
            key: Redis key
            identifier: User ID or IP address
            endpoint: API endpoint path
            tier: Rate limit tier name
            limit: Maximum requests allowed
            window_size_seconds: Window size in seconds

        Returns:
            RateLimitResult with current state

        Raises:
            RedisError: If Redis fails and fail_open=False
        """
        if not self._redis:
            raise RedisError("Redis not initialized")

        try:
            # Load Lua script if not already loaded
            script_sha = await self._ensure_script_loaded()

            # Execute Lua script atomically
            now_ms = int(time.monotonic() * 1000)  # Use monotonic time
            window_size_ms = window_size_seconds * 1000
            req_id = str(uuid4())

            result = await self._redis.evalsha(
                script_sha,
                1,  # Number of keys
                key,
                now_ms,
                window_size_ms,
                limit,
                req_id,
            )

            # Parse Lua script result
            allowed = bool(result[0])
            current_count = int(result[1])
            window_start_ms = int(result[2])

            # Build rate limit state
            reset_at = datetime.now(timezone.utc) + timedelta(
                seconds=window_size_seconds
            )
            state = RateLimitState(
                key=key,
                identifier=identifier,
                endpoint=endpoint,
                tier=tier,
                current_count=current_count,
                limit=limit,
                window_start_ms=window_start_ms,
                window_size_seconds=window_size_seconds,
                reset_at=reset_at,
            )

            return RateLimitResult(
                allowed=allowed,
                state=state,
                reason="rate_limit_exceeded" if not allowed else None,
            )

        except RedisError as e:
            logger.error(f"Redis error during rate limit check: {e}")
            if self.config.fail_open:
                # Fail open: Allow request but log warning
                logger.warning(
                    f"Rate limiting disabled due to Redis error (fail_open=True): {e}"
                )
                return await self._check_memory(
                    key, identifier, endpoint, tier, limit, window_size_seconds
                )
            else:
                # Fail closed: Deny request
                raise

    async def _check_memory(
        self,
        key: str,
        identifier: str,
        endpoint: str,
        tier: str,
        limit: int,
        window_size_seconds: int,
    ) -> RateLimitResult:
        """
        Check rate limit using in-memory store.

        Args:
            key: Store key
            identifier: User ID or IP address
            endpoint: API endpoint path
            tier: Rate limit tier name
            limit: Maximum requests allowed
            window_size_seconds: Window size in seconds

        Returns:
            RateLimitResult with current state
        """
        now_ms = int(time.monotonic() * 1000)  # Use monotonic time
        window_size_ms = window_size_seconds * 1000
        req_id = str(uuid4())

        allowed, current_count, window_start_ms = (
            await self._memory_store.check_and_increment(
                key, now_ms, window_size_ms, limit, req_id
            )
        )

        reset_at = datetime.now(timezone.utc) + timedelta(
            seconds=window_size_seconds
        )
        state = RateLimitState(
            key=key,
            identifier=identifier,
            endpoint=endpoint,
            tier=tier,
            current_count=current_count,
            limit=limit,
            window_start_ms=window_start_ms,
            window_size_seconds=window_size_seconds,
            reset_at=reset_at,
        )

        return RateLimitResult(
            allowed=allowed,
            state=state,
            reason="rate_limit_exceeded" if not allowed else None,
        )

    async def check(
        self,
        identifier: str,
        endpoint: str,
        tier: str,
    ) -> RateLimitResult:
        """
        Check if request is allowed under rate limit.

        This is the main entry point for rate limit enforcement.

        Args:
            identifier: User ID (UUID) or IP address
            endpoint: API endpoint path (e.g., "/api/v1/request")
            tier: Rate limit tier name (e.g., "free", "premium")

        Returns:
            RateLimitResult indicating whether request is allowed

        Raises:
            ValueError: If tier not found in configuration
            RedisError: If Redis fails and fail_open=False
        """
        # Check whitelist (FR-015)
        if identifier in self.config.whitelist:
            # Whitelisted identifiers bypass rate limiting
            # Return dummy state with no actual tracking
            now = datetime.now(timezone.utc)
            state = RateLimitState(
                key=f"ratelimit:{identifier}:{endpoint}",
                identifier=identifier,
                endpoint=endpoint,
                tier="whitelisted",
                current_count=0,
                limit=999999999,
                window_start_ms=int(now.timestamp() * 1000),
                window_size_seconds=1,
                reset_at=now + timedelta(seconds=1),
            )
            return RateLimitResult(allowed=True, state=state)

        # Get effective rate limit for tier + endpoint
        limit, window_size_seconds = self._get_effective_limit(tier, endpoint)

        # Build Redis/memory key
        key = self._build_key(identifier, endpoint)

        # Check rate limit using Redis or in-memory store
        if self._use_redis and self._redis:
            try:
                return await self._check_redis(
                    key, identifier, endpoint, tier, limit, window_size_seconds
                )
            except RedisError as e:
                if self.config.fail_open:
                    logger.warning(f"Falling back to in-memory rate limiting: {e}")
                    return await self._check_memory(
                        key, identifier, endpoint, tier, limit, window_size_seconds
                    )
                else:
                    raise
        else:
            return await self._check_memory(
                key, identifier, endpoint, tier, limit, window_size_seconds
            )

    async def close(self) -> None:
        """Close Redis connection pool."""
        if self._redis:
            await self._redis.close()
        if self._redis_pool:
            await self._redis_pool.disconnect()
        logger.info("Rate limiter Redis connections closed")
