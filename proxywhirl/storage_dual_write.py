"""Dual-write pattern for storage backend migration."""

from __future__ import annotations

from typing import Any, Protocol

from loguru import logger


class StorageBackend(Protocol):
    """Protocol for storage backends."""

    def store(self, key: str, value: Any) -> None:
        """Store a value."""
        ...

    def retrieve(self, key: str) -> Any | None:
        """Retrieve a value."""
        ...

    def delete(self, key: str) -> None:
        """Delete a value."""
        ...


class DualWriteStorage:
    """
    Dual-write storage pattern for gradual migration.

    Writes to both old and new backends simultaneously, allowing
    gradual migration with rollback capability.
    """

    def __init__(
        self,
        primary: StorageBackend,
        secondary: StorageBackend,
        read_from_secondary: bool = False,
    ):
        """
        Initialize dual-write storage.

        Args:
            primary: Primary storage backend (usually old)
            secondary: Secondary storage backend (usually new)
            read_from_secondary: Whether to read from secondary
        """
        self.primary = primary
        self.secondary = secondary
        self.read_from_secondary = read_from_secondary
        self.write_count = 0
        self.read_count = 0
        self.error_count = 0

    def store(self, key: str, value: Any) -> None:
        """
        Store value in both backends.

        Args:
            key: Storage key
            value: Value to store
        """
        errors = []

        # Write to primary
        try:
            self.primary.store(key, value)
            logger.debug(f"Stored {key} in primary backend")
        except Exception as e:
            logger.error(f"Failed to store {key} in primary: {e}")
            errors.append(("primary", e))
            self.error_count += 1

        # Write to secondary
        try:
            self.secondary.store(key, value)
            logger.debug(f"Stored {key} in secondary backend")
        except Exception as e:
            logger.error(f"Failed to store {key} in secondary: {e}")
            errors.append(("secondary", e))
            self.error_count += 1

        self.write_count += 1

        if errors:
            # Fail if both backends failed, warn if one failed
            if len(errors) == 2:
                raise RuntimeError(f"Dual-write failed for {key}: {errors}")
            else:
                logger.warning(f"Partial dual-write for {key}: {errors}")

    def retrieve(self, key: str) -> Any | None:
        """
        Retrieve value from storage.

        Args:
            key: Storage key

        Returns:
            Retrieved value or None
        """
        self.read_count += 1

        # Try to read from preferred backend
        if self.read_from_secondary:
            try:
                value = self.secondary.retrieve(key)
                if value is not None:
                    logger.debug(f"Retrieved {key} from secondary")
                    return value
            except Exception as e:
                logger.warning(f"Failed to retrieve {key} from secondary: {e}")

        # Fall back to primary
        try:
            value = self.primary.retrieve(key)
            if value is not None:
                logger.debug(f"Retrieved {key} from primary")
            return value
        except Exception as e:
            logger.error(f"Failed to retrieve {key} from primary: {e}")
            return None

    def delete(self, key: str) -> None:
        """
        Delete value from both backends.

        Args:
            key: Storage key
        """
        errors = []

        try:
            self.primary.delete(key)
            logger.debug(f"Deleted {key} from primary")
        except Exception as e:
            logger.error(f"Failed to delete {key} from primary: {e}")
            errors.append(("primary", e))

        try:
            self.secondary.delete(key)
            logger.debug(f"Deleted {key} from secondary")
        except Exception as e:
            logger.error(f"Failed to delete {key} from secondary: {e}")
            errors.append(("secondary", e))

        if errors and len(errors) == 2:
            raise RuntimeError(f"Dual-delete failed for {key}: {errors}")

    def switch_to_secondary(self) -> None:
        """Switch primary reads to secondary backend."""
        self.read_from_secondary = True
        logger.info("Switched to reading from secondary backend")

    def switch_to_primary(self) -> None:
        """Switch primary reads back to primary backend."""
        self.read_from_secondary = False
        logger.info("Switched to reading from primary backend")

    def get_stats(self) -> dict[str, int | float]:
        """
        Get dual-write statistics.

        Returns:
            Dictionary with stats
        """
        return {
            "writes": self.write_count,
            "reads": self.read_count,
            "errors": self.error_count,
            "error_rate_percent": (
                self.error_count / (self.write_count + self.read_count) * 100
                if (self.write_count + self.read_count) > 0
                else 0
            ),
        }


class MigrationController:
    """
    Control storage backend migration with dual-write.

    Coordinates migration strategy, validation, and rollback.
    """

    def __init__(
        self,
        primary: StorageBackend,
        secondary: StorageBackend,
    ):
        """
        Initialize migration controller.

        Args:
            primary: Primary backend
            secondary: Secondary backend
        """
        self.storage = DualWriteStorage(primary, secondary)
        self.migration_started = False
        self.migration_percentage = 0

    def start_migration(self) -> None:
        """Start the migration process."""
        self.migration_started = True
        self.migration_percentage = 0
        logger.info("Started storage migration")

    def set_migration_percentage(self, percentage: int) -> None:
        """
        Set migration progress percentage.

        Args:
            percentage: Migration percentage (0-100)
        """
        if not 0 <= percentage <= 100:
            raise ValueError(f"Percentage must be 0-100, got {percentage}")

        self.migration_percentage = percentage

        if percentage >= 100:
            self.complete_migration()
        else:
            logger.info(f"Migration progress: {percentage}%")

    def validate_migration(self) -> bool:
        """
        Validate migration consistency.

        Returns:
            True if validation passed
        """
        logger.info("Validating migration consistency")

        # In real implementation, would compare data between backends
        # For now, just check error rate is acceptable
        stats = self.storage.get_stats()
        error_rate = stats["error_rate_percent"]

        if error_rate > 5.0:
            logger.error(f"Migration validation failed: {error_rate:.1f}% error rate")
            return False

        logger.info("Migration validation passed")
        return True

    def complete_migration(self) -> None:
        """Complete the migration."""
        if not self.validate_migration():
            raise RuntimeError("Migration validation failed")

        self.migration_percentage = 100
        self.storage.switch_to_secondary()
        logger.info("Migration completed successfully")

    def rollback_migration(self) -> None:
        """Rollback to primary backend."""
        self.storage.switch_to_primary()
        self.migration_started = False
        self.migration_percentage = 0
        logger.warning("Migration rolled back")

    def get_migration_status(self) -> dict[str, Any]:
        """
        Get migration status.

        Returns:
            Dictionary with migration info
        """
        return {
            "started": self.migration_started,
            "percentage": self.migration_percentage,
            "reading_from_secondary": self.storage.read_from_secondary,
            "stats": self.storage.get_stats(),
        }
