"""Database schema versioning system for ProxyWhirl.

Implements versioning, migration management, and
backward compatibility for database schema changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from loguru import logger


class MigrationStatus(str, Enum):
    """Status of a schema migration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class SchemaVersion:
    """Represents a database schema version."""

    version: int
    description: str
    created_at: datetime
    applied_at: datetime | None = None
    status: MigrationStatus = MigrationStatus.PENDING

    def __repr__(self) -> str:
        return f"v{self.version}: {self.description}"


class Migration:
    """Represents a database migration."""

    def __init__(
        self,
        version: int,
        description: str,
        up_script: str,
        down_script: str | None = None,
    ) -> None:
        """Initialize migration.

        Args:
            version: Migration version number
            description: Migration description
            up_script: SQL script to apply migration
            down_script: SQL script to rollback migration
        """
        self.version = version
        self.description = description
        self.up_script = up_script
        self.down_script = down_script or f"-- Rollback for v{version}"
        self.created_at = datetime.now(timezone.utc)

    def validate(self) -> bool:
        """Validate migration.

        Returns:
            True if valid
        """
        if not self.version or self.version < 1:
            logger.error(f"Invalid version: {self.version}")
            return False

        if not self.description:
            logger.error("Migration missing description")
            return False

        if not self.up_script:
            logger.error("Migration missing up script")
            return False

        return True


class SchemaVersioningManager:
    """Manages database schema versioning and migrations."""

    def __init__(self) -> None:
        """Initialize schema versioning manager."""
        self._versions: dict[int, SchemaVersion] = {}
        self._migrations: dict[int, Migration] = {}
        self._current_version = 0
        logger.debug("SchemaVersioningManager initialized")

    def register_migration(self, migration: Migration) -> bool:
        """Register a migration.

        Args:
            migration: Migration to register

        Returns:
            True if registered
        """
        if not migration.validate():
            return False

        if migration.version in self._migrations:
            logger.warning(f"Migration v{migration.version} already registered")
            return False

        self._migrations[migration.version] = migration
        logger.debug(f"Migration registered: {migration}")
        return True

    def apply_migration(self, version: int) -> bool:
        """Apply a migration.

        Args:
            version: Migration version to apply

        Returns:
            True if applied
        """
        if version not in self._migrations:
            logger.error(f"Migration v{version} not found")
            return False

        migration = self._migrations[version]

        schema_version = SchemaVersion(
            version=version,
            description=migration.description,
            created_at=migration.created_at,
            applied_at=datetime.now(timezone.utc),
            status=MigrationStatus.COMPLETED,
        )
        self._versions[version] = schema_version
        self._current_version = version
        logger.info(f"Migration applied: {schema_version}")
        return True

    def rollback_migration(self, version: int) -> bool:
        """Rollback a migration.

        Args:
            version: Migration version to rollback

        Returns:
            True if rolled back
        """
        if version not in self._versions:
            logger.error(f"Migration v{version} not found")
            return False

        if version not in self._migrations:
            logger.error(f"Migration script v{version} not found")
            return False

        schema_version = self._versions[version]
        schema_version.status = MigrationStatus.ROLLED_BACK
        self._current_version = version - 1
        logger.info(f"Migration rolled back: v{version}")
        return True

    def get_current_version(self) -> int:
        """Get current schema version.

        Returns:
            Current version number
        """
        return self._current_version

    def get_migration(self, version: int) -> Migration | None:
        """Get a migration.

        Args:
            version: Migration version

        Returns:
            Migration or None if not found
        """
        return self._migrations.get(version)

    def get_pending_migrations(self) -> list[Migration]:
        """Get pending migrations.

        Returns:
            List of pending migrations
        """
        pending = []
        for version in sorted(self._migrations.keys()):
            if version > self._current_version:
                pending.append(self._migrations[version])
        return pending

    def get_applied_migrations(self) -> list[SchemaVersion]:
        """Get applied migrations.

        Returns:
            List of applied migrations
        """
        return [v for v in sorted(self._versions.values(), key=lambda x: x.version)]

    def export_status(self) -> dict[str, Any]:
        """Export migration status.

        Returns:
            Dictionary with status
        """
        return {
            "current_version": self._current_version,
            "total_migrations": len(self._migrations),
            "applied_migrations": len(self._versions),
            "pending_migrations": len(self.get_pending_migrations()),
            "applied": [
                {
                    "version": v.version,
                    "description": v.description,
                    "applied_at": v.applied_at.isoformat() if v.applied_at else None,
                }
                for v in self.get_applied_migrations()
            ],
        }
