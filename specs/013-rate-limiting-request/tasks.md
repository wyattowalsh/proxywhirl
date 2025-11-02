# Tasks: Rate Limiting for Request Management

**Input**: Design documents from `/specs/013-rate-limiting-request/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Test-First Development (TDD) is MANDATORY per Constitution Principle II. All test tasks must be completed and FAILING before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- Source code: `proxywhirl/` at repository root (flat package structure)
- Tests: `tests/` with subdirectories: `unit/`, `integration/`, `property/`, `contract/`, `benchmarks/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [ ] T001 Add Redis dependency via `uv add redis>=5.0.0`
- [ ] T002 [P] Add pytest-asyncio dependency via `uv add --dev pytest-asyncio>=0.23.0`
- [ ] T003 [P] Add pytest-benchmark dependency via `uv add --dev pytest-benchmark>=4.0.0`
- [ ] T004 [P] Add fakeredis dependency via `uv add --dev fakeredis>=2.20.0`
- [ ] T005 [P] Add hypothesis dependency via `uv add --dev hypothesis>=6.88.0`
- [ ] T006 [P] Add freezegun dependency via `uv add --dev freezegun>=1.4.0` for time-travel mocking
- [ ] T007 Create RateLimitExceeded exception in `proxywhirl/exceptions.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core Pydantic models and configuration - MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Foundational Tests (Must FAIL before implementation)

- [ ] T008 [P] Write unit tests for RateLimitTierConfig validation in `tests/unit/test_rate_limit_models.py`
- [ ] T009 [P] Write unit tests for RateLimitConfig validation in `tests/unit/test_rate_limit_models.py`
- [ ] T010 [P] Write unit tests for RateLimitState model in `tests/unit/test_rate_limit_models.py`
- [ ] T011 [P] Write unit tests for RateLimitResult model in `tests/unit/test_rate_limit_models.py`
- [ ] T012 [P] Write unit tests for RateLimitMetrics model in `tests/unit/test_rate_limit_models.py`

### Foundational Implementation

- [ ] T013 Create RateLimitTierConfig Pydantic model in `proxywhirl/rate_limit_models.py`
- [ ] T014 Create RateLimitConfig Pydantic model with BaseSettings in `proxywhirl/rate_limit_models.py`
- [ ] T015 Create RateLimitState Pydantic model with computed fields in `proxywhirl/rate_limit_models.py`
- [ ] T016 Create RateLimitResult Pydantic model in `proxywhirl/rate_limit_models.py`
- [ ] T017 Create RateLimitMetrics Pydantic model in `proxywhirl/rate_limit_models.py`
- [ ] T018 Add field validators for RateLimitTierConfig (name pattern, endpoint validation) in `proxywhirl/rate_limit_models.py`
- [ ] T019 Add field validators for RateLimitConfig (default_tier, whitelist) in `proxywhirl/rate_limit_models.py`
- [ ] T020 Verify all foundational model tests pass (RateLimitConfig, RateLimitTierConfig, RateLimitState, RateLimitResult, RateLimitMetrics validation only) with `uv run pytest tests/unit/test_rate_limit_models.py -v`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Prevent Service Overload (Priority: P1) 🎯 MVP

**Goal**: Basic rate limiting with HTTP 429 responses, sliding window counter algorithm, Redis storage

**Independent Test**: Send 101 requests in 30 seconds with 100 req/min limit. First 100 succeed, 101st returns 429 with Retry-After header.

**Success Criteria**: SC-001 (100% throttling), SC-002 (<5ms latency), SC-004 (state persistence), SC-008 (zero false positives)

### Tests for User Story 1 (Must FAIL before implementation)

- [ ] T021 [P] [US1] Write unit tests for Lua script rate limit logic in `tests/unit/test_rate_limiter.py`
- [ ] T022 [P] [US1] Write unit tests for Redis sliding window counter operations in `tests/unit/test_rate_limiter.py`
- [ ] T023 [P] [US1] Write unit tests for in-memory fallback storage in `tests/unit/test_rate_limiter.py`
- [ ] T024 [P] [US1] Write property tests for sliding window counter algorithm correctness (no false positives) in `tests/property/test_rate_limit_concurrent.py`
- [ ] T024a [P] [US1] Write integration test for window boundary edge cases (requests at exact t=0s and t=60s) in `tests/integration/test_rate_limit_api.py`
- [ ] T025 [P] [US1] Write middleware unit tests for identifier extraction in `tests/unit/test_rate_limit_middleware.py`
- [ ] T026 [P] [US1] Write middleware unit tests for header injection in `tests/unit/test_rate_limit_middleware.py`
- [ ] T027 [P] [US1] Write contract tests for rate limit headers in all responses in `tests/contract/test_rate_limit_headers.py`
- [ ] T028 [P] [US1] Write contract tests for HTTP 429 response format in `tests/contract/test_rate_limit_headers.py`
- [ ] T029 [P] [US1] Write integration test for basic rate limiting with Redis in `tests/integration/test_rate_limit_api.py`
- [ ] T030 [P] [US1] Write integration test for window expiry and reset in `tests/integration/test_rate_limit_api.py`
- [ ] T031 [P] [US1] Write integration test for multiple users with independent limits in `tests/integration/test_rate_limit_api.py`
- [ ] T031a [P] [US1] Write integration test for config changes during active rate limit windows (new limits apply to new windows, existing windows honored) in `tests/integration/test_rate_limit_api.py`
- [ ] T031b [P] [US1] Write integration test for same identifier with multiple concurrent sessions (rate limits apply per identifier, not per session) in `tests/integration/test_rate_limit_api.py`
- [ ] T032 [P] [US1] Write benchmark test for <5ms p95 enforcement latency (SC-002) with 1000 concurrent users (SC-003 scale) in `tests/benchmarks/test_rate_limit_overhead.py`

### Implementation for User Story 1

- [ ] T033 [US1] Create RateLimiter class with Redis connection setup in `proxywhirl/rate_limiter.py`
- [ ] T034 [US1] Implement Lua script for atomic sliding window counter check-and-increment in `proxywhirl/rate_limiter.py`
- [ ] T035 [US1] Implement async `check()` method with Redis EVALSHA call in `proxywhirl/rate_limiter.py`
- [ ] T036 [US1] Implement in-memory fallback storage for testing/single-instance mode in `proxywhirl/rate_limiter.py`
- [ ] T037 [US1] Add Redis error handling with configurable fail-open (allow requests on Redis failure) and fail-closed (deny requests on Redis failure) modes in `proxywhirl/rate_limiter.py`, with explicit unit tests for both modes
- [ ] T038 [US1] Create RateLimitMiddleware class in `proxywhirl/rate_limit_middleware.py`
- [ ] T039 [US1] Implement identifier extraction (API key from header, user ID from JWT, or client IP from X-Forwarded-For/X-Real-IP/request.client.host in priority order) in `proxywhirl/rate_limit_middleware.py`
- [ ] T040 [US1] Implement rate limit check integration in middleware dispatch in `proxywhirl/rate_limit_middleware.py`
- [ ] T041 [US1] Implement HTTP 429 response builder with Retry-After header in `proxywhirl/rate_limit_middleware.py`
- [ ] T042 [US1] Implement rate limit header injection (X-RateLimit-*) in `proxywhirl/rate_limit_middleware.py`
- [ ] T043 [US1] Integrate RateLimitMiddleware into FastAPI app in `proxywhirl/api.py`
- [ ] T044 [US1] Add RateLimitExceeded exception handler in `proxywhirl/api.py`
- [ ] T045 [US1] Verify all US1 unit tests pass with `uv run pytest tests/unit/test_rate_limiter.py tests/unit/test_rate_limit_middleware.py -v`
- [ ] T046 [US1] Verify all US1 contract tests pass with `uv run pytest tests/contract/test_rate_limit_headers.py -v`
- [ ] T047 [US1] Verify all US1 integration tests pass with `uv run pytest tests/integration/test_rate_limit_api.py -v`
- [ ] T048 [US1] Verify all US1 property tests pass with `uv run pytest tests/property/test_rate_limit_concurrent.py -v`
- [ ] T049 [US1] Verify benchmark test meets SC-002 (<5ms p95 latency) with `uv run pytest tests/benchmarks/test_rate_limit_overhead.py -v`

**Checkpoint**: User Story 1 complete - basic rate limiting functional with 429 responses and headers

---

## Phase 4: User Story 2 - Tiered Rate Limiting (Priority: P2)

**Goal**: Different rate limits for free/premium/enterprise tiers with tier-based enforcement

**Independent Test**: Configure free (100 req/min) and premium (1000 req/min) tiers. Free user throttled at 101, premium user continues.

**Success Criteria**: SC-005 (95% of legitimate users never throttled), SC-006 (config updates within 60s)

### Tests for User Story 2 (Must FAIL before implementation)

- [ ] T050 [P] [US2] Write unit tests for tier resolution logic in `tests/unit/test_rate_limiter.py`
- [ ] T051 [P] [US2] Write unit tests for tier configuration loading in `tests/unit/test_rate_limit_models.py`
- [ ] T052 [P] [US2] Write integration test for multi-tier rate limiting in `tests/integration/test_rate_limit_tiers.py`
- [ ] T053 [P] [US2] Write integration test for free vs premium tier enforcement in `tests/integration/test_rate_limit_tiers.py`
- [ ] T054 [P] [US2] Write integration test for unlimited tier (no throttling) in `tests/integration/test_rate_limit_tiers.py`
- [ ] T055 [P] [US2] Write integration test for unauthenticated users (default tier) in `tests/integration/test_rate_limit_tiers.py`

### Implementation for User Story 2

- [ ] T056 [P] [US2] Add tier determination logic to middleware (extract from API key/JWT) in `proxywhirl/rate_limit_middleware.py`
- [ ] T057 [US2] Implement tier config lookup in RateLimiter.check() in `proxywhirl/rate_limiter.py`
- [ ] T058 [US2] Add default tier fallback for unauthenticated users in `proxywhirl/rate_limiter.py`
- [ ] T059 [US2] Create sample rate_limit_config.yaml with free/premium/enterprise tiers in repository root (committed as example; users create custom configs in same location or specify via RATE_LIMIT_CONFIG_PATH env var)
- [ ] T060 [US2] Add YAML config loading support in `proxywhirl/rate_limit_models.py`
- [ ] T061 [US2] Document tier configuration in `proxywhirl/rate_limit_models.py` docstrings
- [ ] T062 [US2] Verify all US2 tests pass with `uv run pytest tests/unit/test_rate_limiter.py tests/integration/test_rate_limit_tiers.py -v`

**Checkpoint**: User Story 2 complete - tiered rate limiting functional with free/premium/enterprise support

---

## Phase 5: User Story 3 - Per-Endpoint Rate Limiting (Priority: P3)

**Goal**: Granular per-endpoint limits with hierarchical precedence (most restrictive wins)

**Independent Test**: Configure /api/v1/request (50 req/min) and /api/v1/health (1000 req/min). Verify independent enforcement.

**Success Criteria**: FR-007 (per-endpoint limits), FR-008 (most restrictive wins)

### Tests for User Story 3 (Must FAIL before implementation)

- [ ] T063 [P] [US3] Write unit tests for endpoint limit resolution (hierarchical precedence) in `tests/unit/test_rate_limiter.py`
- [ ] T064 [P] [US3] Write integration test for per-endpoint limits in `tests/integration/test_rate_limit_api.py`
- [ ] T065 [P] [US3] Write integration test for endpoint override stricter than tier limit in `tests/integration/test_rate_limit_api.py`
- [ ] T066 [P] [US3] Write integration test for multiple endpoints with independent limits in `tests/integration/test_rate_limit_api.py`
- [ ] T067 [P] [US3] Write integration test for endpoint without override using tier limit in `tests/integration/test_rate_limit_api.py`

### Implementation for User Story 3

- [ ] T068 [P] [US3] Add endpoint extraction from request in middleware in `proxywhirl/rate_limit_middleware.py`
- [ ] T069 [US3] Implement endpoint-specific limit lookup in RateLimiter.check() in `proxywhirl/rate_limiter.py`
- [ ] T070 [US3] Implement hierarchical limit calculation (min of tier and endpoint) in `proxywhirl/rate_limiter.py`
- [ ] T071 [US3] Add per-endpoint Redis key generation in `proxywhirl/rate_limiter.py`
- [ ] T072 [US3] Update rate_limit_config.yaml with endpoint overrides examples in repository root
- [ ] T073 [US3] Verify all US3 tests pass with `uv run pytest tests/unit/test_rate_limiter.py tests/integration/test_rate_limit_api.py::test_per_endpoint* -v`

**Checkpoint**: User Story 3 complete - per-endpoint rate limiting functional with hierarchical limits

---

## Phase 6: User Story 4 - Rate Limit Monitoring and Metrics (Priority: P3)

**Goal**: Observability via metrics endpoints, structured logging, and Prometheus integration

**Independent Test**: Make throttled requests, query /api/v1/rate-limit/metrics, verify counts match.

**Success Criteria**: SC-007 (metrics <10s delay), FR-012 (metrics exposition), FR-013 (logging)

### Tests for User Story 4 (Must FAIL before implementation)

- [ ] T074 [P] [US4] Write unit tests for RateLimitMetrics aggregation in `tests/unit/test_rate_limit_models.py`
- [ ] T075 [P] [US4] Write integration test for /api/v1/rate-limit/metrics endpoint in `tests/integration/test_rate_limit_api.py`
- [ ] T076 [P] [US4] Write integration test for /api/v1/rate-limit/config GET endpoint in `tests/integration/test_rate_limit_api.py`
- [ ] T077 [P] [US4] Write integration test for /api/v1/rate-limit/config PUT endpoint in `tests/integration/test_rate_limit_api.py`
- [ ] T078 [P] [US4] Write integration test for /api/v1/rate-limit/status/{identifier} endpoint in `tests/integration/test_rate_limit_api.py`
- [ ] T079 [P] [US4] Write unit tests for Prometheus metrics recording in `tests/unit/test_rate_limiter.py`
- [ ] T080 [P] [US4] Write unit tests for structured logging (verify no sensitive data) in `tests/unit/test_rate_limit_middleware.py`

### Implementation for User Story 4

- [ ] T081 [P] [US4] Add Prometheus Counter for rate_limit_requests_total in `proxywhirl/rate_limiter.py`
- [ ] T082 [P] [US4] Add Prometheus Counter for rate_limit_throttled_total in `proxywhirl/rate_limiter.py`
- [ ] T083 [P] [US4] Add Prometheus Histogram for rate_limit_check_duration_seconds in `proxywhirl/rate_limiter.py`
- [ ] T084 [US4] Integrate Prometheus metrics recording in RateLimiter.check() in `proxywhirl/rate_limiter.py`
- [ ] T085 [US4] Add structured logging with Loguru for rate limit violations in `proxywhirl/rate_limit_middleware.py`
- [ ] T086 [US4] Implement GET /api/v1/rate-limit/metrics endpoint in `proxywhirl/api.py`
- [ ] T087 [US4] Implement GET /api/v1/rate-limit/config endpoint (admin auth) in `proxywhirl/api.py`
- [ ] T088 [US4] Implement PUT /api/v1/rate-limit/config endpoint (admin auth, hot reload) in `proxywhirl/api.py`
- [ ] T088a [US4] Implement config file watcher for automatic hot reload on file changes (watches rate_limit_config.yaml, reloads config within 60s per SC-006) in `proxywhirl/rate_limit_models.py`
- [ ] T089 [US4] Implement GET /api/v1/rate-limit/status/{identifier} endpoint in `proxywhirl/api.py`
- [ ] T090 [US4] Add metrics aggregation logic in RateLimitMetrics in `proxywhirl/rate_limit_models.py`
- [ ] T091 [US4] Verify all US4 tests pass with `uv run pytest tests/unit/test_rate_limiter.py tests/integration/test_rate_limit_api.py::test_*metrics* -v`
- [ ] T092 [US4] Verify metrics endpoint returns valid JSON matching RateLimitMetrics schema

**Checkpoint**: User Story 4 complete - full observability with metrics, config management, and logging

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Quality improvements, documentation, and final validation

- [ ] T093 [P] Add whitelist bypass logic in RateLimiter.check() (FR-015) in `proxywhirl/rate_limiter.py`
- [ ] T094 [P] Write integration test for whitelist exemptions in `tests/integration/test_rate_limit_api.py`
- [ ] T095 [P] Add Redis persistence tests (restart scenario) in `tests/integration/test_rate_limit_redis.py`
- [ ] T096 [P] Add concurrent request correctness tests with Hypothesis in `tests/property/test_rate_limit_concurrent.py`
- [ ] T096a [P] Write unit test for rate limiting resilience to system clock changes using monotonic time in `tests/unit/test_rate_limiter.py`
- [ ] T097 [P] Update OpenAPI schema with rate limit response headers in `proxywhirl/api.py`
- [ ] T098 [P] Add rate limiting section to main README.md with quickstart
- [ ] T099 [P] Create example scripts demonstrating rate limiting in `examples/rate_limiting_example.py`
- [ ] T100 Run full test suite with `uv run pytest tests/ --cov=proxywhirl -v` (PASS CRITERIA: 100% tests passing, 0 failures)
- [ ] T101 Verify mypy --strict passes with `uv run mypy --strict proxywhirl/rate_limit*.py` (PASS CRITERIA: 0 errors, 0 warnings)
- [ ] T102 Verify ruff checks pass with `uv run ruff check proxywhirl/rate_limit*.py` (PASS CRITERIA: 0 errors, 0 warnings)
- [ ] T103 Verify coverage ≥85% for rate limiting modules (PASS CRITERIA: line coverage ≥85%, branch coverage ≥80%)
- [ ] T104 Run quickstart.md scenarios manually to validate end-to-end functionality
- [ ] T105 Document configuration hot reload mechanism in quickstart.md
- [ ] T106 Add troubleshooting section to quickstart.md with common issues

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (T001-T007) - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (T008-T020)
- **User Story 2 (Phase 4)**: Depends on Foundational (T008-T020) AND User Story 1 (T021-T049)
- **User Story 3 (Phase 5)**: Depends on Foundational (T008-T020) AND User Story 1 (T021-T049)
- **User Story 4 (Phase 6)**: Depends on Foundational (T008-T020) AND User Story 1 (T021-T049)
- **Polish (Phase 7)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - core rate limiting with 429 responses
- **User Story 2 (P2)**: Extends US1 - adds tier-based limits (builds on basic rate limiting)
- **User Story 3 (P3)**: Extends US1 - adds per-endpoint limits (independent of US2)
- **User Story 4 (P3)**: Extends US1 - adds monitoring (independent of US2 and US3)

**Note**: US2, US3, US4 all depend on US1 but are independent of each other. After US1 is complete, US2, US3, US4 can be implemented in parallel by different developers.

### Within Each User Story

1. **Tests FIRST** (all tests marked [P] within a story can run in parallel)
2. **Verify tests FAIL** before implementation
3. **Core implementation** (models, services)
4. **Middleware integration** (if applicable)
5. **API endpoints** (if applicable)
6. **Verify all tests PASS**
7. Story complete - independently testable

### Parallel Opportunities

#### Phase 1 (Setup)
- T002, T003, T004, T005, T006 can run in parallel (different dependencies)

#### Phase 2 (Foundational)
- T008-T012 (test writing) can run in parallel (different test files)
- T013-T017 (model creation) must be sequential (same file)

#### Phase 3 (User Story 1)
- T021-T032 (all test writing) can run in parallel
- T033-T037 (rate_limiter.py implementation) must be sequential (same file)
- T038-T042 (rate_limit_middleware.py implementation) can overlap with T033-T037 (different files)
- T043-T044 (api.py integration) must wait for T033-T042

#### Phase 4 (User Story 2)
- T050-T055 (test writing) can run in parallel
- T056-T061 (implementation) has file dependencies

#### Phase 5 (User Story 3)
- T063-T067 (test writing) can run in parallel
- T068-T073 (implementation) has file dependencies

#### Phase 6 (User Story 4)
- T074-T080 (test writing) can run in parallel
- T081-T083 (Prometheus metrics) can run in parallel (same file but independent metrics)
- T086-T089 (API endpoints) can run in parallel (different endpoints)

#### Phase 7 (Polish)
- T093-T099 can run in parallel (different files/concerns)

---

## Parallel Example: User Story 1 Test Writing

```bash
# Developer 1: Unit tests
Task T021: Write unit tests for Lua script rate limit logic

