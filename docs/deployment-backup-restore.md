# Production Deployment: Backup and Restore Strategies

## Overview

This guide details comprehensive backup and restore strategies for production deployments of ProxyWhirl, covering multiple scenarios, recovery objectives, and best practices.

## Strategic Objectives

### Recovery Time Objective (RTO)

- **Tier 1 (Critical)**: < 5 minutes (full service restore)
- **Tier 2 (High)**: < 30 minutes (proxy functionality)
- **Tier 3 (Standard)**: < 2 hours (full restoration)

### Recovery Point Objective (RPO)

- **Continuous replication**: < 1 minute
- **Hourly snapshots**: < 1 hour
- **Daily backups**: < 24 hours

## Multi-Tier Backup Strategy

### Tier 1: Local Snapshots (Hot)

```bash
# Hourly snapshots on local SSD
proxywhirl backup create --frequency hourly --retention 24h --local

# Configuration
[backup.local]
enabled = true
path = "/data/backups/local"
retention_hours = 24
compression = false  # No compression for speed
```

### Tier 2: Regional Backup (Warm)

```bash
# Daily backup to regional storage
proxywhirl backup create --frequency daily --retention 30d --regional

# Configuration
[backup.regional]
enabled = true
destination = "s3://backup-region-1/proxywhirl"
retention_days = 30
compression = "gzip"
encryption = "AES256"
```

### Tier 3: Geographic Redundancy (Cold)

```bash
# Weekly backup to geographically distant location
proxywhirl backup create --frequency weekly --retention 90d --geo-redundant

# Configuration
[backup.geo_redundant]
enabled = true
destination = "s3://backup-geo-distant/proxywhirl"
retention_days = 90
compression = "gzip"
encryption = "AES256"
multipart_upload = true
```

## Backup Architecture

```
Production Database
    ├─ Hourly Snapshots (Local SSD)
    │  └─ Keep: 24 hours
    │
    ├─ Daily Backups (Regional Storage)
    │  └─ Keep: 30 days
    │
    ├─ Weekly Backups (Geo-Distributed)
    │  └─ Keep: 90 days
    │
    └─ Monthly Archives (Compliance)
       └─ Keep: 7 years
```

## Automated Backup Configuration

### AWS S3 Setup

```bash
# Create backup IAM policy
cat > backup-policy.json << 'POLICY'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::proxywhirl-backups",
        "arn:aws:s3:::proxywhirl-backups/*"
      ]
    }
  ]
}
POLICY

# Configure ProxyWhirl for S3
proxywhirl backup config s3 \
  --bucket proxywhirl-backups \
  --region us-east-1 \
  --access-key AKIAIOSFODNN7EXAMPLE \
  --secret-key "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

### Google Cloud Storage Setup

```bash
# Configure GCS for backups
proxywhirl backup config gcs \
  --bucket proxywhirl-backups \
  --project my-project \
  --service-account-json /path/to/service-account.json
```

### Azure Blob Storage Setup

```bash
# Configure Azure for backups
proxywhirl backup config azure \
  --container proxywhirl-backups \
  --account-name myaccount \
  --account-key "DefaultEndpointsProtocol=https;..."
```

## Restore Procedures

### Rapid Recovery (Local Snapshot)

**Time: < 5 minutes**

```bash
# Restore from latest local snapshot
proxywhirl backup restore --local --latest

# Verify restoration
proxywhirl db check-integrity
proxywhirl health check
```

### Regional Restore (Regional Backup)

**Time: 5-30 minutes**

```bash
# List available regional backups
proxywhirl backup list --regional

# Restore from specific backup
proxywhirl backup restore --regional --backup-id backup-20240115-1200

# Verify restoration
proxywhirl db check-integrity
proxywhirl health check full
```

### Full Disaster Recovery (Geo-Distributed)

**Time: 30 minutes - 2 hours**

```bash
# Establish new infrastructure in different region
terraform apply -var="region=us-west-2"

# Restore from geo-distributed backup
proxywhirl backup restore --geo-redundant --backup-id backup-20240108

# Verify complete restoration
proxywhirl db check-integrity --full
proxywhirl health check full
proxywhirl test-connections
```

## Failover Procedures

### Active-Passive Failover

**Setup**:

```yaml
# Primary (Active)
Primary:
  host: primary.example.com
  role: active
  backup_frequency: hourly
  replication: secondary

# Secondary (Passive)
Secondary:
  host: secondary.example.com
  role: standby
  replication_lag: < 1 minute
```

**Failover steps**:

```bash
# 1. Detect primary failure
proxywhirl health monitor --target primary.example.com

# 2. Promote secondary
proxywhirl failover promote --target secondary.example.com

