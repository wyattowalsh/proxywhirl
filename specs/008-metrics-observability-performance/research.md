# Research: Metrics Observability & Performance

**Feature**: 008-metrics-observability-performance  
**Date**: 2025-11-01  
**Phase**: Phase 0 - Research & Technical Decisions

## Overview

This document captures all technical research, decisions, rationale, and alternatives considered for implementing comprehensive metrics, observability, and performance monitoring in ProxyWhirl.

## Research Tasks

### 1. Metrics Collection Library Selection

**Decision**: Use `prometheus-client>=0.19.0`

**Rationale**:
- Industry-standard metrics format with wide ecosystem support
- Native Python client library with minimal overhead (<1ms per metric update)
- Built-in support for Counter, Gauge, Histogram, Summary metric types
- Thread-safe implementation suitable for concurrent proxy operations
- Zero external service dependencies for collection (library-only)
- Pull-based model aligns with Kubernetes/cloud-native deployments
- Supports custom labels for proxy pool, region, status code dimensions

**Alternatives Considered**:
1. **StatsD + Graphite**
   - Rejected: Push-based model requires UDP network calls (higher overhead)
   - Rejected: Less mature Python client, weaker type safety
   - Rejected: Graphite storage less flexible than Prometheus TSDB

2. **OpenTelemetry (OTEL)**
   - Rejected: Heavier dependency footprint (10+ packages)
   - Rejected: More complex configuration for simple use case
   - Rejected: Overkill for metrics-only (includes tracing, logging)
   - Note: Could be future enhancement if distributed tracing needed

3. **Custom metrics with SQLite**
   - Rejected: No standard format, reinventing the wheel
   - Rejected: Difficult to integrate with existing dashboards (Grafana)
   - Rejected: Higher maintenance burden

**References**:
- Prometheus Python Client: https://github.com/prometheus/client_python
- Prometheus Best Practices: https://prometheus.io/docs/practices/instrumentation/

---

### 2. Dashboard Technology Selection

**Decision**: Use Grafana OSS (user-deployed) with pre-built dashboard JSON templates

**Rationale**:
- De-facto standard for Prometheus visualization
- Rich query language (PromQL) for complex aggregations
- Free and open-source (no licensing constraints)
- JSON-based dashboard templates can be version-controlled
- Supports alerts, annotations, variables for flexible filtering
- Large community with existing proxy monitoring templates as starting points
- ProxyWhirl provides dashboard templates, users deploy Grafana themselves

**Alternatives Considered**:
1. **Custom Web Dashboard (React/Vue + FastAPI)**
   - Rejected: Significant development effort (weeks vs. hours)
   - Rejected: Would add frontend dependencies to project scope
   - Rejected: Maintenance burden for UI updates, browser compatibility
   - Note: Could be future enhancement if custom features needed

2. **Prometheus Built-in UI**
   - Rejected: Limited visualization capabilities (basic line charts only)
   - Rejected: No templating, no persistent dashboards
   - Rejected: Not suitable for operations teams (too technical)

3. **Datadog/New Relic SaaS**
   - Rejected: Requires paid accounts, not free for users
   - Rejected: Vendor lock-in, privacy concerns with external data
   - Note: Should support as optional integration in future

**Implementation Approach**:
- ProxyWhirl exposes `/metrics` endpoint (Prometheus exposition format)
- Users deploy Prometheus to scrape ProxyWhirl `/metrics`
- Users deploy Grafana with Prometheus datasource
- ProxyWhirl repo provides pre-built dashboard JSON in `grafana/dashboards/`
- Documentation guides users through setup (5-minute quickstart)

**References**:
- Grafana Documentation: https://grafana.com/docs/
- Grafana Dashboard Examples: https://grafana.com/grafana/dashboards/

---

### 3. Alert Manager Integration

**Decision**: Use Prometheus AlertManager with YAML alert rules

**Rationale**:
- Native integration with Prometheus ecosystem
- Declarative YAML-based rule definitions (easy to version control)
- Built-in notification channels (email, Slack, PagerDuty, webhooks)
- Alert grouping, inhibition, and silencing features
- No code changes needed in ProxyWhirl for alert delivery
- ProxyWhirl only needs to export metrics; alerts defined externally

**Alternatives Considered**:
1. **Custom Alert Engine in ProxyWhirl**
   - Rejected: Would require notification infrastructure (SMTP, HTTP clients)
   - Rejected: Duplicates functionality available in AlertManager
   - Rejected: Would need to handle alert state, deduplication, escalation

2. **Grafana Alerts**
   - Considered: Simpler for users (single tool for dashboards + alerts)
   - Rejected: Less flexible than AlertManager for complex rules
   - Rejected: Requires Grafana to be always-on (availability concern)
   - Note: Can be used as alternative, both approaches supported

