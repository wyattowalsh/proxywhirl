"""Database migration utilities for ProxyWhirl.

This module provides a programmatic API for running Alembic migrations,
following ProxyWhirl's library-first architecture. It allows applications
to manage database schema versions without requiring command-line tools.

Schema SSOT
-----------
All durable DDL lives under ``proxywhirl/_alembic/versions/``; the checkout's
``alembic/`` tree is a CLI bridge to those packaged resources. Application
code (including ``SQLiteStorage.initialize()``) must call
:func:`run_migrations` rather than issuing runtime ``ALTER TABLE`` / ad-hoc
schema patches.

Upgrade command (library)::

    from proxywhirl.migrations import run_migrations

    await run_migrations("sqlite+aiosqlite:///./proxywhirl.db", "head")

CLI equivalent::

    alembic upgrade head

Key Features:
- Programmatic migration execution
- Current revision checking
- Pending migrations detection
- Database initialization
- Async SQLite support

Best Practices:
- Always backup databases before migrations
- Test migrations in development first
- Use check_pending_migrations() in CI/CD
- Call run_migrations() on application startup

Example::

    from proxywhirl.migrations import run_migrations, get_current_revision

    # Run all pending migrations
    await run_migrations("sqlite+aiosqlite:///./mydb.db")

    # Check current version
    revision = await get_current_revision("sqlite+aiosqlite:///./mydb.db")
    print(f"Database at revision: {revision}")
"""

from __future__ import annotations

import asyncio
import hashlib
import tempfile
import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from filelock import FileLock
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from alembic import command

_PACKAGED_ALEMBIC_DIR = Path(__file__).resolve().parent / "_alembic"
_DEFAULT_DATABASE_URL = f"sqlite+aiosqlite:///{Path.home() / '.proxywhirl/proxywhirl.db'}"
_ALEMBIC_COMMAND_LOCK = threading.Lock()
_MIGRATION_LOCK_TIMEOUT_SECONDS = 120.0


def _normalize_database_url(database_url: str) -> str:
    """Normalize and validate a SQLAlchemy database URL for migrations."""
    if "\x00" in database_url:
        raise ValueError("Database URL must not contain null bytes")
    if ":///" not in database_url:
        return database_url

    scheme, path_part = database_url.split(":///", 1)
    if path_part in {":memory:", ""} or path_part.startswith("file:"):
        return database_url

    resolved = str(Path(path_part).expanduser().resolve())
    return f"{scheme}:///{resolved}"


def _get_alembic_config(database_url: str | None = None) -> Config:
    """Get Alembic configuration object.

    Args:
        database_url: SQLAlchemy database URL. If None, uses ProxyWhirl's default.

    Returns:
        Configured Alembic Config object
    """
    env_path = _PACKAGED_ALEMBIC_DIR / "env.py"
    versions_path = _PACKAGED_ALEMBIC_DIR / "versions"
    if not env_path.is_file() or not versions_path.is_dir():
        raise FileNotFoundError(
            "Packaged Alembic resources are incomplete; expected env.py and versions/ "
            f"under {_PACKAGED_ALEMBIC_DIR}"
        )

    config = Config()
    config.set_main_option("script_location", str(_PACKAGED_ALEMBIC_DIR))
    config.set_main_option("prepend_sys_path", str(Path(__file__).resolve().parent.parent))
    config.set_main_option(
        "sqlalchemy.url",
        _normalize_database_url(database_url or _DEFAULT_DATABASE_URL),
    )

    return config


def _sync_migration_url(database_url: str | None) -> str:
    """Return a synchronous URL for Alembic DDL execution."""
    migration_url = database_url or _DEFAULT_DATABASE_URL
    if "sqlite+aiosqlite://" in migration_url:
        return migration_url.replace("sqlite+aiosqlite://", "sqlite://", 1)
    return migration_url


def _migration_lock_path(config: Config) -> Path:
    """Return a credential-safe cross-process lock path for one database URL."""
    database_url = config.get_main_option("sqlalchemy.url") or "proxywhirl-default"
    digest = hashlib.sha256(database_url.encode("utf-8")).hexdigest()
    lock_dir = Path(tempfile.gettempdir()) / "proxywhirl-migration-locks"
    lock_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    return lock_dir / f"{digest}.lock"


def _run_locked_alembic_command(
    operation: Callable[[Config, str], None],
    config: Config,
    target_revision: str,
) -> None:
    """Serialize Alembic's process-global environment and one database target.

    Alembic installs a process-global context proxy while loading ``env.py``.
    Concurrent environment execution in worker threads can corrupt that proxy
    before SQLite has an opportunity to serialize DDL. The in-process mutex
    protects Alembic itself; the hashed file lock also serializes separate
    ProxyWhirl processes targeting the same normalized database URL.
    """
    with _ALEMBIC_COMMAND_LOCK:
        lock = FileLock(
            _migration_lock_path(config),
            timeout=_MIGRATION_LOCK_TIMEOUT_SECONDS,
        )
        with lock:
            operation(config, target_revision)


