"""Gradual rollout system for ProxyWhirl.

Supports canary deployments, blue-green deployments,
and gradual traffic shifting for new proxy sources.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from loguru import logger


class RolloutStrategy(str, Enum):
    """Rollout strategy types."""

    CANARY = "canary"
    BLUE_GREEN = "blue_green"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


@dataclass
class RolloutPhase:
    """Represents a rollout phase."""

    name: str
    traffic_percentage: float
    duration_seconds: int | None = None
    success_threshold: float = 0.95

    def __post_init__(self) -> None:
        """Validate phase configuration."""
        if not 0 <= self.traffic_percentage <= 100:
            msg = "traffic_percentage must be between 0 and 100"
            raise ValueError(msg)


class RolloutConfig:
    """Configuration for a gradual rollout."""

    def __init__(
        self,
        name: str,
        strategy: RolloutStrategy,
        phases: list[RolloutPhase],
    ) -> None:
        """Initialize rollout configuration.

        Args:
            name: Rollout name
            strategy: Rollout strategy
            phases: List of rollout phases
        """
        self.name = name
        self.strategy = strategy
        self.phases = phases
        self.created_at = datetime.now(timezone.utc)

    def validate(self) -> bool:
        """Validate rollout configuration.

        Returns:
            True if valid
        """
        if not self.phases:
            logger.error(f"Rollout {self.name} has no phases")
            return False

        if self.phases[-1].traffic_percentage < 100:
            logger.error(f"Rollout {self.name} final phase must be 100%")
            return False

        return True


@dataclass
class RolloutState:
    """Tracks rollout state."""

    name: str
    current_phase: int = 0
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    phase_started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    requests_processed: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    status: str = "running"

    def get_success_rate(self) -> float:
        """Get success rate.

        Returns:
            Success rate (0-100)
        """
        if self.requests_processed == 0:
            return 0.0
        return (self.successful_requests / self.requests_processed) * 100

    def record_request(self, success: bool) -> None:
        """Record a request result.

        Args:
            success: Whether request succeeded
        """
        self.requests_processed += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1


class RolloutManager:
    """Manages gradual rollouts of new proxy sources."""

    def __init__(self) -> None:
        """Initialize rollout manager."""
        self._rollouts: dict[str, RolloutConfig] = {}
        self._states: dict[str, RolloutState] = {}
        logger.debug("RolloutManager initialized")

    def create_rollout(self, config: RolloutConfig) -> bool:
        """Create a new rollout.

        Args:
            config: Rollout configuration

        Returns:
            True if created, False if invalid
        """
        if not config.validate():
            return False

        self._rollouts[config.name] = config
        self._states[config.name] = RolloutState(name=config.name)
        logger.info(f"Rollout created: {config.name}")
        return True

    def get_traffic_percentage(self, name: str) -> float:
        """Get current traffic percentage for rollout.

        Args:
            name: Rollout name

        Returns:
            Traffic percentage (0-100)
        """
        if name not in self._states:
            return 0.0

        state = self._states[name]
        rollout = self._rollouts.get(name)

        if not rollout or state.current_phase >= len(rollout.phases):
            return 0.0

        phase = rollout.phases[state.current_phase]
        return phase.traffic_percentage

    def should_advance_phase(self, name: str) -> bool:
        """Check if rollout should advance to next phase.

        Args:
            name: Rollout name

        Returns:
            True if should advance
        """
        if name not in self._states:
            return False

        state = self._states[name]
        rollout = self._rollouts.get(name)

        if not rollout or state.current_phase >= len(rollout.phases) - 1:
            return False

        phase = rollout.phases[state.current_phase]

        # Check success threshold
        if phase.success_threshold > 0 and state.get_success_rate() < phase.success_threshold:
            logger.warning(
                f"Rollout {name} failed success threshold "
                f"({state.get_success_rate():.1f}% < {phase.success_threshold * 100:.0f}%)"
            )
            return False

        # Check duration if specified
        if phase.duration_seconds:
            elapsed = (datetime.now(timezone.utc) - state.phase_started_at).total_seconds()
            if elapsed < phase.duration_seconds:
                return False

        return True

    def advance_phase(self, name: str) -> bool:
        """Advance rollout to next phase.

        Args:
            name: Rollout name

        Returns:
            True if advanced
        """
        if not self.should_advance_phase(name):
            return False

        state = self._states[name]
        state.current_phase += 1
        state.phase_started_at = datetime.now(timezone.utc)
        logger.info(f"Rollout {name} advanced to phase {state.current_phase}")
        return True

    def record_request(self, name: str, success: bool) -> None:
        """Record request for rollout.

        Args:
            name: Rollout name
            success: Whether request succeeded
        """
        if name in self._states:
            self._states[name].record_request(success)

    def get_rollout_status(self, name: str) -> dict[str, Any] | None:
        """Get rollout status.

        Args:
            name: Rollout name

        Returns:
            Dictionary with status or None
        """
        if name not in self._states:
            return None

        state = self._states[name]
        rollout = self._rollouts.get(name)

        return {
            "name": name,
            "strategy": rollout.strategy.value if rollout else None,
            "current_phase": state.current_phase,
            "total_phases": len(rollout.phases) if rollout else 0,
            "traffic_percentage": self.get_traffic_percentage(name),
            "requests_processed": state.requests_processed,
            "success_rate": state.get_success_rate(),
            "status": state.status,
        }