**Alert Rule Examples**:
```yaml
# High error rate alert
- alert: ProxyPoolHighErrorRate
  expr: rate(proxywhirl_requests_total{status="error"}[5m]) > 0.05
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High error rate in proxy pool {{ $labels.pool }}"
    description: "Error rate is {{ $value | humanizePercentage }}"
```

**References**:
- AlertManager: https://prometheus.io/docs/alerting/latest/alertmanager/
- Alert Rule Best Practices: https://prometheus.io/docs/practices/alerting/

---

### 4. Historical Metrics Export

**Decision**: Provide Python API for CSV/JSON export via Prometheus Query API

**Rationale**:
- Prometheus stores all historical data (12+ months retention)
- Query API allows retrieving time-range data programmatically
- ProxyWhirl provides helper functions to query and export
- CSV/JSON formats suitable for spreadsheets, data analysis
- No duplicate storage needed (Prometheus is source of truth)

**Implementation**:
```python
from proxywhirl.metrics import export_historical_metrics

# Export last 90 days to CSV
export_historical_metrics(
    metric_name="proxywhirl_request_duration_seconds",
    start_time="2025-08-01",
    end_time="2025-11-01",
    format="csv",
    output_path="metrics_90days.csv"
)
```

**Alternatives Considered**:
1. **Direct Database Export (Prometheus TSDB)**
   - Rejected: Prometheus TSDB is optimized for queries, not exports
   - Rejected: Would bypass Prometheus API, tighter coupling

2. **Real-time Streaming to S3/BigQuery**
   - Rejected: Over-engineered for Phase 1
   - Note: Future enhancement for data lakes

**References**:
- Prometheus HTTP API: https://prometheus.io/docs/prometheus/latest/querying/api/

---

### 5. Metric Naming Conventions

**Decision**: Follow Prometheus naming best practices

**Metric Naming Pattern**:
- Prefix: `proxywhirl_`
- Format: `<prefix><component>_<metric_type>_<unit>`
- Labels: `{pool="pool1", region="us-east-1", status="success|error"}`

**Core Metrics**:
1. **Request Counter**: `proxywhirl_requests_total{pool, region, status, method}`
   - Type: Counter
   - Description: Total number of proxy requests
   - Labels: pool (proxy pool name), region (geo region), status (success/error), method (GET/POST/etc)

2. **Request Duration**: `proxywhirl_request_duration_seconds{pool, region, quantile}`
   - Type: Histogram
   - Description: Request latency distribution
   - Buckets: [0.1, 0.5, 1.0, 2.0, 5.0, 10.0] seconds
   - Labels: pool, region, quantile (0.5, 0.9, 0.95, 0.99)

3. **Proxy Pool Size**: `proxywhirl_pool_proxies{pool, health_status}`
   - Type: Gauge
   - Description: Number of proxies in pool by health status
   - Labels: pool, health_status (healthy/unhealthy/unknown)

4. **Proxy Health**: `proxywhirl_proxy_health_checks_total{pool, proxy_id, result}`
   - Type: Counter
   - Description: Total health check attempts
   - Labels: pool, proxy_id, result (pass/fail/timeout)

5. **Alert State**: `proxywhirl_alerts_active{alert_name, severity}`
   - Type: Gauge
   - Description: Number of active alerts
   - Labels: alert_name, severity (warning/critical)

**Rationale**:
- Clear, self-documenting metric names
- Standardized labels enable aggregation and filtering
- Histogram provides percentile calculations (p50, p95, p99)
- Counters for monotonic values (requests), Gauges for point-in-time (pool size)

**References**:
- Prometheus Naming: https://prometheus.io/docs/practices/naming/
- Metric Types: https://prometheus.io/docs/concepts/metric_types/

---

### 6. Performance Overhead Mitigation

**Decision**: Async metrics collection with background thread

**Approach**:
1. Metrics updates are non-blocking (prometheus-client uses thread-safe counters)
2. Histogram observations are batched (10ms flush interval)
3. No disk I/O during request processing (Prometheus scrapes /metrics endpoint)
4. Labels are pre-allocated to avoid runtime string concatenation

**Benchmark Targets**:
- Metric update overhead: <100μs per request
- /metrics endpoint response time: <50ms
- Memory overhead: <10MB for 100k data points

**Rationale**:
- Prometheus client library is already optimized for performance
- Pull-based model means no network calls during request processing
- Trade-off: 60s scrape interval means potential 60s delay for new metrics

**References**:
- Prometheus Performance: https://prometheus.io/docs/practices/instrumentation/#performance

---

### 7. Metric Retention and Cardinality

**Decision**: 12-month retention with controlled label cardinality

**Cardinality Limits**:
- Max proxy pools: 50 (typical deployment has <10)
- Max regions: 20 (AWS/Azure/GCP regions)
- Max proxies per pool: 1000 (most pools have <100)
- Total unique metric series: ~100k (well within Prometheus limits)

