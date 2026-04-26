"""Circuit breaker configuration and tuning utilities.

Provides advanced configuration options for fine-tuning circuit breaker behavior
for different proxy scenarios and failure patterns.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal

from loguru import logger


class FailurePattern(str, Enum):
    """Common failure patterns for circuit breaker tuning."""

    AGGRESSIVE = "aggressive"  # Fast failure detection, quick recovery
    NORMAL = "normal"  # Balanced detection and recovery
    LENIENT = "lenient"  # Slow failure detection, gradual recovery
    ADAPTIVE = "adaptive"  # Auto-adjust based on error patterns


@dataclass
class CircuitBreakerTuningConfig:
    """Advanced circuit breaker tuning configuration."""

    # State thresholds
    failure_threshold: int = 5  # Failures before opening circuit
    success_threshold: int = 2  # Successes needed to close circuit
    timeout: float = 60.0  # Timeout before trying half-open (seconds)

    # Window configuration
    window_size: int = 100  # Number of requests in rolling window
    time_window: float = 60.0  # Time window in seconds

    # Failure rate thresholds
    failure_rate_threshold: float = 0.5  # Open circuit at 50% failure rate
    minimum_requests_for_threshold: int = 10  # Min requests before checking rate

    # Half-open probe configuration
    half_open_max_calls: int = 1  # Max calls allowed in half-open state
    half_open_probe_interval: float = 10.0  # Interval between half-open probes

    # Recovery configuration
    exponential_backoff: bool = True
    backoff_multiplier: float = 2.0
    max_backoff: float = 300.0  # 5 minutes

    # Event tracking
    track_latency: bool = True
    latency_threshold: float = 5.0  # Seconds before considering timeout
    latency_percentile: float = 95.0  # P95 latency for degradation

    # Alerting
    alert_on_open: bool = True
    alert_on_degradation: bool = True

    # Metrics
    enable_metrics: bool = True
    metrics_namespace: str = "proxywhirl_circuit_breaker"

    @classmethod
    def from_pattern(cls, pattern: FailurePattern) -> CircuitBreakerTuningConfig:
        """Create configuration from predefined failure pattern.

        Args:
            pattern: Failure pattern to use

        Returns:
            Configured CircuitBreakerTuningConfig
        """
        patterns = {
            FailurePattern.AGGRESSIVE: {
                "failure_threshold": 2,
                "success_threshold": 1,
                "timeout": 10.0,
                "half_open_max_calls": 3,
                "backoff_multiplier": 1.5,
            },
            FailurePattern.NORMAL: {
                "failure_threshold": 5,
                "success_threshold": 2,
                "timeout": 60.0,
                "half_open_max_calls": 1,
                "backoff_multiplier": 2.0,
            },
            FailurePattern.LENIENT: {
                "failure_threshold": 10,
                "success_threshold": 5,
                "timeout": 300.0,
                "half_open_max_calls": 1,
                "backoff_multiplier": 3.0,
            },
            FailurePattern.ADAPTIVE: {
                "failure_threshold": 5,
                "success_threshold": 2,
                "timeout": 60.0,
                "exponential_backoff": True,
                "enable_metrics": True,
            },
        }

        config_dict = patterns.get(pattern, {})
        return cls(**config_dict)

    def validate(self) -> bool:
        """Validate configuration consistency.

        Returns:
            True if configuration is valid
        """
        issues = []

        if self.failure_threshold <= 0:
            issues.append("failure_threshold must be positive")

        if self.success_threshold <= 0:
            issues.append("success_threshold must be positive")

        if self.timeout <= 0:
            issues.append("timeout must be positive")

        if not (0.0 < self.failure_rate_threshold < 1.0):
            issues.append("failure_rate_threshold must be between 0 and 1")

        if self.half_open_max_calls <= 0:
            issues.append("half_open_max_calls must be positive")

        if self.backoff_multiplier < 1.0:
            issues.append("backoff_multiplier must be >= 1.0")

        if self.max_backoff <= self.timeout:
            issues.append("max_backoff should be greater than timeout")

        if issues:
            for issue in issues:
                logger.error(f"Configuration validation error: {issue}")
            return False

        return True


class CircuitBreakerTuner:
    """Automatically tune circuit breaker based on observed metrics."""

    def __init__(self, base_config: CircuitBreakerTuningConfig):
        """Initialize tuner.

        Args:
            base_config: Base configuration to tune from
        """
        self.base_config = base_config
        self.current_config = base_config
        self.metrics = {
            "total_calls": 0,
            "failures": 0,
            "timeouts": 0,
            "latencies": [],
        }

    def record_call(self, success: bool, latency: float | None = None) -> None:
        """Record a call outcome.

        Args:
            success: Whether call was successful
            latency: Call latency in seconds
        """
        self.metrics["total_calls"] += 1
        if not success:
            self.metrics["failures"] += 1
        if latency and latency > self.base_config.latency_threshold:
            self.metrics["timeouts"] += 1
        if latency:
            self.metrics["latencies"].append(latency)

    def suggest_adjustments(self) -> CircuitBreakerTuningConfig:
        """Suggest configuration adjustments based on metrics.

        Returns:
            Suggested configuration
        """
        total = self.metrics["total_calls"]
        if total < 10:
            return self.current_config

        failure_rate = self.metrics["failures"] / total
        timeout_rate = self.metrics["timeouts"] / total

        config_updates = {}

        # Adjust failure threshold based on failure rate
        if failure_rate > 0.7:
            # Too many failures, lower threshold
            config_updates["failure_threshold"] = max(
                2,
                self.current_config.failure_threshold - 1,
            )
        elif failure_rate < 0.1:
            # Few failures, can raise threshold
            config_updates["failure_threshold"] = (
                self.current_config.failure_threshold + 1
            )

        # Adjust timeout based on latency
        if self.metrics["latencies"]:
            p95_latency = sorted(self.metrics["latencies"])[
                int(len(self.metrics["latencies"]) * 0.95)
            ]
            if p95_latency > self.current_config.timeout * 0.8:
                config_updates["timeout"] = min(
                    self.current_config.max_backoff,
                    self.current_config.timeout * 1.5,
                )

        # Adjust backoff based on timeout rate
        if timeout_rate > 0.5:
            config_updates["max_backoff"] = (
                self.current_config.max_backoff * 1.5
            )
            config_updates["backoff_multiplier"] = min(
                4.0,
                self.current_config.backoff_multiplier * 1.2,
            )

        # Create new config with updates
        if config_updates:
            import copy

            new_config = copy.copy(self.current_config)
            for key, value in config_updates.items():
                setattr(new_config, key, value)

            if new_config.validate():
                self.current_config = new_config
                logger.info(f"Suggested adjustments: {config_updates}")
                return new_config

        return self.current_config

    def reset_metrics(self) -> None:
        """Reset collected metrics."""
        self.metrics = {
            "total_calls": 0,
            "failures": 0,
            "timeouts": 0,
            "latencies": [],
        }

    def get_metrics(self) -> dict:
        """Get current metrics.

        Returns:
            Dictionary of metrics
        """
        return self.metrics.copy()
