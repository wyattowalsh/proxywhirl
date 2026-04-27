# Database Backup and Recovery Procedures

## Overview

This document describes automated and manual backup procedures for the proxywhirl database, including backup strategies, restoration procedures, and disaster recovery planning.

## Backup Strategies

### 1. Automated Backups

**Schedule**: Daily at 2 AM UTC (configurable)

```bash
# Enable automated backups via CLI
proxywhirl config set backup.enabled true
proxywhirl config set backup.frequency daily
proxywhirl config set backup.retention_days 30
```

**Configuration** (in `config.toml`):

```toml
[backup]
enabled = true
frequency = "daily"
retention_days = 30
backup_path = "~/.proxywhirl/backups"
include_logs = true
compression = "gzip"
```

### 2. Incremental Backups

For large databases, use incremental backups to reduce storage:

```bash
proxywhirl backup create --incremental --name "backup-$(date +%Y%m%d)"
```

### 3. Manual Backups

Create on-demand backups:

```bash
# Full backup
proxywhirl backup create --full

# Backup with timestamp
proxywhirl backup create --full --timestamp

# Backup with compression
proxywhirl backup create --full --compression gzip
```

## Backup Destinations

### Local Storage

```bash
proxywhirl backup config local --path /var/backups/proxywhirl
```

### Cloud Storage (S3)

```bash
proxywhirl backup config s3 \
  --bucket my-proxywhirl-backups \
  --region us-east-1 \
  --encryption AES256
```

### Azure Blob Storage

```bash
proxywhirl backup config azure \
  --container proxywhirl-backups \
  --account-name myaccount
```

## Restoration Procedures

### Restore Latest Backup

```bash
proxywhirl backup restore --latest
```

### Restore Specific Backup

```bash
proxywhirl backup restore --backup-id backup-20240115
```

### Restore to Point in Time

```bash
proxywhirl backup restore --point-in-time "2024-01-15T14:30:00Z"
```

### Restore Specific Tables

```bash
# Restore only proxy table
proxywhirl backup restore --latest --tables proxies

# Restore multiple tables
proxywhirl backup restore --latest --tables proxies,sessions
```

## Verification

### Backup Integrity Checks

```bash
# Verify backup consistency
proxywhirl backup verify --backup-id backup-20240115

# Check backup size and contents
proxywhirl backup info --backup-id backup-20240115
```

### Database Integrity After Restore

```bash
# Run integrity check
proxywhirl db check-integrity

# Generate repair report
proxywhirl db repair --dry-run
```

## Disaster Recovery Plan

### Scenario 1: Database Corruption

1. Create backup of corrupted database
2. Stop all ProxyWhirl instances
3. Restore from latest healthy backup
4. Verify restoration with integrity checks
5. Resume operations

```bash
proxywhirl db stop
proxywhirl backup restore --latest
proxywhirl db check-integrity
proxywhirl db start
```

### Scenario 2: Accidental Data Deletion

```bash
# Find nearest backup before deletion
proxywhirl backup list --before "2024-01-15T14:00:00Z"

# Restore specific table
proxywhirl backup restore --backup-id backup-20240115 --tables proxies
```

### Scenario 3: Hardware Failure

For complete system recovery:

1. Set up new ProxyWhirl instance
2. Restore database from backup
3. Restore configuration from backup
4. Restore certificates and secrets
5. Verify all services

```bash
# Full restore to new system
proxywhirl backup restore --full --backup-id backup-20240115
proxywhirl config import backup-20240115.config.tar.gz
```

## Backup Retention Policy

- **Daily backups**: Retained 30 days
- **Weekly backups**: Retained 90 days
- **Monthly backups**: Retained 1 year
- **Annual backups**: Retained 7 years (compliance)

```bash
proxywhirl backup retention set \
  --daily 30 \
  --weekly 90 \
  --monthly 365 \
  --annual 2555
```

## Monitoring and Alerts

### Backup Status Monitoring

```bash
# Check last backup status
proxywhirl backup status

# Monitor ongoing backups
proxywhirl backup monitor
```

### Alerts

Configure alerts for backup failures:

```bash
proxywhirl alert config backup \
  --failure-threshold 2 \
  --notify-email ops@example.com \
  --notify-slack #backup-alerts
```

## Security Considerations

### Encryption

- All backups encrypted with AES-256
- Separate encryption keys for each environment
- Key rotation every 90 days

```bash
proxywhirl backup config encryption --algorithm AES256 --key-rotation 90
```

### Access Control

- Backups require authentication to restore
- Audit logging for all backup operations
- Role-based access (admin-only restore)

## Testing Disaster Recovery

### Monthly Recovery Drills

```bash
# Restore to test environment
proxywhirl backup restore \
  --backup-id backup-20240115 \
  --target-database test_db \
  --dry-run
```

### Recovery Time Objective (RTO)

- Small database (<1GB): 5 minutes
- Medium database (1-10GB): 15 minutes
- Large database (>10GB): 1 hour

## Troubleshooting

### Backup Fails to Create

```bash
# Check disk space
proxywhirl backup diagnose disk-space

# Verify backup path permissions
proxywhirl backup diagnose permissions

# Check connectivity to storage backend
proxywhirl backup diagnose connectivity
```

### Restore Fails

```bash
# Verify backup integrity first
proxywhirl backup verify --backup-id backup-20240115

# Check database compatibility
proxywhirl db check-compatibility --backup-id backup-20240115

# Attempt restore with verbose logging
proxywhirl backup restore --backup-id backup-20240115 --verbose
```

## Best Practices

1. **Test restores regularly** - Verify backups can actually be restored
2. **Geographic redundancy** - Keep backups in multiple regions
3. **Monitor backup completion** - Set up alerts for failed backups
4. **Document recovery procedures** - Keep procedures current and accessible
5. **Separate encryption keys** - Never store backup keys with backups
6. **Automate backup verification** - Automatically verify backup integrity
