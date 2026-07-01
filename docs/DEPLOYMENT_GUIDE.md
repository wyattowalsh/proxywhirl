# ProxyWhirl Deployment Guide

This guide covers all deployment options for ProxyWhirl, from local development to production Kubernetes clusters.

## Quick Start: Docker Compose (Local Development)

```bash
# Start the complete stack (API, Redis, PostgreSQL, Prometheus, Grafana)
docker-compose -f deploy/docker-compose.yml up -d

# Access services
API:       http://localhost:8000
Prometheus: http://localhost:9091
Grafana:    http://localhost:3000 (admin/admin)
```

## Kubernetes Deployment

### Option 1: Raw Kubernetes Manifests

```bash
# Apply all manifests
kubectl apply -f deploy/kubernetes/

# Verify deployment
kubectl get pods -n proxywhirl
kubectl logs -n proxywhirl -l app=proxywhirl
```

### Option 2: Helm Chart (Recommended)

```bash
# Add Helm repository (if published)
helm repo add proxywhirl https://charts.proxywhirl.io
helm repo update

# Or install from local chart
helm install proxywhirl deploy/helm/ -n proxywhirl --create-namespace

# Customize values
helm install proxywhirl deploy/helm/ \
  --values deploy/helm/values.yaml \
  --set image.tag=v1.0.0 \
  --set replicaCount=5 \
  --set persistence.size=50Gi
```

### Option 3: Manual Helm Deployment with Custom Values

Create `custom-values.yaml`:
```yaml
replicaCount: 5
image:
  tag: v1.0.0
persistence:
  size: 50Gi
  storageClassName: fast-ssd
secrets:
  encryptionKey: your-encryption-key
  apiKey: your-api-key
```

Then deploy:
```bash
helm install proxywhirl deploy/helm/ -f custom-values.yaml
```

## AWS Deployment (Terraform)

### Prerequisites
```bash
# Install Terraform
brew install terraform  # macOS
# or download from https://www.terraform.io/downloads

# Configure AWS credentials
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=yyy
```

### Deploy

```bash
cd deploy/terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var-file=prod.tfvars

# Apply configuration
terraform apply -var-file=prod.tfvars

# Get outputs
terraform output alb_dns_name
terraform output rds_endpoint
```

## Linux Server Deployment (systemd)

### Installation

```bash
# Install ProxyWhirl
pip install proxywhirl

# Copy systemd files
sudo cp deploy/systemd/*.service /etc/systemd/system/
sudo cp deploy/systemd/*.socket /etc/systemd/system/

# Create user and directories
sudo useradd -r -s /bin/false proxywhirl
sudo mkdir -p /opt/proxywhirl /var/lib/proxywhirl /var/log/proxywhirl
sudo chown proxywhirl:proxywhirl /var/lib/proxywhirl /var/log/proxywhirl

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable proxywhirl proxywhirl-worker
sudo systemctl start proxywhirl proxywhirl-worker

# Check status
sudo systemctl status proxywhirl
```

### Environment Configuration

Create `/etc/default/proxywhirl`:
```bash
PROXYWHIRL_LOG_LEVEL=INFO
PROXYWHIRL_STORAGE_PATH=/var/lib/proxywhirl/proxywhirl.db
PROXYWHIRL_ENCRYPTION_KEY=your-key
PROXYWHIRL_API_KEY=your-api-key
```

## Monitoring & Observability

### Access Grafana Dashboard

1. **Local (Docker Compose)**:
   - URL: http://localhost:3000
   - Credentials: admin / admin

2. **Kubernetes**:
   ```bash
   kubectl port-forward -n proxywhirl svc/grafana 3000:3000
   # Then access http://localhost:3000
   ```

### View Prometheus Metrics

```bash
# Local
curl http://localhost:9091/api/v1/query?query=proxywhirl_available_proxies

# Kubernetes
kubectl port-forward -n proxywhirl svc/prometheus 9090:9090
curl http://localhost:9090/api/v1/query?query=proxywhirl_available_proxies
```

## Backup & Restore

### Automated Backups

