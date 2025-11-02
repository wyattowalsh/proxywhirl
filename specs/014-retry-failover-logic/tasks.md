# Tasks: Advanced Retry and Failover Logic

**Feature**: 014-retry-failover-logic  
**Input**: Design documents from `/specs/014-retry-failover-logic/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/retry-api.yaml ✅, quickstart.md ✅

**Tests**: Following Test-First Development (Constitution Principle II) - tests written BEFORE implementation

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create retry package structure per plan.md (add retry_policy.py, circuit_breaker.py, retry_executor.py, retry_metrics.py to proxywhirl/)
- [ ] T002 Verify tenacity>=8.2.0 dependency exists in pyproject.toml (already present per plan.md)
- [ ] T003 [P] Add RetryPolicy, CircuitBreaker, RetryMetrics exports to proxywhirl/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create RetryPolicy Pydantic models in proxywhirl/retry_policy.py (BackoffStrategy enum, RetryPolicy model with 9 parameters per data-model.md)
- [ ] T005 Create CircuitBreakerState enum and CircuitBreaker Pydantic model in proxywhirl/circuit_breaker.py (state machine with CLOSED/OPEN/HALF_OPEN states per data-model.md)
- [ ] T006 Create RetryAttempt and RetryMetrics models in proxywhirl/retry_metrics.py (metrics collection infrastructure per data-model.md)
- [ ] T007 Add retry-specific API models to proxywhirl/api_models.py (RetryPolicyRequest, RetryPolicyResponse, CircuitBreakerResponse per contracts/retry-api.yaml)
- [ ] T008 Create test fixtures for RetryPolicy and CircuitBreaker in tests/unit/conftest.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Automatic Request Retry with Exponential Backoff (Priority: P1) 🎯 MVP

**Goal**: Implement automatic retry with exponential backoff for failed requests, improving success rates for transient failures

**Independent Test**: Send requests through a proxy that intermittently fails, verify automatic retries with increasing delays (1s, 2s, 4s), confirm eventual success or max retry limit

### Tests for User Story 1 (Test-First - Write BEFORE Implementation)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T009 [P] [US1] Unit test RetryPolicy.calculate_delay() method in tests/unit/test_retry_policy.py (verify exponential, linear, fixed backoff calculations)
- [ ] T010 [P] [US1] Unit test RetryPolicy validation in tests/unit/test_retry_policy.py (test Pydantic validators for status codes, max_attempts range)
- [ ] T011 [P] [US1] Property test backoff timing with Hypothesis in tests/property/test_retry_timing_properties.py (verify delays never exceed max_backoff_delay, jitter bounds)
- [ ] T012 [P] [US1] Integration test retry execution with mock httpx client in tests/integration/test_retry_integration.py (simulate 5xx errors, verify retry attempts and delays)
- [ ] T013 [P] [US1] Integration test max_attempts enforcement in tests/integration/test_retry_integration.py (verify stops after configured max_attempts)

### Implementation for User Story 1

- [ ] T014 [US1] Implement RetryExecutor class in proxywhirl/retry_executor.py (tenacity integration, retry orchestration per research.md decision)
- [ ] T015 [US1] Add retry logic to ProxyRotator.request() method in proxywhirl/rotator.py (integrate RetryExecutor, check retry_policy parameter)
- [ ] T016 [US1] Implement backoff delay calculation with jitter support in proxywhirl/retry_policy.py (calculate_delay method per data-model.md: if jitter enabled, multiply delay by random.uniform(0.5, 1.5))
- [ ] T017 [US1] Add retry attempt logging with loguru in proxywhirl/retry_executor.py (log attempt number, proxy used, delay, outcome)
- [ ] T018 [US1] Implement timeout handling in proxywhirl/retry_executor.py (respect total request timeout, cancel remaining retries if exceeded per FR-010)
- [ ] T019 [US1] Add error classification in proxywhirl/retry_executor.py (retryable vs non-retryable errors per FR-011)

**Checkpoint**: At this point, automatic retries with exponential backoff should be fully functional and testable independently

---

## Phase 4: User Story 2 - Circuit Breaker Pattern for Failed Proxies (Priority: P1) 🎯 MVP

**Goal**: Implement circuit breaker pattern to temporarily remove failing proxies from rotation, preventing cascading failures

**Independent Test**: Configure a proxy to fail consistently, verify circuit breaker opens after threshold failures (5 in 60s), confirm proxy removal from rotation, observe half-open recovery tests after 30s timeout

### Tests for User Story 2 (Test-First - Write BEFORE Implementation)

- [ ] T020 [P] [US2] Unit test CircuitBreaker.record_failure() in tests/unit/test_circuit_breaker.py (verify failure count, rolling window cleanup)
- [ ] T021 [P] [US2] Unit test CircuitBreaker state transitions in tests/unit/test_circuit_breaker.py (CLOSED→OPEN, OPEN→HALF_OPEN, HALF_OPEN→CLOSED, HALF_OPEN→OPEN)
- [ ] T022 [P] [US2] Unit test CircuitBreaker.should_attempt_request() in tests/unit/test_circuit_breaker.py (verify returns correct availability based on state)
- [ ] T023 [P] [US2] Property test circuit breaker state machine with Hypothesis in tests/property/test_circuit_breaker_properties.py (generate random failure/success sequences, verify invariants)
- [ ] T024 [P] [US2] Concurrency test for CircuitBreaker thread safety in tests/unit/test_circuit_breaker_concurrency.py (simulate 1000+ concurrent requests, verify no race conditions per SC-008)
- [ ] T025 [P] [US2] Integration test circuit breaker prevents cascading failures in tests/integration/test_circuit_breaker_integration.py (verify OPEN proxies excluded from rotation)
- [ ] T025b [P] [US2] Integration test half-open health checks in tests/integration/test_circuit_breaker_integration.py (verify FR-006: proxy tested once in half-open, transitions to closed on success or reopens on failure)

### Implementation for User Story 2

- [ ] T026 [US2] Implement CircuitBreaker state machine methods in proxywhirl/circuit_breaker.py (record_failure, record_success, should_attempt_request with threading.Lock per research.md)
- [ ] T027 [US2] Implement rolling window failure tracking in proxywhirl/circuit_breaker.py (collections.deque with timestamp filtering per research.md decision)
- [ ] T028 [US2] Add circuit breaker state transition logic in proxywhirl/circuit_breaker.py (_transition_to_open, _transition_to_half_open, _transition_to_closed)
- [ ] T029 [US2] Integrate CircuitBreaker with ProxyRotator in proxywhirl/rotator.py (create circuit breakers per proxy, filter OPEN proxies in _select_proxy())
- [ ] T030 [US2] Implement circuit breaker reset on system restart in proxywhirl/rotator.py (__init__ method initializes all circuit breakers to CLOSED per FR-021)
- [ ] T031 [US2] Add circuit breaker event recording to RetryMetrics in proxywhirl/retry_metrics.py (record_circuit_breaker_event method: CircuitBreakerEvent with proxy_id, from_state, to_state, timestamp, failure_count per data-model.md)
- [ ] T032 [US2] Implement all-circuit-breakers-open detection in proxywhirl/rotator.py (return 503 Service Temporarily Unavailable per FR-019)
- [ ] T032b [P] [US2] Integration test widespread failure detection in tests/integration/test_circuit_breaker_integration.py (verify FR-019: all proxies failing returns 503 immediately without exhausting retries)

**Checkpoint**: At this point, circuit breakers should automatically exclude failing proxies and allow recovery tests

---

## Phase 5: User Story 3 - Intelligent Proxy Failover Selection (Priority: P2)

**Goal**: Implement intelligent proxy selection for retries based on performance metrics, improving retry success rates

**Independent Test**: Simulate proxy failures with varying success rates (95%, 60%), verify system preferentially selects better-performing proxies for retries, measure improved retry success rates vs random selection

### Tests for User Story 3 (Test-First - Write BEFORE Implementation)

- [ ] T033 [P] [US3] Unit test intelligent proxy selection algorithm in tests/unit/test_retry_executor.py (verify excludes failed proxy, prioritizes high success rate)
- [ ] T034 [P] [US3] Integration test performance-based selection in tests/integration/test_intelligent_failover.py (compare retry success rate against random selection baseline)
- [ ] T035 [P] [US3] Integration test geo-targeting awareness in tests/integration/test_intelligent_failover.py (verify region-aware proxy selection for geo-targeted requests)

### Implementation for User Story 3

- [ ] T036 [US3] Implement proxy performance scoring in proxywhirl/retry_executor.py (calculate score based on recent success rate, exclude failed proxy per FR-007)
- [ ] T037 [US3] Add intelligent proxy selection to RetryExecutor in proxywhirl/retry_executor.py (_select_retry_proxy method prioritizes high-scoring proxies)
- [ ] T038 [US3] Integrate with existing rotation strategies in proxywhirl/rotator.py (call RetryExecutor._select_retry_proxy during retry attempts)
- [ ] T039 [US3] Add performance metrics tracking to RetryMetrics in proxywhirl/retry_metrics.py (track success rates per proxy for scoring)

**Checkpoint**: At this point, retries should intelligently select better-performing proxies

---

## Phase 6: User Story 4 - Configurable Retry Policies (Priority: P2)

**Goal**: Allow users to configure retry behavior globally and per-request, enabling fine-tuning for different use cases

**Independent Test**: Configure different retry policies (max_attempts=5, linear backoff, custom status codes), send test requests with each policy, verify behavior matches configuration

### Tests for User Story 4 (Test-First - Write BEFORE Implementation)

- [ ] T040 [P] [US4] Unit test per-request policy override in tests/unit/test_retry_executor.py (verify per-request policy takes precedence over global)
- [ ] T041 [P] [US4] Unit test retry_non_idempotent flag in tests/unit/test_retry_executor.py (verify POST/PUT skipped unless explicitly enabled per FR-018)
- [ ] T042 [P] [US4] Integration test custom status codes in tests/integration/test_retry_policy_config.py (verify only configured codes trigger retries)
- [ ] T043 [P] [US4] Integration test backoff strategy variants in tests/integration/test_retry_policy_config.py (verify exponential, linear, fixed all work correctly)

### Implementation for User Story 4

- [ ] T044 [US4] Add global retry policy configuration to ProxyRotator in proxywhirl/rotator.py (__init__ accepts retry_policy parameter per plan.md)
- [ ] T045 [US4] Implement per-request policy override in proxywhirl/rotator.py (request() method accepts retry_policy parameter per FR-008)
- [ ] T046 [US4] Add non-idempotent request handling in proxywhirl/retry_executor.py (check HTTP method, respect retry_non_idempotent flag per FR-018)
- [ ] T047 [US4] Implement configurable status code filtering in proxywhirl/retry_executor.py (only retry on configured status codes per FR-017)
- [ ] T048 [US4] Add backoff strategy variants to RetryPolicy in proxywhirl/retry_policy.py (support exponential, linear, fixed with parameters per FR-012)

**Checkpoint**: At this point, users can customize retry behavior without code changes

---

## Phase 7: User Story 5 - Retry Metrics and Observability (Priority: P3)

**Goal**: Track and expose detailed retry metrics for monitoring, optimization, and troubleshooting

**Independent Test**: Generate various failure scenarios, collect retry metrics, verify accurate reporting of retry counts, success rates by attempt, latency distributions, and circuit breaker events

### Tests for User Story 5 (Test-First - Write BEFORE Implementation)

- [ ] T049 [P] [US5] Unit test RetryMetrics.record_attempt() in tests/unit/test_retry_metrics.py (verify attempt recording, deque trimming)
- [ ] T050 [P] [US5] Unit test RetryMetrics.aggregate_hourly() in tests/unit/test_retry_metrics.py (verify hourly aggregation logic, 24h retention)
- [ ] T051 [P] [US5] Unit test RetryMetrics.get_summary() in tests/unit/test_retry_metrics.py (verify metrics summary calculation)
- [ ] T052 [P] [US5] Benchmark test metrics API response time in tests/benchmarks/test_retry_performance.py (verify <100ms for 24h queries per SC-007)
- [ ] T053 [P] [US5] Integration test REST API metrics endpoints in tests/integration/test_api_retry.py (verify GET /api/v1/metrics/retries returns correct data)

### Implementation for User Story 5

- [ ] T054 [US5] Implement RetryMetrics collection in proxywhirl/retry_metrics.py (record_attempt, record_circuit_breaker_event with threading.Lock per data-model.md)
- [ ] T055 [US5] Implement hourly aggregation in proxywhirl/retry_metrics.py (aggregate_hourly method with 24h retention per data-model.md)
- [ ] T056 [US5] Add metrics query methods in proxywhirl/retry_metrics.py (get_summary, get_timeseries, get_by_proxy per contracts/retry-api.yaml)
- [ ] T057 [US5] Integrate RetryMetrics with RetryExecutor in proxywhirl/retry_executor.py (create RetryAttempt records on each retry)
- [ ] T058 [US5] Add periodic aggregation scheduler in proxywhirl/rotator.py (use threading.Timer to call aggregate_hourly every 5 minutes, started in __init__, cancelled in __exit__)

**Checkpoint**: At this point, retry metrics should be collected and queryable

---

## Phase 8: REST API Integration

**Purpose**: Expose retry/circuit breaker functionality via REST API endpoints

- [ ] T059 [P] Implement GET /api/v1/retry/policy endpoint in proxywhirl/api.py (return current global retry policy per contracts/retry-api.yaml)
- [ ] T060 [P] Implement PUT /api/v1/retry/policy endpoint in proxywhirl/api.py (update global retry policy per contracts/retry-api.yaml)
- [ ] T061 [P] Implement GET /api/v1/circuit-breakers endpoint in proxywhirl/api.py (list all circuit breaker states per contracts/retry-api.yaml)
- [ ] T062 [P] Implement GET /api/v1/circuit-breakers/{proxyId} endpoint in proxywhirl/api.py (get specific circuit breaker state per contracts/retry-api.yaml)
- [ ] T063 [P] Implement POST /api/v1/circuit-breakers/{proxyId}/reset endpoint in proxywhirl/api.py (manually reset circuit breaker per contracts/retry-api.yaml)
- [ ] T064 [P] Implement GET /api/v1/circuit-breakers/metrics endpoint in proxywhirl/api.py (circuit breaker events per contracts/retry-api.yaml)
- [ ] T065 [P] Implement GET /api/v1/metrics/retries endpoint in proxywhirl/api.py (retry metrics summary per contracts/retry-api.yaml)
- [ ] T066 [P] Implement GET /api/v1/metrics/retries/timeseries endpoint in proxywhirl/api.py (time-series retry data per contracts/retry-api.yaml)
- [ ] T067 [P] Implement GET /api/v1/metrics/retries/by-proxy endpoint in proxywhirl/api.py (per-proxy retry statistics per contracts/retry-api.yaml)
- [ ] T068 [P] Add OpenAPI documentation for retry endpoints in proxywhirl/api.py (integrate retry-api.yaml spec)

---

## Phase 9: Documentation & Examples

**Purpose**: User-facing documentation and example code

- [ ] T069 [P] Create retry examples in examples/retry_examples.py (demonstrate quickstart.md scenarios: basic retry, custom policy, per-request override)
- [ ] T070 [P] Update main README.md with retry feature overview (link to quickstart.md, highlight key capabilities)
- [ ] T071 [P] Validate quickstart.md examples work (run all code examples, verify outputs match descriptions)
- [ ] T072 [P] Add retry/circuit breaker troubleshooting guide to docs/RETRY_FAILOVER_GUIDE.md (common issues, solutions per quickstart.md)

---

## Phase 10: Performance & Quality Assurance

**Purpose**: Verify performance requirements and final quality checks

- [ ] T073 Benchmark circuit breaker state transitions in tests/benchmarks/test_retry_performance.py (verify <1 second per SC-004)
- [ ] T074 Load test with 1000+ concurrent requests in tests/benchmarks/test_retry_performance.py (verify no performance degradation per SC-006)
- [ ] T075 Benchmark retry metrics API queries in tests/benchmarks/test_retry_performance.py (verify <100ms for 24h queries per SC-007)
- [ ] T076 Run full test suite with uv run pytest tests/ --cov=proxywhirl (verify 85%+ coverage, 100% for circuit breaker per constitution)
- [ ] T077 Run type checking with uv run mypy --strict proxywhirl/ (verify 0 errors per constitution)
- [ ] T078 Run linting with uv run ruff check proxywhirl/ (verify 0 errors per constitution)
- [ ] T079 Validate backward compatibility with existing ProxyRotator tests (verify all existing tests pass without modification per FR-020)
- [ ] T080 Memory profiling for 24h metrics retention (verify <100MB for 10k req/hour workload per plan.md constraint)
- [ ] T080b Measure request success rate improvement in tests/benchmarks/test_retry_performance.py (verify SC-001: 15% improvement for transient failures vs single-attempt baseline)
- [ ] T080c Measure wasted retry reduction in tests/benchmarks/test_retry_performance.py (verify SC-002: 80% reduction in retries on proxies with >70% failure rate)
- [ ] T080d Measure retry attempt distribution in tests/benchmarks/test_retry_performance.py (verify SC-010: 90% of successful requests complete within 2 retry attempts)

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting multiple components

- [ ] T081 Add retry/circuit breaker metrics to existing monitoring in proxywhirl/rotator.py (integrate with feature 008 metrics if available)
- [ ] T082 Security audit: verify no credentials in retry logs/metrics in proxywhirl/retry_executor.py and proxywhirl/retry_metrics.py (constitution principle VI)
- [ ] T083 Update CHANGELOG.md with retry feature release notes (follow keep-a-changelog format)
- [ ] T084 Update constitution compliance report in .specify/memory/ (verify all 7 gates still pass)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (P1): Retry logic foundation
  - US2 (P1): Circuit breakers (can start after Foundational, parallel with US1 if staffed)
  - US3 (P2): Depends on US1 (needs retry execution framework), can be parallel with US2
  - US4 (P2): Depends on US1 (extends retry framework), can be parallel with US2/US3
  - US5 (P3): Depends on US1, US2 (needs retry and circuit breaker events)
- **REST API (Phase 8)**: Depends on US1-US5 completion
- **Documentation (Phase 9)**: Can start once US1 is complete (for basic examples), full completion needs US1-US5
- **Performance (Phase 10)**: Depends on US1-US2 completion (core functionality)
- **Polish (Phase 11)**: Depends on all phases

### Critical Path (Minimum for MVP)

1. Phase 1: Setup → 2. Phase 2: Foundational → 3. Phase 3: US1 (Retry) → 4. Phase 4: US2 (Circuit Breaker)

**This is the minimum viable product** - automatic retries with circuit breaker protection.

### Full Feature Completion Order

1. Setup (Phase 1)
2. Foundational (Phase 2) ← BLOCKING
3. US1 (Phase 3) + US2 (Phase 4) in parallel ← MVP Complete
4. US3 (Phase 5) + US4 (Phase 6) in parallel
5. US5 (Phase 7)
6. REST API (Phase 8)
7. Documentation (Phase 9) + Performance (Phase 10) in parallel
8. Polish (Phase 11)

### Parallel Opportunities

**Within Phases**:

- Phase 1: T001, T003 can run in parallel
- Phase 2: All tasks are sequential (each builds foundation for next)
- Phase 3 (US1): T009-T013 (tests) all parallel, then T014-T019 (implementation)
- Phase 4 (US2): T020-T025b (tests) all parallel, then T026-T032b (implementation)
- Phase 5 (US3): T033-T035 (tests) all parallel, then T036-T039 (implementation)
- Phase 6 (US4): T040-T043 (tests) all parallel, then T044-T048 (implementation)
- Phase 7 (US5): T049-T053 (tests) all parallel, then T054-T058 (implementation)
- Phase 8: T059-T068 (API endpoints) all parallel
- Phase 9: T069-T072 (docs) all parallel
- Phase 10: T073, T074, T075 can run in parallel; then T076-T080d sequential

**Across User Stories** (with sufficient team capacity):

- After Phase 2: US1 (Phase 3) and US2 (Phase 4) can proceed in parallel
- After US1 complete: US3 (Phase 5) and US4 (Phase 6) can proceed in parallel
- US5 (Phase 7) requires US1 and US2 complete

---

## Parallel Example: User Story 1 (Retry Logic)

```bash
# Step 1: Launch all tests together (Test-First approach):
Parallel: T009 (unit test calculate_delay), T010 (unit test validation), 
          T011 (property test timing), T012 (integration test retry execution), 
          T013 (integration test max_attempts)

