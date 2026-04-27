"""Blue-green deployment strategy."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from loguru import logger


class EnvironmentColor(str, Enum):
    """Environment colors."""

    BLUE = "blue"
    GREEN = "green"


class DeploymentStatus(str, Enum):
    """Deployment status."""

    IDLE = "idle"
    DEPLOYING = "deploying"
    TESTING = "testing"
    SWITCHING = "switching"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLBACK = "rollback"


@dataclass
class EnvironmentSnapshot:
    """Snapshot of an environment."""

    color: EnvironmentColor
    version: str
    deployed_at: datetime
    replicas: int
    health_status: str = "unknown"
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict.

        Returns:
            Snapshot dict
        """
        return {
            "color": self.color.value,
            "version": self.version,
            "deployed_at": self.deployed_at.isoformat(),
            "replicas": self.replicas,
            "health_status": self.health_status,
            "metrics": self.metrics,
        }


@dataclass
class DeploymentPlan:
    """Blue-green deployment plan."""

    id: str
    new_version: str
    current_version: str
    target_environment: EnvironmentColor
    status: DeploymentStatus = DeploymentStatus.IDLE
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    health_check_timeout: int = 300
    traffic_switch_delay: int = 60
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict.

        Returns:
            Plan dict
        """
        return {
            "id": self.id,
            "new_version": self.new_version,
            "current_version": self.current_version,
            "target_environment": self.target_environment.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class BlueGreenDeployment:
    """Blue-green deployment manager."""

    def __init__(self):
        """Initialize manager."""
        self._active_environment = EnvironmentColor.BLUE
        self._blue_version = "1.0.0"
        self._green_version = "1.0.0"
        self._blue_replicas = 3
        self._green_replicas = 0
        self._plans: dict[str, DeploymentPlan] = {}
        self._deployment_history: list[DeploymentPlan] = []

    def get_active_environment(self) -> EnvironmentColor:
        """Get active environment.

        Returns:
            Active environment color
        """
        return self._active_environment

    def get_inactive_environment(self) -> EnvironmentColor:
        """Get inactive environment.

        Returns:
            Inactive environment color
        """
        return (
            EnvironmentColor.GREEN
            if self._active_environment == EnvironmentColor.BLUE
            else EnvironmentColor.BLUE
        )

    def create_deployment_plan(
        self,
        plan_id: str,
        new_version: str,
    ) -> DeploymentPlan:
        """Create deployment plan.

        Args:
            plan_id: Plan ID
            new_version: New version

        Returns:
            Deployment plan
        """
        target_env = self.get_inactive_environment()
        current_version = (
            self._blue_version
            if self._active_environment == EnvironmentColor.BLUE
            else self._green_version
        )

        plan = DeploymentPlan(
            id=plan_id,
            new_version=new_version,
            current_version=current_version,
            target_environment=target_env,
        )

        self._plans[plan_id] = plan
        logger.info(
            f"Created deployment plan: {plan_id} (Blue={self._blue_version} Green={self._green_version})"
        )

        return plan

    def start_deployment(self, plan_id: str, replicas: int = 3) -> bool:
        """Start deployment.

        Args:
            plan_id: Plan ID
            replicas: Number of replicas

        Returns:
            True if started
        """
        if plan_id not in self._plans:
            return False

        plan = self._plans[plan_id]
        plan.status = DeploymentStatus.DEPLOYING
        plan.started_at = datetime.now()

        if plan.target_environment == EnvironmentColor.GREEN:
            self._green_replicas = replicas
            self._green_version = plan.new_version
        else:
            self._blue_replicas = replicas
            self._blue_version = plan.new_version

        logger.info(f"Started deployment: {plan_id} to {plan.target_environment.value}")

        return True

    def test_environment(self, plan_id: str, health_check_passed: bool) -> bool:
        """Test inactive environment.

        Args:
            plan_id: Plan ID
            health_check_passed: Health check result

        Returns:
            True if passed
        """
        if plan_id not in self._plans:
            return False

        plan = self._plans[plan_id]
        plan.status = DeploymentStatus.TESTING

        if health_check_passed:
            logger.info(f"Environment test passed: {plan_id}")
            plan.status = DeploymentStatus.TESTING
            return True

        logger.error(f"Environment test failed: {plan_id}")
        plan.status = DeploymentStatus.FAILED
        return False

    def switch_traffic(self, plan_id: str) -> bool:
        """Switch traffic to new environment.

        Args:
            plan_id: Plan ID

        Returns:
            True if switched
        """
        if plan_id not in self._plans:
            return False

        plan = self._plans[plan_id]
        plan.status = DeploymentStatus.SWITCHING

        self._active_environment = plan.target_environment
        plan.status = DeploymentStatus.COMPLETED
        plan.completed_at = datetime.now()

        self._deployment_history.append(plan)

        logger.info(f"Traffic switched to {self._active_environment.value}: {plan.new_version}")

        return True

    def rollback(self, plan_id: str) -> bool:
        """Rollback deployment.

        Args:
            plan_id: Plan ID

        Returns:
            True if rolled back
        """
        if plan_id not in self._plans:
            return False

        plan = self._plans[plan_id]
        plan.status = DeploymentStatus.ROLLBACK

        logger.warning(f"Rollback initiated: {plan_id}")

        return True

    def get_deployment_status(self, plan_id: str) -> DeploymentStatus | None:
        """Get deployment status.

        Args:
            plan_id: Plan ID

        Returns:
            Deployment status or None
        """
        plan = self._plans.get(plan_id)
        return plan.status if plan else None

    def get_environment_snapshot(self, color: EnvironmentColor) -> EnvironmentSnapshot:
        """Get environment snapshot.

        Args:
            color: Environment color

        Returns:
            Environment snapshot
        """
        if color == EnvironmentColor.BLUE:
            return EnvironmentSnapshot(
                color=color,
                version=self._blue_version,
                deployed_at=datetime.now(),
                replicas=self._blue_replicas,
                health_status="healthy" if self._blue_replicas > 0 else "down",
            )

        return EnvironmentSnapshot(
            color=color,
            version=self._green_version,
            deployed_at=datetime.now(),
            replicas=self._green_replicas,
            health_status="healthy" if self._green_replicas > 0 else "down",
        )

    def get_stats(self) -> dict[str, Any]:
        """Get deployment stats.

        Returns:
            Stats dict
        """
        return {
            "active_environment": self._active_environment.value,
            "total_plans": len(self._plans),
            "completed_deployments": len(self._deployment_history),
            "blue_version": self._blue_version,
            "green_version": self._green_version,
            "blue_replicas": self._blue_replicas,
            "green_replicas": self._green_replicas,
        }
