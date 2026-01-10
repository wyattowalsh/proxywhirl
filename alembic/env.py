"""Alembic migration environment configuration with async SQLite support.

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
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel

from alembic import context

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import table models to populate metadata (must import to register with SQLModel.metadata)
from proxywhirl.storage import (  # noqa: F401
    CacheEntryTable,
    CircuitBreakerStateTable,
    DailyStatsTable,
    ProxyTable,
    RequestLogTable,
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
    if url and url.startswith("sqlite"):
        # Handle sqlite+aiosqlite:///~/path expansion
        if "///~" in url:
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
    if url and url.startswith("sqlite"):
        # Handle sqlite+aiosqlite:///~/path expansion
        if "///~" in url:
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


def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async support wrapper.

    This is the entry point for online migrations. It wraps the async
    migration runner to work with Alembic's synchronous API.
    """
    asyncio.run(run_async_migrations())


# Determine which mode to run in
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
