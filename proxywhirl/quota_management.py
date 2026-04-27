"""Usage quota management system for ProxyWhirl.

Tracks per-user, per-session, and per-source quota consumption
with configurable limits, reset schedules, and enforcement strategies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from loguru import logger
from pydantic import BaseModel, ConfigDict, Field, field_validator


class QuotaType(str, Enum):
    """Types of quotas that can be enforced."""

    REQUESTS = "requests"
    BANDWIDTH = "bandwidth"
    SESSIONS = "sessions"
    CONCURRENCY = "concurrency"
    API_CALLS = "api_calls"


class QuotaPeriod(str, Enum):
    """Reset periods for quotas."""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    UNLIMITED = "unlimited"


@dataclass
class QuotaLimit:
    """Represents a quota limit configuration."""

    limit: int
    period: QuotaPeriod
    enforce: bool = True
    warning_threshold: float = 0.8
    soft_limit: bool = False

    def is_exceeded(self, current_usage: int) -> bool:
        """Check if usage has exceeded the limit."""
        return current_usage > self.limit if self.enforce else False

    def warning_level(self, current_usage: int) -> bool:
        """Check if usage has reached warning threshold."""
        threshold = int(self.limit * self.warning_threshold)
        return current_usage >= threshold


@dataclass
class QuotaUsage:
    """Tracks quota usage for a specific quota type."""

    quota_type: QuotaType
    current_usage: int = 0
    limit: int = 0
    reset_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    period: QuotaPeriod = QuotaPeriod.DAILY
    last_reset: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def increment(self, amount: int = 1) -> None:
        """Increment usage counter."""
        self.current_usage += amount

    def should_reset(self) -> bool:
        """Check if quota should reset based on period."""
        if self.period == QuotaPeriod.UNLIMITED:
            return False

        now = datetime.now(timezone.utc)
        period_map = {
            QuotaPeriod.HOURLY: timedelta(hours=1),
            QuotaPeriod.DAILY: timedelta(days=1),
            QuotaPeriod.WEEKLY: timedelta(weeks=1),
            QuotaPeriod.MONTHLY: timedelta(days=30),
        }

        elapsed = now - self.last_reset
        return elapsed > period_map.get(self.period, timedelta(days=1))

    def reset(self) -> None:
        """Reset usage counter."""
        self.current_usage = 0
        self.last_reset = datetime.now(timezone.utc)

    def percentage_used(self) -> float:
        """Get percentage of quota used."""
        if self.limit == 0:
            return 0.0
        return (self.current_usage / self.limit) * 100


class QuotaConfig(BaseModel):
    """Configuration for quota management."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    quota_type: QuotaType
    period: QuotaPeriod = QuotaPeriod.DAILY
    limit: int = Field(gt=0)
    enforce: bool = True
    warning_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    soft_limit: bool = False
    alert_enabled: bool = True

    @field_validator("period")
    @classmethod
    def validate_period(cls, v: QuotaPeriod) -> QuotaPeriod:
        """Validate period is not unlimited for managed quotas."""
        if v == QuotaPeriod.UNLIMITED:
            msg = "Unlimited period requires manual quota management"
            raise ValueError(msg)
        return v


class QuotaManager:
    """Manages quota allocation and enforcement across users and sessions."""

    def __init__(self) -> None:
        """Initialize quota manager."""
        self._quotas: dict[str, dict[QuotaType, QuotaUsage]] = {}
        self._limits: dict[QuotaType, QuotaLimit] = {}
        logger.debug("QuotaManager initialized")

    def register_quota(self, entity_id: str, config: QuotaConfig) -> None:
        """Register a quota for an entity (user, session, etc)."""
        if entity_id not in self._quotas:
            self._quotas[entity_id] = {}

        usage = QuotaUsage(
            quota_type=config.quota_type,
            limit=config.limit,
            period=config.period,
        )
        self._quotas[entity_id][config.quota_type] = usage
        self._limits[config.quota_type] = QuotaLimit(
            limit=config.limit,
            period=config.period,
            enforce=config.enforce,
            warning_threshold=config.warning_threshold,
            soft_limit=config.soft_limit,
        )
        logger.debug(f"Quota registered for {entity_id}: {config.quota_type}")

    def consume_quota(self, entity_id: str, quota_type: QuotaType, amount: int = 1) -> bool:
        """Consume quota for an entity.

        Args:
            entity_id: Entity identifier
            quota_type: Type of quota to consume
            amount: Amount to consume

        Returns:
            True if quota consumed successfully, False if limit exceeded
        """
        if entity_id not in self._quotas:
            logger.warning(f"No quota registered for {entity_id}")
            return False

        if quota_type not in self._quotas[entity_id]:
            logger.warning(f"No {quota_type} quota for {entity_id}")
            return False

        usage = self._quotas[entity_id][quota_type]

        if usage.should_reset():
            usage.reset()
            logger.debug(f"Quota reset for {entity_id}: {quota_type}")

        limit = self._limits.get(quota_type)
        if limit and limit.is_exceeded(usage.current_usage + amount):
            logger.warning(
                f"Quota exceeded for {entity_id}: {quota_type} "
                f"({usage.current_usage + amount}/{usage.limit})"
            )
            return False

        usage.increment(amount)

        if limit and limit.warning_level(usage.current_usage):
            logger.info(
                f"Quota warning for {entity_id}: {quota_type} at {usage.percentage_used():.1f}%"
            )

        return True

    def get_usage(self, entity_id: str, quota_type: QuotaType) -> QuotaUsage | None:
        """Get current usage for a quota.

        Args:
            entity_id: Entity identifier
            quota_type: Type of quota

        Returns:
            QuotaUsage object or None if not found
        """
        return self._quotas.get(entity_id, {}).get(quota_type)

    def get_all_usage(self, entity_id: str) -> dict[QuotaType, QuotaUsage]:
        """Get all quota usage for an entity.

        Args:
            entity_id: Entity identifier

        Returns:
            Dictionary of quota types to usage
        """
        return self._quotas.get(entity_id, {}).copy()

    def reset_quota(self, entity_id: str, quota_type: QuotaType) -> bool:
        """Manually reset a quota.

        Args:
            entity_id: Entity identifier
            quota_type: Type of quota

        Returns:
            True if reset successful, False otherwise
        """
        if entity_id not in self._quotas:
            return False

        if quota_type not in self._quotas[entity_id]:
            return False

        self._quotas[entity_id][quota_type].reset()
        logger.info(f"Quota manually reset for {entity_id}: {quota_type}")
        return True

    def set_limit(self, quota_type: QuotaType, limit: int, period: QuotaPeriod) -> None:
        """Set a new limit for a quota type.

        Args:
            quota_type: Type of quota
            limit: New limit value
            period: Reset period
        """
        self._limits[quota_type] = QuotaLimit(
            limit=limit,
            period=period,
        )
        logger.info(f"Quota limit updated: {quota_type} = {limit}/{period.value}")

    def export_metrics(self, entity_id: str) -> dict[str, Any]:
        """Export quota metrics for an entity.

        Args:
            entity_id: Entity identifier

        Returns:
            Dictionary of quota metrics
        """
        metrics = {}
        for quota_type, usage in self._quotas.get(entity_id, {}).items():
            metrics[quota_type.value] = {
                "current_usage": usage.current_usage,
                "limit": usage.limit,
                "period": usage.period.value,
                "percentage_used": usage.percentage_used(),
                "last_reset": usage.last_reset.isoformat(),
            }
        return metrics
