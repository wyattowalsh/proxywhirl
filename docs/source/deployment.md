# Deployment Guide

Production-ready deployment for ProxyWhirl.

## Local Development

### Setup
```bash
git clone https://github.com/wyattowalsh/proxywhirl.git
cd proxywhirl
uv sync
pre-commit install
```

### Run Tests
```bash
task test
```

### Run Locally
```bash
# REST API
uv run python -m proxywhirl.api

# CLI
uv run proxywhirl --help
```

## Docker Deployment

### Build Image
```bash
docker build -t proxywhirl:latest .
```

### Run Container
```bash
docker run -d \
  -p 8000:8000 \
  -e PROXYWHIRL_STORAGE_PATH=/data/proxies.db \
  -v proxywhirl-data:/data \
  --name proxywhirl-api \
  proxywhirl:latest
```

### Docker Compose
```bash
docker compose up -d
```

**Access:** http://localhost:8000/api/health

### Environment Variables
```bash
# Core
PROXYWHIRL_STRATEGY=round-robin
PROXYWHIRL_TIMEOUT=30
PROXYWHIRL_MAX_RETRIES=3

# Storage
PROXYWHIRL_STORAGE_PATH=/data/proxies.db

# API
PROXYWHIRL_REQUIRE_AUTH=false
PROXYWHIRL_API_KEY=your-secret-key

# CORS
PROXYWHIRL_CORS_ORIGINS=*
```

## Kubernetes Deployment

### Helm Chart Structure
```
proxywhirl-helm/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── pvc.yaml
│   ├── hpa.yaml
│   └── ingress.yaml
```

### Install
```bash
helm repo add proxywhirl https://charts.example.com
helm install proxywhirl proxywhirl/proxywhirl -f values.yaml
```

### values.yaml
```yaml
replicaCount: 3

image:
  repository: ghcr.io/wyattowalsh/proxywhirl
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: LoadBalancer
  port: 8000

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: proxies.example.com
      paths:
        - path: /
          pathType: Prefix

resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 2Gi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

persistence:
  enabled: true
  size: 10Gi
  storageClassName: fast-ssd
```

## Cloud Deployment

### AWS ECS

**Dockerfile Push:**
```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

docker tag proxywhirl:latest \
  123456789.dkr.ecr.us-east-1.amazonaws.com/proxywhirl:latest

docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/proxywhirl:latest
```

**CloudFormation Template:**
```yaml
Resources:
  ProxyWhirlTask:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: proxywhirl
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      Cpu: '1024'
      Memory: '2048'
      ContainerDefinitions:
        - Name: proxywhirl-api
          Image: !Sub '${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/proxywhirl:latest'
          PortMappings:
            - ContainerPort: 8000
          Environment:
            - Name: PROXYWHIRL_STORAGE_PATH
              Value: /data/proxies.db
          MountPoints:
            - SourceVolume: proxywhirl-data
              ContainerPath: /data
```

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/proxywhirl

# Deploy
gcloud run deploy proxywhirl \
  --image gcr.io/PROJECT_ID/proxywhirl:latest \
  --memory 2Gi \
  --cpu 1 \
  --region us-central1 \
  --allow-unauthenticated
```

### Heroku

```bash
heroku create proxywhirl-api
heroku container:push web -a proxywhirl-api
heroku container:release web -a proxywhirl-api
```

## Monitoring & Observability

### Prometheus Metrics

**Endpoint:** `/api/metrics`

**Key Metrics:**
- `proxywhirl_pool_size` - Total proxies in pool
- `proxywhirl_healthy_count` - Healthy proxies
- `proxywhirl_request_duration` - Request latency
- `proxywhirl_cache_hits` - Cache hit rate
- `proxywhirl_validation_failures` - Validation errors

### Grafana Dashboard

**Import ID:** 12345

**Key Panels:**
- Pool Health Timeline
- Response Time Distribution
- Country Distribution
- Cache Hit Rate
- Error Rate

### Application Insights

**Setup:**
```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.set_tracer_provider(...)
```

## Logging

### Structured Logging

**Configuration:**
```python
from proxywhirl import configure_logging