# Step 2: After tests written and FAILING, launch implementation:
Sequential: T014 (RetryExecutor) → T015 (integrate with rotator) → 
            T016 (backoff calculation) → T017 (logging) → 
            T018 (timeout handling) → T019 (error classification)

# Verify: All tests now PASS
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only) - RECOMMENDED

**Goal**: Get core retry and circuit breaker functionality working and deployed

1. ✅ Complete Phase 1: Setup (3 tasks)
2. ✅ Complete Phase 2: Foundational (5 tasks) - CRITICAL BLOCKER
3. ✅ Complete Phase 3: User Story 1 - Retry Logic (11 tasks)
4. ✅ Complete Phase 4: User Story 2 - Circuit Breaker (15 tasks)
5. **STOP and VALIDATE**: Test retry + circuit breaker independently
6. Run benchmarks: T073, T074, T075 (verify SC-004, SC-006, SC-007)
7. Deploy/demo MVP

**MVP Scope**: 34 tasks for core retry and failover protection

### Incremental Delivery (Add Features Progressively)

After MVP (US1 + US2) is validated:

1. Add User Story 3: Intelligent Selection (7 tasks) → Test independently → Deploy
2. Add User Story 4: Configurable Policies (9 tasks) → Test independently → Deploy  
3. Add User Story 5: Metrics & Observability (10 tasks) → Test independently → Deploy
4. Add REST API Integration (10 tasks) → Test → Deploy
5. Complete Documentation + Performance + Polish (18 tasks)

