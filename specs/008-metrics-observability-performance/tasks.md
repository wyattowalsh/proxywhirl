# Tasks: Metrics Observability & Performance

**Input**: Design documents from `/specs/008-metrics-observability-performance/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Property tests and benchmarks are included to validate performance requirements (SC-001, SC-002, SC-003).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `proxywhirl/`, `tests/` at repository root
- All tasks use `uv run` prefix per constitution

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [ ] T001 Install prometheus-client>=0.19.0 dependency via `uv add prometheus-client>=0.19.0`
- [ ] T002 Install pytest-benchmark for performance testing via `uv add --dev pytest-benchmark`
- [ ] T003 [P] Create proxywhirl/metrics_models.py for Pydantic models stub
- [ ] T004 [P] Create tests/unit/test_metrics_collector.py stub
- [ ] T005 [P] Create tests/benchmarks/test_metrics_overhead.py stub

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core metrics infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Implement MetricsConfig Pydantic model in proxywhirl/metrics_models.py with all fields from data-model.md
- [ ] T007 Implement MetricType enum in proxywhirl/metrics_models.py (COUNTER, GAUGE, HISTOGRAM, SUMMARY)
- [ ] T008 [P] Implement ProxyMetric model in proxywhirl/metrics_models.py with prometheus_client wrapper
- [ ] T009 Create proxywhirl/metrics_collector.py with MetricsCollector class skeleton
- [ ] T010 Implement metrics registry in proxywhirl/metrics_collector.py for tracking all metrics
- [ ] T011 Implement thread-safe metric update methods in proxywhirl/metrics_collector.py
- [ ] T012 Add cardinality limit enforcement (label_cardinality_limit) in proxywhirl/metrics_collector.py
- [ ] T013 Integrate MetricsCollector with existing rotator.py to emit request metrics
- [ ] T014 Add metrics emission to rotator.py on proxy selection (pool, region labels)
- [ ] T015 Add metrics emission to rotator.py on request completion (success/error, latency)
- [ ] T016 [P] Unit test MetricsConfig validation in tests/unit/test_metrics_models.py
- [ ] T017 [P] Unit test ProxyMetric creation in tests/unit/test_metrics_models.py
- [ ] T018 Unit test MetricsCollector metric registration in tests/unit/test_metrics_collector.py
- [ ] T019 Unit test thread-safe metric updates in tests/unit/test_metrics_collector.py
- [ ] T020 Property test concurrent metric writes with Hypothesis in tests/property/test_metrics_concurrency.py

**Checkpoint**: Foundation ready - metrics collection works, user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Monitor Proxy Health Trends (Priority: P1) 🎯 MVP

**Goal**: Operations leads can view a consolidated dashboard showing proxy pool performance (success rate, error rate, latency) to identify failing proxies before customer impact.

**Independent Test**: Start ProxyWhirl with metrics enabled, generate traffic, verify /metrics endpoint returns Prometheus format data with proxywhirl_requests_total, proxywhirl_request_duration_seconds, proxywhirl_pool_proxies metrics.

### Benchmarks for User Story 1

> **NOTE: Write these benchmarks FIRST, ensure they meet performance targets**

- [ ] T021 [P] [US1] Benchmark metrics collection overhead <5% in tests/benchmarks/test_metrics_overhead.py
- [ ] T022 [P] [US1] Benchmark /metrics endpoint response time <50ms in tests/benchmarks/test_metrics_overhead.py

### Implementation for User Story 1

- [ ] T023 [P] [US1] Create proxywhirl/metrics_exporter.py with MetricsExporter class
- [ ] T024 [US1] Implement Prometheus exposition format endpoint in proxywhirl/metrics_exporter.py
- [ ] T025 [US1] Add HTTP basic auth support (optional) to /metrics endpoint in proxywhirl/metrics_exporter.py
- [ ] T026 [US1] Integrate MetricsExporter with FastAPI in proxywhirl/api.py at /metrics path
- [ ] T027 [US1] Implement start_metrics_server() helper function in proxywhirl/metrics_exporter.py
- [ ] T028 [P] [US1] Define core metrics in proxywhirl/metrics_collector.py:
  - proxywhirl_requests_total (Counter with pool, region, status labels)
  - proxywhirl_request_duration_seconds (Histogram with pool, region labels)
  - proxywhirl_pool_proxies (Gauge with pool, health_status labels)
  - proxywhirl_proxy_health_checks_total (Counter with pool, proxy_id, result labels)
- [ ] T029 [US1] Add enable_process_metrics support (CPU, memory) in proxywhirl/metrics_collector.py
- [ ] T030 [US1] Add enable_pool_metrics support in proxywhirl/metrics_collector.py
- [ ] T031 [US1] Add enable_request_metrics support in proxywhirl/metrics_collector.py
- [ ] T032 [US1] Update rotator.py to track pool size changes (add/remove proxies)
- [ ] T033 [US1] Update rotator.py to track proxy health check results
- [ ] T034 [US1] Extend config.py with metrics settings from MetricsConfig
- [ ] T035 [US1] Add metrics configuration loading from .proxywhirl.toml in config.py
- [ ] T036 [P] [US1] Unit test MetricsExporter Prometheus format in tests/unit/test_metrics_exporter.py
- [ ] T037 [P] [US1] Unit test basic auth for /metrics in tests/unit/test_metrics_exporter.py
- [ ] T038 [US1] Integration test /metrics endpoint returns valid Prometheus data in tests/integration/test_metrics_e2e.py
- [ ] T039 [US1] Integration test metrics update during proxy requests in tests/integration/test_metrics_e2e.py
- [ ] T040 [US1] Verify SC-001: 95% of metrics appear within 60s in tests/integration/test_metrics_e2e.py
- [ ] T041 [US1] Create contracts/prometheus-scrape-config.yml examples (already exists, verify)
- [ ] T042 [US1] Create contracts/grafana-dashboard.json template (already exists, verify panels)
- [ ] T043 [US1] Test Grafana dashboard import with sample data
- [ ] T044 [US1] Add logging for metrics collection errors with loguru integration
- [ ] T045 [US1] Document /metrics endpoint in quickstart.md (already exists, verify)

**Checkpoint**: At this point, User Story 1 should be fully functional - /metrics endpoint serves Prometheus data, Grafana dashboard displays proxy health trends

---

## Phase 4: User Story 2 - Receive Automated Degradation Alerts (Priority: P2)

**Goal**: Site Reliability Engineers receive proactive notifications when proxy performance crosses critical thresholds (error rate, latency) so they can respond quickly.

**Independent Test**: Configure alert rule with low threshold, simulate threshold breach (e.g., high error rate), verify alert rule evaluates correctly and alert state is tracked.

### Implementation for User Story 2

- [ ] T046 [P] [US2] Create proxywhirl/alert_manager.py with AlertManager class
- [ ] T047 [P] [US2] Implement AlertRule Pydantic model in proxywhirl/metrics_models.py from data-model.md
- [ ] T048 [P] [US2] Implement AlertSeverity enum in proxywhirl/metrics_models.py (INFO, WARNING, CRITICAL)
- [ ] T049 [P] [US2] Implement ComparisonOperator enum in proxywhirl/metrics_models.py (GT, LT, EQ, GTE, LTE)
- [ ] T050 [US2] Implement alert rule loading from YAML in proxywhirl/alert_manager.py
- [ ] T051 [US2] Implement alert rule evaluation logic in proxywhirl/alert_manager.py
- [ ] T052 [US2] Implement alert state machine (Inactive, Pending, Firing, Resolved, Suppressed) in proxywhirl/alert_manager.py
- [ ] T053 [US2] Implement duration tracking (alert fires only after condition true for duration) in proxywhirl/alert_manager.py
- [ ] T054 [US2] Implement alert suppression schedule (cron-based) in proxywhirl/alert_manager.py
- [ ] T055 [US2] Add proxywhirl_alerts_active gauge metric in proxywhirl/metrics_collector.py
- [ ] T056 [US2] Integrate AlertManager with MetricsCollector for evaluation in proxywhirl/alert_manager.py
- [ ] T057 [US2] Add alert rule hot-reloading without service restart in proxywhirl/alert_manager.py
- [ ] T058 [US2] Implement PromQL expression validation at load time in proxywhirl/alert_manager.py
- [ ] T059 [US2] Add alert annotations templating ({{ $labels.pool }}, {{ $value }}) in proxywhirl/alert_manager.py
- [ ] T060 [US2] Extend config.py with alert rules configuration path
- [ ] T061 [P] [US2] Unit test AlertRule model validation in tests/unit/test_alert_manager.py
- [ ] T062 [P] [US2] Unit test alert rule YAML loading in tests/unit/test_alert_manager.py
- [ ] T063 [P] [US2] Unit test alert state transitions in tests/unit/test_alert_manager.py
- [ ] T064 [US2] Unit test alert duration tracking in tests/unit/test_alert_manager.py
- [ ] T065 [US2] Unit test alert suppression logic in tests/unit/test_alert_manager.py
- [ ] T066 [US2] Integration test alert fires on threshold breach in tests/integration/test_alert_notifications.py
- [ ] T067 [US2] Integration test alert resolves when condition clears in tests/integration/test_alert_notifications.py
- [ ] T068 [US2] Integration test alert deduplication (multiple breaches) in tests/integration/test_alert_notifications.py
- [ ] T069 [US2] Verify SC-002: Alerts notify within 2 minutes of breach in tests/integration/test_alert_notifications.py
- [ ] T070 [US2] Create contracts/alertmanager-rules.yml with pre-built alert rules (already exists, verify)
- [ ] T071 [US2] Document alert rule configuration in quickstart.md (already exists, verify Step 4)
- [ ] T072 [US2] Add logging for alert state changes with structured context

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - alerts fire when thresholds breach

---

## Phase 5: User Story 3 - Analyze Historical Performance (Priority: P3)

**Goal**: Product managers and analysts can export historical metrics (90+ days) to CSV/JSON for trend analysis, seasonality detection, and capacity planning.

**Independent Test**: Request historical export for last 90 days, verify CSV/JSON file contains aggregated metrics with correct time range and includes metadata (export_id, requested_by, filters).

### Implementation for User Story 3

- [ ] T073 [P] [US3] Implement HistoricalExport Pydantic model in proxywhirl/metrics_models.py from data-model.md
- [ ] T074 [P] [US3] Implement ExportFormat enum in proxywhirl/metrics_models.py (CSV, JSON, PARQUET)
- [ ] T075 [P] [US3] Implement ExportStatus enum in proxywhirl/metrics_models.py (PENDING, IN_PROGRESS, COMPLETED, FAILED)
- [ ] T076 [P] [US3] Create proxywhirl/metrics_exporter.py export_historical_metrics() function
- [ ] T077 [US3] Implement Prometheus Query API client in proxywhirl/metrics_exporter.py
- [ ] T078 [US3] Implement time range query construction (start_time, end_time) in proxywhirl/metrics_exporter.py
- [ ] T079 [US3] Implement label filtering (pool, region, etc.) in proxywhirl/metrics_exporter.py
- [ ] T080 [US3] Implement CSV export format with headers in proxywhirl/metrics_exporter.py
- [ ] T081 [US3] Implement JSON export format with metadata in proxywhirl/metrics_exporter.py
- [ ] T082 [US3] Add export job metadata tracking (export_id, requested_by, timestamps) in proxywhirl/metrics_exporter.py
- [ ] T083 [US3] Add export validation (max 365 days time range) in proxywhirl/metrics_exporter.py
- [ ] T084 [US3] Add export error handling and partial file prevention in proxywhirl/metrics_exporter.py
- [ ] T085 [US3] Add file size calculation after export completion in proxywhirl/metrics_exporter.py
- [ ] T086 [US3] Implement export timeout handling (large time ranges) in proxywhirl/metrics_exporter.py
- [ ] T087 [US3] Add export batching for very large datasets in proxywhirl/metrics_exporter.py
- [ ] T088 [P] [US3] Unit test HistoricalExport model validation in tests/unit/test_metrics_exporter.py
- [ ] T089 [P] [US3] Unit test Prometheus query construction in tests/unit/test_metrics_exporter.py
- [ ] T090 [P] [US3] Unit test CSV export formatting in tests/unit/test_metrics_exporter.py
- [ ] T091 [P] [US3] Unit test JSON export formatting in tests/unit/test_metrics_exporter.py
- [ ] T092 [US3] Integration test export 7-day metrics to CSV in tests/integration/test_dashboard_queries.py
- [ ] T093 [US3] Integration test export 90-day metrics to JSON in tests/integration/test_dashboard_queries.py
- [ ] T094 [US3] Integration test export with filters (pool, region) in tests/integration/test_dashboard_queries.py
- [ ] T095 [US3] Integration test export error handling (invalid time range) in tests/integration/test_dashboard_queries.py
- [ ] T096 [US3] Integration test dashboard query response time <2s for 90 days in tests/integration/test_dashboard_queries.py
- [ ] T097 [US3] Document historical export API in quickstart.md (already exists, verify Step 6)
- [ ] T098 [US3] Add logging for export job lifecycle (pending, in_progress, completed, failed)

**Checkpoint**: All user stories should now be independently functional - exports generate CSV/JSON files with correct data

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and deployment readiness

- [ ] T099 [P] Create proxywhirl/dashboard_models.py with DashboardConfig, DashboardPanel, TimeRange models
- [ ] T100 [P] Implement dashboard JSON generation from DashboardConfig in proxywhirl/dashboard_models.py
- [ ] T101 [P] Add stale data indicators (Prometheus unavailable) in proxywhirl/metrics_exporter.py
- [ ] T102 [P] Add graceful degradation when Prometheus is down in proxywhirl/metrics_collector.py
- [ ] T103 Implement metrics exposition endpoint firewall configuration in proxywhirl/metrics_exporter.py
- [ ] T104 Add TLS support for /metrics endpoint in proxywhirl/metrics_exporter.py
- [ ] T105 Validate no credentials appear in exported metrics (security audit) across all modules
- [ ] T106 [P] Add mypy type checking for all new modules: `uv run mypy proxywhirl/metrics_*.py`
- [ ] T107 [P] Add ruff linting for all new modules: `uv run ruff check proxywhirl/metrics_*.py`
- [ ] T108 [P] Unit test DashboardConfig model validation in tests/unit/test_dashboard_models.py
- [ ] T109 [P] Unit test dashboard JSON generation in tests/unit/test_dashboard_models.py
- [ ] T110 Update README.md with metrics feature section and quickstart link
- [ ] T111 Update contracts/grafana-dashboard.json with all panels from data-model.md
- [ ] T112 Validate quickstart.md end-to-end (15-20 minute setup test)
- [ ] T113 Run full test suite: `uv run pytest tests/` and verify 85%+ coverage
- [ ] T114 Performance validation: Verify metrics collection overhead <5% with real traffic
- [ ] T115 Security audit: Verify SecretStr usage for basic_auth_password
- [ ] T116 Documentation: Add docstrings to all public APIs (metrics_collector, metrics_exporter, alert_manager)
- [ ] T117 [P] Create deployment guide for Kubernetes (Prometheus Operator) in docs/
- [ ] T118 [P] Create deployment guide for Docker Compose in docs/
- [ ] T119 Add metrics feature to main project README.md roadmap

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Uses metrics from US1 but can be developed independently (mocked metrics)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Exports metrics from US1 but can be developed independently (mocked Prometheus)

### Within Each User Story

- Benchmarks/tests should be run continuously during implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 - Setup (All parallel)**:
- T001, T002 (dependency installation)
- T003, T004, T005 (stub file creation)

**Phase 2 - Foundational (Parallelizable groups)**:
- Group A (models): T006, T007, T008 - all metrics models
- Group B (tests): T016, T017 - model tests
- Group C (concurrent tests): T020 - property tests

**Phase 3 - User Story 1 (Parallelizable groups)**:
- Group A (benchmarks): T021, T022 - performance tests
- Group A (implementation): T023, T028 - exporter and metric definitions
- Group B (tests): T036, T037 - unit tests for exporter

**Phase 4 - User Story 2 (Parallelizable groups)**:
- Group A (models): T046, T047, T048, T049 - alert models
- Group B (tests): T061, T062, T063, T064, T065 - unit tests

**Phase 5 - User Story 3 (Parallelizable groups)**:
- Group A (models): T073, T074, T075 - export models
- Group B (tests): T088, T089, T090, T091 - unit tests

**Phase 6 - Polish (Parallelizable groups)**:
- Group A (models): T099, T100 - dashboard models
- Group B (hardening): T101, T102, T103, T104, T105 - production readiness
- Group C (validation): T106, T107 - linting/typing
- Group D (tests): T108, T109 - dashboard tests
- Group E (docs): T110, T117, T118, T119 - documentation

---

## Parallel Example: User Story 1

```bash
# Launch benchmarks together:
Task T021: "Benchmark metrics collection overhead <5% in tests/benchmarks/test_metrics_overhead.py"
Task T022: "Benchmark /metrics endpoint response time <50ms in tests/benchmarks/test_metrics_overhead.py"

