"""Regression test suite framework for ProxyWhirl.

Detects performance regressions, API compatibility changes,
and functional regressions across versions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from loguru import logger


class RegressionType(str, Enum):
    """Types of regressions to detect."""

    PERFORMANCE = "performance"
    MEMORY = "memory"
    API_COMPATIBILITY = "api_compatibility"
    FUNCTIONAL = "functional"
    LATENCY = "latency"


@dataclass
class Baseline:
    """Represents a baseline measurement."""

    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"{self.name}: {self.value} {self.unit}"


@dataclass
class RegressionResult:
    """Represents a regression test result."""

    test_name: str
    regression_type: RegressionType
    baseline: float
    current: float
    unit: str
    threshold: float
    is_regressed: bool
    diff_percentage: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BaselineStore:
    """Stores and retrieves baseline measurements."""

    def __init__(self) -> None:
        """Initialize baseline store."""
        self._baselines: dict[str, Baseline] = {}
        logger.debug("BaselineStore initialized")

    def save_baseline(self, baseline: Baseline) -> None:
        """Save a baseline measurement.

        Args:
            baseline: Baseline to save
        """
        self._baselines[baseline.name] = baseline
        logger.debug(f"Baseline saved: {baseline.name}")

    def get_baseline(self, name: str) -> Baseline | None:
        """Get a baseline measurement.

        Args:
            name: Baseline name

        Returns:
            Baseline object or None if not found
        """
        return self._baselines.get(name)

    def clear_baseline(self, name: str) -> bool:
        """Clear a baseline measurement.

        Args:
            name: Baseline name

        Returns:
            True if cleared, False if not found
        """
        if name in self._baselines:
            del self._baselines[name]
            logger.debug(f"Baseline cleared: {name}")
            return True
        return False

    def get_all_baselines(self) -> dict[str, Baseline]:
        """Get all baselines.

        Returns:
            Dictionary of baselines
        """
        return self._baselines.copy()


class RegressionDetector:
    """Detects regressions in measurements."""

    def __init__(self, baseline_store: BaselineStore | None = None) -> None:
        """Initialize regression detector.

        Args:
            baseline_store: Optional baseline store
        """
        self.baseline_store = baseline_store or BaselineStore()
        self._results: list[RegressionResult] = []

    def detect_performance_regression(
        self,
        test_name: str,
        baseline_value: float,
        current_value: float,
        unit: str = "ms",
        threshold: float = 0.1,
    ) -> RegressionResult:
        """Detect performance regression.

        Args:
            test_name: Name of test
            baseline_value: Baseline measurement value
            current_value: Current measurement value
            unit: Unit of measurement
            threshold: Regression threshold (0.1 = 10%)

        Returns:
            RegressionResult
        """
        diff_percentage = (current_value - baseline_value) / baseline_value
        is_regressed = diff_percentage > threshold

        result = RegressionResult(
            test_name=test_name,
            regression_type=RegressionType.PERFORMANCE,
            baseline=baseline_value,
            current=current_value,
            unit=unit,
            threshold=threshold,
            is_regressed=is_regressed,
            diff_percentage=diff_percentage,
        )

        self._results.append(result)

        if is_regressed:
            logger.warning(
                f"Performance regression detected: {test_name} "
                f"({baseline_value} → {current_value} {unit}, {diff_percentage * 100:.1f}%)"
            )
        else:
            logger.debug(f"No regression: {test_name}")

        return result

    def detect_memory_regression(
        self,
        test_name: str,
        baseline_value: float,
        current_value: float,
        threshold: float = 0.15,
    ) -> RegressionResult:
        """Detect memory regression.

        Args:
            test_name: Name of test
            baseline_value: Baseline memory (MB)
            current_value: Current memory (MB)
            threshold: Regression threshold

        Returns:
            RegressionResult
        """
        result = self.detect_performance_regression(
            test_name, baseline_value, current_value, unit="MB", threshold=threshold
        )
        result.regression_type = RegressionType.MEMORY
        return result

    def detect_latency_regression(
        self,
        test_name: str,
        baseline_value: float,
        current_value: float,
        percentile: int = 95,
        threshold: float = 0.05,
    ) -> RegressionResult:
        """Detect latency regression at given percentile.

        Args:
            test_name: Name of test
            baseline_value: Baseline latency (ms)
            current_value: Current latency (ms)
            percentile: Latency percentile
            threshold: Regression threshold

        Returns:
            RegressionResult
        """
        result = self.detect_performance_regression(
            test_name,
            baseline_value,
            current_value,
            unit=f"ms (p{percentile})",
            threshold=threshold,
        )
        result.regression_type = RegressionType.LATENCY
        return result

    def get_results(self, regressed_only: bool = False) -> list[RegressionResult]:
        """Get regression results.

        Args:
            regressed_only: Only return regressed tests

        Returns:
            List of RegressionResult
        """
        if regressed_only:
            return [r for r in self._results if r.is_regressed]
        return self._results.copy()

    def clear_results(self) -> None:
        """Clear all results."""
        self._results.clear()

    def summary(self) -> dict[str, Any]:
        """Get summary of regression results.

        Returns:
            Dictionary with summary statistics
        """
        total = len(self._results)
        regressed = len([r for r in self._results if r.is_regressed])
        return {
            "total_tests": total,
            "regressed_tests": regressed,
            "pass_rate": ((total - regressed) / total * 100) if total > 0 else 0,
            "regressions": [
                {
                    "test": r.test_name,
                    "type": r.regression_type.value,
                    "diff_percentage": r.diff_percentage * 100,
                }
                for r in self._results
                if r.is_regressed
            ],
        }
