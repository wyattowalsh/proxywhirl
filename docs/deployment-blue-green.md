# Blue-Green Deployment Strategy

## Overview

Blue-Green deployment enables zero-downtime deployments by running two identical production environments. At any time, only one (Blue or Green) handles traffic, while the other is prepared for the next release.

## Architecture

```
                     ┌─────────────────────────────────┐
                     │      Load Balancer / Router     │
                     │   (Traffic Control Point)       │
                     └────────────┬────────────────────┘
                                  │
                    ┌─────────────┴──────────────┐
                    │                            │
            ┌───────▼──────┐          ┌──────────▼────────┐
            │  Blue Env    │          │   Green Env       │
            │  (ACTIVE)    │          │   (STANDBY)       │
            │              │          │                   │
            │ - ProxyWhirl │          │ - ProxyWhirl      │
            │ - Database   │          │ - Database        │
            │ - Config     │          │ - Config          │
            └──────────────┘          └───────────────────┘

Traffic: 100% Blue                    Prepared for next release
```

## Deployment Workflow

### Phase 1: Preparation

```bash
# 1. Verify current active environment (Blue)
proxywhirl deployment status
# Output: Blue is ACTIVE, Green is STANDBY

# 2. Check resource requirements
proxywhirl deployment validate-resources --target green

# 3. Create backup before switching
proxywhirl backup create --full --name "blue-green-20240115-1400"
```

### Phase 2: Deploy to Standby (Green)

```bash
# 1. Stop deployment on active environment
proxywhirl deployment lock blue

# 2. Deploy new version to Green
proxywhirl deployment deploy --target green --version v1.2.0

# 3. Run migrations on Green
proxywhirl db migrate --target green

# 4. Restore latest data to Green
proxywhirl backup restore --target green --latest

# 5. Verify Green deployment
proxywhirl health check --target green --full

# 6. Run integration tests on Green
uv run pytest tests/integration/ --target green -v
```

### Phase 3: Smoke Testing

```bash
# Test all critical endpoints on Green (no traffic)
proxywhirl test --target green --suite smoke

# Verify database connectivity
proxywhirl db test-connection --target green

# Check cache functionality
proxywhirl cache verify --target green

# Test authentication/authorization
proxywhirl test-auth --target green
```

### Phase 4: Traffic Switchover

```bash
# 1. Prepare for switchover
proxywhirl deployment prepare-switchover

# 2. Show current traffic distribution
proxywhirl deployment traffic-status
# Output: Blue 100%, Green 0%

# 3. Switch 100% traffic to Green
proxywhirl deployment switch --from blue --to green

# 4. Verify traffic switched
proxywhirl deployment traffic-status
# Output: Blue 0%, Green 100%

# 5. Monitor for errors
proxywhirl monitor --duration 5m --target green
```

### Phase 5: Validation and Rollback

```bash
# Monitor Green for 5-10 minutes
sleep 300
proxywhirl health check --target green

# If issues detected, immediate rollback
proxywhirl deployment rollback --from green --to blue

# If successful, proceed to cleanup
proxywhirl deployment complete-switch
```

## Automated Blue-Green Deployment

### GitHub Actions Workflow

```yaml
name: Blue-Green Deployment

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to deploy'
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check deployment readiness
        run: proxywhirl deployment check-readiness

      - name: Backup Blue environment
        run: proxywhirl backup create --full

      - name: Deploy to Green
        run: |
          proxywhirl deployment deploy \
            --target green \
            --version ${{ github.event.inputs.version }}

      - name: Run smoke tests on Green
        run: uv run pytest tests/integration/test_smoke.py

      - name: Switch traffic to Green
        if: success()
        run: proxywhirl deployment switch --from blue --to green

      - name: Monitor Green
        run: proxywhirl monitor --duration 5m --target green

      - name: Rollback if needed
        if: failure()
        run: proxywhirl deployment rollback --from green --to blue
```

## Canary Deployment Within Blue-Green

```bash
# Gradual traffic shift from Blue to Green
proxywhirl deployment switch --from blue --to green --canary

# Traffic distribution schedule:
# Time 0:   Blue 100%, Green 0%
# Time 2m:  Blue 95%,  Green 5%
# Time 4m:  Blue 90%,  Green 10%
# Time 6m:  Blue 75%,  Green 25%
# Time 8m:  Blue 50%,  Green 50%
# Time 10m: Blue 25%,  Green 75%
# Time 12m: Blue 0%,   Green 100%

# Monitor error rate during canary
proxywhirl metrics error-rate --watch
```

## Database Synchronization

### Shared Database Approach

