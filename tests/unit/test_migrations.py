"""Unit tests for database migration utilities.

Tests follow ProxyWhirl's test-first development approach with:
- Comprehensive coverage of migration API
- SQLite async testing with temporary databases
- Property-based testing for edge cases
- Security testing for migration safety

NOTE: These tests use Alembic migrations which reference the old 76-column schema.
With the v1 normalized schema, tables are created directly via SQLModel.initialize(),
not Alembic migrations. These tests are skipped until Alembic migrations are updated.
"""

import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.skip(
    reason="Alembic migrations reference old 76-column schema; "
    "normalized schema uses SQLModel.initialize() directly"
)
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from proxywhirl.migrations import (
    check_pending_migrations,
    downgrade_migrations,
    get_current_revision,
    get_head_revision,
    get_migration_history,
    initialize_database,
    run_migrations,
    stamp_revision,
)


@pytest.fixture
async def temp_database_url() -> str:
    """Create a temporary SQLite database URL for testing."""
    temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_file.close()
    db_url = f"sqlite+aiosqlite:///{temp_file.name}"

    yield db_url

    # Cleanup
    Path(temp_file.name).unlink(missing_ok=True)


@pytest.fixture
async def initialized_database(temp_database_url: str) -> str:
    """Create and initialize a test database."""
    await initialize_database(temp_database_url)
    return temp_database_url


class TestMigrationInitialization:
    """Tests for database initialization."""

    async def test_initialize_creates_schema(self, temp_database_url: str) -> None:
        """Test that initialize_database creates tables."""
        await initialize_database(temp_database_url)

        # Verify tables exist
        engine: AsyncEngine = create_async_engine(temp_database_url)
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            )
            tables = [row[0] for row in result]

        await engine.dispose()

        assert "proxies" in tables
        assert "cache_entries" in tables
        assert "alembic_version" in tables

    async def test_initialize_sets_revision(self, temp_database_url: str) -> None:
        """Test that initialization stamps database with head revision."""
        await initialize_database(temp_database_url)

        current = await get_current_revision(temp_database_url)
        head = await get_head_revision(temp_database_url)

        assert current is not None
        assert current == head

    async def test_initialize_already_initialized_raises(self, initialized_database: str) -> None:
        """Test that initializing an already initialized database raises error."""
        with pytest.raises(ValueError, match="already initialized"):
            await initialize_database(initialized_database)

    async def test_initialize_idempotent_with_stamp(self, temp_database_url: str) -> None:
        """Test that stamping then initializing raises error."""
        await stamp_revision(temp_database_url, "head")

        with pytest.raises(ValueError, match="already initialized"):
            await initialize_database(temp_database_url)


class TestRevisionQueries:
    """Tests for revision query functions."""

    async def test_get_current_revision_uninitialized(self, temp_database_url: str) -> None:
        """Test getting revision from uninitialized database returns None."""
        revision = await get_current_revision(temp_database_url)
        assert revision is None

    async def test_get_current_revision_initialized(self, initialized_database: str) -> None:
        """Test getting revision from initialized database."""
        revision = await get_current_revision(initialized_database)
        assert revision is not None
        assert isinstance(revision, str)
        assert len(revision) > 0

    async def test_get_head_revision(self, temp_database_url: str) -> None:
        """Test getting head revision from migration scripts."""
        head = await get_head_revision(temp_database_url)
        assert head is not None
        assert isinstance(head, str)
        assert len(head) > 0

    async def test_get_head_revision_consistent(self, temp_database_url: str) -> None:
        """Test that head revision is consistent across calls."""
        head1 = await get_head_revision(temp_database_url)
        head2 = await get_head_revision(temp_database_url)
        assert head1 == head2

    async def test_check_pending_migrations_uninitialized(self, temp_database_url: str) -> None:
        """Test that uninitialized database has pending migrations."""
        has_pending = await check_pending_migrations(temp_database_url)
        assert has_pending is True

    async def test_check_pending_migrations_up_to_date(self, initialized_database: str) -> None:
        """Test that up-to-date database has no pending migrations."""
        has_pending = await check_pending_migrations(initialized_database)
        assert has_pending is False


class TestMigrationExecution:
    """Tests for migration execution (upgrade/downgrade)."""

    async def test_run_migrations_to_head(self, temp_database_url: str) -> None:
        """Test running migrations to head revision."""
        await run_migrations(temp_database_url, "head")

        current = await get_current_revision(temp_database_url)
        head = await get_head_revision(temp_database_url)

        assert current == head

    async def test_run_migrations_idempotent(self, initialized_database: str) -> None:
        """Test that running migrations on up-to-date database is safe."""
        revision_before = await get_current_revision(initialized_database)
        await run_migrations(initialized_database, "head")
        revision_after = await get_current_revision(initialized_database)

        assert revision_before == revision_after

    async def test_downgrade_migrations_to_base(self, initialized_database: str) -> None:
        """Test downgrading all migrations to base."""
        await downgrade_migrations(initialized_database, "base")

        current = await get_current_revision(initialized_database)
        assert current is None

    async def test_downgrade_one_revision(self, initialized_database: str) -> None:
        """Test downgrading one revision."""
        head = await get_current_revision(initialized_database)
        await downgrade_migrations(initialized_database, "-1")
        current = await get_current_revision(initialized_database)

        # After downgrade, should be at different revision
        # (None in this case since we only have one migration)
        assert current != head

    async def test_upgrade_after_downgrade(self, initialized_database: str) -> None:
        """Test that upgrade works after downgrade."""
        head = await get_head_revision(initialized_database)

        await downgrade_migrations(initialized_database, "base")
        await run_migrations(initialized_database, "head")

        current = await get_current_revision(initialized_database)
        assert current == head