# Launch core implementation together (different files):
Task T023: "Create proxywhirl/metrics_exporter.py with MetricsExporter class"
Task T028: "Define core metrics in proxywhirl/metrics_collector.py"

# Launch unit tests together:
Task T036: "Unit test MetricsExporter Prometheus format in tests/unit/test_metrics_exporter.py"
Task T037: "Unit test basic auth for /metrics in tests/unit/test_metrics_exporter.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (~30 minutes)
2. Complete Phase 2: Foundational (~4-6 hours) - CRITICAL blocking phase
3. Complete Phase 3: User Story 1 (~6-8 hours)
4. **STOP and VALIDATE**: Test User Story 1 independently with quickstart.md
5. Deploy/demo Grafana dashboard showing live proxy metrics

**Estimated MVP Time**: 12-16 hours for a functional metrics dashboard

### Incremental Delivery

1. **Week 1**: Setup + Foundational → Foundation ready
2. **Week 2**: Add User Story 1 → Test independently → Deploy/Demo (MVP!)
   - Operations leads can now monitor proxy health trends
3. **Week 3**: Add User Story 2 → Test independently → Deploy/Demo
   - SREs now receive automated alerts on performance degradation
4. **Week 4**: Add User Story 3 → Test independently → Deploy/Demo
   - Analysts can now export historical data for capacity planning
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (~1 day)
2. Once Foundational is done, split work:
   - **Developer A**: User Story 1 (Dashboard/Metrics) - Most critical
   - **Developer B**: User Story 2 (Alerts) - Can work independently with mocked metrics
   - **Developer C**: User Story 3 (Exports) - Can work independently with mocked Prometheus