# Developer 2: Property tests
Task T024: Write property tests for sliding window correctness

# Developer 3: Middleware tests
Task T025: Write middleware unit tests for identifier extraction
Task T026: Write middleware unit tests for header injection

# Developer 4: Contract tests
Task T027: Write contract tests for rate limit headers in all responses
Task T028: Write contract tests for HTTP 429 response format

# Developer 5: Integration tests
Task T029: Write integration test for basic rate limiting with Redis
Task T030: Write integration test for window expiry and reset
Task T031: Write integration test for multiple users with independent limits

# Developer 6: Benchmark tests
Task T032: Write benchmark test for <5ms enforcement latency
```

All 6 developers can work simultaneously on different test files.

---

## Parallel Example: Multi-Story Development

After Foundational (Phase 2) is complete:

```bash
# Team A: User Story 1 (P1 - MVP)
Complete T021-T049 → Deploy MVP

# Team B: User Story 2 (P2 - Tiers) [waits for US1]
Complete T050-T062 → Deploy tiered limits

# Team C: User Story 3 (P3 - Per-Endpoint) [waits for US1, can start in parallel with US2]
Complete T063-T073 → Deploy per-endpoint limits

# Team D: User Story 4 (P3 - Monitoring) [waits for US1, can start in parallel with US2/US3]
Complete T074-T092 → Deploy full observability
```

After US1 is complete, Teams B, C, D can work in parallel on US2, US3, US4.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. **Phase 1**: Setup (T001-T007) - Install dependencies
2. **Phase 2**: Foundational (T008-T020) - Core models and validation
3. **Phase 3**: User Story 1 (T021-T049) - Basic rate limiting with 429 responses
4. **STOP and VALIDATE**: 
   - Run all US1 tests: `uv run pytest tests/unit/test_rate_limit*.py tests/contract/ tests/integration/test_rate_limit_api.py tests/property/ tests/benchmarks/ -v`
   - Verify SC-001, SC-002, SC-004, SC-008 success criteria
   - Manual test: Send 101 requests, verify 429 on request 101
5. **Deploy MVP**: Basic rate limiting functional

**MVP Delivers**: Protection against service overload, HTTP 429 responses with Retry-After headers, rate limit headers, Redis-backed state persistence, <5ms latency, zero false positives.

### Incremental Delivery

1. **Foundation** (Phase 1 + 2) → Core infrastructure ready
2. **+ User Story 1** (Phase 3) → Test independently → **Deploy MVP** 🎯
3. **+ User Story 2** (Phase 4) → Test independently → **Deploy tiered limits**
4. **+ User Story 3** (Phase 5) → Test independently → **Deploy per-endpoint limits**
5. **+ User Story 4** (Phase 6) → Test independently → **Deploy full observability**
6. **+ Polish** (Phase 7) → Final quality pass → **Production ready**

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With 4 developers after Foundational phase:

```
Week 1: Foundation (Phase 1 + 2) - All 4 developers together

