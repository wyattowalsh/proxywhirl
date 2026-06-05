# Deployment and Operations Guide

## Single Instance Deployment

### Local Installation

```bash
uv add proxywhirl
uv run uvicorn proxywhirl.api:app --host 0.0.0.0 --port 8000
```

### Docker Deployment

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

RUN uv tool install proxywhirl
ENV PATH="/root/.local/bin:${PATH}"

CMD ["uvicorn", "proxywhirl.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: "3.8"
services:
  proxywhirl:
    image: proxywhirl:latest
    ports:
      - "8000:8000"
    environment:
      - PROXYWHIRL_VALIDATION=strict
      - PROXYWHIRL_CACHE_TTL=3600
    volumes:
      - ./data:/app/data
```

## Kubernetes Deployment

### Helm Installation

```bash
helm repo add proxywhirl https://charts.proxywhirl.dev
helm install proxywhirl proxywhirl/proxywhirl
```

### StatefulSet

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: proxywhirl
spec:
  serviceName: proxywhirl
  replicas: 3
  selector:
    matchLabels:
      app: proxywhirl
  template:
    metadata:
      labels:
        app: proxywhirl
    spec:
      containers:
        - name: proxywhirl
          image: proxywhirl:latest
          ports:
            - containerPort: 8000
          volumeMounts:
            - name: data
              mountPath: /data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 10Gi
```

## Configuration Management

### Environment Variables

```bash
export PROXYWHIRL_VALIDATION=strict
export PROXYWHIRL_CACHE_TTL=3600
export PROXYWHIRL_MAX_RETRIES=3
export PROXYWHIRL_LOG_LEVEL=INFO
export PROXYWHIRL_DB_PATH=/data/proxywhirl.db
```

### Configuration File

```yaml
# config.yaml
sources:
  - http://free-proxy-list.net
  - http://proxylist.geonode.com

cache:
  enabled: true
  ttl_seconds: 3600
  max_entries: 5000

validation:
  level: strict
  timeout: 30

strategy:
  name: weighted_round_robin
  weights:
    high_quality: 0.7
    standard: 0.3
```

## Monitoring Setup

### Prometheus Metrics

```yaml
# prometheus.yml
scrape_configs:
  - job_name: proxywhirl
    static_configs:
      - targets: ["localhost:8000"]
```

### Key Metrics

- `proxywhirl_proxy_count` - Total proxies
- `proxywhirl_proxy_healthy_count` - Healthy proxies
- `proxywhirl_cache_hit_rate` - Cache efficiency
- `proxywhirl_validation_latency` - Validation performance
- `proxywhirl_source_fetch_duration` - Source fetch time

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "ProxyWhirl",
    "panels": [
      {
        "title": "Proxy Health",
        "targets": [
          { "expr": "proxywhirl_proxy_healthy_count / proxywhirl_proxy_count" }
        ]
      }
    ]
  }
}
```

## Logging Configuration

### Structured Logging

```python
from proxywhirl import configure_logging

configure_logging(
    level='INFO',
    format='json',
    output='file',
    path='/var/log/proxywhirl/app.log'
)
```

### Log Aggregation with ELK

```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/proxywhirl/*.log
output.elasticsearch:
  hosts: ["localhost:9200"]
```

## Backup and Recovery

### Database Backup

```bash
# Automatic SQLite backup
uv run python -c "import sqlite3; src = sqlite3.connect('proxywhirl.db'); dst = sqlite3.connect('backup.db'); src.backup(dst); dst.close(); src.close()"

# Schedule with cron
0 2 * * * sqlite3 proxywhirl.db ".backup /backups/proxywhirl-$(date +\%Y\%m\%d).db"
```

### Recovery

```bash
cp backup.db proxywhirl.db
```

## Health Checks

### API Health Endpoint

```bash
curl http://localhost:8000/api/health
```

Response:

```json
{
  "status": "healthy",
  "proxy_count": 1250,
  "healthy_count": 1100,
  "cache_hit_rate": 0.85,
  "uptime_seconds": 3600
}
```

### Kubernetes Health Probe

```yaml
livenessProbe:
  httpGet:
    path: /api/health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /api/health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

## Scaling

### Horizontal Scaling

```bash
# Multiple instances with shared database
Instance 1: uv run uvicorn proxywhirl.api:app --port 8000
Instance 2: uv run uvicorn proxywhirl.api:app --port 8001
Instance 3: uv run uvicorn proxywhirl.api:app --port 8002

# Load balancer
nginx upstream proxywhirl {
  server localhost:8000;
  server localhost:8001;
  server localhost:8002;
}
```

### Vertical Scaling

Increase resources:

- Cache size
- Max retries
- Validation timeout

## Performance Tuning

### Connection Pool

```python
config = ProxyConfiguration(
    connection_pool_size=100,
    connection_timeout=10
)
```

### Cache Configuration

```python
config = ProxyConfiguration(
    cache_config=CacheConfig(
        ttl_seconds=7200,
        max_entries=10000,
        compression_level=5
    )
)
```

## Troubleshooting

### High Memory Usage

```bash
# Check cache size
proxywhirl cache stats

# Clear cache
proxywhirl cache clear

# Reduce cache size
proxywhirl config set --cache-max 1000
```

### Slow Response Times

```bash
# Profile performance
proxywhirl profile --duration 60

# Check proxy health
proxywhirl health stats
```

### Failing Health Checks

```bash
# Refresh sources
proxywhirl source refresh --all

# Increase validation timeout
proxywhirl config set --validation-timeout 60
```