3. Stories complete and integrate independently within 1-2 weeks

---

## Success Criteria Validation

### SC-001: 95% of metrics updates appear within 60 seconds
- **Validated by**: T040 in Phase 3 (User Story 1)
- **Test**: Generate traffic, measure time from metric update to Prometheus scrape
- **Target**: <60s latency for 95% of metrics

### SC-002: Automated alerts notify within 2 minutes of threshold breach
- **Validated by**: T069 in Phase 4 (User Story 2)
- **Test**: Simulate threshold breach, measure alert evaluation time
- **Target**: Alert fires within 2 minutes, includes affected proxy scope

### SC-003: 90% of operations stakeholders can identify root causes using dashboard alone
- **Validated by**: T043, T045 in Phase 3 (User Story 1)
- **Test**: User acceptance testing with operations team
- **Target**: Dashboard provides sufficient context for troubleshooting

### SC-004: 30% reduction in customer-facing downtime within 3 months
- **Validated by**: Post-launch measurement (not in tasks)
- **Test**: Compare incident response times before/after metrics implementation
- **Target**: Faster issue detection leads to 30% downtime reduction

### Performance Benchmarks
- **Metrics overhead <5%**: T021, T114
- **Dashboard query <2s for 90 days**: T096
- **/metrics endpoint <50ms**: T022

