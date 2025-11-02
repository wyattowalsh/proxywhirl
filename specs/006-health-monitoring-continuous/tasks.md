# Tasks: Health Monitoring

**Input**: Design documents from `/specs/006-health-monitoring-continuous/`  
**Prerequisites**: plan.md (✅), spec.md (✅), research.md (✅), data-model.md (✅), contracts/ (✅)

**Tests**: This feature follows TDD (Test-First Development per constitution). All tests MUST be written BEFORE implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and health monitoring module structure

- [ ] T001 Create health monitoring module structure (proxywhirl/health.py, proxywhirl/health_models.py, proxywhirl/health_worker.py)
- [ ] T002 [P] Create test directory structure (tests/unit/test_health*.py, tests/integration/test_health*.py, tests/property/test_health_properties.py, tests/benchmarks/test_health_performance.py)
- [ ] T003 [P] Update proxywhirl/__init__.py to export HealthChecker and health models
- [ ] T004 Verify no new external dependencies required (httpx, threading, loguru, pydantic already present)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Extend Proxy model in proxywhirl/models.py with health state fields (health_status, last_health_check, consecutive_failures, consecutive_successes, recovery_attempt, next_check_time, last_health_error, total_checks, total_failures)
- [ ] T006 Extend SQLite schema in proxywhirl/cache_tiers.py with health columns (ALTER TABLE cache_entries ADD COLUMN health_status, last_health_check, consecutive_failures, etc.)
- [ ] T007 Create health_history table in proxywhirl/cache_tiers.py (id, proxy_key, check_time, status, response_time_ms, error_message, check_url with indexes)
- [ ] T008 Implement schema migration logic in cache_tiers.py to add health columns non-destructively (check column existence before ALTER)
- [ ] T009 Add invalidate_by_health() method to CacheManager in proxywhirl/cache.py for cache invalidation on health failures
- [ ] T010 Extend CacheEntry model in proxywhirl/cache_models.py to include health state fields

**Checkpoint**: Foundation ready - health monitoring infrastructure in place, user story implementation can now begin

---

## Phase 3: User Story 1 - Automated Proxy Health Checks (Priority: P1) 🎯 MVP

**Goal**: Background health checking system that automatically detects and marks dead proxies

**Independent Test**: Add proxies to pool, start health checker, verify dead proxies are detected and marked unhealthy within failure threshold

### Tests for User Story 1 (TDD - Write FIRST)

> **CRITICAL: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T011 [P] [US1] Create test_health_models.py with unit tests for HealthStatus enum (state transitions, validation rules) in tests/unit/test_health_models.py
- [ ] T012 [P] [US1] Create test_health_models.py with unit tests for HealthCheckResult model (field validation, timezone-aware datetime, immutability) in tests/unit/test_health_models.py
- [ ] T013 [P] [US1] Create test_health_models.py with unit tests for HealthCheckConfig model (interval validation >=10s, threshold >=1, field defaults) in tests/unit/test_health_models.py
- [ ] T014 [P] [US1] Create test_health.py with unit tests for HealthChecker.__init__ (cache integration, config defaults, callback registration) in tests/unit/test_health.py
- [ ] T015 [P] [US1] Create test_health.py with unit tests for HealthChecker.add_proxy() (proxy registration, duplicate detection, raises ValueError) in tests/unit/test_health.py
- [ ] T016 [P] [US1] Create test_health.py with unit tests for HealthChecker.check_proxy() (HTTP HEAD request, status code validation, timeout handling, result creation) in tests/unit/test_health.py
- [ ] T017 [P] [US1] Create test_health.py with unit tests for failure threshold logic (consecutive failures tracked, mark unhealthy after N failures, reset on success) in tests/unit/test_health.py
- [ ] T018 [P] [US1] Create test_health_worker.py with unit tests for HealthWorker thread lifecycle (start, stop, graceful shutdown) in tests/unit/test_health_worker.py
- [ ] T019 [P] [US1] Create test_health_worker.py with unit tests for check scheduling (jitter calculation, next_check_time updates, interval enforcement) in tests/unit/test_health_worker.py
- [ ] T019a [P] [US1] Create test_health.py with unit tests for zombie task cleanup (thread running >2x interval, joined but not deregistered, forceful cleanup with timeout) in tests/unit/test_health.py
- [ ] T020 [P] [US1] Create test_health_integration.py with integration test for end-to-end health check flow (add proxy, start checker, verify check executes, status updates) in tests/integration/test_health_integration.py
- [ ] T021 [P] [US1] Create test_health_cache_sync.py with integration test for cache invalidation on health failure (proxy becomes unhealthy, verify cache entry invalidated) in tests/integration/test_health_cache_sync.py

