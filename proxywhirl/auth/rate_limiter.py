"""
Per-API-key rate limiting for ProxyWhirl.

Provides granular rate limiting per API key.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass
from threading import Lock

from pydantic import BaseModel, ConfigDict, Field


@dataclass(frozen=True)
class RateLimitQuota:
    """Rate limit quota for an API key."""

    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int


class KeyRateLimiter(BaseModel):
    """Per-API-key rate limiter using token bucket algorithm."""

    default_quota: RateLimitQuota = Field(
        default=RateLimitQuota(
            requests_per_minute=60, requests_per_hour=1000, requests_per_day=10000
        )
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data):
        super().__init__(**data)
        self._buckets: dict[str, dict[str, float]] = defaultdict(
            lambda: {
                "minute": 0.0,
                "hour": 0.0,
                "day": 0.0,
                "reset_minute": 0.0,
                "reset_hour": 0.0,
                "reset_day": 0.0,
            }
        )
        self._key_quotas: dict[str, RateLimitQuota] = {}
        self._lock = Lock()

    def set_quota(self, key_id: str, quota: RateLimitQuota) -> None:
        """Set custom rate limit quota for a key.

        Args:
            key_id: The API key identifier
            quota: The rate limit quota
        """
        with self._lock:
            self._key_quotas[key_id] = quota

    def check_limit(self, key_id: str) -> tuple[bool, dict[str, int]]:
        """Check if request is within rate limit.

        Args:
            key_id: The API key identifier

        Returns:
            Tuple of (allowed: bool, remaining: dict of remaining requests)
        """
        with self._lock:
            quota = self._key_quotas.get(key_id, self.default_quota)
            bucket = self._buckets[key_id]
            current_time = time.time()

            # Reset buckets if windows have expired
            if current_time >= bucket["reset_minute"]:
                bucket["minute"] = 0.0
                bucket["reset_minute"] = current_time + 60

            if current_time >= bucket["reset_hour"]:
                bucket["hour"] = 0.0
                bucket["reset_hour"] = current_time + 3600

            if current_time >= bucket["reset_day"]:
                bucket["day"] = 0.0
                bucket["reset_day"] = current_time + 86400

            # Check all limits
            minute_ok = bucket["minute"] < quota.requests_per_minute
            hour_ok = bucket["hour"] < quota.requests_per_hour
            day_ok = bucket["day"] < quota.requests_per_day

            remaining = {
                "minute": max(0, int(quota.requests_per_minute - bucket["minute"])),
                "hour": max(0, int(quota.requests_per_hour - bucket["hour"])),
                "day": max(0, int(quota.requests_per_day - bucket["day"])),
            }

            if minute_ok and hour_ok and day_ok:
                bucket["minute"] += 1
                bucket["hour"] += 1
                bucket["day"] += 1
                return True, remaining

        return False, remaining

    def get_reset_times(self, key_id: str) -> dict[str, float]:
        """Get reset times for rate limit windows.

        Args:
            key_id: The API key identifier

        Returns:
            Dict with reset times for each window
        """
        with self._lock:
            bucket = self._buckets.get(key_id, {})
            return {
                "minute": bucket.get("reset_minute", 0.0),
                "hour": bucket.get("reset_hour", 0.0),
                "day": bucket.get("reset_day", 0.0),
            }
