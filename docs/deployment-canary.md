# Canary Release Automation and Validation

## Overview

Canary releases gradually roll out new versions to a subset of production traffic, enabling early detection of issues before full deployment.

## Architecture

```
User Traffic (100%)
    │
    ├─ 95% → Stable Version (v1.0.0)
    │
    └─ 5% → Canary Version (v1.1.0)

If error rate < threshold after period:
    Increase canary % (5% → 10% → 25% → 50% → 100%)

If error rate > threshold:
    Rollback canary immediately
```

## Automated Canary Deployment

### Phase 1: Preparation

```bash
proxywhirl canary prepare --version v1.1.0 --initial-percentage 5

# Verify canary environment
proxywhirl health check --environment canary
```

### Phase 2: Gradual Rollout

```bash
# Configure rollout schedule
proxywhirl canary config \
  --version v1.1.0 \
  --schedule linear \
  --duration 30m \
  --steps "5%, 10%, 25%, 50%, 100%"

# Start canary release
proxywhirl canary deploy --version v1.1.0

# Monitor progress
proxywhirl canary monitor --watch
```

### Phase 3: Automatic Validation

```bash
# Metrics-based validation
proxywhirl canary metrics \
  --baseline v1.0.0 \
  --canary v1.1.0 \
  --thresholds \
    error_rate=0.5% \
    latency_p99=500ms \
    cpu_usage=80%

# Validation passes if:
# - Error rate increase < 0.5%
# - Latency p99 within 500ms of baseline
# - CPU usage < 80%
```

## Metrics for Canary Validation

```yaml
metrics:
  - name: error_rate
    threshold: "+0.5%"  # 0.5% increase over baseline
    action: "rollback_if_exceeded"
  
  - name: latency_p99
    threshold: "+100ms"  # Max 100ms increase
    action: "pause_and_alert"
  
  - name: cpu_usage
    threshold: 85%
    action: "rollback"
  
  - name: memory_usage
    threshold: 85%
    action: "rollback"
  
  - name: database_connections
    threshold: "+20%"
    action: "pause_and_alert"
```

## Automated Rollback

```bash
# Immediate rollback on critical metric
proxywhirl canary rollback --version v1.1.0 --reason "error_rate_exceeded"

# Verify rollback
proxywhirl canary status
```

## GitOps Integration

```yaml
name: Canary Release
on:
  release:
    types: [created]

jobs:
  canary_deploy:
    steps:
      - name: Start canary at 5%
        run: proxywhirl canary deploy --version ${{ github.event.release.tag_name }} --percentage 5
      
      - name: Wait and monitor
        run: sleep 300 && proxywhirl canary metrics --check-health
      
      - name: Increase to 25%
        if: success()
        run: proxywhirl canary deploy --percentage 25
      
      - name: Final check before full rollout
        run: proxywhirl canary validate --strict
      
      - name: Complete rollout
        if: success()
        run: proxywhirl canary complete --version ${{ github.event.release.tag_name }}
```

## Monitoring and Alerts

```bash
# Alert on canary metrics
proxywhirl alert create canary-error-rate \
  --condition "error_rate > baseline * 1.005" \
  --action "pause_canary"

proxywhirl alert create canary-latency \
  --condition "latency_p99 > baseline + 100ms" \
  --action "page_oncall"
```

See `deployment-canary.md` for complete details.
