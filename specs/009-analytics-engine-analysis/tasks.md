# Tasks: Analytics Engine & Usage Insights

**Input**: Design documents from `/specs/009-analytics-engine-analysis/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/analytics-api.md, quickstart.md

**Tests**: Test-first development is MANDATORY per constitutional principle #2. All tests must be written BEFORE implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Source: `proxywhirl/` (flat package architecture)
- Tests: `tests/unit/`, `tests/integration/`, `tests/property/`
- All paths are absolute from repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency setup

- [ ] T001 Add pandas>=2.0.0 dependency to pyproject.toml using `uv add pandas>=2.0.0`
- [ ] T002 Create proxywhirl/analytics_models.py with empty module structure and docstring
- [ ] T003 Create proxywhirl/analytics.py with empty module structure and docstring
- [ ] T004 [P] Update proxywhirl/__init__.py to export AnalyticsEngine and analytics models
- [ ] T005 [P] Create tests/unit/test_analytics.py with test class structure
- [ ] T006 [P] Create tests/unit/test_analytics_sampling.py with test class structure
- [ ] T007 [P] Create tests/unit/test_analytics_queries.py with test class structure
- [ ] T008 [P] Create tests/unit/test_analytics_export.py with test class structure
- [ ] T009 [P] Create tests/integration/test_analytics_integration.py with test class structure
- [ ] T010 [P] Create tests/integration/test_analytics_performance.py with test class structure
- [ ] T011 [P] Create tests/property/test_analytics_sampling_properties.py with test class structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models and database schema that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundation

- [ ] T012 [P] Write property tests for UsageRecord validation in tests/property/test_analytics_sampling_properties.py (MUST FAIL)
- [ ] T013 [P] Write unit tests for AggregateMetric model in tests/unit/test_analytics.py (MUST FAIL)
- [ ] T014 [P] Write unit tests for CostRecord model in tests/unit/test_analytics.py (MUST FAIL)
- [ ] T015 [P] Write unit tests for RetentionPolicy model in tests/unit/test_analytics.py (MUST FAIL)
- [ ] T016 [P] Write unit tests for ExportJob model in tests/unit/test_analytics.py (MUST FAIL)
- [ ] T017 [P] Write unit tests for AccessAuditLog model in tests/unit/test_analytics.py (MUST FAIL)

### Implementation for Foundation

- [ ] T018 [P] Implement UsageRecord Pydantic model in proxywhirl/analytics_models.py with full validation
- [ ] T019 [P] Implement AggregateMetric Pydantic model in proxywhirl/analytics_models.py with full validation
- [ ] T020 [P] Implement CostRecord Pydantic model in proxywhirl/analytics_models.py with full validation
- [ ] T021 [P] Implement RetentionPolicy Pydantic model in proxywhirl/analytics_models.py with full validation
- [ ] T022 [P] Implement ExportJob Pydantic model in proxywhirl/analytics_models.py with full validation
- [ ] T023 [P] Implement AccessAuditLog Pydantic model in proxywhirl/analytics_models.py with full validation
- [ ] T024 Extend proxywhirl/storage.py with analytics_usage table schema (CREATE TABLE with all indexes)
- [ ] T025 [P] Extend proxywhirl/storage.py with analytics_hourly table schema (CREATE TABLE with indexes)
- [ ] T026 [P] Extend proxywhirl/storage.py with analytics_daily table schema (CREATE TABLE with indexes)
- [ ] T027 [P] Extend proxywhirl/storage.py with analytics_costs table schema
- [ ] T028 [P] Extend proxywhirl/storage.py with analytics_retention table schema
- [ ] T029 [P] Extend proxywhirl/storage.py with analytics_exports table schema
- [ ] T030 [P] Extend proxywhirl/storage.py with analytics_audit_log table schema
- [ ] T031 Verify all foundation tests pass with mypy --strict compliance

**Checkpoint**: Foundation ready - all 6 entities defined with Pydantic models and database schema

---

## Phase 3: User Story 1 - Track Proxy Usage Patterns (Priority: P1) 🎯 MVP

**Goal**: Enable developers and operations teams to understand proxy usage across applications, endpoints, and time periods

**Independent Test**: Generate usage reports for a 24-hour period and verify request counts, success rates, and usage patterns are accurately captured

### Tests for User Story 1

- [ ] T032 [P] [US1] Write unit tests for AdaptiveSampler class in tests/unit/test_analytics_sampling.py (MUST FAIL)
- [ ] T033 [P] [US1] Write property tests for sampling distribution preservation in tests/property/test_analytics_sampling_properties.py (MUST FAIL)
- [ ] T034 [P] [US1] Write unit tests for usage collection in tests/unit/test_analytics.py (MUST FAIL)
- [ ] T035 [P] [US1] Write unit tests for query_usage method in tests/unit/test_analytics_queries.py (MUST FAIL)
- [ ] T036 [P] [US1] Write unit tests for time range parsing in tests/unit/test_analytics_queries.py (MUST FAIL)
- [ ] T037 [P] [US1] Write integration test for basic usage tracking in tests/integration/test_analytics_integration.py (MUST FAIL)
- [ ] T038 [P] [US1] Write integration test for grouped analysis in tests/integration/test_analytics_integration.py (MUST FAIL)
- [ ] T039 [P] [US1] Write integration test for period comparison in tests/integration/test_analytics_integration.py (MUST FAIL)

### Implementation for User Story 1

- [ ] T040 [P] [US1] Implement AdaptiveSampler class in proxywhirl/analytics.py with reservoir sampling logic
- [ ] T041 [P] [US1] Implement TimeRange helper in proxywhirl/analytics_models.py with string parsing ("24h", "7d", "30d")
- [ ] T042 [P] [US1] Implement QueryFilters Pydantic model in proxywhirl/analytics_models.py
- [ ] T043 [US1] Implement AnalyticsEngine.__init__ in proxywhirl/analytics.py with database setup
- [ ] T044 [US1] Implement AnalyticsEngine.collect_usage in proxywhirl/analytics.py with async collection
- [ ] T045 [US1] Implement AnalyticsEngine.query_usage in proxywhirl/analytics.py with filtering and grouping
- [ ] T046 [US1] Add usage collection hooks to proxywhirl/rotator.py in request method
- [ ] T047 [US1] Implement initial query result caching for common date ranges ("24h", "7d", "30d") in proxywhirl/analytics.py
- [ ] T048 [US1] Add validation for query_usage parameters (time range, filters, group_by)
- [ ] T049 [US1] Add error handling for database operations in collect_usage and query_usage
- [ ] T050 [US1] Verify all US1 tests pass and achieve >85% coverage for analytics.py

**Checkpoint**: Users can track proxy usage patterns, filter by application/endpoint, and compare time periods

---

## Phase 4: User Story 2 - Analyze Proxy Source Performance (Priority: P1)

**Goal**: Enable technical teams to evaluate which proxy sources are most reliable and performant

**Independent Test**: Review analytics for multiple proxy sources and verify success rates, response times, and failure patterns are accurately tracked

### Tests for User Story 2

- [ ] T051 [P] [US2] Write unit tests for get_source_performance method in tests/unit/test_analytics_queries.py (MUST FAIL)
- [ ] T052 [P] [US2] Write unit tests for PerformanceMetrics model in tests/unit/test_analytics.py (MUST FAIL)
- [ ] T053 [P] [US2] Write integration test for source comparison in tests/integration/test_analytics_integration.py (MUST FAIL)
- [ ] T054 [P] [US2] Write integration test for temporal analysis in tests/integration/test_analytics_integration.py (MUST FAIL)
- [ ] T055 [P] [US2] Write integration test for failure analysis in tests/integration/test_analytics_integration.py (MUST FAIL)

### Implementation for User Story 2

- [ ] T056 [P] [US2] Implement PerformanceMetrics Pydantic model in proxywhirl/analytics_models.py
- [ ] T057 [US2] Implement AnalyticsEngine.get_source_performance in proxywhirl/analytics.py
- [ ] T058 [US2] Implement source comparison logic with trend indicators in proxywhirl/analytics.py
- [ ] T059 [US2] Add temporal analysis query support (hourly/daily breakdown) in proxywhirl/analytics.py
- [ ] T060 [US2] Add failure pattern detection (error_code grouping) in proxywhirl/analytics.py
- [ ] T061 [US2] Optimize queries with covering indexes (verify EXPLAIN QUERY PLAN)
- [ ] T062 [US2] Add performance degradation detection logic in proxywhirl/analytics.py
- [ ] T063 [US2] Verify all US2 tests pass and maintain >85% coverage

**Checkpoint**: Users can analyze source-level performance, compare sources, and identify degradation patterns

---

## Phase 5: User Story 3 - Generate Cost and ROI Insights (Priority: P2)

**Goal**: Enable business stakeholders to understand cost-effectiveness of proxy usage and ROI

**Independent Test**: Generate cost reports based on usage data and verify costs are accurately attributed with ROI calculations

### Tests for User Story 3

- [ ] T064 [P] [US3] Write unit tests for calculate_costs method in tests/unit/test_analytics_queries.py (MUST FAIL)
- [ ] T065 [P] [US3] Write unit tests for CostReport model in tests/unit/test_analytics.py (MUST FAIL)
- [ ] T066 [P] [US3] Write integration test for cost calculation in tests/integration/test_analytics_integration.py (MUST FAIL)
- [ ] T067 [P] [US3] Write integration test for cost allocation in tests/integration/test_analytics_integration.py (MUST FAIL)
- [ ] T068 [P] [US3] Write integration test for ROI analysis in tests/integration/test_analytics_integration.py (MUST FAIL)

### Implementation for User Story 3

- [ ] T069 [P] [US3] Implement CostReport Pydantic model in proxywhirl/analytics_models.py
- [ ] T070 [P] [US3] Implement CostModel enum in proxywhirl/analytics_models.py (per-request, subscription, data transfer, hybrid)
- [ ] T071 [US3] Implement AnalyticsEngine.calculate_costs in proxywhirl/analytics.py
- [ ] T072 [US3] Implement cost allocation logic by application in proxywhirl/analytics.py
- [ ] T073 [US3] Implement ROI calculation comparing premium vs free sources in proxywhirl/analytics.py
- [ ] T074 [US3] Add cost trend analysis (daily/weekly/monthly) in proxywhirl/analytics.py
- [ ] T075 [US3] Add cost-per-successful-request metric calculation in proxywhirl/analytics.py
- [ ] T076 [US3] Verify all US3 tests pass and maintain >85% coverage

**Checkpoint**: Users can generate cost reports, allocate costs by application, and analyze ROI

---

## Phase 6: User Story 4 - Export Analytics for Reporting (Priority: P2)

**Goal**: Enable analysts and stakeholders to export analytics data in standard formats for integration with BI tools

**Independent Test**: Export analytics data in CSV, JSON, and report formats; verify completeness and proper formatting

### Tests for User Story 4

- [ ] T077 [P] [US4] Write unit tests for export_analytics method in tests/unit/test_analytics_export.py (MUST FAIL)
- [ ] T078 [P] [US4] Write unit tests for ExportFormat enum in tests/unit/test_analytics_export.py (MUST FAIL)
- [ ] T079 [P] [US4] Write integration test for CSV export in tests/integration/test_analytics_integration.py (MUST FAIL)
- [ ] T080 [P] [US4] Write integration test for JSON export in tests/integration/test_analytics_integration.py (MUST FAIL)
- [ ] T081 [P] [US4] Write integration test for filtered export in tests/integration/test_analytics_integration.py (MUST FAIL)

### Implementation for User Story 4

- [ ] T082 [P] [US4] Implement ExportFormat enum in proxywhirl/analytics_models.py (CSV, JSON, EXCEL)
- [ ] T083 [US4] Implement AnalyticsEngine.export_analytics in proxywhirl/analytics.py
- [ ] T084 [US4] Implement CSV export with pandas DataFrame.to_csv in proxywhirl/analytics.py
- [ ] T085 [US4] Implement JSON export with proper datetime serialization in proxywhirl/analytics.py
- [ ] T086 [US4] Implement Excel export with pandas DataFrame.to_excel in proxywhirl/analytics.py
- [ ] T087 [US4] Implement AnalyticsEngine.get_export_status in proxywhirl/analytics.py
- [ ] T088 [US4] Implement AnalyticsEngine.download_export in proxywhirl/analytics.py
- [ ] T089 [US4] Add export job tracking to analytics_exports table in proxywhirl/analytics.py
- [ ] T090 [US4] Add audit logging for export operations to analytics_audit_log table
- [ ] T091 [US4] Implement field selection for configurable exports in proxywhirl/analytics.py
- [ ] T092 [US4] Verify all US4 tests pass and maintain >85% coverage

**Checkpoint**: Users can export analytics in multiple formats with audit trails

---

## Phase 7: User Story 5 - Configure Analytics Retention and Aggregation (Priority: P3)

**Goal**: Enable administrators to control how long analytics data is retained and how it's aggregated

**Independent Test**: Configure retention policies and aggregation rules; verify old data is archived/deleted according to policy

### Tests for User Story 5

- [ ] T093 [P] [US5] Write unit tests for set_retention_policy method in tests/unit/test_analytics.py (MUST FAIL)
- [ ] T094 [P] [US5] Write unit tests for trigger_aggregation method in tests/unit/test_analytics.py (MUST FAIL)
- [ ] T095 [P] [US5] Write unit tests for trigger_backup method in tests/unit/test_analytics.py (MUST FAIL)
- [ ] T096 [P] [US5] Write integration test for retention enforcement in tests/integration/test_analytics_integration.py (MUST FAIL)
- [ ] T097 [P] [US5] Write integration test for hourly aggregation in tests/integration/test_analytics_integration.py (MUST FAIL)
- [ ] T098 [P] [US5] Write integration test for daily aggregation in tests/integration/test_analytics_integration.py (MUST FAIL)

### Implementation for User Story 5

- [ ] T099 [US5] Implement AnalyticsEngine.set_retention_policy in proxywhirl/analytics.py (admin-only)
- [ ] T100 [US5] Implement AnalyticsEngine.get_retention_policy in proxywhirl/analytics.py
- [ ] T101 [US5] Implement AnalyticsEngine.set_sampling_thresholds in proxywhirl/analytics.py (admin-only)
- [ ] T102 [US5] Implement retention enforcement logic in proxywhirl/analytics.py (delete old raw data)
- [ ] T103 [US5] Implement AnalyticsEngine.trigger_aggregation in proxywhirl/analytics.py
- [ ] T104 [US5] Implement hourly aggregation logic in proxywhirl/analytics.py (calc metrics, insert into analytics_hourly)
- [ ] T105 [US5] Implement daily aggregation logic in proxywhirl/analytics.py (calc metrics, insert into analytics_daily)
- [ ] T106 [US5] Implement AnalyticsEngine.trigger_backup in proxywhirl/analytics.py
- [ ] T107 [US5] Implement database backup to file in proxywhirl/analytics.py (SQLite .backup())
- [ ] T108 [US5] Add GitHub LFS upload support in proxywhirl/analytics.py (git lfs track, commit, push)
- [ ] T109 [US5] Add Kaggle dataset upload support in proxywhirl/analytics.py (kaggle API)
- [ ] T110 [US5] Add permission checks for admin-only methods in proxywhirl/analytics.py
- [ ] T111 [US5] Verify all US5 tests pass and maintain >85% coverage

**Checkpoint**: Administrators can configure retention, aggregation, and backups with proper access control

---

## Phase 8: Performance Optimization & Benchmarks

**Purpose**: Ensure performance targets are met across all operations

- [ ] T112 [P] Write performance benchmark for collection overhead in tests/integration/test_analytics_performance.py (target: <5ms p95)
- [ ] T113 [P] Write performance benchmark for query response time in tests/integration/test_analytics_performance.py (target: <5s for 30d)
- [ ] T114 [P] Write performance benchmark for adaptive sampling activation in tests/integration/test_analytics_performance.py (target: <100ms)
- [ ] T115 [P] Write performance benchmark for export generation in tests/integration/test_analytics_performance.py (target: <3min)
- [ ] T116 Optimize query_usage with EXPLAIN QUERY PLAN analysis in proxywhirl/analytics.py
- [ ] T117 Expand and optimize caching patterns from T047 (add more cache keys, TTL tuning, LRU eviction) in proxywhirl/analytics.py
- [ ] T118 Add database connection pooling if needed in proxywhirl/analytics.py
- [ ] T119 Optimize aggregation queries with batch processing in proxywhirl/analytics.py
- [ ] T120 Run all performance benchmarks and verify targets met

---

## Phase 9: Integration & Configuration

**Purpose**: Integrate analytics with existing proxywhirl components and configuration

- [ ] T121 Extend proxywhirl/config.py with AnalyticsConfig Pydantic settings model
- [ ] T122 Add analytics configuration to environment variables (PROXYWHIRL_ANALYTICS_*)
- [ ] T123 Update proxywhirl/rotator.py to initialize AnalyticsEngine from config
- [ ] T124 Add analytics enable/disable flag to ProxyRotator configuration
- [ ] T125 Integrate with loguru structured logging for audit trails
- [ ] T126 [P] Write integration test for rotator + analytics in tests/integration/test_analytics_integration.py
- [ ] T127 Verify quickstart.md examples work end-to-end

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and documentation

- [ ] T128 [P] Add comprehensive docstrings to all public methods in proxywhirl/analytics.py
- [ ] T129 [P] Add comprehensive docstrings to all Pydantic models in proxywhirl/analytics_models.py
- [ ] T130 [P] Update README.md with analytics feature section
- [ ] T131 [P] Create analytics usage examples in examples/analytics_example.py
- [ ] T132 Run mypy --strict on proxywhirl/analytics.py and proxywhirl/analytics_models.py (must pass 0 errors)
- [ ] T133 Run ruff check on all analytics files (must pass 0 errors)
- [ ] T134 Run ruff format on all analytics files
- [ ] T135 Run full test suite with coverage report (target: >85% for analytics modules)
- [ ] T136 Review and update CHANGELOG.md with analytics feature entry
- [ ] T137 Run constitutional compliance check against all 7 principles
- [ ] T138 Validate all quickstart.md examples execute successfully

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2 completion - Core MVP functionality
- **Phase 4 (US2)**: Depends on Phase 2 completion - Can run parallel with US1 (different methods)
- **Phase 5 (US3)**: Depends on Phase 2 completion - Can run parallel with US1/US2 (different methods)
- **Phase 6 (US4)**: Depends on Phase 2 completion - Can run parallel with other stories (export logic separate)
- **Phase 7 (US5)**: Depends on Phase 2 completion - Can run parallel with other stories (admin methods separate)
- **Phase 8 (Performance)**: Depends on Phases 3-7 completion - Optimization pass
- **Phase 9 (Integration)**: Depends on Phases 3-7 completion - Wiring everything together
- **Phase 10 (Polish)**: Depends on all phases - Final quality pass

### User Story Dependencies

- **US1 (Usage Tracking)**: Core foundation - No dependencies on other stories
- **US2 (Source Performance)**: Independent - Uses same data model as US1 but separate methods
- **US3 (Cost/ROI)**: Independent - Adds cost analysis on top of usage data
- **US4 (Export)**: Independent - Exports data from any user story
- **US5 (Retention)**: Independent - Manages data lifecycle for all stories

### Within Each User Story

1. Tests FIRST (write, verify they FAIL)
2. Models (Pydantic classes)
3. Core implementation (AnalyticsEngine methods)
4. Integration with existing code
5. Validation and error handling
6. Verify tests PASS

### Parallel Opportunities

**Phase 1 (Setup)**: T002-T011 can all run in parallel (different files)

**Phase 2 (Foundation - Tests)**: T012-T017 can all run in parallel (different test files)

**Phase 2 (Foundation - Models)**: T018-T023 can all run in parallel (different models)

**Phase 2 (Foundation - Tables)**: T025-T030 can all run in parallel (different tables)

**Once Foundation Complete (Phase 2)**: All user stories (Phases 3-7) can start in parallel if team capacity allows:
- Developer A: US1 (Usage Tracking) - T032-T050
- Developer B: US2 (Source Performance) - T051-T063
- Developer C: US3 (Cost/ROI) - T064-T076
- Developer D: US4 (Export) - T077-T092
- Developer E: US5 (Retention) - T093-T111

**Phase 8 (Benchmarks)**: T112-T115 can run in parallel (different benchmark tests)

**Phase 10 (Polish)**: T128-T131 can run in parallel (different documentation files)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task T032: "Write unit tests for AdaptiveSampler class"
Task T033: "Write property tests for sampling distribution"
Task T034: "Write unit tests for usage collection"
Task T035: "Write unit tests for query_usage method"
Task T036: "Write unit tests for time range parsing"
Task T037: "Write integration test for basic usage tracking"
Task T038: "Write integration test for grouped analysis"
Task T039: "Write integration test for period comparison"

# Launch parallel implementation tasks:
Task T040: "Implement AdaptiveSampler class"
Task T041: "Implement TimeRange helper"
Task T042: "Implement QueryFilters model"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T011) - ~2 hours
2. Complete Phase 2: Foundational (T012-T031) - ~8 hours (CRITICAL BLOCKER)
3. Complete Phase 3: User Story 1 (T032-T050) - ~12 hours
4. **STOP and VALIDATE**: Test US1 independently with quickstart.md examples
5. Deploy/demo MVP capability

**Total MVP Time**: ~22 hours (assuming sequential work)

### Incremental Delivery

1. **Foundation Ready** (Phases 1-2): All data models and schema complete
2. **MVP Release** (Phase 3): Usage tracking live - users can track proxy patterns
3. **Performance Analysis** (Phase 4): Source-level insights available
4. **Cost Visibility** (Phase 5): Business stakeholders get ROI data
5. **Data Export** (Phase 6): Integration with BI tools enabled
6. **Lifecycle Management** (Phase 7): Admins control retention and backups
7. **Production Ready** (Phases 8-10): Performance optimized, fully integrated

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With 5 developers after Foundation phase (Phase 2):

- **Developer A**: US1 (Usage Tracking) - 12 hours
- **Developer B**: US2 (Source Performance) - 8 hours
- **Developer C**: US3 (Cost/ROI) - 8 hours
- **Developer D**: US4 (Export) - 10 hours
- **Developer E**: US5 (Retention) - 12 hours

All stories complete in parallel (~12 hours wall time vs 50 hours sequential)

---

## Quality Gates

### Per User Story
- ✅ All tests pass (100%)
- ✅ Coverage >85% for new code
- ✅ mypy --strict passes (0 errors)
- ✅ ruff check passes (0 errors)
- ✅ Story independently testable per spec.md criteria

### Final (Phase 10)
- ✅ All 138 tasks complete
- ✅ Overall coverage >85%
- ✅ All quickstart.md examples work
- ✅ Performance targets met (<5ms collection, <5s queries)
- ✅ Constitutional compliance verified (all 7 principles)
- ✅ Security audit (no credentials in analytics, proper access control)

---

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[Story] labels**: Map tasks to user stories for traceability
- **Test-First**: ALL tests written BEFORE implementation (constitutional requirement)
- **Type Safety**: mypy --strict compliance mandatory throughout
- **Security**: 100% credential protection, access control on admin methods
- **Performance**: Targets explicit in Phase 8, optimizations in Phase 9
- **Independence**: Each user story completable and testable independently
- Commit after each logical group of tasks
- Stop at checkpoints to validate story independently
