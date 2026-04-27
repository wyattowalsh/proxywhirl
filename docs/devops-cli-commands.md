# ProxyWhirl CLI Commands (DevOps)

## Deployment Commands

```bash
# Deploy to environment
proxywhirl deploy --environment production --version v1.2.3

# Blue-green deployment
proxywhirl deploy blue-green --primary-version v1.2.2 --canary-version v1.2.3

# Canary deployment
proxywhirl deploy canary --version v1.2.3 --schedule linear:10,30,70,100

# Rollback to previous version
proxywhirl deploy rollback

# List deployment history
proxywhirl deploy history --environment production --limit 10

# Check deployment status
proxywhirl deploy status --environment production
```

## Monitoring Commands

```bash
# System health status
proxywhirl monitor health

# Real-time metrics
proxywhirl monitor metrics --interval 5s

# Alert status
proxywhirl monitor alerts --severity high

# Logs
proxywhirl monitor logs --tail 100 --since 1h

# Database metrics
proxywhirl monitor db --detailed
```

## Backup & Recovery Commands

```bash
# Create backup
proxywhirl backup create --destination s3://backups/proxywhirl

# List backups
proxywhirl backup list --days 7

# Restore from backup
proxywhirl backup restore --backup-id daily-2024-01-15

# Verify backup
proxywhirl backup verify --backup-id daily-2024-01-15

# Test restore (non-destructive)
proxywhirl backup restore-test --backup-id daily-2024-01-15
```

## Scaling Commands

```bash
# Scale API servers
proxywhirl scale api --replicas 10

# Auto-scaling policy
proxywhirl scale auto --min 2 --max 50 --cpu-threshold 80

# Database scaling
proxywhirl scale database --disk-size 500GB

# Cache scaling
proxywhirl scale cache --memory 128GB
```

## Admin Commands

```bash
# User management
proxywhirl admin user create --email user@example.com --role admin
proxywhirl admin user list
proxywhirl admin user delete --id user-id

# Audit log
proxywhirl admin audit --resource-type proxy --action delete --limit 100

# Configuration
proxywhirl admin config get --key database.pool_size
proxywhirl admin config set --key database.pool_size --value 30

# Maintenance mode
proxywhirl admin maintenance --enable --message "Scheduled maintenance"
```
