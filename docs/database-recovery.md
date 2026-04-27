# Database Recovery Procedures

## Overview

This document provides comprehensive procedures for recovering ProxyWhirl databases from various failure scenarios, including corruption, loss, and inconsistency issues.

## Recovery Scenarios

### Scenario 1: Database File Corruption

**Symptoms**: Error messages about corrupted database pages, inability to read records, crashes on query execution.

**Recovery Steps**:

1. **Identify the problem**:
```bash
# Check database integrity
proxywhirl db check-integrity --verbose

# Get detailed diagnosis
proxywhirl db diagnose corruption
```

2. **Create backup of corrupted database**:
```bash
# Preserve corrupted database for analysis
cp proxywhirl.db proxywhirl.db.corrupted
```

3. **Attempt automatic repair**:
```bash
# SQLite built-in PRAGMA integrity_check
proxywhirl db repair --auto-fix

# Verify after repair
proxywhirl db check-integrity
```

4. **If auto-repair fails, restore from backup**:
```bash
# List available backups
proxywhirl backup list

# Restore from pre-corruption backup
proxywhirl backup restore --point-in-time "2024-01-15T14:00:00Z"

# Verify restored database
proxywhirl db check-integrity
```

### Scenario 2: Accidental Data Deletion

**Symptoms**: Missing proxy records, deleted sessions, removed configurations.

**Recovery Steps**:

1. **Identify deletion time**:
```bash
# Check audit trail for deletion events
proxywhirl audit show --action delete --limit 100
```

2. **Find pre-deletion backup**:
```bash
# List backups before deletion
proxywhirl backup list --before "2024-01-15T14:30:00Z"

# Restore specific table if possible
proxywhirl backup restore --backup-id backup-20240115-1400 --tables proxies
```

3. **Selective recovery**:
```bash
# Restore to temporary database
proxywhirl backup restore --backup-id backup-20240115-1400 --target temp_db

# Extract needed data
proxywhirl db export --database temp_db --table proxies > proxies_recovery.json

# Import recovered data
proxywhirl db import --table proxies --source proxies_recovery.json
```

### Scenario 3: Incomplete Transactions

**Symptoms**: Inconsistent data, orphaned records, referential integrity violations.

**Recovery Steps**:

1. **Detect inconsistencies**:
```bash
# Run integrity checks
proxywhirl db check-integrity --full

# Check referential integrity
proxywhirl db check-references

# Generate repair suggestions
proxywhirl db repair --dry-run
```

2. **Automated inconsistency repair**:
```bash
# Fix referential integrity issues
proxywhirl db repair --fix-references

# Clean orphaned records
proxywhirl db cleanup --remove-orphaned

# Verify repairs
proxywhirl db check-integrity
```

### Scenario 4: Disk Space Issues

**Symptoms**: Database unable to write, transaction rollback, "database disk image is malformed".

**Recovery Steps**:

1. **Free disk space**:
```bash
# Check disk usage
proxywhirl db disk-usage

# Vacuum to reclaim space
proxywhirl db vacuum

# Archive old data
proxywhirl db archive --older-than 90days --destination archive_db
```

2. **Optimize database size**:
```bash
# Rebuild indexes
proxywhirl db reindex

# Compact database
proxywhirl db compact
```

3. **If still insufficient**:
```bash
# Restore to larger disk
proxywhirl backup restore --latest --target /larger-disk/proxywhirl.db
```

### Scenario 5: Hardware Failure

**Symptoms**: Complete database loss, corrupted WAL files, unrecoverable storage.

**Recovery Steps**:

1. **Set up new system**:
```bash
# Install ProxyWhirl on new hardware
uv sync

# Initialize new database
proxywhirl db init
```

2. **Restore from backup**:
```bash
# Restore full database
proxywhirl backup restore --full --backup-id backup-20240115-1400

# Restore configuration
proxywhirl config import config-backup-20240115.tar.gz

# Restore certificates
proxywhirl cert import certs-backup-20240115.tar.gz
```

3. **Verify recovery**:
```bash
# Check database integrity
proxywhirl db check-integrity

# Verify all services
proxywhirl status

# Run smoke tests
uv run pytest tests/integration/ -k "critical"
```

## Recovery Tools and Commands

### Database Integrity

