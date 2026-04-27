"""Tests for database schema migrations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest


@dataclass
class Migration:
    """Represents a migration."""

    version: int
    name: str
    up_sql: str
    down_sql: str
    applied: bool = False


class MigrationManager:
    """Manages database migrations."""

    def __init__(self) -> None:
        """Initialize manager."""
        self.migrations: list[Migration] = []
        self.current_version = 0

    def add_migration(self, migration: Migration) -> None:
        """Add a migration."""
        self.migrations.append(migration)

    def apply_migration(self, version: int) -> bool:
        """Apply migration."""
        for migration in self.migrations:
            if migration.version == version and not migration.applied:
                migration.applied = True
                self.current_version = version
                return True
        return False

    def rollback_migration(self, version: int) -> bool:
        """Rollback migration."""
        for migration in self.migrations:
            if migration.version == version and migration.applied:
                migration.applied = False
                self.current_version = version - 1
                return True
        return False

    def get_pending_migrations(self) -> list[Migration]:
        """Get migrations not yet applied."""
        return [m for m in self.migrations if not m.applied]

    def apply_all(self) -> None:
        """Apply all pending migrations."""
        for migration in self.get_pending_migrations():
            migration.applied = True
            self.current_version = migration.version

    def is_reversible(self, version: int) -> bool:
        """Check if migration has down path."""
        for m in self.migrations:
            if m.version == version:
                return bool(m.down_sql)
        return False


class TestSchemaMigrations:
    """Test database schema migrations."""

    @pytest.fixture
    def manager(self) -> MigrationManager:
        """Provide migration manager."""
        return MigrationManager()

    def test_add_migration(self, manager) -> None:
        """Test adding migration."""
        mig = Migration(
            version=1,
            name="initial",
            up_sql="CREATE TABLE test (id INT)",
            down_sql="DROP TABLE test",
        )
        manager.add_migration(mig)
        assert len(manager.migrations) == 1

    def test_apply_migration(self, manager) -> None:
        """Test applying migration."""
        mig = Migration(
            version=1,
            name="create_table",
            up_sql="CREATE TABLE users (id INT)",
            down_sql="DROP TABLE users",
        )
        manager.add_migration(mig)

        assert manager.apply_migration(1)
        assert mig.applied is True
        assert manager.current_version == 1

    def test_rollback_migration(self, manager) -> None:
        """Test rolling back migration."""
        mig = Migration(
            version=1,
            name="create_table",
            up_sql="CREATE TABLE users (id INT)",
            down_sql="DROP TABLE users",
        )
        manager.add_migration(mig)
        manager.apply_migration(1)

        assert manager.rollback_migration(1)
        assert not mig.applied

    def test_get_pending_migrations(self, manager) -> None:
        """Test getting pending migrations."""
        mig1 = Migration(1, "first", "UP1", "DOWN1")
        mig2 = Migration(2, "second", "UP2", "DOWN2")

        manager.add_migration(mig1)
        manager.add_migration(mig2)

        pending = manager.get_pending_migrations()
        assert len(pending) == 2

    def test_apply_all_migrations(self, manager) -> None:
        """Test applying all migrations."""
        mig1 = Migration(1, "first", "UP1", "DOWN1")
        mig2 = Migration(2, "second", "UP2", "DOWN2")
        mig3 = Migration(3, "third", "UP3", "DOWN3")

        manager.add_migration(mig1)
        manager.add_migration(mig2)
        manager.add_migration(mig3)

        manager.apply_all()

        assert mig1.applied
        assert mig2.applied
        assert mig3.applied
        assert manager.current_version == 3

    def test_sequential_migrations(self, manager) -> None:
        """Test migrations applied in sequence."""
        mig1 = Migration(1, "v1", "CREATE TABLE t1 (id INT)", "DROP TABLE t1")
        mig2 = Migration(2, "v2", "CREATE TABLE t2 (id INT)", "DROP TABLE t2")

        manager.add_migration(mig1)
        manager.add_migration(mig2)

        manager.apply_migration(1)
        assert manager.current_version == 1

        manager.apply_migration(2)
        assert manager.current_version == 2

    def test_is_reversible(self, manager) -> None:
        """Test checking if migration is reversible."""
        mig = Migration(1, "test", "UP", "DOWN")
        manager.add_migration(mig)

        assert manager.is_reversible(1)

    def test_not_reversible(self, manager) -> None:
        """Test migration without down path."""
        mig = Migration(1, "test", "UP", "")
        manager.add_migration(mig)

        assert not manager.is_reversible(1)

    def test_multiple_up_down_paths(self, manager) -> None:
        """Test migrations have both up and down."""
        for i in range(5):
            mig = Migration(
                version=i + 1,
                name=f"version_{i + 1}",
                up_sql=f"CREATE TABLE t{i + 1} (id INT)",
                down_sql=f"DROP TABLE t{i + 1}",
            )
            manager.add_migration(mig)

        for version in range(1, 6):
            assert manager.is_reversible(version)

    def test_migration_version_ordering(self, manager) -> None:
        """Test migrations maintain version order."""
        for version in [3, 1, 2, 4]:
            mig = Migration(version, f"v{version}", f"UP{version}", f"DOWN{version}")
            manager.add_migration(mig)

        # Order should be preserved as added
        assert manager.migrations[0].version == 3
        assert manager.migrations[1].version == 1

    def test_cannot_apply_twice(self, manager) -> None:
        """Test migration applied only once."""
        mig = Migration(1, "test", "UP", "DOWN")
        manager.add_migration(mig)

        assert manager.apply_migration(1)
        assert not manager.apply_migration(1)

    def test_rollback_nonexistent(self, manager) -> None:
        """Test rolling back nonexistent migration."""
        assert not manager.rollback_migration(999)

    def test_apply_nonexistent(self, manager) -> None:
        """Test applying nonexistent migration."""
        assert not manager.apply_migration(999)