### Implementation for User Story 1

- [ ] T022 [P] [US1] Implement HealthStatus enum in proxywhirl/health_models.py (HEALTHY, UNHEALTHY, CHECKING, RECOVERING, PERMANENTLY_FAILED, UNKNOWN values)
- [ ] T023 [P] [US1] Implement HealthCheckResult model in proxywhirl/health_models.py (proxy_url, check_time, status, response_time_ms, status_code, error_message, check_url fields with validators)
- [ ] T024 [P] [US1] Implement HealthCheckConfig model in proxywhirl/health_models.py (all configuration fields with defaults and validators)
- [ ] T025 [US1] Implement HealthChecker.__init__ in proxywhirl/health.py (cache integration, config storage, callback registration, RLock initialization)
- [ ] T026 [US1] Implement HealthChecker.add_proxy() in proxywhirl/health.py (register proxy, check duplicates, initialize health state, persist to cache)
- [ ] T027 [US1] Implement HealthChecker.remove_proxy() in proxywhirl/health.py (stop monitoring, remove from pool, return boolean)
- [ ] T028 [US1] Implement HealthChecker.check_proxy() in proxywhirl/health.py (HTTP HEAD request via httpx, timeout handling, create HealthCheckResult, update consecutive failures/successes)
- [ ] T029 [US1] Implement failure threshold logic in proxywhirl/health.py (_update_health_status method: track consecutive failures, mark unhealthy after threshold, emit event)
- [ ] T030 [US1] Implement cache invalidation on health failure in proxywhirl/health.py (call cache.invalidate_by_health() when proxy marked unhealthy)
- [ ] T031 [US1] Implement HealthWorker class in proxywhirl/health_worker.py (background thread per source, check scheduling loop, ThreadPoolExecutor integration)
- [ ] T032 [US1] Implement HealthChecker.start() in proxywhirl/health.py (create thread pool, start HealthWorker threads per source, set _running flag)
- [ ] T033 [US1] Implement HealthChecker.stop() in proxywhirl/health.py (signal threads to stop, wait for completion with timeout, cleanup thread pool)
- [ ] T034 [US1] Add structured logging for health events in proxywhirl/health.py (loguru.warning for proxy_down, loguru.info for checks)
- [ ] T035 [US1] Verify all US1 tests pass (run uv run pytest tests/unit/test_health*.py tests/integration/test_health_integration.py tests/integration/test_health_cache_sync.py)

**Checkpoint**: User Story 1 complete - background health checking fully functional, dead proxies detected and marked unhealthy

---

## Phase 4: User Story 2 - Configurable Health Check Intervals (Priority: P1)

**Goal**: Different proxy sources can have different check intervals based on reliability

**Independent Test**: Configure two sources with different intervals (e.g., 60s vs 300s), verify checks run at correct frequencies

### Tests for User Story 2 (TDD - Write FIRST)

- [ ] T036 [P] [US2] Create test_health_config.py with unit tests for per-source interval configuration in tests/unit/test_health_config.py
- [ ] T037 [P] [US2] Create test_health_worker.py with unit tests for interval enforcement per source (verify check timing matches config) in tests/unit/test_health_worker.py
- [ ] T038 [P] [US2] Create test_health_integration.py with integration test for multiple sources with different intervals (verify independent timing) in tests/integration/test_health_integration.py