```bash
# Create backup
./deploy/scripts/backup-restore.sh backup

# List backups
./deploy/scripts/backup-restore.sh list

# Restore from backup
./deploy/scripts/backup-restore.sh restore /path/to/backup.db.gz

# Upload to S3
export S3_BUCKET=my-backups
./deploy/scripts/backup-restore.sh backup
```

## Zero-Downtime Deployments

### Blue-Green Deployment

```bash
# Deploy new version while keeping current version running
./deploy/scripts/blue-green-deploy.sh

# Automatic health checks and traffic switching
# Rollback if needed: ./deploy/scripts/blue-green-deploy.sh rollback
```

## Health Checks

```bash
# Manual health check
./deploy/scripts/health-check.sh

# Set custom API URL
PROXYWHIRL_API_URL=https://api.example.com ./deploy/scripts/health-check.sh
```

## CI/CD Pipeline

The project includes comprehensive CI/CD workflows:

### On Every Commit
- ✅ Code linting (Ruff)
- ✅ Type checking (mypy)
- ✅ Unit tests
- ✅ Code coverage (80% minimum)

### On Push to Main
- ✅ Integration tests (Python 3.9-3.12)
- ✅ E2E tests with API
- ✅ Performance benchmarks
- ✅ Security scanning (CodeQL, SAST, dependencies)
- ✅ Multi-platform Docker builds (amd64, arm64)

### On Tag Release
- ✅ Changelog generation
- ✅ PyPI package publishing
- ✅ GitHub release creation with artifacts

## Configuration

### Environment Variables

```bash
PROXYWHIRL_LOG_LEVEL=INFO              # Logging level
PROXYWHIRL_STORAGE_PATH=/data/db.db    # Database path
PROXYWHIRL_ENCRYPTION_KEY=key          # Encryption key
PROXYWHIRL_API_KEY=key                 # API authentication
PROXYWHIRL_CACHE_ENCRYPTION_KEY=key    # Cache encryption
REDIS_URL=redis://localhost:6379       # Redis connection
DATABASE_URL=postgres://...            # PostgreSQL connection
```

### Kubernetes ConfigMap

Edit `deploy/kubernetes/config-map.yaml` to customize:
- API host/port
- Storage backend (SQLite/PostgreSQL)
- Cache configuration
- Logging level
- Rotation strategy

## Troubleshooting

### API Won't Start

```bash
# Check logs
docker logs proxywhirl-api        # Docker Compose
kubectl logs -n proxywhirl <pod>  # Kubernetes
journalctl -u proxywhirl -n 100   # systemd

# Verify health
./deploy/scripts/health-check.sh
```

### Database Connection Issues

```bash
# Test database
sqlite3 /data/proxywhirl.db ".tables"
psql $DATABASE_URL

# Restore from backup
./deploy/scripts/backup-restore.sh restore /backups/proxywhirl_*.db.gz
```

### Performance Issues

Check Grafana dashboards:
- Error rate (should be <5%)
- Request latency (p95 <10s)
- Available proxies (>100)
- Cache hit rate (>80%)

## Scaling

### Horizontal Scaling (Kubernetes/ECS)

```bash
# Kubernetes
kubectl scale deployment proxywhirl -n proxywhirl --replicas=10

# Helm
helm upgrade proxywhirl deploy/helm/ --set replicaCount=10
```

### Vertical Scaling

Update resource requests/limits:
```yaml
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 2Gi
```

## Security

### Network Policies

Already configured in Kubernetes manifests:
- Only allow ingress from Ingress controller
- Only allow egress to Redis, databases, external services
- Default-deny all other traffic

### Pod Security

- Non-root user (uid 1000)
- Read-only root filesystem
- No privilege escalation
- Dropped all capabilities (CAP_ALL)

### Secret Management

- Encryption keys stored in Kubernetes Secrets
- Never hardcoded in images or manifests
- Rotate regularly

## Support

For issues and questions:
- GitHub Issues: https://github.com/wyattowalsh/proxywhirl/issues
- Documentation: https://proxywhirl.readthedocs.io
- Email: support@proxywhirl.dev

---

**Last Updated**: 2024
**Supported Platforms**: Kubernetes, Docker, Linux (systemd), AWS (Terraform)
**Python Versions**: 3.9, 3.10, 3.11, 3.12
