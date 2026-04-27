# Alert Thresholds & Response

## Service Level Indicators (SLIs)

```yaml
availability:
  threshold: 99.9%
  alert: < 99.0%
  
latency:
  p50: 50ms
  p95: 200ms
  p99: 500ms
  alert_p99: > 750ms
  
error_rate:
  target: < 0.1%
  alert: > 0.5%
  
throughput:
  target: 10k req/s
  alert: < 5k req/s (capacity issue)
```

## Alert Severity & Response Time

| Severity | Response Time | Escalation |
|----------|---------------|-----------|
| Critical | 5 minutes | Immediate page + VP notification |
| High | 15 minutes | Page on-call engineer |
| Medium | 1 hour | Ticket creation |
| Low | 4 hours | Daily review |

## Alert Examples

```yaml
critical:
  - api_down: http_requests == 0 for 1m
  - database_down: postgres_up == 0 for 30s
  - data_loss_detected: audit_entries decreasing for 5m

high:
  - error_rate: (errors / requests) > 0.005 for 5m
  - cpu_exhausted: cpu > 95 for 10m
  - replication_lag: lag > 5s for 5m
  - memory_exhausted: memory > 95 for 10m

medium:
  - slow_queries: query_time_p99 > 1s for 15m
  - disk_usage: usage > 85 for 30m
  - cache_miss_rate: miss_rate > 0.3 for 30m
```

## On-call Escalation

```
L1 (30 min): Service engineer
  ↓ (no response)
L2 (15 min): Team lead
  ↓ (no response)
L3 (10 min): Engineering manager
  ↓ (no response)
L4 (5 min): VP Engineering
```