### Implementation for User Story 2

- [ ] T039 [P] [US2] Extend HealthCheckConfig in proxywhirl/health_models.py to support per-source interval overrides (source_intervals: dict[str, int] field)
- [ ] T040 [US2] Modify HealthWorker in proxywhirl/health_worker.py to use source-specific interval from config (lookup source in config.source_intervals, fallback to default)
- [ ] T041 [US2] Update HealthChecker.start() in proxywhirl/health.py to pass source-specific config to each HealthWorker
- [ ] T042 [US2] Add validation in HealthCheckConfig to enforce minimum interval (10s) per source
- [ ] T043 [US2] Verify all US2 tests pass (run uv run pytest tests/unit/test_health_config.py tests/unit/test_health_worker.py -k interval tests/integration/test_health_integration.py -k interval)

**Checkpoint**: User Story 2 complete - per-source interval configuration works independently

---

## Phase 5: User Story 3 - Real-Time Pool Status Tracking (Priority: P2)

**Goal**: Operators can query pool health statistics in real-time

**Independent Test**: Add proxies, run checks, query get_pool_status(), verify counts match actual pool state

### Tests for User Story 3 (TDD - Write FIRST)

- [ ] T044 [P] [US3] Create test_health_models.py with unit tests for PoolStatus model (count fields, computed health_percentage property, is_degraded property) in tests/unit/test_health_models.py
- [ ] T045 [P] [US3] Create test_health_models.py with unit tests for SourceStatus model (source-level statistics) in tests/unit/test_health_models.py
- [ ] T046 [P] [US3] Create test_health.py with unit tests for HealthChecker.get_pool_status() (accurate counts, cache behavior, performance <50ms) in tests/unit/test_health.py
- [ ] T047 [P] [US3] Create test_health.py with unit tests for HealthChecker.get_proxy_status() (single proxy query, returns ProxyHealthState or None) in tests/unit/test_health.py
- [ ] T048 [P] [US3] Create test_health_integration.py with integration test for real-time status updates (change proxy health, verify status reflects change) in tests/integration/test_health_integration.py
- [ ] T049 [P] [US3] Create test_health_performance.py with benchmark test for status query latency (verify <50ms for SC-004) in tests/benchmarks/test_health_performance.py

### Implementation for User Story 3

- [ ] T050 [P] [US3] Implement PoolStatus model in proxywhirl/health_models.py (all count fields, computed properties health_percentage and is_degraded, by_source breakdown)
- [ ] T051 [P] [US3] Implement SourceStatus model in proxywhirl/health_models.py (source-level health statistics)
- [ ] T052 [US3] Implement HealthChecker.get_pool_status() in proxywhirl/health.py (iterate all proxies, count by status, create PoolStatus, cache for 1 second)
- [ ] T053 [US3] Implement HealthChecker.get_proxy_status() in proxywhirl/health.py (lookup single proxy, return ProxyHealthState or None)
- [ ] T054 [US3] Add pool status caching with 1-second TTL in proxywhirl/health.py (reduce query load, invalidate on health change)
- [ ] T055 [US3] Verify all US3 tests pass including performance benchmark (run uv run pytest tests/unit/test_health.py -k status tests/integration/test_health_integration.py -k status tests/benchmarks/test_health_performance.py)

**Checkpoint**: User Story 3 complete - real-time pool status queries work independently with <50ms latency

---

## Phase 6: User Story 4 - Health Check Customization (Priority: P2)

**Goal**: Users can customize health check behavior (timeout, target URL, expected response)

**Independent Test**: Configure custom check URL, timeout, and expected status codes, verify health checks use specified parameters

### Tests for User Story 4 (TDD - Write FIRST)

