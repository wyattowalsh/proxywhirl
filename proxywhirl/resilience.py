"""Resilience patterns and failure handling."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from loguru import logger


class FailureMode(str, Enum):
    """Types of failures to handle."""

    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    AUTH_ERROR = "auth_error"
    RATE_LIMIT = "rate_limit"
    PROXY_ERROR = "proxy_error"
    VALIDATION_ERROR = "validation_error"
    UNKNOWN = "unknown"


@dataclass
class FailureRecord:
    """Record of a failure."""

    mode: FailureMode
    message: str
    timestamp: float = 0.0
    retryable: bool = False
    details: dict = field(default_factory=dict)


class BulkheadPattern:
    """
    Bulkhead pattern for isolating failures.

    Divides resources into separate compartments to prevent
    cascading failures across the system.
    """

    def __init__(self, max_concurrent: int = 10):
        """
        Initialize bulkhead.

        Args:
            max_concurrent: Maximum concurrent operations per compartment
        """
        self.max_concurrent = max_concurrent
        self.active_count = 0
        self.compartments: dict[str, int] = {}

    def acquire(self, compartment_id: str) -> bool:
        """
        Acquire a resource in a compartment.

        Args:
            compartment_id: Compartment identifier

        Returns:
            True if acquired, False if at capacity
        """
        if self.active_count >= self.max_concurrent:
            return False

        if compartment_id not in self.compartments:
            self.compartments[compartment_id] = 0

        self.compartments[compartment_id] += 1
        self.active_count += 1
        return True

    def release(self, compartment_id: str) -> None:
        """
        Release a resource in a compartment.

        Args:
            compartment_id: Compartment identifier
        """
        if compartment_id in self.compartments and self.compartments[compartment_id] > 0:
            self.compartments[compartment_id] -= 1
            self.active_count -= 1

    def get_utilization(self, compartment_id: str | None = None) -> dict | float:
        """
        Get resource utilization.

        Args:
            compartment_id: Specific compartment or None for all

        Returns:
            Utilization percentage or dict of percentages
        """
        if compartment_id:
            count = self.compartments.get(compartment_id, 0)
            return count / self.max_concurrent * 100 if self.max_concurrent > 0 else 0

        return {cid: count / self.max_concurrent * 100 for cid, count in self.compartments.items()}


class FailureDetector:
    """
    Failure detector for rapid failure identification.

    Tracks failures and can determine if a service is degraded.
    """

    def __init__(self, window_size: int = 100, error_threshold_percent: float = 50.0):
        """
        Initialize failure detector.

        Args:
            window_size: Number of operations to track
            error_threshold_percent: Error percentage to trigger degradation alert
        """
        self.window_size = window_size
        self.error_threshold_percent = error_threshold_percent
        self.failure_records: list[FailureRecord] = []
        self.success_count = 0
        self.failure_count = 0

    def record_failure(
        self,
        mode: FailureMode,
        message: str = "",
        retryable: bool = False,
    ) -> None:
        """
        Record a failure.

        Args:
            mode: Type of failure
            message: Failure message
            retryable: Whether failure is retryable
        """
        record = FailureRecord(
            mode=mode,
            message=message,
            retryable=retryable,
        )

        self.failure_records.append(record)
        self.failure_count += 1

        if len(self.failure_records) > self.window_size:
            self.failure_records.pop(0)

        logger.warning(f"Failure recorded: {mode.value} - {message}")

    def record_success(self) -> None:
        """Record a successful operation."""
        self.success_count += 1

    def is_degraded(self) -> bool:
        """
        Check if service is degraded.

        Returns:
            True if error rate exceeds threshold
        """
        total = self.success_count + self.failure_count
        if total == 0:
            return False

        error_rate = self.failure_count / total * 100
        return error_rate >= self.error_threshold_percent

    def get_failure_rate(self) -> float:
        """
        Get current failure rate.

        Returns:
            Failure percentage
        """
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0

        return self.failure_count / total * 100

    def get_failure_modes(self) -> dict[str, int]:
        """
        Get count of failures by mode.

        Returns:
            Dictionary of failure mode counts
        """
        counts: dict[str, int] = {}
        for record in self.failure_records:
            counts[record.mode.value] = counts.get(record.mode.value, 0) + 1

        return counts

    def reset(self) -> None:
        """Reset failure tracking."""
        self.failure_records = []
        self.success_count = 0
        self.failure_count = 0


class AdaptiveTimeout:
    """
    Adaptive timeout based on system load.

    Automatically adjusts timeout values based on observed
    response times and system conditions.
    """

    def __init__(self, base_timeout: float = 5.0, max_timeout: float = 30.0):
        """
        Initialize adaptive timeout.

        Args:
            base_timeout: Base timeout in seconds
            max_timeout: Maximum timeout in seconds
        """
        self.base_timeout = base_timeout
        self.max_timeout = max_timeout
        self.response_times: list[float] = []
        self.window_size = 100

    def record_response_time(self, elapsed_seconds: float) -> None:
        """
        Record a response time.

        Args:
            elapsed_seconds: Response time in seconds
        """
        self.response_times.append(elapsed_seconds)

        if len(self.response_times) > self.window_size:
            self.response_times.pop(0)

    def get_current_timeout(self) -> float:
        """
        Get current recommended timeout.

        Returns:
            Timeout in seconds
        """
        if not self.response_times:
            return self.base_timeout

        # Calculate p95 of response times
        sorted_times = sorted(self.response_times)
        idx = int(len(sorted_times) * 0.95)
        p95 = sorted_times[idx] if idx < len(sorted_times) else self.base_timeout

        # Add 50% buffer
        timeout = p95 * 1.5

        # Clamp to [base, max]
        return min(max(timeout, self.base_timeout), self.max_timeout)

    def is_slow(self) -> bool:
        """
        Check if system is slow.

        Returns:
            True if response times are elevated
        """
        current_timeout = self.get_current_timeout()
        return current_timeout > self.base_timeout * 1.5


class GracefulDegradation:
    """
    Graceful degradation strategies.

    Allows system to degrade services gracefully instead of failing.
    """

    def __init__(self):
        """Initialize graceful degradation manager."""
        self.disabled_services: set[str] = set()
        self.reduced_features: dict[str, list[str]] = {}

    def disable_service(self, service_name: str) -> None:
        """
        Disable a service.

        Args:
            service_name: Service name
        """
        self.disabled_services.add(service_name)
        logger.warning(f"Service disabled: {service_name}")

    def enable_service(self, service_name: str) -> None:
        """
        Re-enable a service.

        Args:
            service_name: Service name
        """
        self.disabled_services.discard(service_name)
        logger.info(f"Service re-enabled: {service_name}")

    def is_service_enabled(self, service_name: str) -> bool:
        """
        Check if service is enabled.

        Args:
            service_name: Service name

        Returns:
            True if enabled
        """
        return service_name not in self.disabled_services

    def reduce_features(self, service_name: str, feature_names: list[str]) -> None:
        """
        Reduce features for a service.

        Args:
            service_name: Service name
            feature_names: Features to disable
        """
        self.reduced_features[service_name] = feature_names
        logger.warning(f"Features reduced for {service_name}: {', '.join(feature_names)}")

    def get_available_features(self, service_name: str, all_features: list[str]) -> list[str]:
        """
        Get available features for a service.

        Args:
            service_name: Service name
            all_features: All possible features

        Returns:
            List of available features
        """
        reduced = self.reduced_features.get(service_name, [])
        return [f for f in all_features if f not in reduced]
