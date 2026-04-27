# Centralized Logging & Aggregation

## Log Sources

1. Application logs → structured JSON to stdout
2. System logs → journalctl/syslog
3. Access logs → nginx/HAProxy
4. Audit logs → database/API audit trail

## Stack Configuration

### ELK Stack

```yaml
elasticsearch:
  version: 8.0
  cluster.name: proxywhirl
  
kibana:
  elasticsearch.hosts: ["http://elasticsearch:9200"]
  
filebeat:
  inputs:
    - type: log
      paths: ["/var/log/proxywhirl/*.log"]
      processors:
        - add_kubernetes_metadata: ~
```

### Loki Stack (Kubernetes)

```yaml
loki:
  ingester:
    chunk_idle_period: 3m
    chunk_retain_period: 1m
    
promtail:
  clients:
    - url: http://loki:3100/loki/api/v1/push
```

## Query Examples

```bash
# Search errors
curl 'http://kibana:5601/_search?q=level:ERROR&size=100'

# Latency distribution
curl 'http://elasticsearch:9200/_search' -d '{
  "aggs": {
    "latency": {
      "percentiles": {"field": "duration_ms", "percents": [50, 95, 99]}
    }
  }
}'
```

## Retention Policies

- Hot data (7 days): Full resolution
- Warm data (30 days): 1-hour aggregation
- Cold data (1 year): Daily summaries
- Archive: S3 Glacier

## Cost Optimization

- Sampling: Log only 10% of successful requests
- Compression: gzip on S3
- Tiering: Move to cheaper storage after 30 days
