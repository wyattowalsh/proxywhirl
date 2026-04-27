"""Database migration documentation and tracking."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from loguru import logger


class MigrationStatus(str, Enum):
    """Migration status."""

    PENDING = "pending"
    APPLIED = "applied"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class MigrationType(str, Enum):
    """Type of migration."""

    SCHEMA_CHANGE = "schema_change"
    DATA_MIGRATION = "data_migration"
    INDEX_ADDITION = "index_addition"
    PERFORMANCE = "performance"


@dataclass
class Migration:
    """Database migration definition."""

    version: str
    name: str
    migration_type: MigrationType
    description: str
    sql: str
    rollback_sql: str | None = None
    applies_to_version: str | None = None
    created_at: datetime | None = None
    applied_at: datetime | None = None
    status: MigrationStatus = MigrationStatus.PENDING

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict."""
        return {
            "version": self.version,
            "name": self.name,
            "type": self.migration_type.value,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "rollback_available": self.rollback_sql is not None,
        }


class MigrationRegistry:
    """Registry of database migrations."""

    def __init__(self):
        """Initialize migration registry."""
        self._migrations: dict[str, Migration] = {}
        self._applied: list[str] = []

    def register(self, migration: Migration) -> None:
        """Register a migration.

        Args:
            migration: Migration to register
        """
        self._migrations[migration.version] = migration
        logger.info(f"Registered migration {migration.version}: {migration.name}")

    def get_migration(self, version: str) -> Migration | None:
        """Get migration by version.

        Args:
            version: Migration version

        Returns:
            Migration or None
        """
        return self._migrations.get(version)

    def get_pending_migrations(self) -> list[Migration]:
        """Get migrations pending application.

        Returns:
            List of pending migrations
        """
        return [m for m in self._migrations.values() if m.status == MigrationStatus.PENDING]

    def get_applied_migrations(self) -> list[Migration]:
        """Get applied migrations.

        Returns:
            List of applied migrations
        """
        return [m for m in self._migrations.values() if m.status == MigrationStatus.APPLIED]

    def mark_applied(self, version: str) -> None:
        """Mark migration as applied.

        Args:
            version: Migration version
        """
        if version in self._migrations:
            self._migrations[version].status = MigrationStatus.APPLIED
            self._migrations[version].applied_at = datetime.now()
            self._applied.append(version)
            logger.info(f"Marked migration as applied: {version}")

    def mark_failed(self, version: str, error: str) -> None:
        """Mark migration as failed.

        Args:
            version: Migration version
            error: Error message
        """
        if version in self._migrations:
            self._migrations[version].status = MigrationStatus.FAILED
            logger.error(f"Migration failed: {version}: {error}")

    def get_migration_history(self) -> list[dict[str, Any]]:
        """Get migration history.

        Returns:
            List of migration dicts
        """
        return [
            m.to_dict()
            for m in sorted(
                self._migrations.values(),
                key=lambda x: x.version,
            )
        ]


class MigrationDocumenter:
    """Generates migration documentation."""

    def __init__(self, registry: MigrationRegistry):
        """Initialize documenter.

        Args:
            registry: Migration registry
        """
        self.registry = registry

    def generate_markdown(self) -> str:
        """Generate markdown documentation.

        Returns:
            Markdown documentation
        """
        lines = [
            "# Database Migrations\n",
            "This document tracks all database schema migrations.\n",
            f"Generated: {datetime.now().isoformat()}\n",
        ]

        # Applied migrations section
        applied = self.registry.get_applied_migrations()
        if applied:
            lines.append("## Applied Migrations\n")
            for migration in sorted(applied, key=lambda x: x.version):
                lines.append(f"### {migration.version}: {migration.name}\n")
                lines.append(f"- **Type**: {migration.migration_type.value}\n")
                lines.append(f"- **Description**: {migration.description}\n")
                if migration.applied_at:
                    lines.append(f"- **Applied**: {migration.applied_at.isoformat()}\n")
                lines.append("")

        # Pending migrations section
        pending = self.registry.get_pending_migrations()
        if pending:
            lines.append("## Pending Migrations\n")
            for migration in sorted(pending, key=lambda x: x.version):
                lines.append(f"### {migration.version}: {migration.name}\n")
                lines.append(f"- **Type**: {migration.migration_type.value}\n")
                lines.append(f"- **Description**: {migration.description}\n")
                lines.append("")

        return "\n".join(lines)

    def generate_sql_script(self) -> str:
        """Generate SQL migration script.

        Returns:
            SQL script
        """
        lines = [
            "-- Database migration script",
            f"-- Generated: {datetime.now().isoformat()}",
            "",
        ]

        pending = self.registry.get_pending_migrations()
        for migration in sorted(pending, key=lambda x: x.version):
            lines.append(f"-- Migration {migration.version}: {migration.name}")
            lines.append(migration.sql)
            lines.append("")

        return "\n".join(lines)

    def save_documentation(self, filepath: str | Path) -> None:
        """Save documentation to file.

        Args:
            filepath: Path to output file
        """
        content = self.generate_markdown()
        Path(filepath).write_text(content)
        logger.info(f"Saved migration documentation to {filepath}")


def create_migration(
    version: str,
    name: str,
    migration_type: MigrationType,
    description: str,
    sql: str,
    rollback_sql: str | None = None,
) -> Migration:
    """Factory function to create migration.

    Args:
        version: Migration version (e.g., "001")
        name: Migration name
        migration_type: Type of migration
        description: Detailed description
        sql: SQL to apply
        rollback_sql: Optional rollback SQL

    Returns:
        Migration instance
    """
    return Migration(
        version=version,
        name=name,
        migration_type=migration_type,
        description=description,
        sql=sql,
        rollback_sql=rollback_sql,
        created_at=datetime.now(),
    )
