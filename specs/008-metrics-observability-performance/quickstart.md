# Quick Start: Metrics Observability & Performance

**Feature**: 008-metrics-observability-performance  
**Estimated Time**: 15-20 minutes  
**Prerequisites**: Docker installed (for Prometheus/Grafana)

---

## Overview

This guide will help you set up comprehensive metrics, observability, and performance monitoring for ProxyWhirl in under 20 minutes. You'll get:

- ✅ Real-time dashboard with success rates, latency, and pool health
- ✅ Automated alerts for performance degradations
- ✅ Historical metrics export for trend analysis

---

## Step 1: Enable Metrics in ProxyWhirl (2 minutes)

### 1.1 Install ProxyWhirl with Metrics Support

```bash
pip install "proxywhirl[metrics]>=0.4.0"
```

### 1.2 Configure Metrics

Create a `.proxywhirl.toml` configuration file:

```toml
[tool.proxywhirl.metrics]
enabled = true
exposition_host = "0.0.0.0"
exposition_port = 9090
exposition_path = "/metrics"
scrape_interval_seconds = 60
histogram_buckets = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]

# Optional: Secure /metrics endpoint with basic auth
# basic_auth_username = "prometheus"
# basic_auth_password = "secure_password"
```

### 1.3 Start Metrics Endpoint

```python
from proxywhirl import ProxyRotator
from proxywhirl.metrics import start_metrics_server

# Start metrics server in background
start_metrics_server()  # Listens on 0.0.0.0:9090/metrics

# Use ProxyWhirl normally - metrics are collected automatically
rotator = ProxyRotator(proxies=["http://proxy1.com:8080"])
response = rotator.get("https://httpbin.org/ip")
```

**Verify metrics endpoint:**

```bash
curl http://localhost:9090/metrics
# Should see Prometheus metrics output
```

---

## Step 2: Deploy Prometheus (5 minutes)

### 2.1 Create Prometheus Configuration

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 60s
  evaluation_interval: 60s

scrape_configs:
  - job_name: 'proxywhirl'
    static_configs:
      - targets: ['host.docker.internal:9090']  # Mac/Windows
        # - targets: ['172.17.0.1:9090']         # Linux
        labels:
          environment: 'production'
```

**Note**: `host.docker.internal` allows Docker containers to access host services.

### 2.2 Start Prometheus Container

```bash
docker run -d \
  --name prometheus \
  -p 9091:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml:ro \
  prom/prometheus:latest \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.retention.time=365d
```

**Verify Prometheus:**

- Open <http://localhost:9091>
- Go to Status > Targets
- Verify `proxywhirl` target is "UP"

---

## Step 3: Deploy Grafana (3 minutes)

### 3.1 Start Grafana Container

```bash
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -e "GF_SECURITY_ADMIN_PASSWORD=admin" \
  grafana/grafana:latest
```

### 3.2 Configure Prometheus Datasource

1. Open <http://localhost:3000> (username: `admin`, password: `admin`)
2. Go to **Configuration** > **Data Sources** > **Add data source**
3. Select **Prometheus**
4. Set URL: `http://host.docker.internal:9091` (Mac/Windows) or `http://172.17.0.1:9091` (Linux)
5. Click **Save & Test** (should see "Data source is working")

### 3.3 Import ProxyWhirl Dashboard

1. Go to **Dashboards** > **Import**
2. Upload `contracts/grafana-dashboard.json` from this spec directory
3. Select **Prometheus** datasource
4. Click **Import**

**You should now see the ProxyWhirl Performance Dashboard!**

---

## Step 4: Configure Alerts (5 minutes)

### 4.1 Create Alert Rules File

Create `proxywhirl-alerts.yml` (copy from `contracts/alertmanager-rules.yml`):

```yaml
groups:
  - name: proxywhirl_performance
    interval: 60s
    rules:
      - alert: ProxyPoolHighErrorRate
        expr: |
          (rate(proxywhirl_requests_total{status="error"}[5m]) 
           / rate(proxywhirl_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate in proxy pool {{ $labels.pool }}"
```

### 4.2 Update Prometheus Configuration

Edit `prometheus.yml` to include alert rules:

```yaml
rule_files:
  - 'proxywhirl-alerts.yml'

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']  # AlertManager (optional)
```

### 4.3 Reload Prometheus

```bash
docker restart prometheus
```

---

## Step 5: Test End-to-End (3 minutes)

### 5.1 Generate Traffic

Run this script to generate proxy requests:

```python
from proxywhirl import ProxyRotator
import time

rotator = ProxyRotator(proxies=[
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080"
])

for i in range(100):
    try:
        response = rotator.get("https://httpbin.org/delay/1")
        print(f"Request {i}: {response.status_code}")
    except Exception as e:
        print(f"Request {i}: ERROR - {e}")
    time.sleep(0.5)  # 2 req/s
```

### 5.2 View Metrics in Grafana

1. Open <http://localhost:3000/d/proxywhirl-performance>
2. Select time range: **Last 15 minutes**
3. You should see:
   - Request success rate updating
   - Latency graphs (P95, P99)
   - Proxy pool size
   - Health check results

### 5.3 Trigger an Alert (Optional)

Simulate high error rate:

```python
# Temporarily add a bad proxy to trigger errors
rotator.add_proxy("http://invalid-proxy:8080")

# Generate requests - should trigger high error rate alert after 5 minutes
for i in range(50):
    try:
        rotator.get("https://httpbin.org/ip")
    except:
        pass
```

