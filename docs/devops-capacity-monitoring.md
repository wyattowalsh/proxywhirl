# Capacity Monitoring & Alerting

## Key Metrics

```yaml
compute:
  - cpu_utilization: < 80%
  - memory_utilization: < 85%
  - disk_usage: < 90%
  - network_bandwidth: < 75%

database:
  - connections_in_use: < 80% of pool_size
  - query_latency_p99: < 500ms
  - replication_lag: < 1s
  - transaction_rate: monotonic increase

cache:
  - eviction_rate: < 1/sec
  - hit_ratio: > 80%
  - memory_utilization: < 85%
  - key_count: stable or growing
```

## Alert Rules

```yaml
alerts:
  - name: HighCPU
    expr: cpu_utilization > 80
    for: 5m
    action: page_oncall

  - name: DiskAlmostFull
    expr: disk_usage > 90
    for: 1m
    action: page_oncall + auto_cleanup

  - name: ReplicationLag
    expr: replication_lag > 5s
    for: 2m
    action: page_oncall

  - name: CacheEvictionRate
    expr: eviction_rate > 1
    for: 5m
    action: warn_team
```

## Capacity Planning

```bash
# Trend analysis
proxywhirl analytics trend \
  --metric cpu_utilization \
  --days 30 \
  --unit percent

# Forecast growth
proxywhirl analytics forecast \
  --metric requests_per_second \
  --days 90 \
  --model linear
```

## Auto-scaling Policies

```yaml
autoscaling:
  compute:
    scale_up: "avg_cpu > 75 for 5m"
    scale_down: "avg_cpu < 25 for 15m"
    cooldown: 5m
    max_instances: 50

  database_replica:
    scale_up: "replication_lag > 2s"
    scale_down: "replication_lag < 100ms for 30m"
