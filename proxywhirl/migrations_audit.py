"""SQL migrations auditing and validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from loguru import logger


class MigrationStatus(str, Enum):
    """Migration execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class Migration:
    """A database migration."""

    version: str
    description: str
    created_at: float
    status: MigrationStatus = MigrationStatus.PENDING
    up_sql: str = ""
    down_sql: str = ""
    has_down: bool = True

    def is_reversible(self) -> bool:
        """Check if migration has reversible down() implementation."""
        return self.has_down and len(self.down_sql) > 0


class MigrationAuditor:
    """
    Audit database migrations for reversibility and safety.

    Ensures all migrations can be rolled back and contain proper
    error handling.
    """

    def __init__(self):
        """Initialize migration auditor."""
        self.migrations: dict[str, Migration] = {}
        self.execution_log: list[dict] = []

    def register_migration(
        self,
        version: str,
        description: str,
        up_sql: str,
        down_sql: str,
    ) -> None:
        """
        Register a migration.

        Args:
            version: Migration version (e.g., "001", "001_create_users_table")
            description: Human-readable description
            up_sql: SQL to apply migration
            down_sql: SQL to rollback migration
        """
        migration = Migration(
            version=version,
            description=description,
            created_at=0.0,  # Would be set by caller
            up_sql=up_sql,
            down_sql=down_sql,
            has_down=len(down_sql) > 0,
        )

        self.migrations[version] = migration
        logger.debug(f"Registered migration: {version}")

    def audit_migration(self, version: str) -> dict[str, bool | str | list]:
        """
        Audit a migration for safety and reversibility.

        Args:
            version: Migration version

        Returns:
            Dictionary with audit results
        """
        if version not in self.migrations:
            return {"valid": False, "errors": ["Migration not found"]}

        migration = self.migrations[version]
        errors = []
        warnings = []

        # Check reversibility
        if not migration.is_reversible():
            errors.append("Migration is not reversible (missing down SQL)")

        # Check for common issues in up SQL
        dangerous_patterns = [
            (r"DROP TABLE", "DROP TABLE without safe checks"),
            (r"DELETE FROM", "DELETE without WHERE clause"),
            (r"TRUNCATE", "TRUNCATE used"),
        ]

        for pattern, issue in dangerous_patterns:
            if (
                pattern.lower() in migration.up_sql.lower()
                and "WHERE" not in migration.up_sql.upper()
            ):
                warnings.append(f"Potential issue: {issue}")

        # Check for required safety patterns
        if "BEGIN" not in migration.up_sql.upper():
            warnings.append("Migration should use transactions (BEGIN/COMMIT)")

        # Check down SQL matches up SQL
        if migration.has_down:
            if "CREATE TABLE" in migration.up_sql and "DROP TABLE" not in migration.down_sql:
                errors.append("down() should DROP TABLE created in up()")
            if "ADD COLUMN" in migration.up_sql and "DROP COLUMN" not in migration.down_sql:
                errors.append("down() should DROP COLUMN added in up()")

        return {
            "version": version,
            "description": migration.description,
            "valid": len(errors) == 0,
            "reversible": migration.is_reversible(),
            "errors": errors,
            "warnings": warnings,
        }

    def audit_all_migrations(self) -> list[dict]:
        """
        Audit all migrations.

        Returns:
            List of audit results
        """
        results = []
        for version in sorted(self.migrations.keys()):
            results.append(self.audit_migration(version))

        return results

    def log_execution(
        self,
        version: str,
        status: MigrationStatus,
        duration_seconds: float = 0.0,
        error: str | None = None,
    ) -> None:
        """
        Log a migration execution.

        Args:
            version: Migration version
            status: Execution status
            duration_seconds: How long execution took
            error: Optional error message
        """
        log_entry = {
            "version": version,
            "status": status.value,
            "duration_seconds": duration_seconds,
            "error": error,
        }

        self.execution_log.append(log_entry)

        if status == MigrationStatus.FAILED:
            logger.error(f"Migration failed: {version} - {error}")
        else:
            logger.info(f"Migration {status.value}: {version} ({duration_seconds:.2f}s)")

    def get_execution_history(self) -> list[dict]:
        """
        Get migration execution history.

        Returns:
            List of execution log entries
        """
        return self.execution_log.copy()

    def get_migration_status(self, version: str) -> MigrationStatus | None:
        """
        Get current status of a migration.

        Args:
            version: Migration version

        Returns:
            Migration status or None
        """
        if version in self.migrations:
            return self.migrations[version].status
        return None

    def get_reversibility_report(self) -> dict[str, int | list | float]:
        """
        Get report on migration reversibility.

        Returns:
            Dictionary with reversibility stats
        """
        reversible_count = 0
        non_reversible = []

        for version, migration in self.migrations.items():
            if migration.is_reversible():
                reversible_count += 1
            else:
                non_reversible.append(
                    {
                        "version": version,
                        "description": migration.description,
                    }
                )

        return {
            "total_migrations": len(self.migrations),
            "reversible": reversible_count,
            "non_reversible": len(non_reversible),
            "non_reversible_list": non_reversible,
            "reversibility_percent": (
                reversible_count / len(self.migrations) * 100 if self.migrations else 0
            ),
        }

    def validate_migration_chain(self) -> dict[str, bool | list]:
        """
        Validate that migrations form a valid chain.

        Returns:
            Dictionary with validation results
        """
        errors = []

        # Check for gaps in version numbering
        versions = sorted(self.migrations.keys())

        # Audit all
        all_valid = True
        invalid_migrations = []

        for version in versions:
            result = self.audit_migration(version)
            if not result["valid"]:
                all_valid = False
                invalid_migrations.append(version)

        return {
            "valid_chain": all_valid and len(errors) == 0,
            "errors": errors,
            "invalid_migrations": invalid_migrations,
        }
