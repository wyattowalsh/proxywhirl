# Implementation Plan: Metrics Observability & Performance

**Branch**: `008-metrics-observability-performance` | **Date**: 2025-11-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-metrics-observability-performance/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a comprehensive metrics, observability, and performance monitoring system for ProxyWhirl proxy operations. The system will provide a real-time dashboard displaying success rates, error rates, latency, and throughput metrics aggregated by proxy pool and geographic region. Automated alerting will notify on-call engineers when performance thresholds are breached. Historical metrics export enables trend analysis and capacity planning. Technical approach uses Prometheus for metrics collection, Grafana for visualization, and AlertManager for threshold-based notifications, with <60s latency from data collection to display.

## Technical Context

**Language/Version**: Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13)

**Primary Dependencies**: 
- prometheus-client>=0.19.0 (metrics collection and exposition)
- fastapi>=0.100.0 (already in dependencies - for metrics HTTP endpoint)
- uvicorn[standard]>=0.24.0 (already in dependencies - for serving metrics)
- pydantic>=2.0.0 (already in dependencies - for alert rule configuration)
- pydantic-settings>=2.0.0 (already in dependencies - for metrics config)
- loguru>=0.7.0 (already in dependencies - for structured metric logging)

**Storage**: 
- Time-series metrics storage: Prometheus TSDB (external service, pull-based)
- Alert rules: Configuration files (YAML) + in-memory state
- Historical exports: CSV/JSON files
- Optional: SQLite for local metrics buffering during Prometheus downtime

**Testing**: 
- pytest (unit, integration, property tests with Hypothesis)
- pytest-asyncio for async metrics collection tests
- pytest-benchmark for metrics overhead validation
- respx for mocking Prometheus HTTP endpoints

**Target Platform**: Linux/macOS/Windows servers (Prometheus exporters are cross-platform)

**Project Type**: Single project (library extension with optional dashboard integration)

**Performance Goals**: 
- <60s metrics collection-to-display latency (SC-001)
- <2min alert notification latency (SC-002)
- Metrics collection overhead <5% of proxy request processing time
- Dashboard query response time <2s for 90-day historical data

**Constraints**:
- Must not block proxy request processing (async metrics collection)
- Metrics exposition endpoint must be thread-safe
- Alert rules must be hot-reloadable without service restart
- Dashboard must handle Prometheus unavailability gracefully (stale data indicators)
- No sensitive data (credentials, IPs) in exported metrics (per constitution security principles)
- Must integrate with existing loguru structured logging (007-logging-system-structured)

**Scale/Scope**:
- Support 10,000+ proxy requests/second with metrics collection
- Handle 50+ proxy pools with independent metrics
- Store 12+ months of historical metrics (Prometheus retention)
- Support 20+ concurrent dashboard users without degradation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. Library-First Architecture** | ✅ PASS | Extends existing ProxyWhirl library with metrics collection. All functionality usable via Python import. Prometheus client library provides programmatic API. Type hints with `py.typed` marker. |
| **II. Test-First Development** | ✅ PASS | TDD workflow enforced in tasks.md (to be created). Unit tests for metric collectors, exporters, alert rules. Integration tests for dashboard queries. Property tests for concurrent metrics collection. Target 85%+ coverage. |
| **III. Type Safety & Runtime Validation** | ✅ PASS | Pydantic models for MetricsConfig and AlertRuleConfig. Full type hints for all public APIs. mypy --strict compliance. Pydantic-settings for configuration validation. |
| **IV. Independent User Stories** | ✅ PASS | 3 user stories (US1-US3) each independently testable. US1 (dashboard) can be implemented without US2-US3. US2 (alerts) independent of US3 (exports). No hidden dependencies. |
| **V. Performance Standards** | ✅ PASS | Success criteria defined: <60s latency (SC-001), <2min alerts (SC-002), 30% reduction in downtime (SC-004). Async metrics collection prevents blocking. Benchmark tests required. |
| **VI. Security-First Design** | ✅ PASS | No credentials in metrics per constitution. Alert rules validated before execution. Metrics endpoint can be firewalled. Integration with existing structured logging (007). |
| **VII. Simplicity & Flat Architecture** | ✅ PASS | Adds ~3-4 modules: metrics_collector.py, metrics_exporter.py, alert_rules.py, dashboard_config.py. Total modules: ~22/20. **VIOLATION: Exceeds 20-module limit**. See Complexity Tracking. |

**uv run Enforcement**: All Python commands will use `uv run` prefix per constitution (e.g., `uv run pytest tests/`).

**Constitution Violation Detected**: Module count will exceed 20 (currently at 19, adding 3-4 = 22-23 total).

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
proxywhirl/                          # Flat package structure (existing)
├── metrics_collector.py             # NEW: Prometheus metrics collection
├── metrics_exporter.py              # NEW: HTTP /metrics endpoint
├── alert_manager.py                 # NEW: Alert rule evaluation & firing
├── dashboard_models.py              # NEW: Pydantic models for dashboard config
├── rotator.py                       # EXISTING: Will emit metrics on rotation
├── api.py                           # EXISTING: Will add /metrics endpoint
├── config.py                        # EXISTING: Will extend with metrics settings
├── logging_config.py                # EXISTING (007): Integrate metrics with logs
└── ...                              # Other existing modules

tests/
├── unit/
│   ├── test_metrics_collector.py    # NEW: Metric collection logic
│   ├── test_metrics_exporter.py     # NEW: Prometheus exposition format
│   ├── test_alert_manager.py        # NEW: Alert rule evaluation
│   └── test_dashboard_models.py     # NEW: Config validation
├── integration/
│   ├── test_metrics_e2e.py          # NEW: End-to-end metrics flow
│   ├── test_alert_notifications.py  # NEW: Alert delivery
│   └── test_dashboard_queries.py    # NEW: Historical data retrieval
├── property/
│   └── test_metrics_concurrency.py  # NEW: Concurrent metric writes
└── benchmarks/
    └── test_metrics_overhead.py     # NEW: SC-001, SC-002 validation

# External services (not in repo, deployment only)
prometheus/
├── prometheus.yml                   # Prometheus server configuration
└── alerts/
    └── proxywhirl_alerts.yml        # Alert rules (generated from config)

grafana/
├── dashboards/
│   └── proxywhirl_dashboard.json    # Dashboard JSON export
└── datasources/
    └── prometheus.yml               # Prometheus datasource config
```

**Structure Decision**: Single project (Option 1) - Flat module structure per Constitution VII. Adding 4 new modules (metrics_collector, metrics_exporter, alert_manager, dashboard_models) brings total to 23/20 modules, which **violates the 20-module limit**. This violation is justified in Complexity Tracking section due to the observability requirements being cross-cutting concerns that cannot be merged with existing modules without creating God objects.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Module count: 23/20 (exceeds limit by 3) | Observability is a cross-cutting concern requiring distinct separation: (1) metrics_collector.py handles async collection without blocking proxies, (2) metrics_exporter.py manages Prometheus HTTP exposition format, (3) alert_manager.py evaluates rules independently, (4) dashboard_models.py provides type-safe config. | Merging into existing modules would create God objects: (a) Adding to rotator.py couples rotation logic with observability (violates SRP), (b) Adding to api.py mixes REST API with metrics exposition (different protocols), (c) Adding to config.py creates a 500+ line configuration monster. Observability requires clean boundaries for testing and future extensions (e.g., Datadog, New Relic). |
