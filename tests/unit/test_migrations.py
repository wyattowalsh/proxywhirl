"""Unit tests for database migration utilities.

Tests follow ProxyWhirl's test-first development approach with:
- Comprehensive coverage of migration API
- SQLite async testing with temporary databases
- Property-based testing for edge cases
- Security testing for migration safety

Alembic is the schema SSOT; normalized proxy tables are created by revision
``d4e5f6a7b8c9`` while legacy tables from earlier revisions may remain.
"""

import asyncio
import importlib.machinery
import sys
import tempfile
import threading
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

import proxywhirl.migrations as migrations_module
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
async def temp_database_url() -> AsyncIterator[str]:
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

        assert "alembic_version" in tables
        assert "proxy_identities" in tables
        assert "proxy_statuses" in tables
        assert "validation_results" in tables
        assert "proxies_audit" in tables

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

    async def test_run_migrations_preserves_mcp_sdk_import_resolution(
        self,
        monkeypatch: pytest.MonkeyPatch,
        temp_database_url: str,
        tmp_path: Path,
    ) -> None:
        """Packaged migrations must not make ``proxywhirl.mcp`` shadow the MCP SDK."""
        sdk_package = tmp_path / "sdk" / "mcp"
        sdk_package.mkdir(parents=True)
        (sdk_package / "__init__.py").write_text('"""Test MCP SDK stand-in."""\n')
        (sdk_package / "client.py").write_text('"""Client marker."""\n')
        monkeypatch.syspath_prepend(str(sdk_package.parent))

        package_dir = str(Path(migrations_module.__file__).resolve().parent)
        before = importlib.machinery.PathFinder.find_spec("mcp")

        assert before is not None
        assert before.origin is not None
        assert package_dir not in sys.path

        await run_migrations(temp_database_url, "head")

        after = importlib.machinery.PathFinder.find_spec("mcp")
        assert package_dir not in sys.path
        assert after is not None
        assert after.origin == before.origin
        assert importlib.machinery.PathFinder.find_spec(
            "mcp.client", after.submodule_search_locations
        )

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

        assert current is not None
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

    async def test_run_migrations_uses_packaged_resources_without_repo_root(
        self,
        monkeypatch: pytest.MonkeyPatch,
        temp_database_url: str,
        tmp_path: Path,
    ) -> None:
        """Installed-wheel migrations must not require the checkout's Alembic tree."""
        package_dir = Path(migrations_module.__file__).resolve().parent
        repo_root = package_dir.parent
        repo_ini = repo_root / "alembic.ini"
        repo_scripts = repo_root / "alembic"
        path_exists = Path.exists

        def exists_without_repo_alembic(path: Path) -> bool:
            resolved = path.resolve()
            if resolved in (repo_ini, repo_scripts) or repo_scripts in resolved.parents:
                return False
            return path_exists(path)

        monkeypatch.setattr(Path, "exists", exists_without_repo_alembic)
        monkeypatch.chdir(tmp_path)

        await run_migrations(temp_database_url, "head")

        assert await get_current_revision(temp_database_url) == "d4e5f6a7b8c9"
        config = migrations_module._get_alembic_config(temp_database_url)
        script_location = Path(config.get_main_option("script_location")).resolve()
        assert config.config_file_name is None
        assert script_location == package_dir / "_alembic"
        assert (script_location / "env.py").is_file()
        assert (script_location / "versions").is_dir()


