"""Tests for schema versioning system."""

from proxywhirl.storage import (
    Migration,
    SchemaVersioningManager,
)


class TestMigration:
    """Test Migration class."""

    def test_migration_creation(self):
        """Test migration creation."""
        migration = Migration(
            version=1,
            description="Initial schema",
            up_script="CREATE TABLE proxy...",
        )
        assert migration.version == 1
        assert migration.description == "Initial schema"

    def test_migration_validate_valid(self):
        """Test validating valid migration."""
        migration = Migration(
            version=1,
            description="Initial schema",
            up_script="CREATE TABLE proxy...",
        )
        assert migration.validate()

    def test_migration_validate_invalid_version(self):
        """Test validating migration with invalid version."""
        migration = Migration(
            version=0,
            description="Initial schema",
            up_script="CREATE TABLE proxy...",
        )
        assert not migration.validate()

    def test_migration_validate_missing_description(self):
        """Test validating migration with missing description."""
        migration = Migration(
            version=1,
            description="",
            up_script="CREATE TABLE proxy...",
        )
        assert not migration.validate()

    def test_migration_validate_missing_script(self):
        """Test validating migration with missing script."""
        migration = Migration(
            version=1,
            description="Initial schema",
            up_script="",
        )
        assert not migration.validate()


class TestSchemaVersioningManager:
    """Test SchemaVersioningManager class."""

    def test_register_migration(self):
        """Test registering migration."""
        manager = SchemaVersioningManager()
        migration = Migration(
            version=1,
            description="Initial schema",
            up_script="CREATE TABLE proxy...",
        )
        assert manager.register_migration(migration)

    def test_register_duplicate_migration(self):
        """Test registering duplicate migration."""
        manager = SchemaVersioningManager()
        migration = Migration(
            version=1,
            description="Initial schema",
            up_script="CREATE TABLE proxy...",
        )
        manager.register_migration(migration)
        assert not manager.register_migration(migration)

    def test_apply_migration(self):
        """Test applying migration."""
        manager = SchemaVersioningManager()
        migration = Migration(
            version=1,
            description="Initial schema",
            up_script="CREATE TABLE proxy...",
        )
        manager.register_migration(migration)
        assert manager.apply_migration(1)
        assert manager.get_current_version() == 1

    def test_get_current_version(self):
        """Test getting current version."""
        manager = SchemaVersioningManager()
        assert manager.get_current_version() == 0

    def test_get_pending_migrations(self):
        """Test getting pending migrations."""
        manager = SchemaVersioningManager()
        m1 = Migration(version=1, description="First", up_script="...")
        m2 = Migration(version=2, description="Second", up_script="...")
        manager.register_migration(m1)
        manager.register_migration(m2)
        manager.apply_migration(1)
        pending = manager.get_pending_migrations()
        assert len(pending) == 1
        assert pending[0].version == 2

    def test_rollback_migration(self):
        """Test rolling back migration."""
        manager = SchemaVersioningManager()
        migration = Migration(
            version=1,
            description="Initial schema",
            up_script="CREATE TABLE proxy...",
            down_script="DROP TABLE proxy...",
        )
        manager.register_migration(migration)
        manager.apply_migration(1)
        assert manager.rollback_migration(1)
        assert manager.get_current_version() == 0

    def test_export_status(self):
        """Test exporting migration status."""
        manager = SchemaVersioningManager()
        migration = Migration(
            version=1,
            description="Initial schema",
            up_script="CREATE TABLE proxy...",
        )
        manager.register_migration(migration)
        manager.apply_migration(1)
        status = manager.export_status()
        assert status["current_version"] == 1
        assert status["applied_migrations"] == 1