```bash
# Both Blue and Green use same database
proxywhirl deployment configure --shared-db

# Run migrations before switch
proxywhirl db migrate --version v1.2.0

# Backward compatibility required for version transitions
```

### Separate Database Approach

```bash
# Each environment has separate database
proxywhirl deployment configure --separate-db

# Sync data before switch
proxywhirl db sync --from blue --to green

# Verify data consistency
proxywhirl db compare --blue-db --green-db
```

### Dual-Write Approach

```bash
# During transition, write to both databases
proxywhirl deployment enable-dual-write

# Monitor sync lag
proxywhirl monitor sync-lag --target green

# Verify both databases match
proxywhirl db verify-sync --blue-db --green-db

# Switch reads to Green when lag < 100ms
proxywhirl deployment complete-switch
```

## Rollback Procedures

### Immediate Rollback

```bash
# If critical issues detected immediately after switch
proxywhirl deployment rollback --from green --to blue

# Verify rollback
proxywhirl health check --target blue --full

# Investigate issue
proxywhirl logs analyze --target green --duration 5m
```

### Scheduled Rollback

```bash
# Keep both environments running for 24 hours
proxywhirl deployment keep-both --duration 24h

# If issues detected within 24h:
proxywhirl deployment rollback --from green --to blue
```

### Partial Rollback

```bash
# Rollback specific services only
proxywhirl deployment rollback-service --service cache --target green

# Keep other services on new version
proxywhirl deployment status
```

## Monitoring During Switch

### Key Metrics to Monitor

```bash
# Error rate (target: < 0.1%)
proxywhirl metrics error-rate

# Response time (target: < 200ms p99)
proxywhirl metrics latency --percentile 99

# Database connections
proxywhirl metrics db-connections

# CPU/Memory usage
proxywhirl metrics resource-usage

# API availability
proxywhirl metrics api-availability
```

### Automated Monitoring

```bash
# Enable continuous monitoring
proxywhirl monitor deploy --target green \
  --alert-on-error-rate 0.5% \
  --alert-on-latency 500ms \
  --alert-on-failures 5

# Receive alerts via:
proxywhirl alert configure \
  --email ops@example.com \
  --slack #deployment-alerts \
  --pagerduty p1-escalation-policy
```

## Environment Configuration

### Blue Environment (Active)

```bash
# Current production configuration
proxywhirl deployment config --target blue --show

# Lock blue from changes
proxywhirl deployment lock --target blue
```

### Green Environment (Standby)

```bash
# Prepare Green for deployment
proxywhirl deployment prepare --target green

# Copy configuration from Blue
proxywhirl deployment sync-config --from blue --to green

# Override specific settings for testing
proxywhirl deployment config --target green --set FEATURE_FLAG_X=true
```

## Cleanup After Successful Deployment

```bash
# After successful Green deployment:

# 1. Mark Blue as old environment
proxywhirl deployment mark-old --target blue

# 2. Keep Blue as rollback target for 24 hours
proxywhirl deployment keep-backup --target blue --duration 24h

# 3. After 24h, clean up Blue
proxywhirl deployment cleanup --target blue --safe
```

## Cost Optimization

```bash
# Reduce resource allocation on standby during off-hours
proxywhirl deployment schedule-scale-down \
  --target green \
  --hours "22:00-08:00" \
  --replicas 1

# Scale back up for production
proxywhirl deployment schedule-scale-up \
  --target green \
  --hours "08:00-22:00" \
  --replicas 3
```

## Troubleshooting

### Deployment Takes Too Long

```bash
# Check deployment progress
proxywhirl deployment progress

# Identify slow steps
proxywhirl deployment analyze-timing

# Optimize using parallel deployment
proxywhirl deployment deploy --target green --parallel
```

### Data Sync Issues

```bash
# Verify database consistency
proxywhirl db compare --blue-db --green-db

# Check for replication lag
proxywhirl monitor sync-lag

# Manually sync if needed
proxywhirl db sync --from blue --to green --full
```

### Traffic Switchover Failures

```bash
# Check load balancer health
proxywhirl lb status

# Verify DNS resolution
nslookup api.example.com

# Check Green environment health
proxywhirl health check --target green --full

# Retry switch with verbose logging
proxywhirl deployment switch --from blue --to green --verbose
```

## Best Practices

1. **Test before switch** - Run full test suite on Green
2. **Monitor actively** - Don't automate without monitoring
3. **Keep rollback ready** - Always maintain rollback path
4. **Document changes** - Track what changed between Blue/Green
5. **Schedule wisely** - Deploy during low-traffic periods
6. **Verify in staging** - Test full process in staging environment
7. **Communicate clearly** - Notify stakeholders of deployment
8. **Plan for failure** - Have rollback procedures ready