- [ ] T056 [P] [US4] Create test_health_config.py with unit tests for custom check_url configuration in tests/unit/test_health_config.py
- [ ] T057 [P] [US4] Create test_health_config.py with unit tests for custom timeout configuration (check_timeout_seconds validation) in tests/unit/test_health_config.py
- [ ] T058 [P] [US4] Create test_health_config.py with unit tests for expected_status_codes configuration (list of integers, default [200]) in tests/unit/test_health_config.py
- [ ] T059 [P] [US4] Create test_health.py with unit tests for check_proxy() using custom URL (verify HTTP HEAD sent to custom URL) in tests/unit/test_health.py
- [ ] T060 [P] [US4] Create test_health.py with unit tests for check_proxy() respecting custom timeout in tests/unit/test_health.py
- [ ] T061 [P] [US4] Create test_health.py with unit tests for response validation against expected_status_codes in tests/unit/test_health.py

### Implementation for User Story 4

- [ ] T062 [US4] Update HealthChecker.check_proxy() in proxywhirl/health.py to use config.check_url instead of hardcoded URL
- [ ] T063 [US4] Update HealthChecker.check_proxy() in proxywhirl/health.py to use config.check_timeout_seconds for httpx timeout
- [ ] T064 [US4] Update HealthChecker.check_proxy() in proxywhirl/health.py to validate response status_code against config.expected_status_codes
- [ ] T065 [US4] Add URL validator in HealthCheckConfig in proxywhirl/health_models.py (must be valid http/https URL)
- [ ] T066 [US4] Verify all US4 tests pass (run uv run pytest tests/unit/test_health_config.py tests/unit/test_health.py -k custom)

**Checkpoint**: User Story 4 complete - health check customization works independently

---

## Phase 7: User Story 5 - Automatic Proxy Recovery (Priority: P2)

**Goal**: Unhealthy proxies automatically retried after exponential backoff cooldown

**Independent Test**: Mark proxy unhealthy, wait for cooldown, verify recovery check attempted and proxy restored on success

### Tests for User Story 5 (TDD - Write FIRST)

- [ ] T067 [P] [US5] Create test_health.py with unit tests for exponential backoff calculation (cooldown doubles on each retry) in tests/unit/test_health.py
- [ ] T068 [P] [US5] Create test_health.py with unit tests for recovery attempt tracking (recovery_attempt increments, resets on success) in tests/unit/test_health.py
- [ ] T069 [P] [US5] Create test_health.py with unit tests for max recovery attempts (PERMANENTLY_FAILED after max retries) in tests/unit/test_health.py
- [ ] T070 [P] [US5] Create test_health.py with unit tests for recovery cooldown scheduling (next_check_time calculated correctly) in tests/unit/test_health.py
- [ ] T071 [P] [US5] Create test_health_recovery.py with integration test for full recovery flow (unhealthy → recovering → checking → healthy) in tests/integration/test_health_recovery.py
- [ ] T072 [P] [US5] Create test_health_recovery.py with integration test for permanent failure after max retries in tests/integration/test_health_recovery.py

### Implementation for User Story 5

- [ ] T073 [US5] Implement exponential backoff calculation in proxywhirl/health.py (_calculate_recovery_cooldown method: base * 2^attempt)
- [ ] T074 [US5] Update _update_health_status in proxywhirl/health.py to mark proxy as RECOVERING and schedule recovery check
- [ ] T075 [US5] Implement recovery check logic in proxywhirl/health.py (_attempt_recovery method: run check, update status, reset or increment attempt)
- [ ] T076 [US5] Modify HealthWorker in proxywhirl/health_worker.py to respect next_check_time for recovery scheduling
- [ ] T077 [US5] Implement permanent failure logic in proxywhirl/health.py (mark PERMANENTLY_FAILED after max_recovery_attempts)
- [ ] T078 [US5] Add recovery_attempt field updates in check_proxy() in proxywhirl/health.py (increment on failure, reset on success)
- [ ] T079 [US5] Verify all US5 tests pass (run uv run pytest tests/unit/test_health.py -k recovery tests/integration/test_health_recovery.py)

