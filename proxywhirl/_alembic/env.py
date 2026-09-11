"""Packaged Alembic migration environment with async SQLite support.

This module configures the Alembic migration environment for ProxyWhirl's
SQLite database with async support using aiosqlite. It follows best practices
for SQLite migrations including batch operations for ALTER TABLE statements.

Key Features:
- Async SQLite support via aiosqlite
- Batch mode for SQLite ALTER TABLE operations
- Naming conventions for constraints and indexes
- Static schema approach (no model imports in migrations)
- Support for programmatic migration execution

References:
- Alembic async docs: https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio
- SQLite batch mode: https://alembic.sqlalchemy.org/en/latest/batch.html
"""

import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel

from alembic import context

# Import table models to populate metadata (must import to register with SQLModel.metadata)
from proxywhirl.storage import (  # noqa: F401
    ProxyAuditTable,
    ProxyIdentityTable,
    ProxyStatusTable,
    ValidationResultTable,
)

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate support
# This includes all SQLModel table definitions
target_metadata = SQLModel.metadata

# Naming convention for constraints (helps with autogenerate)
# This ensures consistent naming across different database backends
target_metadata.naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine, though an
    Engine is acceptable here as well. By skipping the Engine creation we don't
    even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    if url and url.startswith("sqlite") and "///~" in url:
        # Handle sqlite+aiosqlite:///~/path expansion
        url = url.replace("///~", f"///{os.path.expanduser('~')}")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Enable batch mode for SQLite
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection.

    Args:
        connection: SQLAlchemy connection to use for migrations
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # Enable batch mode for SQLite ALTER TABLE operations
        render_as_batch=True,
        # Compare types to detect column type changes
        compare_type=True,
        # Compare server defaults
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async support.

    In this scenario we need to create an Engine and associate a connection
    with the context. This uses the async engine from config.
    """
    # Create async engine from config
    configuration = config.get_section(config.config_ini_section, {})
    url = configuration.get("sqlalchemy.url")
    if url and url.startswith("sqlite") and "///~" in url:
        # Handle sqlite+aiosqlite:///~/path expansion
        url = url.replace("///~", f"///{os.path.expanduser('~')}")
        configuration["sqlalchemy.url"] = url

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_sync_migrations() -> None:
    """Run migrations with a synchronous engine (preferred under test load).

    Programmatic callers often invoke Alembic via ``asyncio.to_thread`` while an
    event loop is already running. Nesting ``asyncio.run`` + aiosqlite in that
    worker has been observed to hang under full-suite thread pressure. Sync
    SQLite avoids the nested loop entirely and is sufficient for DDL.
    """
    from sqlalchemy import engine_from_config

    configuration = config.get_section(config.config_ini_section, {})
    url = configuration.get("sqlalchemy.url")
    if url and url.startswith("sqlite") and "///~" in url:
        url = url.replace("///~", f"///{os.path.expanduser('~')}")
        configuration["sqlalchemy.url"] = url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Prefer the sync engine whenever the configured URL is not an explicit async
    driver. Async (``asyncio.run`` + aiosqlite) is retained only for direct
    async URLs when no event loop is already running.
    """
    url = config.get_main_option("sqlalchemy.url") or ""
    uses_async_driver = "+aiosqlite" in url or url.startswith("postgresql+asyncpg")

    if uses_async_driver:
        # If a loop is already running (e.g. mis-nested call), fall back to sync
        # so we never nest asyncio.run inside a live loop / saturated executor.
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(run_async_migrations())
            return
        # Convert async SQLite URL to sync for this process and re-enter sync path.
        if "+aiosqlite" in url:
            config.set_main_option("sqlalchemy.url", url.replace("sqlite+aiosqlite", "sqlite", 1))
        run_sync_migrations()
        return

    run_sync_migrations()


# Determine which mode to run in
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