configure_logging(
    level="INFO",
    format="json",
    output="stdout"
)
```

**Log Levels:**
- `DEBUG` - Detailed debugging info
- `INFO` - General information
- `WARNING` - Warning messages
- `ERROR` - Error conditions
- `CRITICAL` - Critical failures

### Log Aggregation

**ELK Stack:**
```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/proxywhirl/*.log

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

**CloudWatch:**
```python
import logging
import watchtower

handler = watchtower.CloudWatchLogHandler(
    log_group="/aws/ecs/proxywhirl",
    stream_name="api"
)
logging.getLogger().addHandler(handler)
```

## Security

### API Authentication

**Enable authentication:**
```bash
export PROXYWHIRL_REQUIRE_AUTH=true
export PROXYWHIRL_API_KEY=$(openssl rand -base64 32)
```

**Client usage:**
```python
import httpx

headers = {"Authorization": f"Bearer {API_KEY}"}
response = httpx.get(
    "http://localhost:8000/api/health",
    headers=headers
)
```

### HTTPS/TLS

**Nginx reverse proxy:**
```nginx
upstream proxywhirl {
    server localhost:8000;
}

server {
    listen 443 ssl http2;
    server_name proxies.example.com;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    location / {
        proxy_pass http://proxywhirl;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Rate Limiting

**Environment:**
```bash
export PROXYWHIRL_RATE_LIMIT_ENABLED=true
export PROXYWHIRL_RATE_LIMIT_REQUESTS=100
export PROXYWHIRL_RATE_LIMIT_PERIOD=60
```

## Backup & Recovery

### Database Backup

**Automated backup script:**
```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
sqlite3 /data/proxies.db ".backup /backups/proxies_$TIMESTAMP.db"

# Upload to S3
aws s3 cp /backups/proxies_$TIMESTAMP.db s3://backups/proxywhirl/
```

**Restore:**
```bash
sqlite3 /data/proxies.db ".restore /backups/proxies_TIMESTAMP.db"
```

### High Availability

**Setup replication:**
```bash
# Primary
docker run -d --name proxywhirl-primary \
  -e PROXYWHIRL_STORAGE_PATH=/data/proxies.db \
  -v primary-data:/data \
  proxywhirl:latest

# Replica
docker run -d --name proxywhirl-replica \
  -e PROXYWHIRL_STORAGE_PATH=/data/proxies.db \
  -e PROXYWHIRL_REPLICA_OF=primary \
  -v replica-data:/data \
  proxywhirl:latest
```

## Performance Tuning

### Resource Allocation

**Recommended:**
```
CPU: 1-2 cores (depends on concurrency)
Memory: 512MB - 2GB (proxy pool size dependent)
Storage: 100MB - 10GB (proxy database)
```

### Optimization Tips

1. **Enable caching:**
   ```bash
   export PROXYWHIRL_CACHE_ENABLED=true
   export PROXYWHIRL_CACHE_TTL=3600
   ```

2. **Tune pool size:**
   ```bash
   export PROXYWHIRL_MAX_POOL_SIZE=10000
   ```

3. **Batch operations:**
   ```python
   proxies = rotator.get_proxies(limit=1000)
   ```

4. **Connection pooling:**
   ```python
   import httpx
   async with httpx.AsyncClient(limits=httpx.Limits(max_connections=100)) as client:
       # Make requests
   ```

## Troubleshooting

### Container won't start
```bash
docker logs proxywhirl-api
# Check for configuration errors, missing volumes
```

### High memory usage
```bash
# Reduce pool size or enable cache eviction
export PROXYWHIRL_MAX_POOL_SIZE=5000
export PROXYWHIRL_CACHE_MAX_SIZE=1000
```

### Database locked errors
```bash
# Restart container or check concurrent access
docker restart proxywhirl-api
```

### Slow proxy responses
```bash
# Increase timeout
export PROXYWHIRL_TIMEOUT=60

# Reduce validation frequency
export PROXYWHIRL_VALIDATION_INTERVAL=3600
```

See [Troubleshooting Guide](guides/troubleshooting.md) for more.
