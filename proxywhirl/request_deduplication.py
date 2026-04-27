"""Request deduplication and caching."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable

from loguru import logger


@dataclass
class DedupEntry:
    """Deduplication entry for a request."""

    key: str
    result: Any
    timestamp: datetime = field(default_factory=datetime.now)
    ttl_seconds: int = 300


class RequestDeduplicator:
    """Deduplicates duplicate requests within a time window."""

    def __init__(self, ttl_seconds: int = 300, max_entries: int = 1000):
        """Initialize deduplicator.

        Args:
            ttl_seconds: Time-to-live for entries
            max_entries: Maximum entries to keep
        """
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._cache: dict[str, DedupEntry] = {}
        self._stats = {"hits": 0, "misses": 0, "evictions": 0}

    def _generate_key(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        include_body: bool = False,
        body: Any = None,
    ) -> str:
        """Generate cache key.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            include_body: Whether to include body in key
            body: Request body

        Returns:
            Cache key
        """
        key_parts = [method.upper(), url]

        if params:
            sorted_params = sorted(params.items())
            key_parts.append(str(sorted_params))

        if include_body and body:
            key_parts.append(str(body))

        key_str = "|".join(key_parts)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def get(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
    ) -> Any | None:
        """Get cached result if available.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters

        Returns:
            Cached result or None
        """
        key = self._generate_key(method, url, params)

        if key in self._cache:
            entry = self._cache[key]

            # Check if expired
            if datetime.now() - entry.timestamp > timedelta(seconds=entry.ttl_seconds):
                del self._cache[key]
                self._stats["misses"] += 1
                return None

            self._stats["hits"] += 1
            logger.debug(f"Request dedup cache hit: {method} {url}")
            return entry.result

        self._stats["misses"] += 1
        return None

    def set(
        self,
        method: str,
        url: str,
        result: Any,
        params: dict[str, Any] | None = None,
        ttl_seconds: int | None = None,
    ) -> None:
        """Cache a result.

        Args:
            method: HTTP method
            url: Request URL
            result: Result to cache
            params: Query parameters
            ttl_seconds: TTL override
        """
        key = self._generate_key(method, url, params)

        entry = DedupEntry(
            key=key,
            result=result,
            ttl_seconds=ttl_seconds or self.ttl_seconds,
        )

        self._cache[key] = entry

        # Enforce size limit
        if len(self._cache) > self.max_entries:
            # Remove oldest entry
            oldest_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k].timestamp,
            )
            del self._cache[oldest_key]
            self._stats["evictions"] += 1

    def clear(self) -> None:
        """Clear all cache."""
        self._cache.clear()
        logger.info("Cleared request dedup cache")

    def cleanup_expired(self) -> int:
        """Remove expired entries.

        Returns:
            Number of entries removed
        """
        now = datetime.now()
        expired_keys = [
            key
            for key, entry in self._cache.items()
            if now - entry.timestamp > timedelta(seconds=entry.ttl_seconds)
        ]

        for key in expired_keys:
            del self._cache[key]

        logger.debug(f"Cleaned up {len(expired_keys)} expired dedup entries")
        return len(expired_keys)

    def get_statistics(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Statistics dict
        """
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total * 100) if total > 0 else 0

        return {
            "entries": len(self._cache),
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "evictions": self._stats["evictions"],
            "hit_rate_percent": hit_rate,
        }


class DedupDecorator:
    """Decorator to add request deduplication to functions."""

    def __init__(self, dedup: RequestDeduplicator):
        """Initialize decorator.

        Args:
            dedup: RequestDeduplicator instance
        """
        self.dedup = dedup

    def __call__(self, func: Callable) -> Callable:
        """Decorate a function."""

        def wrapper(
            method: str,
            url: str,
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            # Try cache first
            result = self.dedup.get(method, url, kwargs.get("params"))
            if result is not None:
                return result

            # Call function
            result = func(method, url, *args, **kwargs)

            # Cache result
            self.dedup.set(method, url, result, kwargs.get("params"))

            return result

        return wrapper