**Checkpoint**: User Story 5 complete - automatic proxy recovery with exponential backoff works independently

---

## Phase 8: User Story 6 - Health Event Notifications (Priority: P3)

**Goal**: Operations team receives notifications when significant health events occur

**Independent Test**: Register event callback, trigger health events (proxy down, recovered, pool degraded), verify callback invoked with correct event data

### Tests for User Story 6 (TDD - Write FIRST)

- [ ] T080 [P] [US6] Create test_health_models.py with unit tests for HealthEvent model (event_type validation, timestamp, metadata) in tests/unit/test_health_models.py
- [ ] T081 [P] [US6] Create test_health.py with unit tests for event callback registration (on_event parameter in __init__) in tests/unit/test_health.py
- [ ] T082 [P] [US6] Create test_health.py with unit tests for proxy_down event emission (triggered when proxy marked unhealthy) in tests/unit/test_health.py
- [ ] T083 [P] [US6] Create test_health.py with unit tests for proxy_recovered event emission (triggered when unhealthy proxy passes check) in tests/unit/test_health.py
- [ ] T084 [P] [US6] Create test_health.py with unit tests for pool_degraded event emission (triggered when health_percentage < 50%) in tests/unit/test_health.py
- [ ] T085 [P] [US6] Create test_health.py with unit tests for pool_recovered event emission (triggered when health returns to normal) in tests/unit/test_health.py
- [ ] T086 [P] [US6] Create test_health_integration.py with integration test for event notification flow (end-to-end event triggering) in tests/integration/test_health_integration.py

### Implementation for User Story 6

- [ ] T087 [P] [US6] Implement HealthEvent model in proxywhirl/health_models.py (event_type, proxy_url, timestamp, previous_status, new_status, failure_count, metadata fields with validators)
- [ ] T088 [US6] Implement _emit_event helper in proxywhirl/health.py (create HealthEvent, log via loguru, call on_event callback if registered)
- [ ] T089 [US6] Update _update_health_status in proxywhirl/health.py to emit proxy_down event when marking unhealthy
- [ ] T090 [US6] Update _attempt_recovery in proxywhirl/health.py to emit proxy_recovered event on successful recovery
- [ ] T091 [US6] Update get_pool_status in proxywhirl/health.py to detect and emit pool_degraded/pool_recovered events
- [ ] T092 [US6] Add structured logging for all health events in proxywhirl/health.py (loguru with extra fields)
- [ ] T093 [US6] Verify all US6 tests pass (run uv run pytest tests/unit/test_health.py -k event tests/integration/test_health_integration.py -k event)

**Checkpoint**: User Story 6 complete - health event notifications work independently

---

## Phase 9: Additional Core Features

**Purpose**: Remaining core features from contracts and requirements

- [ ] T094 [P] Implement HealthChecker.pause() in proxywhirl/health.py (set _paused flag, workers check flag before checks)
- [ ] T095 [P] Implement HealthChecker.resume() in proxywhirl/health.py (clear _paused flag, resume checks)
- [ ] T096 [P] Implement HealthChecker.get_health_history() in proxywhirl/health.py (query health_history table, return list[HealthCheckResult] for last N hours)
- [ ] T097 [P] Implement history retention cleanup in proxywhirl/health.py (DELETE old records based on config.history_retention_hours)
- [ ] T098 [P] Add thread-safe access to all shared state in proxywhirl/health.py (verify all mutable state protected by RLock)
- [ ] T099 Implement graceful degradation in proxywhirl/health.py (catch exceptions in worker threads, log errors, continue operation)

---

## Phase 10: Property-Based Tests & Performance Validation

**Purpose**: Advanced testing for invariants and performance requirements