async def run_migrations(database_url: str | None = None, target_revision: str = "head") -> None:
    """Run all pending migrations up to target revision.

    This is the canonical schema upgrade entry point. Alembic revisions under
    ``proxywhirl/_alembic/versions/`` are the sole source of truth for durable DDL;
    ``SQLiteStorage.initialize()`` delegates here.

    This function executes Alembic migrations programmatically, allowing
    applications to manage schema versions without CLI tools. Synchronous
    Alembic DDL execution is moved off the caller's event-loop thread.

    Args:
        database_url: SQLAlchemy async database URL (e.g., "sqlite+aiosqlite:///./db.sqlite").
            If None, uses ProxyWhirl's default database path.
        target_revision: Target revision to migrate to. Defaults to "head" (latest).
            Can be specific revision ID, relative revision (e.g., "+1", "-2"),
            or branch label.

    Raises:
        FileNotFoundError: If the packaged migration resources are incomplete
        ValueError: If target revision is invalid
        Exception: If migration fails

    Example::

        # Migrate to latest
        await run_migrations("sqlite+aiosqlite:///./proxywhirl.db")

        # Migrate to specific revision
        await run_migrations("sqlite+aiosqlite:///./db.sqlite", "58c0fadfa0ca")

        # Rollback one revision
        await run_migrations("sqlite+aiosqlite:///./db.sqlite", "-1")
    """
    # Prefer sync SQLite for Alembic DDL. env.py still accepts aiosqlite URLs,
    # but nesting asyncio.run inside asyncio.to_thread under full-suite load has
    # hung the default executor (see quality-gates timeouts on SQLiteStorage.initialize).
    config = _get_alembic_config(_sync_migration_url(database_url))

    # Alembic command API is synchronous; run off the event loop thread.
    await asyncio.to_thread(_run_locked_alembic_command, command.upgrade, config, target_revision)


async def downgrade_migrations(
    database_url: str | None = None, target_revision: str = "-1"
) -> None:
    """Downgrade database to a previous revision.

    Use with caution in production. Always backup data before downgrading.

    Args:
        database_url: SQLAlchemy async database URL
        target_revision: Target revision to downgrade to. Defaults to "-1" (previous).
            Can be specific revision ID, relative revision, or "base" for complete
            rollback.

    Raises:
        FileNotFoundError: If the packaged migration resources are incomplete
        ValueError: If target revision is invalid
        Exception: If downgrade fails

    Example::

        # Downgrade one revision
        await downgrade_migrations("sqlite+aiosqlite:///./db.sqlite")

        # Downgrade to specific revision
        await downgrade_migrations("sqlite+aiosqlite:///./db.sqlite", "58c0fadfa0ca")

        # Rollback all migrations
        await downgrade_migrations("sqlite+aiosqlite:///./db.sqlite", "base")
    """
    config = _get_alembic_config(_sync_migration_url(database_url))
    await asyncio.to_thread(_run_locked_alembic_command, command.downgrade, config, target_revision)


async def get_current_revision(database_url: str | None = None) -> str | None:
    """Get the current migration revision of the database.

    Args:
        database_url: SQLAlchemy async database URL

    Returns:
        Current revision ID, or None if database is uninitialized

    Example::

        revision = await get_current_revision("sqlite+aiosqlite:///./db.sqlite")
        if revision:
            print(f"Database at revision: {revision}")
        else:
            print("Database not initialized")
    """
    config = _get_alembic_config(database_url)
    url = config.get_main_option("sqlalchemy.url")

    if not url:
        raise ValueError("No database URL configured")

    # Create async engine
    engine: AsyncEngine = create_async_engine(url, echo=False)

    try:
        async with engine.connect() as connection:

            def get_revision(conn):
                context = MigrationContext.configure(conn)
                return context.get_current_revision()

            revision = await connection.run_sync(get_revision)
            return revision
    finally:
        await engine.dispose()


async def get_head_revision(database_url: str | None = None) -> str:
    """Get the latest (head) migration revision available.

    Args:
        database_url: SQLAlchemy async database URL (used to get config)

    Returns:
        Head revision ID

    Example::

        head = await get_head_revision()
        current = await get_current_revision()
        if head != current:
            print(f"Migrations pending: {current} -> {head}")
    """
    config = _get_alembic_config(database_url)
    script_dir = ScriptDirectory.from_config(config)
    head = script_dir.get_current_head()

    if not head:
        raise ValueError("No migrations found in alembic/versions/")

    return head


async def check_pending_migrations(database_url: str | None = None) -> bool:
    """Check if there are pending migrations that need to be applied.

    This is useful for CI/CD pipelines and application health checks.

    Args:
        database_url: SQLAlchemy async database URL

    Returns:
        True if pending migrations exist, False otherwise

    Example::

        if await check_pending_migrations("sqlite+aiosqlite:///./db.sqlite"):
            print("WARNING: Pending migrations detected!")
            await run_migrations()
    """
    current = await get_current_revision(database_url)
    head = await get_head_revision(database_url)

    # If current is None, database is uninitialized (pending migrations)
    if current is None:
        return True

    return current != head


