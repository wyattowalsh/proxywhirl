"""Gradual rollout support for new proxies."""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from loguru import logger


class RolloutPhase(str, Enum):
    """Phases of gradual rollout."""

    INITIAL = "initial"
    CANARY = "canary"
    PARTIAL = "partial"
    EXPANDED = "expanded"
    FULL = "full"


@dataclass
class RolloutMetrics:
    """Metrics for rollout monitoring."""

    phase: RolloutPhase
    traffic_percentage: float
    start_time: float
    requests: int = 0
    errors: int = 0
    error_rate: float = 0.0


class GradualRollout:
    """
    Manage gradual rollout of new proxies.

    Implements canary pattern:
    1% -> 10% -> 50% -> 100%
    With error monitoring at each stage.
    """

    def __init__(self, proxy_id: str, initial_traffic_percent: float = 1.0):
        """
        Initialize gradual rollout.

        Args:
            proxy_id: Proxy to gradually roll out
            initial_traffic_percent: Starting traffic percentage
        """
        self.proxy_id = proxy_id
        self.current_traffic_percent = initial_traffic_percent
        self.start_time = time.time()
        self.metrics = RolloutMetrics(
            phase=RolloutPhase.INITIAL,
            traffic_percentage=initial_traffic_percent,
            start_time=self.start_time,
        )
        self.phase_history: list[tuple[RolloutPhase, float, float]] = []  # (phase, %, time)
        self.last_phase_change = time.time()
        self.error_threshold = 0.05  # 5% error rate

    def should_advance_phase(self) -> bool:
        """
        Determine if rollout should advance to next phase.

        Returns:
            True if ready to advance
        """
        if self.metrics.requests < 100:  # Need minimum requests
            return False

        if self.metrics.error_rate > self.error_threshold:
            logger.warning(
                f"Rollout {self.proxy_id}: Error rate {self.metrics.error_rate:.1%} "
                f"exceeds threshold {self.error_threshold:.1%}"
            )
            return False

        # Check if sufficient time has passed (5 minutes minimum)
        return (time.time() - self.last_phase_change) >= 300

    def advance_phase(self) -> bool:
        """
        Advance to the next rollout phase.

        Returns:
            True if advanced, False if already at full rollout
        """
        current_phase = self.metrics.phase
        next_phase = None
        new_traffic = None

        if current_phase == RolloutPhase.INITIAL:
            next_phase = RolloutPhase.CANARY
            new_traffic = 10.0
        elif current_phase == RolloutPhase.CANARY:
            next_phase = RolloutPhase.PARTIAL
            new_traffic = 50.0
        elif current_phase == RolloutPhase.PARTIAL:
            next_phase = RolloutPhase.EXPANDED
            new_traffic = 75.0
        elif current_phase == RolloutPhase.EXPANDED:
            next_phase = RolloutPhase.FULL
            new_traffic = 100.0
        else:
            return False  # Already at full

        self.metrics.phase = next_phase
        self.current_traffic_percent = new_traffic
        self.last_phase_change = time.time()
        self.phase_history.append((current_phase, new_traffic, self.last_phase_change))

        logger.info(f"Rollout {self.proxy_id}: Advanced to {next_phase} ({new_traffic}% traffic)")

        return True

    def record_request(self, success: bool = True) -> None:
        """
        Record a request in the rollout.

        Args:
            success: Whether request was successful
        """
        self.metrics.requests += 1
        if not success:
            self.metrics.errors += 1

        # Update error rate
        if self.metrics.requests > 0:
            self.metrics.error_rate = self.metrics.errors / self.metrics.requests

    def get_traffic_allocation(self) -> float:
        """
        Get current traffic allocation percentage.

        Returns:
            Traffic percentage (0-100)
        """
        return self.current_traffic_percent

    def get_status(self) -> dict[str, float | int | str]:
        """
        Get rollout status.

        Returns:
            Dictionary with status information
        """
        return {
            "proxy_id": self.proxy_id,
            "phase": self.metrics.phase.value,
            "traffic_percent": self.current_traffic_percent,
            "requests": self.metrics.requests,
            "errors": self.metrics.errors,
            "error_rate_percent": self.metrics.error_rate * 100,
            "duration_seconds": time.time() - self.start_time,
        }

    def rollback(self) -> None:
        """Rollback to previous phase."""
        if not self.phase_history:
            logger.warning(f"Rollout {self.proxy_id}: No previous phases to rollback to")
            return

        prev_phase, prev_traffic, _prev_time = self.phase_history.pop()
        self.metrics.phase = prev_phase
        self.current_traffic_percent = prev_traffic
        self.last_phase_change = time.time()

        logger.warning(
            f"Rollout {self.proxy_id}: Rolled back to {prev_phase} ({prev_traffic}% traffic)"
        )

    def is_complete(self) -> bool:
        """
        Check if rollout is complete (100% traffic).

        Returns:
            True if at full rollout
        """
        return self.metrics.phase == RolloutPhase.FULL

    def pause(self) -> None:
        """Pause the rollout."""
        logger.info(f"Rollout {self.proxy_id}: Paused at {self.current_traffic_percent}%")

    def resume(self) -> None:
        """Resume the rollout."""
        logger.info(f"Rollout {self.proxy_id}: Resumed at {self.current_traffic_percent}%")


class RolloutManager:
    """Manage rollouts for multiple proxies."""

    def __init__(self):
        """Initialize rollout manager."""
        self.rollouts: dict[str, GradualRollout] = {}

    def start_rollout(
        self,
        proxy_id: str,
        initial_traffic_percent: float = 1.0,
    ) -> GradualRollout:
        """
        Start a new rollout.

        Args:
            proxy_id: Proxy to rollout
            initial_traffic_percent: Starting traffic percentage

        Returns:
            GradualRollout instance
        """
        rollout = GradualRollout(proxy_id, initial_traffic_percent)
        self.rollouts[proxy_id] = rollout
        logger.info(f"Started rollout for {proxy_id}")
        return rollout

    def get_rollout(self, proxy_id: str) -> GradualRollout | None:
        """
        Get rollout for a proxy.

        Args:
            proxy_id: Proxy identifier

        Returns:
            GradualRollout or None
        """
        return self.rollouts.get(proxy_id)

    def check_all_rollouts(self) -> list[str]:
        """
        Check all rollouts and advance if ready.

        Returns:
            List of proxy_ids that advanced
        """
        advanced = []
        for proxy_id, rollout in self.rollouts.items():
            if rollout.should_advance_phase() and rollout.advance_phase():
                advanced.append(proxy_id)

        return advanced

    def get_traffic_allocation(self, proxy_id: str) -> float:
        """
        Get traffic allocation for a proxy.

        Args:
            proxy_id: Proxy identifier

        Returns:
            Traffic percentage or 0 if not in rollout
        """
        rollout = self.rollouts.get(proxy_id)
        return rollout.get_traffic_allocation() if rollout else 0.0

    def get_all_statuses(self) -> dict[str, dict]:
        """
        Get status for all rollouts.

        Returns:
            Dictionary mapping proxy_id to status
        """
        return {proxy_id: rollout.get_status() for proxy_id, rollout in self.rollouts.items()}