**Retention Strategy**:
- Default: 12 months (configurable in Prometheus server)
- Downsampling: Not needed for Phase 1 (future: aggregate to hourly after 30 days)

**Rationale**:
- Prometheus handles millions of series efficiently
- ProxyWhirl label cardinality is naturally bounded (fixed proxy pools, regions)
- 12-month retention supports annual trend analysis

**Cardinality Anti-Patterns to Avoid**:
- ❌ DO NOT use `proxy_url` as label (high cardinality, 1000+ unique values)
- ❌ DO NOT use `request_id` as label (unbounded, one per request)
- ✅ DO use `pool` and `region` (low cardinality, <100 unique combinations)

**References**:
- Cardinality Best Practices: https://prometheus.io/docs/practices/naming/#labels

---

### 8. Dashboard Query Optimization

**Decision**: Pre-aggregate metrics using recording rules

**Recording Rules**:
Prometheus recording rules pre-compute expensive queries and store as new metrics:

```yaml
# Pre-aggregate success rate by pool (updated every 1m)
- record: proxywhirl:pool_success_rate:1m
  expr: |
    rate(proxywhirl_requests_total{status="success"}[1m]) 
    / 
    rate(proxywhirl_requests_total[1m])

# Pre-aggregate p95 latency by pool (updated every 1m)
- record: proxywhirl:pool_latency_p95:1m
  expr: |
    histogram_quantile(0.95, 
      rate(proxywhirl_request_duration_seconds_bucket[1m])
    )
```

**Rationale**:
- Dashboard queries use pre-aggregated metrics (fast)
- Raw metrics still available for ad-hoc investigation
- Reduces dashboard query complexity (simpler PromQL)

**References**:
- Recording Rules: https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/

---

### 9. Security Considerations

**Decision**: No sensitive data in metrics, firewall /metrics endpoint

**Security Measures**:
1. **No Credentials in Metrics**: Proxy usernames/passwords never exported
2. **No IP Addresses**: Use proxy pool names, not individual IPs (prevents enumeration)
3. **Firewall /metrics**: Endpoint only accessible from Prometheus server (not public)
4. **Optional Basic Auth**: /metrics endpoint can require HTTP basic auth
5. **TLS**: Support HTTPS for /metrics endpoint (mutual TLS for Prometheus)

**Rationale**:
- Aligns with ProxyWhirl constitution (security-first design)
- Metrics are operational data, not business logic
- Prometheus scraping can be secured with mutual TLS

**References**:
- Prometheus Security: https://prometheus.io/docs/operating/security/

---

### 10. Integration with Existing Logging (007)

**Decision**: Emit metrics alongside structured logs

**Approach**:
- When rotator.py logs a request (via loguru), also update Prometheus metrics
- Shared context: `correlation_id` appears in both logs and metric labels
- Log level >= WARNING triggers metric: `proxywhirl_log_events_total{level="warning"}`

**Example**:
```python
# In rotator.py
logger.info("Proxy request successful", 
    extra={"pool": pool_name, "latency_ms": 123})
metrics.requests_total.labels(pool=pool_name, status="success").inc()
metrics.request_duration.labels(pool=pool_name).observe(0.123)
```

**Rationale**:
- Unified observability: logs for debugging, metrics for monitoring
- Avoids duplication: single instrumentation point
- Correlation IDs link logs to metrics for root cause analysis

**References**:
- ProxyWhirl Logging Spec: `specs/007-logging-system-structured/`

---

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| **Metrics Library** | prometheus-client>=0.19.0 | Industry standard, minimal overhead, wide ecosystem |
| **Dashboard** | Grafana OSS (user-deployed) | De-facto standard, free, JSON templates |
| **Alerting** | Prometheus AlertManager | Native integration, declarative rules, notification channels |
| **Exports** | Python API for CSV/JSON via Prometheus Query API | No duplicate storage, flexible formats |
| **Naming** | Prometheus best practices (prefix, labels) | Clear, self-documenting, aggregation-friendly |
| **Performance** | Async collection, batched updates | <100μs overhead, non-blocking |
| **Retention** | 12 months, controlled cardinality | Annual trends, bounded memory |
| **Optimization** | Prometheus recording rules | Fast dashboard queries, pre-aggregated |
| **Security** | No credentials, firewall /metrics, TLS | Constitution compliance, defense-in-depth |
| **Logging** | Integrate with 007-logging-system | Unified observability, correlation IDs |

---

## Next Steps (Phase 1)

With research complete, proceed to Phase 1:
1. **data-model.md**: Define Pydantic models (MetricsConfig, AlertRule, DashboardConfig)
2. **contracts/**: OpenAPI spec for /metrics endpoint, Prometheus scrape config
3. **quickstart.md**: 5-minute setup guide (install, deploy Prometheus/Grafana)
