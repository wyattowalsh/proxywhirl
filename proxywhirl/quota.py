"""Proxy quota tracking - limit requests per proxy (soft/hard limits).

Implements soft limits (warnings) and hard limits (enforce) for proxy usage.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from loguru import logger


@dataclass
class QuotaLimit:
    """Quota limit configuration."""

    max_requests: int
    window_seconds: int
    soft_limit_percent: float = 0.8  # Warn at 80%
    hard_limit_percent: float = 1.0  # Enforce at 100%

    def calculate_soft_limit(self) -> int:
        """Calculate soft limit threshold."""
        return int(self.max_requests * self.soft_limit_percent)

    def calculate_hard_limit(self) -> int:
        """Calculate hard limit threshold."""
        return int(self.max_requests * self.hard_limit_percent)


@dataclass
class ProxyQuota:
    """Quota tracking for a single proxy."""

    proxy_id: str
    limit: QuotaLimit
    request_count: int = 0
    window_start: datetime = field(default_factory=datetime.now)
    soft_limit_reached: bool = False
    hard_limit_reached: bool = False
    last_reset_at: datetime = field(default_factory=datetime.now)

    def is_window_expired(self) -> bool:
        """Check if quota window has expired."""
        expiry = self.window_start + timedelta(seconds=self.limit.window_seconds)
        return datetime.now() > expiry

    def reset_if_needed(self) -> None:
        """Reset quota if window expired."""
        if self.is_window_expired():
            self.request_count = 0
            self.window_start = datetime.now()
            self.soft_limit_reached = False
            self.hard_limit_reached = False
            self.last_reset_at = datetime.now()

    def increment(self) -> tuple[bool, bool]:
        """Increment request count.

        Returns:
            (soft_limit_hit, hard_limit_hit) tuple
        """
        self.reset_if_needed()
        self.request_count += 1

        soft_limit = self.limit.calculate_soft_limit()
        hard_limit = self.limit.calculate_hard_limit()

        soft_hit = self.request_count == soft_limit
        hard_hit = self.request_count >= hard_limit

        if soft_hit:
            self.soft_limit_reached = True

        if hard_hit:
            self.hard_limit_reached = True

        return soft_hit, hard_hit

    def can_request(self) -> bool:
        """Check if proxy can handle another request."""
        self.reset_if_needed()
        hard_limit = self.limit.calculate_hard_limit()
        return self.request_count < hard_limit

    def get_remaining_quota(self) -> int:
        """Get remaining requests in current window."""
        self.reset_if_needed()
        hard_limit = self.limit.calculate_hard_limit()
        return max(0, hard_limit - self.request_count)

    def get_usage_percent(self) -> float:
        """Get current usage as percentage."""
        self.reset_if_needed()
        hard_limit = self.limit.calculate_hard_limit()
        return (self.request_count / hard_limit * 100) if hard_limit > 0 else 0.0


class QuotaManager:
    """Manages quotas for multiple proxies."""

    def __init__(self) -> None:
        """Initialize quota manager."""
        self.quotas: dict[str, ProxyQuota] = {}
        self.default_limit: Optional[QuotaLimit] = None

    def set_default_limit(self, limit: QuotaLimit) -> None:
        """Set default quota limit for new proxies."""
        self.default_limit = limit
        logger.debug(f"Set default quota limit: {limit.max_requests} per {limit.window_seconds}s")

    def set_proxy_limit(
        self,
        proxy_id: str,
        max_requests: int,
        window_seconds: int,
        soft_limit_percent: float = 0.8,
    ) -> None:
        """Set quota limit for specific proxy."""
        limit = QuotaLimit(
            max_requests=max_requests,
            window_seconds=window_seconds,
            soft_limit_percent=soft_limit_percent,
        )
        self.quotas[proxy_id] = ProxyQuota(proxy_id=proxy_id, limit=limit)
        logger.debug(f"Set quota limit for {proxy_id}: {max_requests} per {window_seconds}s")

    def get_quota(self, proxy_id: str) -> Optional[ProxyQuota]:
        """Get quota for proxy."""
        if proxy_id in self.quotas:
            return self.quotas[proxy_id]

        if self.default_limit:
            self.quotas[proxy_id] = ProxyQuota(proxy_id=proxy_id, limit=self.default_limit)
            return self.quotas[proxy_id]

        return None

    def record_request(self, proxy_id: str) -> tuple[bool, bool]:
        """Record a request for proxy.

        Returns:
            (soft_limit_reached, hard_limit_reached) tuple
        """
        quota = self.get_quota(proxy_id)

        if not quota:
            logger.warning(f"No quota configured for {proxy_id}")
            return False, False

        soft_hit, hard_hit = quota.increment()

        if soft_hit:
            logger.warning(f"Soft quota limit reached for {proxy_id}")

        if hard_hit:
            logger.error(f"Hard quota limit reached for {proxy_id}")

        return soft_hit, hard_hit

    def can_request(self, proxy_id: str) -> bool:
        """Check if proxy can handle another request."""
        quota = self.get_quota(proxy_id)

        if not quota:
            return True  # No quota configured

        return quota.can_request()

    def get_status(self, proxy_id: str) -> dict:
        """Get quota status for proxy."""
        quota = self.get_quota(proxy_id)

        if not quota:
            return {"proxy_id": proxy_id, "configured": False}

        quota.reset_if_needed()

        return {
            "proxy_id": proxy_id,
            "configured": True,
            "request_count": quota.request_count,
            "max_requests": quota.limit.max_requests,
            "remaining": quota.get_remaining_quota(),
            "usage_percent": quota.get_usage_percent(),
            "soft_limit_reached": quota.soft_limit_reached,
            "hard_limit_reached": quota.hard_limit_reached,
            "window_expires_at": (
                quota.window_start + timedelta(seconds=quota.limit.window_seconds)
            ).isoformat(),
        }

    def get_all_stats(self) -> dict[str, dict]:
        """Get quota status for all proxies."""
        return {pid: self.get_status(pid) for pid in self.quotas}

    def reset_proxy_quota(self, proxy_id: str) -> bool:
        """Reset quota for specific proxy."""
        quota = self.get_quota(proxy_id)

        if quota:
            quota.reset_if_needed()
            quota.request_count = 0
            logger.debug(f"Reset quota for {proxy_id}")
            return True

        return False

    def cleanup_expired_windows(self) -> int:
        """Trigger window resets for all expired quotas."""
        count = 0

        for quota in self.quotas.values():
            if quota.is_window_expired():
                quota.reset_if_needed()
                count += 1

        if count > 0:
            logger.debug(f"Reset {count} expired quota windows")

        return count


class AdaptiveQuotaManager(QuotaManager):
    """Adaptive quota manager that adjusts limits based on usage patterns."""

    def __init__(self) -> None:
        """Initialize adaptive quota manager."""
        super().__init__()
        self.usage_history: dict[str, list] = {}

    def record_request(self, proxy_id: str) -> tuple[bool, bool]:
        """Record request and track usage."""
        if proxy_id not in self.usage_history:
            self.usage_history[proxy_id] = []

        self.usage_history[proxy_id].append(datetime.now())

        # Clean old history (older than 1 hour)
        cutoff = datetime.now() - timedelta(hours=1)
        self.usage_history[proxy_id] = [t for t in self.usage_history[proxy_id] if t > cutoff]

        return super().record_request(proxy_id)

    def adjust_quota(self, proxy_id: str, multiplier: float) -> None:
        """Adjust quota limit by multiplier."""
        quota = self.get_quota(proxy_id)

        if quota:
            quota.limit.max_requests = int(quota.limit.max_requests * multiplier)
            logger.info(f"Adjusted quota for {proxy_id}: multiplier={multiplier}")

    def auto_adjust_quotas(self) -> None:
        """Auto-adjust quotas based on usage patterns."""
        for proxy_id, history in self.usage_history.items():
            if len(history) < 5:
                continue

            # Calculate recent usage rate
            quota = self.get_quota(proxy_id)
            if not quota:
                continue

            usage_percent = quota.get_usage_percent()

            # Increase quota if consistently using <50%
            if usage_percent < 50:
                self.adjust_quota(proxy_id, 1.1)
            # Decrease quota if consistently using >95%
            elif usage_percent > 95:
                self.adjust_quota(proxy_id, 0.9)