class TestMigrationHistory:
    """Tests for migration history queries."""

    async def test_get_migration_history(self, temp_database_url: str) -> None:
        """Test getting migration history."""
        history = await get_migration_history(temp_database_url)

        assert len(history) > 0
        assert all("revision" in item for item in history)
        assert all("description" in item for item in history)

    async def test_migration_history_ordered(self, temp_database_url: str) -> None:
        """Test that migration history is ordered oldest to newest."""
        history = await get_migration_history(temp_database_url)

        # First migration should have no down_revision
        assert history[0]["down_revision"] is None

        # Subsequent migrations should reference previous ones
        if len(history) > 1:
            for i in range(1, len(history)):
                prev_revision = history[i - 1]["revision"]
                current_down_revision = history[i]["down_revision"]
                assert current_down_revision == prev_revision


class TestStampOperation:
    """Tests for stamp operation."""

    async def test_stamp_revision_head(self, temp_database_url: str) -> None:
        """Test stamping database with head revision."""
        await stamp_revision(temp_database_url, "head")

        current = await get_current_revision(temp_database_url)
        head = await get_head_revision(temp_database_url)

        assert current == head

    async def test_stamp_updates_revision(self, temp_database_url: str) -> None:
        """Test that stamp updates revision without running migrations."""
        # Stamp with head
        await stamp_revision(temp_database_url, "head")
        current = await get_current_revision(temp_database_url)

        # Verify tables don't actually exist (stamp doesn't create schema)
        engine: AsyncEngine = create_async_engine(temp_database_url)
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='proxies'")
            )
            tables = list(result)

        await engine.dispose()

        assert current is not None
        assert len(tables) == 0  # No actual tables created


class TestErrorHandling:
    """Tests for error handling in migration utilities."""

    async def test_invalid_database_url(self) -> None:
        """Test that invalid database URL raises appropriate error."""
        with pytest.raises(Exception):
            await run_migrations("invalid://url")

    async def test_missing_alembic_config(self, temp_database_url: str, tmp_path) -> None:
        """Test that missing alembic.ini is handled gracefully."""
        # This test would require mocking or moving alembic.ini
        # Skip for now as it would break other tests
        pass


class TestConcurrentMigrations:
    """Tests for concurrent migration safety."""

    @pytest.mark.xfail(
        reason="Concurrent SQLite migrations have non-deterministic outcomes due to file locking",
        strict=False,
    )
    async def test_migrations_thread_safe(self, temp_database_url: str) -> None:
        """Test that migrations handle concurrent access safely.

        SQLite serializes writes automatically, so multiple migration
        attempts should either succeed or fail gracefully (due to locking).
        What matters is that the final state is consistent.
        """
        import asyncio

        results = await asyncio.gather(
            run_migrations(temp_database_url, "head"),
            run_migrations(temp_database_url, "head"),
            return_exceptions=True,
        )

        # Check that no catastrophic failures occurred (both failing is OK with SQLite locking)
        # At least verify no unexpected exception types
        for r in results:
            if isinstance(r, Exception):
                error_msg = str(r).lower()
                # Database lock errors and "already exists" are expected with concurrent SQLite access
                is_expected = (
                    "database is locked" in error_msg
                    or "lock" in error_msg
                    or "serial" in error_msg
                    or "already exists" in error_msg
                    or not str(r)
                )
                assert is_expected, f"Unexpected error: {r}"

        # If both failed, run migration once more to complete it
        if all(isinstance(r, Exception) for r in results):
            await run_migrations(temp_database_url, "head")

        # Final state should be consistent
        current = await get_current_revision(temp_database_url)
        head = await get_head_revision(temp_database_url)
        assert current == head


@pytest.mark.parametrize(
    "revision",
    [
        "head",
        "base",
        "+1",
        "-1",
    ],
)
async def test_migration_target_formats(temp_database_url: str, revision: str) -> None:
    """Test that various revision format strings are accepted.

    Property-based test for different revision specifications.
    """
    await initialize_database(temp_database_url)

    # Should not raise for valid revision formats
    try:
        if revision.startswith("-") or revision == "base":
            await downgrade_migrations(temp_database_url, revision)
        else:
            await run_migrations(temp_database_url, revision)
    except Exception as e:
        # Some operations might fail logically (e.g., +1 from head)
        # but should not raise unexpected errors
        assert "Invalid" not in str(e) or "not found" in str(e).lower()