**Full Feature**: 89 tasks total

### Parallel Team Strategy

With multiple developers after Foundational phase complete:

- **Developer A**: User Story 1 (Phase 3) - Retry logic
- **Developer B**: User Story 2 (Phase 4) - Circuit breakers (parallel with A)
- **Code Review & Merge**: Integrate US1 + US2
- **Developer A**: User Story 3 (Phase 5) - Intelligent selection
- **Developer B**: User Story 4 (Phase 6) - Configuration (parallel with A)
- **Developer C**: User Story 5 (Phase 7) - Metrics
- **All**: REST API + Documentation + Performance + Polish

---

## Task Estimation Summary

**Total Tasks**: 89

**By Phase**:

- Phase 1 (Setup): 3 tasks
- Phase 2 (Foundational): 5 tasks
- Phase 3 (US1 - Retry): 11 tasks (5 tests + 6 impl)
- Phase 4 (US2 - Circuit Breaker): 15 tasks (7 tests + 8 impl)
- Phase 5 (US3 - Intelligent Selection): 7 tasks (3 tests + 4 impl)
- Phase 6 (US4 - Configuration): 9 tasks (4 tests + 5 impl)
- Phase 7 (US5 - Metrics): 10 tasks (5 tests + 5 impl)
- Phase 8 (REST API): 10 tasks
- Phase 9 (Documentation): 4 tasks
- Phase 10 (Performance): 11 tasks
- Phase 11 (Polish): 4 tasks