- [ ] T100 [P] Create test_health_properties.py with Hypothesis tests for health status state machine (valid transitions only) in tests/property/test_health_properties.py
- [ ] T101 [P] Create test_health_properties.py with Hypothesis tests for failure count invariants (monotonic until reset) in tests/property/test_health_properties.py
- [ ] T102 [P] Create test_health_properties.py with Hypothesis tests for pool status integrity (counts sum to total) in tests/property/test_health_properties.py
- [ ] T103 [P] Create test_health_properties.py with Hypothesis tests for exponential backoff monotonicity in tests/property/test_health_properties.py
- [ ] T104 [P] Create test_health_performance.py with benchmark for SC-001 (dead proxy detection <1 minute) in tests/benchmarks/test_health_performance.py
- [ ] T105 [P] Create test_health_performance.py with benchmark for SC-003 (CPU overhead <5%) in tests/benchmarks/test_health_performance.py
- [ ] T106 [P] Create test_health_performance.py with benchmark for SC-006 (1000 concurrent checks) in tests/benchmarks/test_health_performance.py
- [ ] T107 [P] Create test_health_performance.py with benchmark for SC-007 (false positive rate <1%) in tests/benchmarks/test_health_performance.py
- [ ] T108 [P] Create test_health_performance.py with benchmark for SC-010 (10k proxies in 5 minutes) in tests/benchmarks/test_health_performance.py

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T109 [P] Add comprehensive docstrings to all public methods in proxywhirl/health.py (following Google style)
- [ ] T110 [P] Add comprehensive docstrings to all models in proxywhirl/health_models.py
- [ ] T111 [P] Update proxywhirl/__init__.py to export all public health monitoring APIs
- [ ] T112 Verify mypy --strict compliance for all health monitoring modules (run uv run mypy --strict proxywhirl/health*.py)
- [ ] T113 Verify ruff compliance for all health monitoring modules (run uv run ruff check proxywhirl/health*.py)
- [ ] T114 Run full test suite and verify 85%+ coverage (run uv run pytest tests/ --cov=proxywhirl --cov-report=term-missing)
- [ ] T115 Validate quickstart.md examples (manually run all code examples from quickstart.md)
- [ ] T116 Update main README.md with health monitoring usage section
- [ ] T117 Update CHANGELOG.md with health monitoring feature details
- [ ] T118 Final constitution compliance check (verify all 7 principles still pass)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-8)**: All depend on Foundational phase completion
  - US1 (P1): Can start after Phase 2 - No dependencies on other stories
  - US2 (P1): Can start after Phase 2 - No dependencies (but extends US1 config)
  - US3 (P2): Can start after Phase 2 - Works independently but uses US1 health checks
  - US4 (P2): Can start after Phase 2 - Extends US1 check_proxy() method
  - US5 (P2): Can start after Phase 2 - Extends US1 health status updates
  - US6 (P3): Can start after Phase 2 - Works independently, notifies about US1-US5 events
- **Additional Features (Phase 9)**: Can run after Phase 2, independent of user stories
- **Property Tests (Phase 10)**: Can run in parallel with implementation (continuous validation)
- **Polish (Phase 11)**: Depends on all desired user stories being complete

### User Story Independence

Each user story is designed to be independently testable:

- **US1**: Background checks work without any other stories
- **US2**: Interval configuration works without requiring US3-US6
- **US3**: Status queries work even if US2, US4, US5, US6 not implemented
- **US4**: Custom URLs work even if US2, US3, US5, US6 not implemented
- **US5**: Recovery works even if US2, US3, US4, US6 not implemented
- **US6**: Notifications work for any implemented stories

### Within Each User Story

1. Tests MUST be written FIRST and verified to FAIL
2. Models before services/logic
3. Core implementation before integration
4. Verify all tests pass before moving to next story

### Parallel Opportunities

**Setup (Phase 1)**: T002, T003, T004 can run in parallel

**Foundational (Phase 2)**: T006, T007, T010 can run in parallel after T005 completes

**User Story Tests**: All test tasks within a story marked [P] can run in parallel (different test files)

**User Story Implementation**: All implementation tasks within a story marked [P] can run in parallel (different source files)

