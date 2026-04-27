"""A/B testing framework for routing traffic between test and control proxies.

Allows comparing different proxy sources or strategies via randomized trial routing.
"""

import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from loguru import logger

from proxywhirl.models import ProxyPool


class ExperimentStatus(str, Enum):
    """Status of an A/B test experiment."""

    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ExperimentVariant:
    """A variant in A/B test (control or treatment)."""

    name: str
    pool: ProxyPool
    traffic_percent: float
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time_ms: float = 0.0

    def record_success(self, response_time_ms: float) -> None:
        """Record successful request."""
        self.total_requests += 1
        self.successful_requests += 1
        self.total_response_time_ms += response_time_ms

    def record_failure(self) -> None:
        """Record failed request."""
        self.total_requests += 1
        self.failed_requests += 1

    def get_success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    def get_avg_response_time(self) -> float:
        """Get average response time."""
        if self.successful_requests == 0:
            return 0.0
        return self.total_response_time_ms / self.successful_requests


@dataclass
class ABExperiment:
    """A/B test experiment configuration and results."""

    experiment_id: str
    control: ExperimentVariant
    treatment: ExperimentVariant
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    status: ExperimentStatus = ExperimentStatus.RUNNING
    significance_threshold: float = 0.05  # 5% significance level

    def is_running(self) -> bool:
        """Check if experiment is running."""
        return self.status == ExperimentStatus.RUNNING

    def get_results(self) -> dict:
        """Get experiment results."""
        return {
            "experiment_id": self.experiment_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "control": {
                "name": self.control.name,
                "total_requests": self.control.total_requests,
                "successful": self.control.successful_requests,
                "failed": self.control.failed_requests,
                "success_rate": self.control.get_success_rate(),
                "avg_response_time_ms": self.control.get_avg_response_time(),
            },
            "treatment": {
                "name": self.treatment.name,
                "total_requests": self.treatment.total_requests,
                "successful": self.treatment.successful_requests,
                "failed": self.treatment.failed_requests,
                "success_rate": self.treatment.get_success_rate(),
                "avg_response_time_ms": self.treatment.get_avg_response_time(),
            },
        }

    def calculate_difference(self) -> tuple[float, str]:
        """Calculate difference between variants.

        Returns:
            (difference_percent, winner) tuple
        """
        control_rate = self.control.get_success_rate()
        treatment_rate = self.treatment.get_success_rate()
        diff = treatment_rate - control_rate

        if diff > 0:
            winner = f"{self.treatment.name} wins by {abs(diff):.2f}%"
        elif diff < 0:
            winner = f"{self.control.name} wins by {abs(diff):.2f}%"
        else:
            winner = "No significant difference"

        return diff, winner