**By User Story**:

- US1 (P1 - Retry): 11 tasks
- US2 (P1 - Circuit Breaker): 15 tasks
- US3 (P2 - Intelligent Selection): 7 tasks
- US4 (P2 - Configuration): 9 tasks
- US5 (P3 - Metrics): 10 tasks
- Infrastructure + Polish: 37 tasks

**MVP Scope** (US1 + US2): 34 tasks (38% of total)  
**Full Feature**: 89 tasks (100%)

**Parallelizable Tasks**: 48 tasks marked [P] (54% of total)

**Independent Test Criteria**:

- US1: Send requests through intermittently-failing proxy, verify retries with delays
- US2: Configure failing proxy, verify circuit opens, proxy excluded, recovery tests
- US3: Simulate proxies with different success rates, verify intelligent selection
- US4: Configure policies, verify behavior matches configuration
- US5: Generate failures, query metrics, verify accurate reporting

**Success Metrics**:

- SC-001: 15% improvement in success rate for transient failures
- SC-002: 80% reduction in wasted retries on bad proxies
- SC-003: P95 latency <5s for retried requests
- SC-004: Circuit breaker transitions <1s
- SC-005: 20% higher retry success on first attempt (intelligent selection)
- SC-006: 1000+ concurrent requests without degradation
- SC-007: Metrics API <100ms response
- SC-008: Zero race conditions under load
- SC-009: Custom policies without code changes
- SC-010: 90% of successes within 2 retries

---

## Format Validation

✅ All tasks follow checklist format: `- [ ] [ID] [P?] [Story?] Description with path`  
✅ Sequential Task IDs: T001-T087 (89 tasks total)  
✅ [P] marker for parallelizable tasks (48 tasks)  
✅ [Story] labels for user story phases: [US1], [US2], [US3], [US4], [US5]  
✅ File paths included in all implementation tasks  
✅ User stories organized by priority (P1, P2, P3)  
✅ Independent test criteria defined for each user story  
✅ MVP scope clearly identified (US1 + US2 = 34 tasks)  
✅ Dependencies and execution order documented  
✅ Parallel opportunities identified and grouped

**Status**: Ready for execution ✅