**Between User Stories**: Once Foundational completes, all 6 user stories (Phases 3-8) can be worked on in parallel by different developers

---

## Parallel Example: User Story 1

```bash
# Phase 1: All tests for User Story 1 can be written in parallel:
T011 [P] [US1] test_health_models.py (HealthStatus enum tests)
T012 [P] [US1] test_health_models.py (HealthCheckResult tests)
T013 [P] [US1] test_health_models.py (HealthCheckConfig tests)
T014 [P] [US1] test_health.py (HealthChecker.__init__ tests)
T015 [P] [US1] test_health.py (add_proxy tests)
T016 [P] [US1] test_health.py (check_proxy tests)
# ... etc (all [P] test tasks)

# Phase 2: Model implementations can run in parallel:
T022 [P] [US1] health_models.py (HealthStatus enum)
T023 [P] [US1] health_models.py (HealthCheckResult model)
T024 [P] [US1] health_models.py (HealthCheckConfig model)

# Remaining US1 tasks are sequential (depend on previous completions)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Background health checks)
4. **STOP and VALIDATE**: Test US1 independently (dead proxy detection works)
5. Deploy/demo basic health monitoring

**Rationale**: US1 provides core value - automatic dead proxy detection. This is a functional MVP that solves the primary problem.

### Incremental Delivery (Recommended Order)

1. **Foundation**: Phases 1-2 → Health infrastructure ready
2. **MVP**: Phase 3 (US1) → Background health checks working → Deploy/Demo
3. **Enhancement**: Phase 4 (US2) → Per-source intervals → Deploy/Demo
4. **Visibility**: Phase 5 (US3) → Pool status queries → Deploy/Demo
5. **Flexibility**: Phase 6 (US4) → Custom check params → Deploy/Demo
6. **Resilience**: Phase 7 (US5) → Auto recovery → Deploy/Demo
7. **Observability**: Phase 8 (US6) → Event notifications → Deploy/Demo
8. **Completion**: Phases 9-11 → Additional features, validation, polish

Each phase adds incremental value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers (after Phase 2 completes):

- **Developer A**: US1 (P1) - Core health checks
- **Developer B**: US2 (P1) - Interval configuration
- **Developer C**: US3 (P2) - Status queries
- **Developer D**: US4 (P2) - Customization
- **Developer E**: US5 (P2) - Recovery
- **Developer F**: US6 (P3) - Notifications

All stories integrate cleanly via the foundational infrastructure (Phase 2).

---

## Task Summary

**Total Tasks**: 118 tasks

**By Phase**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 6 tasks
- Phase 3 (US1): 24 tasks (11 tests + 13 implementation)
- Phase 4 (US2): 8 tasks (3 tests + 5 implementation)
- Phase 5 (US3): 12 tasks (6 tests + 6 implementation)
- Phase 6 (US4): 11 tasks (6 tests + 5 implementation)
- Phase 7 (US5): 13 tasks (6 tests + 7 implementation)
- Phase 8 (US6): 14 tasks (7 tests + 7 implementation)
- Phase 9 (Additional): 6 tasks
- Phase 10 (Property/Performance): 9 tasks
- Phase 11 (Polish): 10 tasks

**Parallel Opportunities**: 65 tasks marked [P] can run in parallel (55% of total)

**Independent Test Criteria**:
- US1: Dead proxies detected and marked unhealthy
- US2: Different sources checked at different intervals
- US3: Pool status queries return accurate real-time data
- US4: Custom check URLs and timeouts respected
- US5: Unhealthy proxies automatically recover after cooldown
- US6: Health events trigger notifications

**MVP Scope**: Phases 1-3 (34 tasks) deliver functional health monitoring

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- TDD strictly enforced: Write tests FIRST, verify they FAIL, then implement
- Each user story is independently testable and deployable
- Constitution compliance verified throughout (mypy --strict, ruff, 85%+ coverage)
- Performance benchmarks (SC-001 to SC-010) validated in Phase 10
- All 118 tasks use exact file paths for clarity