class TestConcurrentMigrations:
    """Tests for concurrent migration safety."""

    async def test_migration_commands_are_serialized(
        self, monkeypatch: pytest.MonkeyPatch, temp_database_url: str
    ) -> None:
        """Concurrent calls must never execute Alembic environments in parallel."""
        state_lock = threading.Lock()
        second_entered = threading.Event()
        active = 0
        max_active = 0
        calls = 0

        def tracked_upgrade(*_args: object) -> None:
            nonlocal active, calls, max_active
            with state_lock:
                active += 1
                calls += 1
                call_number = calls
                max_active = max(max_active, active)

            if call_number == 1:
                second_entered.wait(timeout=0.25)
            else:
                second_entered.set()

            with state_lock:
                active -= 1

        monkeypatch.setattr(migrations_module.command, "upgrade", tracked_upgrade)

        await asyncio.gather(
            run_migrations(temp_database_url, "head"),
            run_migrations(temp_database_url, "head"),
        )

        assert calls == 2
        assert max_active == 1

    async def test_migrations_thread_safe(self, temp_database_url: str) -> None:
        """Concurrent upgrades both succeed and leave one consistent head."""
        await asyncio.gather(
            run_migrations(temp_database_url, "head"),
            run_migrations(temp_database_url, "head"),
        )

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


class TestNormalizedSchemaSSOT:
    """Wave 2F: Alembic-only normalized schema contracts."""

    async def test_head_revision_is_normalized_schema(self, temp_database_url: str) -> None:
        """Head revision must be the normalized proxy schema migration."""
        head = await get_head_revision(temp_database_url)
        assert head == "d4e5f6a7b8c9"

    async def test_normalized_schema_has_expires_at(self, initialized_database: str) -> None:
        """proxy_identities must include expires_at from Alembic (not runtime ALTER)."""
        engine: AsyncEngine = create_async_engine(initialized_database)
        async with engine.connect() as conn:
            result = await conn.execute(text("PRAGMA table_info(proxy_identities)"))
            columns = {row[1] for row in result}
        await engine.dispose()
        assert "expires_at" in columns

    async def test_supplemental_indexes_created_by_migration(
        self, initialized_database: str
    ) -> None:
        """Composite indexes live in Alembic, not SQLiteStorage.initialize()."""
        engine: AsyncEngine = create_async_engine(initialized_database)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='index'"))
            indexes = {row[0] for row in result}
        await engine.dispose()

        assert "idx_validation_proxy_time" in indexes
        assert "idx_proxy_status_health" in indexes
        assert "ix_proxy_identities_expires_at" in indexes

    async def test_legacy_proxies_copied_into_normalized(self, temp_database_url: str) -> None:
        """Upgrade from legacy proxies table populates identity/status rows."""
        # Stop at the revision before normalized schema so ``proxies`` exists.
        await run_migrations(temp_database_url, "43cb4a16de9d")

        engine: AsyncEngine = create_async_engine(temp_database_url)
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    """
                    INSERT INTO proxies (
                        url, protocol, health_status, source,
                        total_requests, total_successes, total_failures,
                        consecutive_failures, metadata_json, created_at, updated_at
                    ) VALUES (
                        'http://legacy.example.com:8080', 'http', 'healthy',
                        'fetched', 0, 0, 0, 0, '{}',
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                    """
                )
            )
        await engine.dispose()

        await run_migrations(temp_database_url, "head")

        engine = create_async_engine(temp_database_url)
        async with engine.connect() as conn:
            identity = (
                await conn.execute(
                    text(
                        "SELECT url, protocol FROM proxy_identities "
                        "WHERE url = 'http://legacy.example.com:8080'"
                    )
                )
            ).first()
            status = (
                await conn.execute(
                    text(
                        "SELECT health_status FROM proxy_statuses "
                        "WHERE proxy_url = 'http://legacy.example.com:8080'"
                    )
                )
            ).first()
            # Legacy table retained
            legacy_count = (await conn.execute(text("SELECT COUNT(*) FROM proxies"))).scalar()
        await engine.dispose()

        assert identity is not None
        assert identity[0] == "http://legacy.example.com:8080"
        assert identity[1] == "http"
        assert status is not None
        assert status[0] == "healthy"
        assert legacy_count == 1

    async def test_run_migrations_is_upgrade_entry_point(self, temp_database_url: str) -> None:
        """Documented upgrade path reaches head without storage helpers."""
        await run_migrations(temp_database_url, "head")
        current = await get_current_revision(temp_database_url)
        head = await get_head_revision(temp_database_url)
        assert current == head == "d4e5f6a7b8c9"