async def initialize_database(database_url: str | None = None) -> None:
    """Initialize a new database with the latest schema.

    This is a convenience function that creates all tables at the current
    head revision without running individual migrations. Equivalent to
    running all migrations from scratch.

    Args:
        database_url: SQLAlchemy async database URL

    Raises:
        Exception: If database already has schema or initialization fails

    Example::

        # Initialize new database
        await initialize_database("sqlite+aiosqlite:///./newdb.sqlite")
    """
    current = await get_current_revision(database_url)

    if current is not None:
        raise ValueError(
            f"Database already initialized at revision {current}. Use run_migrations() to upgrade."
        )

    await run_migrations(database_url, "head")


async def get_migration_history(
    database_url: str | None = None,
) -> list[dict[str, str | None]]:
    """Get the migration history showing all applied migrations.

    Args:
        database_url: SQLAlchemy async database URL

    Returns:
        list[dict[str, str | None]]: Migration records with keys revision, down_revision, description.

    Example::

        history = await get_migration_history()
        for migration in history:
            print(f"{migration['revision']}: {migration['description']}")
    """
    config = _get_alembic_config(database_url)
    script_dir = ScriptDirectory.from_config(config)

    history = []
    for revision in script_dir.walk_revisions("base", "head"):
        history.append(
            {
                "revision": revision.revision,
                "down_revision": revision.down_revision,
                "description": revision.doc,
            }
        )

    # Reverse to show oldest first
    return list(reversed(history))


async def stamp_revision(database_url: str | None = None, revision: str = "head") -> None:
    """Stamp the database with a specific revision without running migrations.

    This is useful when importing an existing database that matches a specific
    schema version, or for recovering from migration issues.

    **Use with extreme caution!** This bypasses actual schema changes.

    Args:
        database_url: SQLAlchemy async database URL
        revision: Revision to stamp database with

    Example::

        # Stamp database as being at head revision
        await stamp_revision("sqlite+aiosqlite:///./db.sqlite", "head")
    """
    config = _get_alembic_config(_sync_migration_url(database_url))
    await asyncio.to_thread(_run_locked_alembic_command, command.stamp, config, revision)


# ---------------------------------------------------------------------------
# In-memory migration registry (tests / tooling only). Production schema SSOT
# is Alembic revisions under ``proxywhirl/_alembic/versions/``.
# ---------------------------------------------------------------------------


class MigrationStatus(str, Enum):
    """Status of an in-memory schema migration record."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class _SchemaVersion:
    """Represents a database schema version (in-memory registry)."""

    version: int
    description: str
    created_at: datetime
    applied_at: datetime | None = None
    status: MigrationStatus = MigrationStatus.PENDING

    def __repr__(self) -> str:
        return f"v{self.version}: {self.description}"


class Migration:
    """In-memory migration descriptor (does not execute SQL)."""

    def __init__(
        self,
        version: int,
        description: str,
        up_script: str,
        down_script: str | None = None,
    ) -> None:
        self.version = version
        self.description = description
        self.up_script = up_script
        self.down_script = down_script or f"-- Rollback for v{version}"
        self.created_at = datetime.now(timezone.utc)

    def validate(self) -> bool:
        if not self.version or self.version < 1:
            return False
        if not self.description:
            return False
        return bool(self.up_script)


class SchemaVersioningManager:
    """In-memory migration registry for tests. Use :func:`run_migrations` in production."""

    def __init__(self) -> None:
        self._versions: dict[int, _SchemaVersion] = {}
        self._migrations: dict[int, Migration] = {}
        self._current_version = 0

    def register_migration(self, migration: Migration) -> bool:
        if not migration.validate():
            return False
        if migration.version in self._migrations:
            return False
        self._migrations[migration.version] = migration
        return True

    def apply_migration(self, version: int) -> bool:
        if version not in self._migrations:
            return False
        migration = self._migrations[version]
        schema_version = _SchemaVersion(
            version=version,
            description=migration.description,
            created_at=migration.created_at,
            applied_at=datetime.now(timezone.utc),
            status=MigrationStatus.COMPLETED,
        )
        self._versions[version] = schema_version
        self._current_version = version
        return True

    def rollback_migration(self, version: int) -> bool:
        if version not in self._versions or version not in self._migrations:
            return False
        schema_version = self._versions[version]
        schema_version.status = MigrationStatus.ROLLED_BACK
        self._current_version = version - 1
        return True

    def get_current_version(self) -> int:
        return self._current_version

    def get_migration(self, version: int) -> Migration | None:
        return self._migrations.get(version)

    def get_pending_migrations(self) -> list[Migration]:
        pending = []
        for version in sorted(self._migrations.keys()):
            if version > self._current_version:
                pending.append(self._migrations[version])
        return pending

    def get_applied_migrations(self) -> list[_SchemaVersion]:
        return sorted(self._versions.values(), key=lambda x: x.version)

    def export_status(self) -> dict[str, Any]:
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