---

## Notes

- All tasks use `uv run` prefix per constitution (e.g., `uv run pytest tests/`)
- [P] tasks = different files, no dependencies within that group
- [Story] label maps task to specific user story (US1, US2, US3) for traceability
- Each user story should be independently completable and testable
- Constitution violation (23/20 modules) is justified - observability requires clean separation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Module count: 4 new modules added (metrics_collector, metrics_exporter, alert_manager, dashboard_models)
- Total estimated tasks: 119 tasks across 6 phases
- Recommended MVP: Phases 1-3 only (User Story 1) = 45 tasks = ~12-16 hours

---

## Task Count Summary

- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 15 tasks (BLOCKING)
- **Phase 3 (User Story 1 - Dashboard)**: 25 tasks
- **Phase 4 (User Story 2 - Alerts)**: 27 tasks
- **Phase 5 (User Story 3 - Exports)**: 26 tasks
- **Phase 6 (Polish)**: 21 tasks

**Total**: 119 tasks

**Parallel Opportunities**: 
- Phase 1: 3 parallel groups (dependency install, stub creation)
- Phase 2: 3 parallel groups (models, tests, property tests)
- Phase 3: 5 parallel groups (benchmarks, implementation, tests)
- Phase 4: 5 parallel groups (models, tests)
- Phase 5: 5 parallel groups (models, tests)
- Phase 6: 5 parallel groups (models, hardening, validation, tests, docs)

**Suggested MVP Scope**: Phases 1-3 (User Story 1 only) = 45 tasks = Dashboard monitoring ready
