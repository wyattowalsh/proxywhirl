"""Version upgrade guidance system.

Provides guidance and warnings for version upgrades,
deprecations, and breaking changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from loguru import logger


class UpgradeSeverity(str, Enum):
    """Severity of upgrade issue."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class UpgradeGuidance:
    """Guidance for version upgrade."""

    from_version: str
    to_version: str
    severity: UpgradeSeverity
    title: str
    description: str
    migration_steps: list[str] | None = None
    breaking_changes: list[str] | None = None


class UpgradeGuidanceManager:
    """Manages version upgrade guidance."""

    def __init__(self) -> None:
        """Initialize upgrade guidance manager."""
        self._guidance: dict[str, list[UpgradeGuidance]] = {}
        logger.debug("UpgradeGuidanceManager initialized")

    def register_guidance(self, guidance: UpgradeGuidance) -> bool:
        """Register upgrade guidance.

        Args:
            guidance: Upgrade guidance

        Returns:
            True if registered
        """
        key = f"{guidance.from_version}->{guidance.to_version}"

        if key not in self._guidance:
            self._guidance[key] = []

        self._guidance[key].append(guidance)
        logger.info(f"Guidance registered: {key}")
        return True

    def get_guidance(self, from_version: str, to_version: str) -> list[UpgradeGuidance]:
        """Get guidance for version upgrade.

        Args:
            from_version: From version
            to_version: To version

        Returns:
            List of guidance items
        """
        key = f"{from_version}->{to_version}"
        return self._guidance.get(key, [])

    def has_breaking_changes(self, from_version: str, to_version: str) -> bool:
        """Check if upgrade has breaking changes.

        Args:
            from_version: From version
            to_version: To version

        Returns:
            True if has breaking changes
        """
        guidance = self.get_guidance(from_version, to_version)
        return any(g.breaking_changes for g in guidance)

    def get_critical_issues(self, from_version: str, to_version: str) -> list[UpgradeGuidance]:
        """Get critical upgrade issues.

        Args:
            from_version: From version
            to_version: To version

        Returns:
            List of critical guidance items
        """
        guidance = self.get_guidance(from_version, to_version)
        return [g for g in guidance if g.severity == UpgradeSeverity.CRITICAL]

    def export_report(self, from_version: str, to_version: str) -> dict[str, Any]:
        """Export upgrade guidance report.

        Args:
            from_version: From version
            to_version: To version

        Returns:
            Dictionary with report
        """
        guidance = self.get_guidance(from_version, to_version)
        critical = self.get_critical_issues(from_version, to_version)

        return {
            "from_version": from_version,
            "to_version": to_version,
            "total_items": len(guidance),
            "critical_items": len(critical),
            "has_breaking_changes": self.has_breaking_changes(from_version, to_version),
            "guidance": [
                {
                    "severity": g.severity.value,
                    "title": g.title,
                    "description": g.description,
                    "migration_steps": g.migration_steps or [],
                    "breaking_changes": g.breaking_changes or [],
                }
                for g in guidance
            ],
        }
