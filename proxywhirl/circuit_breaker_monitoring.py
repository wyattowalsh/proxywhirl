"""Circuit breaker monitoring and analytics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from loguru import logger


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Blocked operation
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitMetrics:
    """Metrics for a circuit breaker."""

    state: CircuitState = CircuitState.CLOSED
    success_count: int = 0
    failure_count: int = 0
    last_failure_time: float | None = None
    last_success_time: float | None = None
    state_changes: int = 0
    total_requests: int = 0


class CircuitBreakerMonitor:
    """
    Monitor circuit breaker health and state changes.

    Tracks metrics, detects anomalies, and provides insights
    into circuit breaker behavior across the system.
    """

    def __init__(self, num_circuits: int = 10):
        """
        Initialize monitor.

        Args:
            num_circuits: Expected number of circuits to monitor
        """
        self.circuits: dict[str, CircuitMetrics] = {}
        self.state_change_log: list[dict] = []
        self.num_circuits = num_circuits

    def register_circuit(self, circuit_id: str) -> None:
        """
        Register a circuit for monitoring.

        Args:
            circuit_id: Circuit identifier
        """
        if circuit_id not in self.circuits:
            self.circuits[circuit_id] = CircuitMetrics()
            logger.debug(f"Registered circuit: {circuit_id}")

    def record_success(self, circuit_id: str) -> None:
        """
        Record a successful request through circuit.

        Args:
            circuit_id: Circuit identifier
        """
        if circuit_id not in self.circuits:
            self.register_circuit(circuit_id)

        metrics = self.circuits[circuit_id]
        metrics.success_count += 1
        metrics.total_requests += 1

    def record_failure(self, circuit_id: str) -> None:
        """
        Record a failed request through circuit.

        Args:
            circuit_id: Circuit identifier
        """
        if circuit_id not in self.circuits:
            self.register_circuit(circuit_id)

        metrics = self.circuits[circuit_id]
        metrics.failure_count += 1
        metrics.total_requests += 1

    def change_state(
        self,
        circuit_id: str,
        new_state: CircuitState,
        reason: str = "",
    ) -> None:
        """
        Record a state change.

        Args:
            circuit_id: Circuit identifier
            new_state: New circuit state
            reason: Reason for change
        """
        if circuit_id not in self.circuits:
            self.register_circuit(circuit_id)

        metrics = self.circuits[circuit_id]
        old_state = metrics.state

        if old_state != new_state:
            metrics.state = new_state
            metrics.state_changes += 1

            log_entry = {
                "circuit_id": circuit_id,
                "from_state": old_state.value,
                "to_state": new_state.value,
                "reason": reason,
            }

            self.state_change_log.append(log_entry)
            logger.info(
                f"Circuit {circuit_id} changed: {old_state.value} → {new_state.value} ({reason})"
            )

    def get_circuit_metrics(self, circuit_id: str) -> CircuitMetrics | None:
        """
        Get metrics for a circuit.

        Args:
            circuit_id: Circuit identifier

        Returns:
            Circuit metrics or None
        """
        return self.circuits.get(circuit_id)

    def get_failure_rate(self, circuit_id: str) -> float:
        """
        Get failure rate for a circuit.

        Args:
            circuit_id: Circuit identifier

        Returns:
            Failure rate percentage
        """
        if circuit_id not in self.circuits:
            return 0.0

        metrics = self.circuits[circuit_id]

        if metrics.total_requests == 0:
            return 0.0

        return metrics.failure_count / metrics.total_requests * 100

    def get_all_metrics(self) -> dict[str, CircuitMetrics]:
        """
        Get metrics for all circuits.

        Returns:
            Dictionary of circuit metrics
        """
        return self.circuits.copy()

    def get_system_health(self) -> dict[str, int | float]:
        """
        Get overall system health based on circuits.

        Returns:
            Health metrics
        """
        if not self.circuits:
            return {"health_percent": 100.0, "circuits": 0}

        open_count = sum(1 for m in self.circuits.values() if m.state == CircuitState.OPEN)
        half_open_count = sum(
            1 for m in self.circuits.values() if m.state == CircuitState.HALF_OPEN
        )

        total_circuits = len(self.circuits)

        health_percent = (
            (total_circuits - open_count - half_open_count * 0.5) / total_circuits * 100
            if total_circuits > 0
            else 100.0
        )

        return {
            "health_percent": health_percent,
            "total_circuits": total_circuits,
            "open_circuits": open_count,
            "half_open_circuits": half_open_count,
            "closed_circuits": total_circuits - open_count - half_open_count,
        }

    def get_state_change_log(self, limit: int = 100) -> list[dict]:
        """
        Get state change log.

        Args:
            limit: Maximum entries to return

        Returns:
            List of state changes
        """
        return self.state_change_log[-limit:].copy()

    def reset_circuit(self, circuit_id: str) -> None:
        """
        Reset a circuit metrics.

        Args:
            circuit_id: Circuit identifier
        """
        if circuit_id in self.circuits:
            self.circuits[circuit_id] = CircuitMetrics()
            logger.info(f"Reset circuit: {circuit_id}")

    def reset_all(self) -> None:
        """Reset all circuit metrics."""
        self.circuits.clear()
        self.state_change_log.clear()
        logger.info("Reset all circuits")

    def get_anomalies(self) -> list[dict[str, str | int]]:
        """
        Detect anomalies in circuit behavior.

        Returns:
            List of detected anomalies
        """
        anomalies = []

        for circuit_id, metrics in self.circuits.items():
            if metrics.state == CircuitState.OPEN:
                anomalies.append(
                    {
                        "circuit_id": circuit_id,
                        "type": "circuit_open",
                        "severity": "high",
                    }
                )

            if metrics.total_requests > 100:
                failure_rate = self.get_failure_rate(circuit_id)

                if failure_rate > 50:
                    anomalies.append(
                        {
                            "circuit_id": circuit_id,
                            "type": "high_failure_rate",
                            "failure_rate_percent": failure_rate,
                            "severity": "high",
                        }
                    )

                elif failure_rate > 20:
                    anomalies.append(
                        {
                            "circuit_id": circuit_id,
                            "type": "elevated_failure_rate",
                            "failure_rate_percent": failure_rate,
                            "severity": "medium",
                        }
                    )

        return anomalies

    def get_summary_stats(self) -> dict[str, int | float | dict]:
        """
        Get summary statistics.

        Returns:
            Summary statistics
        """
        total_success = sum(m.success_count for m in self.circuits.values())
        total_failure = sum(m.failure_count for m in self.circuits.values())
        total_requests = total_success + total_failure

        return {
            "total_circuits": len(self.circuits),
            "total_requests": total_requests,
            "total_successes": total_success,
            "total_failures": total_failure,
            "overall_failure_rate_percent": (
                total_failure / total_requests * 100 if total_requests > 0 else 0
            ),
            "state_changes": len(self.state_change_log),
            "health": self.get_system_health(),
        }
