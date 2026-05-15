# Pre-built Monitoring Integration Configs

## Prometheus Integration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'proxywhirl'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/metrics'
    scrape_interval: 15s

  - job_name: 'proxywhirl-database'
    static_configs:
      - targets: ['localhost:5432']
    scrape_interval: 30s
```

## Grafana Dashboards

Pre-built dashboards available:
- Proxy Performance Overview
- Health Check Status
- Error Rate and Latency
- Resource Utilization
- Database Performance
- Cache Hit Rates

```bash
# Import dashboards
proxywhirl monitoring import-dashboard --name "proxy-performance"
```

## Alerting Rules

```yaml
groups:
  - name: proxywhirl
    rules:
      - alert: HighErrorRate
        expr: rate(proxy_errors[5m]) > 0.01
        for: 5m
        annotations:
          summary: "High error rate detected"

      - alert: HighLatency
        expr: proxy_latency_p99 > 500
        for: 5m
        annotations:
          summary: "High latency detected"
```

## Datadog Integration

```bash
proxywhirl monitoring datadog \
  --api-key ${DATADOG_API_KEY} \
  --app-key ${DATADOG_APP_KEY}
```

## Elastic Stack Integration

```bash
proxywhirl monitoring elastic \
  --host localhost:9200 \
  --index proxywhirl-logs
```

See detailed docs for complete monitoring setup.