Wait 5 minutes, then check Prometheus:

- Open <http://localhost:9091/alerts>
- Verify `ProxyPoolHighErrorRate` alert is "FIRING"

---

## Step 6: Export Historical Metrics (2 minutes)

### 6.1 Export via Python API

```python
from proxywhirl.metrics import export_historical_metrics
from datetime import datetime, timedelta, timezone

# Export last 7 days to CSV
export_historical_metrics(
    metric_names=["proxywhirl_requests_total", "proxywhirl_request_duration_seconds"],
    start_time=datetime.now(timezone.utc) - timedelta(days=7),
    end_time=datetime.now(timezone.utc),
    format="csv",
    output_path="proxywhirl_metrics_7days.csv"
)
```

### 6.2 Export via Prometheus API (Alternative)

```bash
# Query Prometheus HTTP API
curl 'http://localhost:9091/api/v1/query_range?query=proxywhirl_requests_total&start=2025-10-25T00:00:00Z&end=2025-11-01T00:00:00Z&step=3600' \
  | jq '.data.result[] | {pool: .metric.pool, values: .values}' > export.json
```

---

## Troubleshooting

### Metrics Endpoint Not Reachable

**Problem**: Prometheus shows `proxywhirl` target as "DOWN"

**Solution**:

1. Verify ProxyWhirl metrics server is running:

   ```bash
   curl http://localhost:9090/metrics
   ```

2. Check Docker networking:

   ```bash
   # Mac/Windows: Use host.docker.internal
   # Linux: Use 172.17.0.1 (Docker bridge IP)
   docker inspect prometheus | grep IPAddress
   ```

3. If using firewall, allow port 9090:

   ```bash
   # Linux
   sudo ufw allow 9090/tcp
   ```

### Dashboard Shows No Data

**Problem**: Grafana dashboard panels are empty

**Solution**:

1. Verify Prometheus datasource is configured correctly:
   - Go to **Configuration** > **Data Sources** > **Prometheus**
   - Test connection (should be green)

2. Check Prometheus is scraping metrics:
   - Open <http://localhost:9091/targets>
   - Verify `proxywhirl` target is "UP" with recent scrape time

3. Verify metrics exist in Prometheus:
   - Go to <http://localhost:9091/graph>
   - Run query: `proxywhirl_requests_total`
   - Should see data points

4. Adjust time range in Grafana:
   - Dashboard might be looking at wrong time window
   - Try "Last 5 minutes" instead of "Last 6 hours"

### Alerts Not Firing

**Problem**: Alert rules don't trigger even when conditions are met

**Solution**:

1. Verify alert rules are loaded:

   ```bash
   # Check Prometheus logs
   docker logs prometheus | grep proxywhirl-alerts.yml
   ```

2. Check alert rule syntax:
   - Go to <http://localhost:9091/rules>
   - Verify `proxywhirl_performance` group is listed
   - Check for syntax errors (red X icons)

3. Verify alert conditions are actually met:
   - Go to <http://localhost:9091/graph>
   - Run the alert expression manually
   - Check if result > threshold

4. Check `for` duration:
   - Alerts only fire after condition is true for specified duration
   - Example: `for: 5m` means condition must be true for 5 minutes

---

## Next Steps

### Production Deployment

For production environments:

1. **Secure /metrics endpoint**:

   ```toml
   [tool.proxywhirl.metrics]
   basic_auth_username = "prometheus"
   basic_auth_password = "secure_password"
   ```

2. **Use persistent storage**:

   ```bash
   docker run -d \
     --name prometheus \
     -v prometheus-data:/prometheus \
     prom/prometheus:latest
   ```

3. **Deploy AlertManager** for notification routing:

   ```bash
   docker run -d \
     --name alertmanager \
     -p 9093:9093 \
     prom/alertmanager:latest
   ```

### Advanced Configuration

- **Custom dashboards**: Edit `contracts/grafana-dashboard.json`
- **Additional alerts**: Add rules to `proxywhirl-alerts.yml`
- **Recording rules**: Pre-aggregate expensive queries (see `contracts/alertmanager-rules.yml`)
- **Multi-instance**: Scrape multiple ProxyWhirl instances with Prometheus service discovery

### Integration with Existing Monitoring

If you already have Prometheus/Grafana:

1. Add ProxyWhirl scrape config to existing `prometheus.yml`
2. Import `contracts/grafana-dashboard.json` into existing Grafana
3. Merge `contracts/alertmanager-rules.yml` into existing alert rules

---

## Kubernetes Deployment

For Kubernetes environments, use Prometheus Operator:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: proxywhirl
  labels:
    app: proxywhirl
spec:
  selector:
    matchLabels:
      app: proxywhirl
  endpoints:
    - port: metrics
      interval: 60s
      path: /metrics
```

See `contracts/prometheus-scrape-config.yml` for full Kubernetes example.

---

## Summary

You now have:

- ✅ **Real-time dashboard**: <http://localhost:3000/d/proxywhirl-performance>
- ✅ **Prometheus metrics**: <http://localhost:9091>
- ✅ **Alert rules**: Configured for error rate, latency, pool health
- ✅ **Historical exports**: Python API and Prometheus query API

**Total Time**: ~15-20 minutes

**Next**: Customize dashboards and alerts for your specific use case!