```bash
# Full integrity check
proxywhirl db check-integrity --full

# Quick integrity check
proxywhirl db check-integrity

# Detailed diagnostics
proxywhirl db diagnose

# Repair options
proxywhirl db repair --help
```

### Backup and Restore

```bash
# List backups
proxywhirl backup list

# Backup info
proxywhirl backup info --backup-id backup-20240115

# Verify backup
proxywhirl backup verify --backup-id backup-20240115

# Restore options
proxywhirl backup restore --help
```

### Data Export/Import

```bash
# Export data
proxywhirl db export --table proxies --format json

# Import data
proxywhirl db import --table proxies --source proxies.json

# Bulk operations
proxywhirl db export-all --destination export_20240115.tar.gz
```

## Point-in-Time Recovery (PITR)

### Enable PITR

```bash
# Configure transaction logging
proxywhirl config set recovery.pitr.enabled true
proxywhirl config set recovery.pitr.log_level detailed
```

### Perform PITR

```bash
# Restore to specific point in time
proxywhirl backup restore \
  --point-in-time "2024-01-15T14:30:00Z" \
  --target recovered_db

# Verify recovery
proxywhirl db check-integrity --database recovered_db
```

## Automated Recovery

### Enable Auto-Recovery

```bash
# Enable automatic corruption detection and repair
proxywhirl config set recovery.auto_repair true
proxywhirl config set recovery.check_interval 3600  # 1 hour

# Configure alert notifications
proxywhirl alert config recovery \
  --notify-email ops@example.com \
  --notify-slack #database-alerts
```

### Monitor Auto-Recovery

```bash
# Check recovery status
proxywhirl recovery status

# View recovery logs
tail -f /var/log/proxywhirl/recovery.log

# Get recovery metrics
proxywhirl metrics recovery
```

## Prevention and Maintenance

### Regular Maintenance

```bash
# Schedule regular maintenance
proxywhirl db maintenance schedule \
  --frequency weekly \
  --day sunday \
  --time "02:00Z"

# Manual maintenance
proxywhirl db maintenance run --full
```

### Monitoring and Alerts

```bash
# Enable health monitoring
proxywhirl monitor database --interval 60

# Configure alerts
proxywhirl alert config database \
  --corruption-detection true \
  --performance-threshold 1000ms \
  --notify-email ops@example.com
```

## Testing Recovery Procedures

### Monthly Recovery Drills

```bash
# Restore to test environment
proxywhirl backup restore \
  --backup-id backup-latest \
  --target test_db

# Verify test restore
proxywhirl db check-integrity --database test_db

# Document RTO and RPO
echo "Recovery Time Objective (RTO): $(proxywhirl metrics recovery rto)"
echo "Recovery Point Objective (RPO): $(proxywhirl metrics recovery rpo)"
```

### Recovery Runbook

Keep a documented recovery runbook:

```
RECOVERY RUNBOOK
================

Critical Scenarios:
1. Database Corruption -> Use db repair or restore backup
2. Data Deletion -> Find pre-deletion backup, selective restore
3. Hardware Failure -> Restore full backup to new hardware
4. Disk Full -> Archive old data, vacuum, resize disk

Contact Information:
- Database Admin: dba@example.com
- On-Call: +1-555-0123

Escalation:
- P1: Immediate response, up to 5 min
- P2: Response within 15 minutes
- P3: Response within 1 hour
```

## Troubleshooting Recovery

### Restore Fails

```bash
# Check backup integrity
proxywhirl backup verify --backup-id backup-20240115

# Check target database compatibility
proxywhirl db check-compatibility --backup-id backup-20240115

# Attempt restore with verbose logging
proxywhirl backup restore --backup-id backup-20240115 --verbose
```

### Recovery Too Slow

```bash
# Check disk I/O
proxywhirl diagnose disk-io

# Use faster storage
# Restore to SSD instead of HDD

# Parallel restore
proxywhirl backup restore --backup-id backup-20240115 --parallel 4
```

### Partial Recovery Failures

```bash
# Restore single tables
proxywhirl backup restore --backup-id backup-20240115 --tables proxies

# Skip corrupted tables
proxywhirl backup restore --backup-id backup-20240115 --skip-tables corrupted_table

# Manual recovery for specific records
proxywhirl db recover-records --backup-id backup-20240115 --record-ids 1,2,3
```
