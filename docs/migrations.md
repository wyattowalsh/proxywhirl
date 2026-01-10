# Database Migrations Guide

ProxyWhirl uses [Alembic](https://alembic.sqlalchemy.org/) for database schema migrations, providing robust version control for the SQLite database schema.

## Overview

Alembic manages incremental changes to the database schema over time, allowing you to:

- **Track schema versions** in version control alongside code
- **Upgrade databases** to newer schema versions
- **Rollback changes** if needed
- **Generate migrations** automatically from model changes
- **Test migrations** before deploying to production

## Quick Start

### Initialize a New Database

For new applications, initialize the database with the latest schema:

```python
from proxywhirl.migrations import initialize_database

# Initialize database at latest schema
await initialize_database("sqlite+aiosqlite:///./proxywhirl.db")
```

### Run Migrations Programmatically

ProxyWhirl provides a library-first API for migrations:

```python
from proxywhirl.migrations import (
    run_migrations,
    check_pending_migrations,
    get_current_revision,
)

# Check if migrations are needed
if await check_pending_migrations("sqlite+aiosqlite:///./mydb.db"):
    print("Migrations pending...")
    await run_migrations("sqlite+aiosqlite:///./mydb.db")

# Check current database version
revision = await get_current_revision("sqlite+aiosqlite:///./mydb.db")
print(f"Database at revision: {revision}")
```

### Run Migrations via CLI

For command-line usage, use the Alembic CLI:

```bash
# Upgrade to latest version
uv run alembic upgrade head

# Show current revision
uv run alembic current

# Show migration history
uv run alembic history --verbose

# Downgrade one revision
uv run alembic downgrade -1

# Generate new migration after model changes
uv run alembic revision --autogenerate -m "description"
```

## Migration API Reference

### Core Functions

#### `initialize_database(database_url=None)`

Initialize a new database with the latest schema. Equivalent to running all migrations from scratch.

**Parameters:**
- `database_url` (str, optional): SQLAlchemy async database URL. If None, uses default from `alembic.ini`.

**Raises:**
- `ValueError`: If database is already initialized

**Example:**
```python
await initialize_database("sqlite+aiosqlite:///./newdb.sqlite")
```

---

#### `run_migrations(database_url=None, target_revision="head")`

Run all pending migrations up to the target revision.

**Parameters:**
- `database_url` (str, optional): SQLAlchemy async database URL
- `target_revision` (str): Target revision (default: "head")
  - `"head"` - Latest revision
  - `"58c0fadfa0ca"` - Specific revision ID
  - `"+1"` - One revision forward
  - `"-1"` - One revision back

**Example:**
```python
# Migrate to latest
await run_migrations("sqlite+aiosqlite:///./db.sqlite")

# Migrate to specific revision
await run_migrations("sqlite+aiosqlite:///./db.sqlite", "58c0fadfa0ca")
```

---

#### `downgrade_migrations(database_url=None, target_revision="-1")`

Downgrade database to a previous revision. **Use with caution in production.**

**Parameters:**
- `database_url` (str, optional): SQLAlchemy async database URL
- `target_revision` (str): Target revision (default: "-1")
  - `"-1"` - Previous revision
  - `"base"` - Rollback all migrations
  - `"58c0fadfa0ca"` - Specific revision ID

**Example:**
```python
# Downgrade one revision
await downgrade_migrations("sqlite+aiosqlite:///./db.sqlite")

# Rollback all migrations
await downgrade_migrations("sqlite+aiosqlite:///./db.sqlite", "base")
```

---

#### `get_current_revision(database_url=None)`

Get the current migration revision of the database.

**Returns:** Current revision ID (str) or None if uninitialized

**Example:**
```python
revision = await get_current_revision("sqlite+aiosqlite:///./db.sqlite")
if revision:
    print(f"Database at revision: {revision}")
else:
    print("Database not initialized")
```

---

#### `get_head_revision(database_url=None)`

Get the latest (head) migration revision available in code.

**Returns:** Head revision ID (str)

**Example:**
```python
head = await get_head_revision()
current = await get_current_revision()
if head != current:
    print(f"Migrations pending: {current} -> {head}")
```

---

#### `check_pending_migrations(database_url=None)`

Check if there are pending migrations that need to be applied.

**Returns:** True if pending migrations exist, False otherwise

**Example:**
```python
if await check_pending_migrations("sqlite+aiosqlite:///./db.sqlite"):
    print("WARNING: Pending migrations detected!")
    await run_migrations()
```

---

#### `get_migration_history(database_url=None)`

Get the complete migration history.

**Returns:** List of dicts with keys: `revision`, `down_revision`, `description`

**Example:**
```python
history = await get_migration_history()
for migration in history:
    print(f"{migration['revision']}: {migration['description']}")
```

---

#### `stamp_revision(database_url=None, revision="head")`

Stamp the database with a specific revision without running migrations.

**⚠️ Use with extreme caution!** This bypasses actual schema changes.

Useful for:
- Importing existing databases that match a schema version
- Recovering from migration issues

**Example:**
```python
# Mark database as being at head revision
await stamp_revision("sqlite+aiosqlite:///./db.sqlite", "head")
```

## Creating New Migrations

### Automatic Generation (Recommended)

After modifying SQLModel table definitions in `proxywhirl/storage.py`:

```bash
# Generate migration automatically
uv run alembic revision --autogenerate -m "add_column_xyz"

# Review generated migration in alembic/versions/
# Edit if needed (especially for data migrations)

# Test migration
uv run alembic upgrade head

# Verify with tests
uv run pytest tests/unit/test_migrations.py
```

### Manual Migration

For complex data migrations or when autogenerate isn't sufficient:

```bash
# Create empty migration
uv run alembic revision -m "custom_data_migration"

# Edit alembic/versions/TIMESTAMP_custom_data_migration.py
# Add upgrade() and downgrade() logic
```

Example manual migration:

```python
def upgrade() -> None:
    """Add default values to existing records."""
    op.execute(
        """
        UPDATE proxies 
        SET health_status = 'unknown' 
        WHERE health_status IS NULL
        """
    )

def downgrade() -> None:
    """Revert changes."""
    pass  # Data migrations often can't be cleanly reverted
```

## Best Practices

### 1. Always Test Migrations

```bash
# Create test database
uv run python -c "
from proxywhirl.migrations import initialize_database
import asyncio
asyncio.run(initialize_database('sqlite+aiosqlite:///./test.db'))
"

# Test upgrade
uv run alembic upgrade head

# Test downgrade
uv run alembic downgrade -1

# Test re-upgrade
uv run alembic upgrade head

# Run automated tests
uv run pytest tests/unit/test_migrations.py
```

### 2. Use Batch Operations for SQLite

SQLite has limited `ALTER TABLE` support. Always use batch operations:

```python
def upgrade() -> None:
    with op.batch_alter_table('proxies', schema=None) as batch_op:
        batch_op.add_column(sa.Column('new_field', sa.String()))
        batch_op.create_index('ix_new_field', ['new_field'])
```

Alembic's `render_as_batch=True` (configured in `alembic/env.py`) handles this automatically.

### 3. Never Import Models in Migrations

❌ **Don't do this:**
```python
from proxywhirl.storage import ProxyTable  # BAD!

def upgrade() -> None:
    # Model might change in future, breaking old migrations
    op.create_table(ProxyTable.__tablename__, ...)
```

✅ **Do this instead:**
```python
def upgrade() -> None:
    # Static schema definition
    op.create_table(
        'proxies',
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('protocol', sa.String(), nullable=True),
        # ...
    )
```

### 4. Make Migrations Reversible

Always implement both `upgrade()` and `downgrade()`:

```python
def upgrade() -> None:
    op.add_column('proxies', sa.Column('rating', sa.Float()))

def downgrade() -> None:
    op.drop_column('proxies', 'rating')
```

### 5. Use Comments

Add comments to complex migrations:

```python
def upgrade() -> None:
    """Add proxy rating system.
    
    Adds a rating column (0.0-1.0) to track proxy quality based on
    success rate and response time. Existing proxies default to 0.5.
    """
    op.add_column('proxies', sa.Column('rating', sa.Float(), default=0.5))
```

### 6. Check Migrations in CI/CD

Add to your CI pipeline:

```bash
# Check for pending migrations
uv run alembic check || {
    echo "ERROR: Database schema changes detected!"
    echo "Generate migrations with:"
    echo "  uv run alembic revision --autogenerate -m 'description'"
    exit 1
}
```

### 7. Backup Before Production Migrations

```bash
# Backup database
cp proxywhirl.db proxywhirl.db.backup.$(date +%Y%m%d_%H%M%S)

# Run migration
uv run alembic upgrade head

# Verify
uv run alembic current
```

## Application Integration

### Startup Migration Check

Run migrations automatically on application startup:

```python
from proxywhirl.migrations import check_pending_migrations, run_migrations
from loguru import logger

async def initialize_app():
    """Initialize application with database migrations."""
    db_url = "sqlite+aiosqlite:///./proxywhirl.db"
    
    if await check_pending_migrations(db_url):
        logger.info("Pending migrations detected, upgrading...")
        await run_migrations(db_url)
        logger.info("Migrations complete")
    else:
        logger.info("Database up to date")
```

### Health Check Endpoint

For REST API:

```python
from fastapi import FastAPI, HTTPException
from proxywhirl.migrations import get_current_revision, check_pending_migrations

app = FastAPI()

@app.get("/health/database")
async def database_health():
    """Check database health and migration status."""
    db_url = "sqlite+aiosqlite:///./proxywhirl.db"
    
    current = await get_current_revision(db_url)
    if current is None:
        raise HTTPException(
            status_code=500,
            detail="Database not initialized"
        )
    
    has_pending = await check_pending_migrations(db_url)
    
    return {
        "status": "warning" if has_pending else "healthy",
        "current_revision": current,
        "pending_migrations": has_pending,
    }
```

## Troubleshooting

### "Database already initialized" Error

This occurs when trying to initialize an already-initialized database:

```python
# Check current revision first
revision = await get_current_revision(db_url)
if revision:
    print(f"Database already initialized at {revision}")
    await run_migrations(db_url)  # Use upgrade instead
else:
    await initialize_database(db_url)
```

### Migration Conflicts

If multiple branches create migrations:

```bash
# Merge branches with migrations
uv run alembic merge heads -m "merge_branches"

# Or manually edit migration to specify down_revision
```

### Corrupted Migration State

If migration state is corrupted:

```bash
# Option 1: Stamp with correct revision (if schema matches)
uv run alembic stamp head

# Option 2: Restore from backup
cp proxywhirl.db.backup proxywhirl.db

# Option 3: Reinitialize (LOSES DATA!)
rm proxywhirl.db
uv run alembic upgrade head
```

### Testing Migration Recovery

Simulate failures:

```python
async def test_migration_recovery():
    """Test migration error handling."""
    db_url = "sqlite+aiosqlite:///./test.db"
    
    try:
        await run_migrations(db_url)
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        # Restore from backup
        await restore_from_backup()
        raise
```

## Directory Structure

```
proxywhirl/
├── alembic.ini              # Alembic configuration
├── alembic/
│   ├── env.py              # Migration environment (async support)
│   ├── script.py.mako      # Migration template
│   └── versions/           # Migration scripts
│       └── 20251120_..._initial_schema.py
└── proxywhirl/
    ├── storage.py          # SQLModel table definitions
    └── migrations.py       # Programmatic migration API
```

## Configuration

### alembic.ini

Key configuration options:

```ini
[alembic]
# Migration scripts location
script_location = alembic

# Database URL (can be overridden programmatically)
sqlalchemy.url = sqlite+aiosqlite:///./proxywhirl.db

# Filename template for migrations
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s

# Timezone for timestamps
timezone = UTC
```

### env.py

Configured with:
- **Async SQLite support** via aiosqlite
- **Batch mode** for SQLite ALTER operations
- **Naming conventions** for consistent constraint names
- **Type comparison** enabled for detecting column changes

## See Also

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [ProxyWhirl Configuration Guide](configuration.md)
- [ProxyWhirl API Reference](../reference/migrations.md)
