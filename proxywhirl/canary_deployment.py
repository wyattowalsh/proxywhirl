"""Canary deployment strategy."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from loguru import logger


class CanaryPhase(str, Enum):
    """Canary deployment phases."""

    INITIAL = "initial"
    CANARY = "canary"
    RAMP_UP = "ramp_up"
    FULL_ROLLOUT = "full_rollout"
    COMPLETE = "complete"
    ROLLED_BACK = "rolled_back"


@dataclass
class TrafficAllocation:
    """Traffic allocation between versions."""

    stable_version: str
    canary_version: str
    stable_percentage: int
    canary_percentage: int
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate percentages."""
        if self.stable_percentage + self.canary_percentage != 100:
            raise ValueError("Percentages must sum to 100")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict.

        Returns:
            Allocation dict
        """
        return {
            "stable_version": self.stable_version,
            "canary_version": self.canary_version,
            "stable_percentage": self.stable_percentage,
            "canary_percentage": self.canary_percentage,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class CanaryMetrics:
    """Canary metrics for analysis."""

    error_rate: float = 0.0
    latency_p99: float = 0.0
    success_rate: float = 100.0
    custom_metrics: dict[str, float] = field(default_factory=dict)

    def is_healthy(
        self,
        error_rate_threshold: float = 5.0,
        latency_threshold: float = 1000.0,
    ) -> bool:
        """Check if metrics are healthy.

        Args:
            error_rate_threshold: Max error rate %
            latency_threshold: Max latency ms

        Returns:
            True if healthy
        """
        return (
            self.error_rate <= error_rate_threshold
            and self.latency_p99 <= latency_threshold
            and self.success_rate >= 95.0
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict.

        Returns:
            Metrics dict
        """
        return {
            "error_rate": self.error_rate,
            "latency_p99": self.latency_p99,
            "success_rate": self.success_rate,
            "custom_metrics": self.custom_metrics,
        }


class CanaryDeployment:
    """Canary deployment manager."""

    def __init__(self):
        """Initialize manager."""
        self._phase = CanaryPhase.INITIAL
        self._stable_version = "1.0.0"
        self._canary_version = "1.0.0"
        self._stable_replicas = 3
        self._canary_replicas = 1
        self._traffic_allocation: list[TrafficAllocation] = []
        self._metrics_history: list[CanaryMetrics] = []
        self._started_at: datetime | None = None
        self._ramp_up_stages: list[int] = [10, 25, 50, 75, 100]
        self._current_stage_index = 0

    def start_canary(self, canary_version: str, replicas: int = 1) -> bool:
        """Start canary deployment.

        Args:
            canary_version: Canary version
            replicas: Canary replicas

        Returns:
            True if started
        """
        if self._phase != CanaryPhase.INITIAL:
            return False

        self._canary_version = canary_version
        self._canary_replicas = replicas
        self._phase = CanaryPhase.CANARY
        self._started_at = datetime.now()

        allocation = TrafficAllocation(
            stable_version=self._stable_version,
            canary_version=self._canary_version,
            stable_percentage=90,
            canary_percentage=10,
        )
        self._traffic_allocation.append(allocation)

        logger.info(f"Started canary: {canary_version} with 10% traffic ({replicas} replicas)")

        return True

    def check_canary_health(self, metrics: CanaryMetrics) -> bool:
        """Check canary metrics.

        Args:
            metrics: Canary metrics

        Returns:
            True if healthy
        """
        self._metrics_history.append(metrics)

        if not metrics.is_healthy():
            logger.error(
                f"Canary unhealthy: error_rate={metrics.error_rate}% latency={metrics.latency_p99}ms"
            )
            self._phase = CanaryPhase.ROLLED_BACK
            return False

        logger.info(
            f"Canary healthy: error_rate={metrics.error_rate}% latency={metrics.latency_p99}ms"
        )

        return True

    def ramp_up_canary(self) -> bool:
        """Ramp up traffic to canary.

        Returns:
            True if ramped up
        """
        if self._phase == CanaryPhase.ROLLED_BACK:
            return False

        if self._current_stage_index < len(self._ramp_up_stages):
            canary_percentage = self._ramp_up_stages[self._current_stage_index]

            allocation = TrafficAllocation(
                stable_version=self._stable_version,
                canary_version=self._canary_version,
                stable_percentage=100 - canary_percentage,
                canary_percentage=canary_percentage,
            )
            self._traffic_allocation.append(allocation)

            self._current_stage_index += 1

            if canary_percentage == 100:
                self._phase = CanaryPhase.FULL_ROLLOUT

            logger.info(f"Ramped up canary to {canary_percentage}% traffic")

            return True

        return False

    def complete_deployment(self) -> bool:
        """Complete canary deployment.

        Returns:
            True if completed
        """
        if self._phase != CanaryPhase.FULL_ROLLOUT:
            return False

        self._stable_version = self._canary_version
        self._canary_replicas = 0
        self._phase = CanaryPhase.COMPLETE

        logger.info(f"Canary deployment completed: {self._canary_version} is now stable")

        return True

    def rollback_canary(self) -> bool:
        """Rollback canary deployment.

        Returns:
            True if rolled back
        """
        self._canary_replicas = 0
        self._canary_version = self._stable_version
        self._phase = CanaryPhase.ROLLED_BACK
        self._current_stage_index = 0

        logger.warning(f"Canary rolled back to {self._stable_version}")

        return True

    def get_current_traffic_allocation(self) -> TrafficAllocation | None:
        """Get current traffic allocation.

        Returns:
            Current allocation or None
        """
        if self._traffic_allocation:
            return self._traffic_allocation[-1]
        return None

    def get_latest_metrics(self) -> CanaryMetrics | None:
        """Get latest metrics.

        Returns:
            Latest metrics or None
        """
        if self._metrics_history:
            return self._metrics_history[-1]
        return None

    def get_stats(self) -> dict[str, Any]:
        """Get deployment stats.

        Returns:
            Stats dict
        """
        return {
            "phase": self._phase.value,
            "stable_version": self._stable_version,
            "canary_version": self._canary_version,
            "stable_replicas": self._stable_replicas,
            "canary_replicas": self._canary_replicas,
            "total_allocations": len(self._traffic_allocation),
            "total_metrics": len(self._metrics_history),
            "started_at": self._started_at.isoformat() if self._started_at else None,
        }