Week 2-3: 
  Dev 1-2: User Story 1 (T021-T049) → MVP deployed ✅

Week 4:
  Dev 1: User Story 2 (T050-T062) → Tiered limits
  Dev 2: User Story 3 (T063-T073) → Per-endpoint limits
  Dev 3: User Story 4 (T074-T092) → Monitoring
  Dev 4: Polish (T093-T099) → Examples and docs

Week 5:
  All: Final validation (T100-T106) → Production deployment ✅
```

---

## Task Summary

- **Total Tasks**: 111 (was 106, added 5 new tasks from analysis remediation)
- **Setup Tasks**: 7 (T001-T007)
- **Foundational Tasks**: 13 (T008-T020)
- **User Story 1 Tasks**: 33 (T021-T049 + T024a, T031a, T031b) - 15 test tasks, 18 implementation tasks
- **User Story 2 Tasks**: 13 (T050-T062) - 6 test tasks, 7 implementation tasks
- **User Story 3 Tasks**: 11 (T063-T073) - 5 test tasks, 6 implementation tasks
- **User Story 4 Tasks**: 20 (T074-T092 + T088a) - 7 test tasks, 13 implementation tasks
- **Polish Tasks**: 15 (T093-T106 + T096a)

**Test Coverage**: 30 test tasks + additional polish tests = robust TDD approach

**Parallel Opportunities**: 45+ tasks can run in parallel with proper team coordination

**Independent Test Criteria Met**: Each user story has explicit independent test validation checkpoints

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1) = 49 tasks for minimal viable product

---

## Notes

- **[P]** tasks = different files or independent concerns, can run in parallel
- **[Story]** label maps task to specific user story for traceability
- **Test-First**: All tests MUST be written and FAILING before implementation starts (Constitution Principle II)
- **mypy --strict**: Required to pass for all rate limiting modules
- **Coverage**: Target ≥85% (100% for security-related code)
- **uv run**: ALL Python commands MUST use `uv run` prefix (Constitution requirement)
- **Commit Strategy**: Commit after each task or logical group for safe rollback
- **Checkpoints**: Stop at each checkpoint to validate story independently before proceeding
- **File Conflicts**: Avoid concurrent edits to same file - coordinate or serialize
- **Redis Setup**: Requires Redis running locally or via Docker for integration tests

**Constitution Compliance**: This task breakdown enforces Test-First Development (Principle II), maintains Independent User Stories (Principle IV), and supports Performance Standards validation (Principle V) through benchmark tests.