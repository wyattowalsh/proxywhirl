# Database Migration Procedures

## Overview

ProxyWhirl uses SQLModel with Alembic for database schema migrations. This document describes the migration process, best practices, and rollback procedures.

## Schema Evolution

### Current Database Schema

The database consists of the following primary tables:

- **proxies**: Proxy configuration and metadata
- **sessions**: User session management
- **health_checks**: Proxy health status history
- **metrics**: Performance metrics and statistics
- **audit_logs**: Audit trail of changes
- **configurations**: Application configuration snapshots

### Creating Migrations

#### Automatic Migration Generation

```bash
# After modifying SQLModel models, generate migration
alembic revision --autogenerate -m "description of changes"

# Review generated migration in alembic/versions/
cat alembic/versions/xxxx_description_of_changes.py
```

#### Manual Migration Creation

For complex changes:

```bash
# Create empty migration
alembic revision -m "custom migration description"

# Edit the created file to implement custom logic
nano alembic/versions/xxxx_custom_migration_description.py
```

### Migration Script Template

```python
"""Migration template for complex operations."""

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Apply migration."""
    # Schema changes
    op.add_column('proxies', sa.Column('new_field', sa.String(255)))
    
    # Data migrations
    connection = op.get_bind()
    # Add custom data transformation logic here
    
    # Index creation
    op.create_index('ix_proxies_new_field', 'proxies', ['new_field'])


def downgrade():
    """Rollback migration."""
    op.drop_index('ix_proxies_new_field')
    op.drop_column('proxies', 'new_field')
```

## Applying Migrations

### Development Environment

```bash
# Apply latest migrations
alembic upgrade head

# Apply specific revision
alembic upgrade xxxx

# Check current revision
alembic current

# View migration history
alembic history
```

### Production Environment

Always follow these procedures for production migrations:

#### 1. Pre-Migration Checklist

```bash
# 1. Backup database
proxywhirl backup create --full --name "pre-migration-$(date +%Y%m%d-%H%M%S)"

# 2. Verify backup
proxywhirl backup verify --latest

# 3. Test migrations on staging
alembic upgrade head --sql  # Generate SQL without applying

# 4. Schedule maintenance window
# - Notify stakeholders
# - Prepare rollback procedure
```

#### 2. Execute Migration

```bash
# Start migration with rollback capability
alembic upgrade head

# Monitor for errors
tail -f /var/log/proxywhirl/migrations.log

# Verify data integrity
proxywhirl db check-integrity
```

#### 3. Verification

```bash
# Confirm all changes applied
alembic current

# Validate schema integrity
proxywhirl db validate-schema

# Check for any migrations pending
alembic stamp head
```

## Rollback Procedures

### Automatic Rollback

If migration fails:

```bash
# Rollback to previous version
alembic downgrade -1  # Previous revision
alembic downgrade xxxx  # Specific revision

# Verify rollback
alembic current
```

### Full Database Restore

For critical migration failures:

```bash
# Restore from pre-migration backup
proxywhirl backup restore --backup-id "pre-migration-20240115-120000"

# Verify restored state
proxywhirl db check-integrity
```

## Migration Examples

### Example 1: Add New Column

```python
def upgrade():
    op.add_column(
        'proxies',
        sa.Column('proxy_chain', sa.String(255), nullable=True)
    )

def downgrade():
    op.drop_column('proxies', 'proxy_chain')
```

### Example 2: Rename Column

```python
def upgrade():
    op.alter_column('proxies', 'old_name', new_column_name='new_name')

def downgrade():
    op.alter_column('proxies', 'new_name', new_column_name='old_name')
```

### Example 3: Add Constraint

```python
def upgrade():
    op.create_unique_constraint(
        'uq_proxies_url',
        'proxies',
        ['url']
    )

def downgrade():
    op.drop_constraint('uq_proxies_url', 'proxies')
```

### Example 4: Add Index

```python
def upgrade():
    op.create_index(
        'ix_proxies_country',
        'proxies',
        ['country'],
        unique=False
    )

def downgrade():
    op.drop_index('ix_proxies_country')
```

### Example 5: Data Migration

```python
def upgrade():
    connection = op.get_bind()
    
    # Add new column
    op.add_column('proxies', sa.Column('status_v2', sa.String(50)))
    
    # Migrate data
    connection.execute("""
        UPDATE proxies
        SET status_v2 = CASE status
            WHEN 'active' THEN 'online'
            WHEN 'inactive' THEN 'offline'
            ELSE 'unknown'
        END
    """)
    
    # Drop old column
    op.drop_column('proxies', 'status')
    
    # Rename new column
    op.alter_column('proxies', 'status_v2', new_column_name='status')
```

## Best Practices

1. **One change per migration** - Keep migrations focused and reversible
2. **Always test rollbacks** - Verify downgrade() works
3. **Backup before production** - Never skip backup step
4. **Monitor application** - Watch for errors after migration
5. **Document changes** - Add comments to complex migrations
6. **Use descriptive names** - Migration filenames should describe changes
7. **Test in staging first** - Always test in staging environment
8. **Plan maintenance windows** - Schedule during low-traffic periods

## Troubleshooting

### Migration Fails to Apply

```bash
# Check migration syntax
alembic current

# View failed migration
cat alembic/versions/xxxx_failed_migration.py

# Get detailed error information
alembic upgrade head --verbose

# Check database logs
tail -f /var/log/proxywhirl/database.log
```

### Unable to Rollback

```bash
# Restore from backup if rollback fails
proxywhirl backup restore --latest

# Or manually execute downgrade
alembic downgrade base  # Rollback all migrations
```

### Schema Mismatch

```bash
# Verify schema integrity
proxywhirl db check-integrity

# Repair if possible
proxywhirl db repair --auto-fix

# Or restore from backup
proxywhirl backup restore --latest
```

## Migration Versioning

Migrations follow this naming convention:

```
XXXX_description_of_changes.py
```

Where:
- `XXXX` = 4-digit version number (auto-generated)
- `description_of_changes` = Descriptive name in snake_case

## Advanced Topics

### Zero-Downtime Migrations

For large tables, use multi-step migrations:

1. Create new column/table
2. Start dual-writing to old and new
3. Migrate historical data
4. Verify data completeness
5. Switch read traffic to new
6. Remove old column/table

### Concurrent Migrations

ProxyWhirl prevents concurrent migrations automatically:

```python
# Auto-locking during migration
with database_lock:
    apply_migration()
```

### Testing Migrations

```bash
# Create test database
pytest tests/integration/test_migrations.py

# Test specific migration
pytest tests/integration/test_migrations.py::test_migration_xxxx
```
