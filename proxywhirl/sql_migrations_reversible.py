"""Reversible database migrations system.

Ensures all migrations have reversible down scripts
and tracks migration state for reliable rollback.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from loguru import logger


class ReversibilityStatus(str, Enum):
    """Status of migration reversibility."""

    FULLY_REVERSIBLE = "fully_reversible"
    PARTIALLY_REVERSIBLE = "partially_reversible"
    NOT_REVERSIBLE = "not_reversible"
    UNTESTED = "untested"


@dataclass
class MigrationRecord:
    """Record of applied migration."""

    version: int
    description: str
    applied_at: datetime
    reversible: ReversibilityStatus
    up_script: str
    down_script: str
    metadata: dict[str, Any]

    def can_rollback(self) -> bool:
        """Check if migration can be rolled back.

        Returns:
            True if reversible
        """
        return self.reversible != ReversibilityStatus.NOT_REVERSIBLE


class ReversibleMigrationManager:
    """Manages reversible database migrations."""

    def __init__(self) -> None:
        """Initialize reversible migration manager."""
        self._migrations: dict[int, MigrationRecord] = {}
        self._applied_order: list[int] = []
        logger.debug("ReversibleMigrationManager initialized")

    def register_migration(
        self,
        version: int,
        description: str,
        up_script: str,
        down_script: str,
        reversibility: ReversibilityStatus = ReversibilityStatus.UNTESTED,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Register a migration.

        Args:
            version: Migration version
            description: Migration description
            up_script: Up migration SQL
            down_script: Down migration SQL
            reversibility: Reversibility status
            metadata: Optional metadata

        Returns:
            True if registered
        """
        if version in self._migrations:
            logger.warning(f"Migration {version} already registered")
            return False

        if not down_script:
            logger.warning(f"Migration {version} has no down script")
            reversibility = ReversibilityStatus.NOT_REVERSIBLE

        record = MigrationRecord(
            version=version,
            description=description,
            applied_at=datetime.now(timezone.utc),
            reversible=reversibility,
            up_script=up_script,
            down_script=down_script,
            metadata=metadata or {},
        )
        self._migrations[version] = record
        logger.info(f"Migration registered: v{version} ({reversibility.value})")
        return True

    def apply_migration(self, version: int) -> bool:
        """Apply a migration.

        Args:
            version: Migration version

        Returns:
            True if applied
        """
        if version not in self._migrations:
            logger.error(f"Migration {version} not found")
            return False

        if version in self._applied_order:
            logger.warning(f"Migration {version} already applied")
            return False

        self._applied_order.append(version)
        logger.info(f"Migration applied: v{version}")
        return True

    def rollback_migration(self, version: int) -> bool:
        """Rollback a migration.

        Args:
            version: Migration version

        Returns:
            True if rolled back
        """
        if version not in self._migrations:
            logger.error(f"Migration {version} not found")
            return False

        record = self._migrations[version]
        if not record.can_rollback():
            logger.error(f"Migration {version} is not reversible")
            return False

        if version not in self._applied_order:
            logger.warning(f"Migration {version} not applied")
            return False

        self._applied_order.remove(version)
        logger.info(f"Migration rolled back: v{version}")
        return True

    def get_reversibility(self, version: int) -> ReversibilityStatus | None:
        """Get reversibility status of migration.

        Args:
            version: Migration version

        Returns:
            ReversibilityStatus or None
        """
        if version not in self._migrations:
            return None
        return self._migrations[version].reversible

    def set_reversibility(self, version: int, status: ReversibilityStatus) -> bool:
        """Set reversibility status.

        Args:
            version: Migration version
            status: Reversibility status

        Returns:
            True if set
        """
        if version not in self._migrations:
            return False

        self._migrations[version].reversible = status
        logger.info(f"Migration {version} reversibility set to {status.value}")
        return True

    def get_applied_migrations(self) -> list[int]:
        """Get applied migrations in order.

        Returns:
            List of applied migration versions
        """
        return self._applied_order.copy()

    def export_status(self) -> dict[str, Any]:
        """Export migration status.

        Returns:
            Dictionary of status
        """
        return {
            "total_migrations": len(self._migrations),
            "applied_migrations": len(self._applied_order),
            "reversible_migrations": len(
                [m for m in self._migrations.values() if m.can_rollback()]
            ),
            "migrations": {
                v: {
                    "description": record.description,
                    "reversible": record.reversible.value,
                    "applied": v in self._applied_order,
                }
                for v, record in sorted(self._migrations.items())
            },
        }