# 3. Verify promotion
proxywhirl status --target secondary.example.com

# 4. Update DNS/routing
# Contact DNS administrator to switch traffic
```

### Active-Active Replication

**Setup**:

```bash
# Enable bidirectional replication
proxywhirl replication enable \
  --primary primary.example.com \
  --secondary secondary.example.com \
  --bidirectional

# Configure conflict resolution
proxywhirl replication config \
  --conflict-resolution "last-write-wins"
```

## Disaster Recovery Scenarios

### Scenario A: Single Server Failure

```bash
# 1. Restore to replacement server
proxywhirl backup restore --latest

# 2. Restore configuration
proxywhirl config restore

# 3. Verify services
proxywhirl status
uv run pytest tests/integration/ -k "smoke"

# 4. Update DNS records
# DNS TTL: 5 minutes
```

**RTO**: 15 minutes | **RPO**: 1 hour

### Scenario B: Data Center Outage

```bash
# 1. Activate disaster recovery site
terraform apply -var="region=dr-region"

# 2. Restore databases
proxywhirl backup restore \
  --geo-redundant \
  --backup-id latest \
  --target /var/lib/proxywhirl

# 3. Restore configuration and secrets
proxywhirl config import dr-config-backup.tar.gz
proxywhirl secret import dr-secrets-backup.tar.gz

# 4. Verify all systems
proxywhirl health check full
proxywhirl test-api --target dr-region

# 5. Update global load balancer
# Point 100% traffic to DR region
```

**RTO**: 45 minutes | **RPO**: < 1 hour

### Scenario C: Ransomware Attack

```bash
# 1. Isolate affected systems
proxywhirl isolate-instance --instance-id i-xxx

# 2. Identify clean backup
proxywhirl backup list --before "2024-01-15T00:00:00Z"

# 3. Restore clean version
proxywhirl backup restore --backup-id backup-20240114-2300

# 4. Scan restored database
proxywhirl security scan --full

# 5. Verify integrity
proxywhirl db check-integrity

# 6. Resume operations
proxywhirl services start
```

**RTO**: 2 hours | **RPO**: 24 hours

## Backup Verification

### Automated Verification

```bash
# Daily backup verification
proxywhirl backup verify --daily

# Weekly full restore test
proxywhirl backup test-restore --weekly --dry-run
```

### Manual Verification

```bash
# List backup contents
proxywhirl backup info --backup-id backup-20240115

# Restore to test environment
proxywhirl backup restore \
  --backup-id backup-20240115 \
  --target test_db \
  --dry-run

# Verify test restore
proxywhirl db check-integrity --database test_db
```

## Retention Policies

```bash
# Configure retention
proxywhirl backup retention set \
  --local-hours 24 \
  --regional-days 30 \
  --geo-days 90 \
  --archive-years 7 \
  --compliance-years 10

# View current policy
proxywhirl backup retention show
```

## Monitoring and Alerting

### Backup Monitoring

```bash
# Enable backup monitoring
proxywhirl monitor backup --interval 3600

# Create alerts
proxywhirl alert create backup-failed \
  --condition "status = 'failed'" \
  --action email:ops@example.com

proxywhirl alert create backup-slow \
  --condition "duration > 3600" \
  --action slack:#database-alerts
```

### Restore Testing Alerts

```bash
# Alert if restore test fails
proxywhirl alert create restore-test-failed \
  --condition "test_status = 'failed'" \
  --action email:dba@example.com,slack:#critical

# Alert on restore duration
proxywhirl alert create restore-slow \
  --condition "duration > rto_target" \
  --action pagerduty:service-key
```

## Cost Optimization

### Tiered Storage

```bash
# Use lifecycle policies for cost optimization
# Local (Hot): $0.023/GB-month
# Regional (Warm): $0.012/GB-month
# Geo (Cold): $0.004/GB-month

proxywhirl backup lifecycle set \
  --move-to-regional-after 24h \
  --move-to-geo-after 30d \
  --delete-after 90d
```

### Deduplication

```bash
# Enable backup deduplication
proxywhirl backup config deduplication \
  --enabled true \
  --algorithm variable-length-chunking
```

## Documentation and Runbooks

Create and maintain:

1. **Backup Runbook**: Daily operations
2. **Restore Runbook**: Recovery procedures
3. **Failover Runbook**: Failover steps
4. **Disaster Recovery Plan**: Complete recovery guide
5. **RTO/RPO Agreement**: Define objectives
6. **Contact List**: Emergency contacts

## Testing Schedule

- **Weekly**: Local snapshot restore test
- **Monthly**: Regional backup restore test
- **Quarterly**: Full disaster recovery drill
- **Annually**: Geo-distributed backup test