class ABTestingFramework:
    """Framework for A/B testing different proxy sources."""

    def __init__(self) -> None:
        """Initialize A/B testing framework."""
        self.experiments: dict[str, ABExperiment] = {}
        self.active_experiment: Optional[ABExperiment] = None

    def create_experiment(
        self,
        experiment_id: str,
        control_pool: ProxyPool,
        treatment_pool: ProxyPool,
        treatment_traffic_percent: float = 50.0,
    ) -> ABExperiment:
        """Create new A/B test experiment."""
        if treatment_traffic_percent < 0 or treatment_traffic_percent > 100:
            raise ValueError("Traffic percent must be between 0 and 100")

        control = ExperimentVariant(
            name="control",
            pool=control_pool,
            traffic_percent=100 - treatment_traffic_percent,
        )
        treatment = ExperimentVariant(
            name="treatment",
            pool=treatment_pool,
            traffic_percent=treatment_traffic_percent,
        )

        experiment = ABExperiment(
            experiment_id=experiment_id,
            control=control,
            treatment=treatment,
        )

        self.experiments[experiment_id] = experiment
        self.active_experiment = experiment
        logger.info(f"Created A/B experiment: {experiment_id}")

        return experiment

    def get_experiment(self, experiment_id: str) -> Optional[ABExperiment]:
        """Get experiment by ID."""
        return self.experiments.get(experiment_id)

    def select_variant(
        self,
        experiment_id: Optional[str] = None,
    ) -> tuple[ExperimentVariant, ProxyPool]:
        """Select variant for request using traffic split.

        Returns:
            (selected_variant, proxy_pool) tuple
        """
        exp_id = experiment_id or (
            self.active_experiment.experiment_id if self.active_experiment else None
        )

        if not exp_id:
            raise ValueError("No active experiment or experiment ID provided")

        experiment = self.get_experiment(exp_id)
        if not experiment or not experiment.is_running():
            raise ValueError(f"Experiment {exp_id} is not running")

        # Randomly select variant based on traffic split
        rand = random.random() * 100

        if rand < experiment.control.traffic_percent:
            return experiment.control, experiment.control.pool
        else:
            return experiment.treatment, experiment.treatment.pool

    def record_request(
        self,
        experiment_id: str,
        variant_name: str,
        success: bool,
        response_time_ms: Optional[float] = None,
    ) -> None:
        """Record request result for variant."""
        experiment = self.get_experiment(experiment_id)
        if not experiment:
            logger.warning(f"Experiment not found: {experiment_id}")
            return

        variant = None
        if variant_name == "control":
            variant = experiment.control
        elif variant_name == "treatment":
            variant = experiment.treatment

        if not variant:
            logger.warning(f"Unknown variant: {variant_name}")
            return

        if success and response_time_ms is not None:
            variant.record_success(response_time_ms)
        else:
            variant.record_failure()

    def stop_experiment(self, experiment_id: str) -> Optional[dict]:
        """Stop experiment and get results."""
        experiment = self.get_experiment(experiment_id)
        if not experiment:
            return None

        experiment.status = ExperimentStatus.COMPLETED
        experiment.ended_at = datetime.now()
        self.active_experiment = None

        logger.info(f"Stopped experiment: {experiment_id}")
        return experiment.get_results()

    def pause_experiment(self, experiment_id: str) -> bool:
        """Pause experiment (can be resumed)."""
        experiment = self.get_experiment(experiment_id)
        if experiment:
            experiment.status = ExperimentStatus.PAUSED
            logger.info(f"Paused experiment: {experiment_id}")
            return True
        return False

    def resume_experiment(self, experiment_id: str) -> bool:
        """Resume paused experiment."""
        experiment = self.get_experiment(experiment_id)
        if experiment:
            experiment.status = ExperimentStatus.RUNNING
            self.active_experiment = experiment
            logger.info(f"Resumed experiment: {experiment_id}")
            return True
        return False

    def get_all_results(self) -> dict[str, dict]:
        """Get results for all experiments."""
        return {exp_id: exp.get_results() for exp_id, exp in self.experiments.items()}

    def find_winner(self, experiment_id: str) -> Optional[str]:
        """Determine statistical winner (if any)."""
        experiment = self.get_experiment(experiment_id)
        if not experiment:
            return None

        control_rate = experiment.control.get_success_rate()
        treatment_rate = experiment.treatment.get_success_rate()

        # Simple t-test-like check
        if control_rate > treatment_rate:
            diff = control_rate - treatment_rate
            if diff > 5:  # >5% difference threshold
                return experiment.control.name
        elif treatment_rate > control_rate:
            diff = treatment_rate - control_rate
            if diff > 5:  # >5% difference threshold
                return experiment.treatment.name

        return None


class MultiVariantTest:
    """Support for testing more than 2 variants."""

    def __init__(self, test_id: str) -> None:
        """Initialize multi-variant test."""
        self.test_id = test_id
        self.variants: dict[str, ExperimentVariant] = {}
        self.status = ExperimentStatus.RUNNING

    def add_variant(
        self,
        name: str,
        pool: ProxyPool,
        traffic_percent: float,
    ) -> None:
        """Add variant to test."""
        if sum(v.traffic_percent for v in self.variants.values()) + traffic_percent > 100:
            raise ValueError("Total traffic percent cannot exceed 100")

        variant = ExperimentVariant(
            name=name,
            pool=pool,
            traffic_percent=traffic_percent,
        )
        self.variants[name] = variant
        logger.info(f"Added variant {name} to test {self.test_id}")

    def select_variant(self) -> tuple[str, ProxyPool]:
        """Select variant using traffic split."""
        rand = random.random() * 100
        cumulative = 0.0

        for name, variant in self.variants.items():
            cumulative += variant.traffic_percent
            if rand <= cumulative:
                return name, variant.pool

        # Fallback (shouldn't happen)
        first_variant = list(self.variants.values())[0]
        return first_variant.name, first_variant.pool

    def get_results(self) -> dict:
        """Get results for all variants."""
        return {
            name: {
                "total_requests": variant.total_requests,
                "successful": variant.successful_requests,
                "failed": variant.failed_requests,
                "success_rate": variant.get_success_rate(),
                "avg_response_time_ms": variant.get_avg_response_time(),
            }
            for name, variant in self.variants.items()
        }
