"""Database migration utilities for ProxyWhirl.

This module provides a programmatic API for running Alembic migrations,
following ProxyWhirl's library-first architecture. It allows applications
to manage database schema versions without requiring command-line tools.

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

Example:
    ```python
    from proxywhirl.migrations import run_migrations, get_current_revision

    # Run all pending migrations
    await run_migrations("sqlite+aiosqlite:///./mydb.db")

    # Check current version
    revision = await get_current_revision("sqlite+aiosqlite:///./mydb.db")
    print(f"Database at revision: {revision}")
    ```
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from alembic import command


def _get_alembic_config(database_url: str | None = None) -> Config:
    """Get Alembic configuration object.

    Args:
        database_url: SQLAlchemy database URL. If None, uses default from alembic.ini

    Returns:
        Configured Alembic Config object
    """
    # Find alembic.ini in project root
    ini_path = Path(__file__).parent.parent / "alembic.ini"
    if not ini_path.exists():
        raise FileNotFoundError(
            f"alembic.ini not found at {ini_path}. Run 'alembic init alembic' to initialize."
        )

    config = Config(str(ini_path))

    # Override database URL if provided
    if database_url:
        config.set_main_option("sqlalchemy.url", database_url)

    return config


async def run_migrations(database_url: str | None = None, target_revision: str = "head") -> None:
    """Run all pending migrations up to target revision.

    This function executes Alembic migrations programmatically, allowing
    applications to manage schema versions without CLI tools. It uses
    async SQLite support for non-blocking execution.

    Args:
        database_url: SQLAlchemy async database URL (e.g., "sqlite+aiosqlite:///./db.sqlite").
            If None, uses default from alembic.ini
        target_revision: Target revision to migrate to. Defaults to "head" (latest).
            Can be specific revision ID, relative revision (e.g., "+1", "-2"),
            or branch label.

    Raises:
        FileNotFoundError: If alembic.ini or migration scripts not found
        ValueError: If target revision is invalid
        Exception: If migration fails

    Example:
        ```python
        # Migrate to latest
        await run_migrations("sqlite+aiosqlite:///./proxywhirl.db")

        # Migrate to specific revision
        await run_migrations("sqlite+aiosqlite:///./db.sqlite", "58c0fadfa0ca")

        # Rollback one revision
        await run_migrations("sqlite+aiosqlite:///./db.sqlite", "-1")
        ```
    """
    config = _get_alembic_config(database_url)

    # Run migration in async context
    # Note: Alembic command API is synchronous, but the migrations themselves
    # use async engine via env.py configuration
    await asyncio.get_event_loop().run_in_executor(None, command.upgrade, config, target_revision)


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
        FileNotFoundError: If alembic.ini or migration scripts not found
        ValueError: If target revision is invalid
        Exception: If downgrade fails

    Example:
        ```python
        # Downgrade one revision
        await downgrade_migrations("sqlite+aiosqlite:///./db.sqlite")

        # Downgrade to specific revision
        await downgrade_migrations("sqlite+aiosqlite:///./db.sqlite", "58c0fadfa0ca")

        # Rollback all migrations
        await downgrade_migrations("sqlite+aiosqlite:///./db.sqlite", "base")
        ```
    """
    config = _get_alembic_config(database_url)
    await asyncio.get_event_loop().run_in_executor(None, command.downgrade, config, target_revision)


async def get_current_revision(database_url: str | None = None) -> str | None:
    """Get the current migration revision of the database.

    Args:
        database_url: SQLAlchemy async database URL

    Returns:
        Current revision ID, or None if database is uninitialized

    Example:
        ```python
        revision = await get_current_revision("sqlite+aiosqlite:///./db.sqlite")
        if revision:
            print(f"Database at revision: {revision}")
        else:
            print("Database not initialized")
        ```
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

    Example:
        ```python
        head = await get_head_revision()
        current = await get_current_revision()
        if head != current:
            print(f"Migrations pending: {current} -> {head}")
        ```
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

    Example:
        ```python
        if await check_pending_migrations("sqlite+aiosqlite:///./db.sqlite"):
            print("WARNING: Pending migrations detected!")
            await run_migrations()
        ```
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

    Example:
        ```python
        # Initialize new database
        await initialize_database("sqlite+aiosqlite:///./newdb.sqlite")
        ```
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
        List of migration info dicts with keys: revision, down_revision, description

    Example:
        ```python
        history = await get_migration_history()
        for migration in history:
            print(f"{migration['revision']}: {migration['description']}")
        ```
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

    Example:
        ```python
        # Stamp database as being at head revision
        await stamp_revision("sqlite+aiosqlite:///./db.sqlite", "head")
        ```
    """
    config = _get_alembic_config(database_url)
    await asyncio.get_event_loop().run_in_executor(None, command.stamp, config, revision)
