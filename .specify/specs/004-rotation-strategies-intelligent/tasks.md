# Tasks: Intelligent Rotation Strategies

**Input**: Design documents from `.specify/specs/004-rotation-strategies-intelligent/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md (Phase 0 output), data-model.md (Phase 1 output), contracts/ (Phase 1 output)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story following Test-Driven Development (TDD) principles.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)
- Tests written FIRST, must FAIL before implementation

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Review existing `proxywhirl/strategies.py` and `proxywhirl/models.py` to understand current implementation
- [X] T002 Review existing test structure in `tests/unit/`, `tests/integration/`, `tests/property/`
- [X] T003 [P] Ensure development dependencies are current: `pytest`, `hypothesis`, `pytest-benchmark`, `mypy`, `ruff`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure enhancements that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Enhanced Proxy Metadata Tracking

- [ ] T004 Enhance `Proxy` model in `proxywhirl/models.py` to add comprehensive request tracking fields:
  - `requests_started: int = 0`
  - `requests_completed: int = 0`
  - `requests_active: int = 0` (in-flight)
  - Update existing `total_requests`, `total_successes`, `total_failures` to align with new tracking
- [ ] T005 Add EMA tracking fields to `Proxy` model in `proxywhirl/models.py`:
  - `ema_response_time_ms: Optional[float] = None`
  - `ema_alpha: float = 0.2` (configurable smoothing factor)
- [ ] T006 Add sliding window tracking to `Proxy` model in `proxywhirl/models.py`:
  - `window_start: Optional[datetime] = None`
  - `window_duration_seconds: int = 3600` (default 1 hour)
- [ ] T007 Add geo-location field to `Proxy` model in `proxywhirl/models.py`:
  - `country_code: Optional[str] = None` (ISO 3166-1 alpha-2)
  - `region: Optional[str] = None`
- [X] **T008**: Implement `Proxy.start_request()` method (increments `requests_started` and `requests_active`) ⏱️ 1h
- [X] **T009**: Implement `Proxy.complete_request(success, response_time_ms)` method (updates counters and EMA) ⏱️ 1h
- [X] **T010**: Implement `Proxy.reset_window()` method (resets sliding window counters) ⏱️ 30m
- [X] **T011**: Implement `Proxy.is_window_expired()` property (checks window expiration) ⏱️ 30m

### Strategy Infrastructure

- [X] T012 Create `StrategyConfig` Pydantic model in `proxywhirl/models.py`:
  - `weights: dict[str, float] = Field(default_factory=dict)`
  - `session_timeout_seconds: int = 3600`
  - `fallback_strategy: Optional[str] = None`
  - `geo_preferences: list[str] = Field(default_factory=list)`
  - `ema_alpha: float = 0.2`
  ⏱️ 1h
- [X] T013 Create `SelectionContext` Pydantic model in `proxywhirl/models.py`:
  - `session_id: Optional[str] = None`
  - `target_url: Optional[str] = None`
  - `request_priority: Optional[int] = None`
  - `failed_proxy_ids: list[str] = Field(default_factory=list)`
  - `metadata: dict[str, Any] = Field(default_factory=dict)`
  ⏱️ 1h
- [X] T014 Create `Session` model in `proxywhirl/models.py`:
  - `session_id: str`
  - `proxy_id: str`
  - `created_at: datetime`
  - `expires_at: datetime`
  - `last_used_at: datetime`
  - `request_count: int = 0`
  ⏱️ 1h
- [ ] T015 Create `SessionManager` class in `proxywhirl/strategies.py`:

### Thread Safety & Concurrency

- [X] T016 Add `threading.RLock` to `ProxyPool` class in `proxywhirl/models.py` for thread-safe operations
- [X] T017 Implement context manager for `ProxyPool` to handle lock acquisition/release
- [X] T018 Add thread-safe `ProxyPool.get_proxy_by_id(id: UUID) -> Optional[Proxy]` method
- [X] T019 Add thread-safe `ProxyPool.update_proxy(proxy: Proxy) -> None` method

### Session Management

- [X] T020 Create `SessionManager` class in `proxywhirl/strategies.py`:
  - `sessions: dict[str, Session]` (thread-safe storage)
  - `create_session(proxy: Proxy, timeout_seconds: int) -> str` (returns session ID)
  - `get_session(session_id: str) -> Optional[Session]`
  - `close_session(session_id: str) -> None`
  - `cleanup_expired_sessions() -> int` (returns count of removed sessions)

**Checkpoint**: Foundation ready - all models enhanced, thread safety implemented, session management in place. User story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Round-Robin Rotation (Priority: P1) 🎯 MVP

**Goal**: Implement enhanced round-robin strategy with comprehensive metadata tracking and health checking

**Independent Test**: Can be tested by making sequential requests and verifying each uses the next proxy in circular order, skipping unhealthy proxies

### Tests for User Story 1 (TDD - Write FIRST, ensure they FAIL)

- [X] T021 [P] [US1] Unit test for round-robin in `tests/unit/test_strategies.py`:
  - Test sequential selection (proxy0, proxy1, proxy2, proxy0...)
  - Test wraparound from last to first proxy
  - Test skipping unhealthy proxies
  - Test metadata updates on selection
- [X] T022 [P] [US1] Property test for round-robin distribution in `tests/property/test_strategies.py`:
  - Use Hypothesis to verify uniform distribution over N proxies
  - Verify ±1 request variance across all proxies
- [X] T023 [P] [US1] Integration test for round-robin in `tests/integration/test_rotation_strategies.py`:
  - Test with real proxy pool and request simulation
  - Verify SC-001: Perfect distribution (±1 request)
- [ ] T024 [P] [US1] Benchmark test for round-robin in `tests/benchmarks/test_strategy_performance.py`:
  - Verify SC-007: <5ms overhead per selection
  - Test with 10,000 concurrent selections (SC-008)

### Implementation for User Story 1

- [X] T025 [US1] Update `RoundRobinStrategy` class in `proxywhirl/strategies.py`:
  - Accept `SelectionContext` parameter in `select()` method
  - Implement `configure(config: StrategyConfig)` method
  - Implement `validate_metadata(pool: ProxyPool)` method (always returns True for round-robin)
- [X] T026 [US1] Enhance `RoundRobinStrategy.select()` to:
  - Filter out unhealthy proxies first
  - Call `proxy.start_request()` before returning
  - Handle empty pool with clear error message
  - Reset window if expired before counting
  - Log selection decision (FR-017)
- [X] T027 [US1] Enhance `RoundRobinStrategy.record_result()` to:
  - Call `proxy.complete_request(success, response_time_ms)`
  - Update EMA response time
  - Log result with metadata
- [ ] T028 [US1] Add thread-safety to `RoundRobinStrategy`:
  - Add `_lock: threading.RLock` for protecting `_current_index`
  - Use lock in `select()` method

**Checkpoint**: Round-robin strategy fully functional with enhanced tracking, health checking, thread safety, and performance validated

---

## Phase 4: User Story 2 - Random Selection Strategy (Priority: P2)

**Goal**: Implement enhanced random selection with uniform distribution and weighted variants

**Independent Test**: Can be tested by making 1000+ requests and verifying proxy usage follows uniform random distribution

### Tests for User Story 2 (TDD - Write FIRST, ensure they FAIL)

- [ ] T029 [P] [US2] Unit test for `RandomStrategy.select()` in `tests/unit/test_strategies.py`:
  - Test random selection from healthy proxies only
  - Test that same proxy can be selected consecutively
  - Test metadata updates on selection
- [ ] T030 [P] [US2] Unit test for `WeightedRandomStrategy.select()` in `tests/unit/test_strategies.py`:
  - Test weighted selection based on success rates
  - Test that high-performing proxies selected more frequently
  - Test handling of zero/negative weights
- [ ] T031 [P] [US2] Property test for random distribution in `tests/property/test_strategies.py`:
  - Use Hypothesis to verify 10% variance over 1000 requests
  - Test uniform distribution across N proxies
- [ ] T032 [P] [US2] Integration test for random selection in `tests/integration/test_rotation_strategies.py`:
  - Verify SC-002: Uniform distribution within 10% variance over 1000 requests
- [ ] T033 [P] [US2] Benchmark test for random selection in `tests/benchmarks/test_strategy_performance.py`:
  - Verify SC-007: <5ms overhead per selection

### Implementation for User Story 2

- [ ] T034 [P] [US2] Update `RandomStrategy` class in `proxywhirl/strategies.py`:
  - Accept `SelectionContext` parameter
  - Implement `configure(config: StrategyConfig)` method
  - Implement `validate_metadata(pool: ProxyPool)` method
  - Call `proxy.start_request()` before returning
  - Add logging for selection decision
- [ ] T035 [P] [US2] Update `WeightedRandomStrategy` class in `proxywhirl/strategies.py`:
  - Rename to `WeightedStrategy` for consistency
  - Accept `SelectionContext` parameter
  - Implement custom weight support via `StrategyConfig.weights`
  - Handle zero/negative weights (skip or use minimum threshold)
  - Implement fallback to uniform random when weights invalid
  - Call `proxy.start_request()` before returning
  - Add logging for weighted selection decision
- [ ] T036 [US2] Add thread-safety to both random strategies (if needed based on `random` module usage)

**Checkpoint**: Random and weighted-random strategies functional, validated for uniform/weighted distribution

---

## Phase 5: User Story 3 - Least-Used Strategy (Priority: P2)

**Goal**: Implement least-used proxy selection with load balancing

**Independent Test**: Can be tested by tracking request counts and verifying least-used proxy is always selected next

### Tests for User Story 3 (TDD - Write FIRST, ensure they FAIL)

- [ ] T037 [P] [US3] Unit test for `LeastUsedStrategy.select()` in `tests/unit/test_strategies.py`:
  - Test selection of proxy with lowest `requests_completed` count
  - Test tie-breaking when multiple proxies have same count
  - Test counter increment after selection
  - Test metadata validation
- [ ] T038 [P] [US3] Property test for load balancing in `tests/property/test_strategies.py`:
  - Use Hypothesis to verify variance stays under 20%
  - Test with varying request patterns
- [ ] T039 [P] [US3] Integration test for least-used in `tests/integration/test_rotation_strategies.py`:
  - Verify SC-003: Request count variance under 20%
  - Test with sliding window reset
- [ ] T040 [P] [US3] Benchmark test for least-used in `tests/benchmarks/test_strategy_performance.py`:
  - Verify SC-007: <5ms overhead (should be O(n) for pool scan)

### Implementation for User Story 3

- [ ] T041 [US3] Update `LeastUsedStrategy` class in `proxywhirl/strategies.py`:
  - Accept `SelectionContext` parameter
  - Implement `configure(config: StrategyConfig)` method
  - Implement `validate_metadata(pool: ProxyPool)` method
- [ ] T042 [US3] Enhance `LeastUsedStrategy.select()` to:
  - Use `requests_completed` instead of `total_requests` for selection
  - Filter healthy proxies first
  - Check and reset expired windows before comparison
  - Implement deterministic tie-breaking (lowest UUID) or random (configurable)
  - Call `proxy.start_request()` before returning
  - Add logging for selection with count information
- [ ] T043 [US3] Add `ProxyPool.reset_counters()` method in `proxywhirl/models.py` for pool modifications
- [ ] T044 [US3] Implement automatic window reset logic in `LeastUsedStrategy`

**Checkpoint**: Least-used strategy functional with proper load balancing and window management

---

## Phase 6: User Story 4 - Performance-Based Strategy (Priority: P2)

**Goal**: Implement performance-based weighted selection using EMA response times

**Independent Test**: Can be tested by tracking proxy latencies and verifying faster proxies are selected more frequently

### Tests for User Story 4 (TDD - Write FIRST, ensure they FAIL)

- [ ] T045 [P] [US4] Unit test for `PerformanceBasedStrategy.select()` in `tests/unit/test_strategies.py`:
  - Test weighting by EMA response time (inverse weighting - lower = better)
  - Test that faster proxies selected more frequently
  - Test fallback when all proxies slow or no EMA data
  - Test metadata validation (requires EMA data)
- [ ] T046 [P] [US4] Unit test for EMA calculation in `tests/unit/test_models.py`:
  - Test EMA update formula correctness
  - Test alpha parameter effect (0.1, 0.2, 0.5)
  - Test initialization of first EMA value
- [ ] T047 [P] [US4] Integration test for performance-based in `tests/integration/test_rotation_strategies.py`:
  - Verify SC-004: 15-25% response time reduction vs round-robin
  - Test with simulated varying proxy speeds
  - Test adaptive behavior when proxy performance degrades
- [ ] T048 [P] [US4] Benchmark test for performance-based in `tests/benchmarks/test_strategy_performance.py`:
  - Verify SC-007: <5ms overhead (weighted selection is O(n))

### Implementation for User Story 4

- [ ] T049 [US4] Create `PerformanceBasedStrategy` class in `proxywhirl/strategies.py`:
  - Accept `SelectionContext` parameter
  - Implement `configure(config: StrategyConfig)` method to set alpha
  - Implement `validate_metadata(pool: ProxyPool)` to check for EMA data
  - Implement fallback strategy support (FR-022)
- [ ] T050 [US4] Implement `PerformanceBasedStrategy.select()`:
  - Calculate inverse weights from EMA response times (faster = higher weight)
  - Filter healthy proxies with valid EMA data
  - Use weighted random selection (similar to `WeightedStrategy`)
  - Handle missing EMA data per FR-021 (reject with error or use fallback)
  - Call `proxy.start_request()` before returning
  - Add detailed logging of performance metrics
- [ ] T051 [US4] Implement fallback behavior:
  - If no proxies have EMA data, use configured fallback strategy
  - If no fallback configured, raise clear error
  - Log fallback invocation for monitoring

**Checkpoint**: Performance-based strategy functional with EMA tracking and validated latency reduction

---

## Phase 7: User Story 5 - Session Persistence Strategy (Priority: P3)

**Goal**: Implement session persistence for maintaining same proxy across related requests

**Independent Test**: Can be tested by creating a session and verifying all requests within that session use the same proxy

### Tests for User Story 5 (TDD - Write FIRST, ensure they FAIL)

- [ ] T052 [P] [US5] Unit test for `SessionPersistenceStrategy` in `tests/unit/test_strategies.py`:
  - Test session creation and proxy assignment
  - Test reusing same proxy for existing session
  - Test session expiration and new proxy selection
  - Test session failover when assigned proxy becomes unhealthy
- [ ] T053 [P] [US5] Unit test for `SessionManager` in `tests/unit/test_strategies.py`:
  - Test `create_session()`, `get_session()`, `close_session()`
  - Test `cleanup_expired_sessions()`
  - Test thread-safe session access
- [ ] T054 [P] [US5] Integration test for session persistence in `tests/integration/test_rotation_strategies.py`:
  - Verify SC-005: 99.9% same-proxy guarantee
  - Test multiple concurrent sessions
  - Test session timeout behavior
  - Test extremely long-lived sessions (edge case)

### Implementation for User Story 5

- [ ] T055 [US5] Create `SessionPersistenceStrategy` class in `proxywhirl/strategies.py`:
  - Accept `SelectionContext` with `session_id`
  - Implement `configure(config: StrategyConfig)` for timeout settings
  - Implement `validate_metadata(pool: ProxyPool)` (always True)
  - Integrate with `SessionManager`
- [ ] T056 [US5] Implement `SessionPersistenceStrategy.select()`:
  - Check if `context.session_id` exists in `SessionManager`
  - If exists and not expired: return assigned proxy (after health check)
  - If exists but proxy unhealthy: select new proxy, update session, log failover
  - If not exists: create new session with selected proxy (use fallback strategy)
  - Call `proxy.start_request()` before returning
  - Update session `last_used_at` timestamp
  - Add logging for session operations
- [ ] T057 [US5] Add `SessionManager._lock` for thread-safe operations
- [ ] T058 [US5] Implement automatic session cleanup in background (optional enhancement)

**Checkpoint**: Session persistence functional with failover support and validated same-proxy guarantee

---

## Phase 8: User Story 6 - Geo-Targeted Strategy (Priority: P3)

**Goal**: Implement geo-targeted proxy selection based on country/region

**Independent Test**: Can be tested by requesting proxies from specific regions and verifying selected proxies match the criteria

### Tests for User Story 6 (TDD - Write FIRST, ensure they FAIL)

- [ ] T059 [P] [US6] Unit test for `GeoTargetedStrategy` in `tests/unit/test_strategies.py`:
  - Test filtering proxies by country code
  - Test filtering proxies by region
  - Test behavior when no proxies match target region
  - Test fallback to any region (if configured)
  - Test secondary strategy application (round-robin, random)
- [ ] T060 [P] [US6] Integration test for geo-targeting in `tests/integration/test_rotation_strategies.py`:
  - Verify SC-006: 100% correct region selection when available
  - Test with multiple regions
  - Test fallback behavior
- [ ] T061 [P] [US6] Property test for geo-targeting in `tests/property/test_strategies.py`:
  - Use Hypothesis to verify correct filtering across random proxy sets

### Implementation for User Story 6

- [ ] T062 [US6] Create `GeoTargetedStrategy` class in `proxywhirl/strategies.py`:
  - Accept `SelectionContext` with `target_region`
  - Implement `configure(config: StrategyConfig)` for geo preferences and fallback
  - Implement `validate_metadata(pool: ProxyPool)` to check for country codes
- [ ] T063 [US6] Implement `GeoTargetedStrategy.select()`:
  - Extract `target_region` from `SelectionContext`
  - Filter healthy proxies by `country_code` or `region`
  - If no matches and fallback enabled: select from any region
  - If no matches and no fallback: raise clear error (FR-021)
  - Apply secondary strategy to filtered proxies (configurable: round-robin, random, etc.)
  - Call `proxy.start_request()` before returning
  - Add logging with region information
- [ ] T064 [US6] Implement strategy composition pattern in `GeoTargetedStrategy`:
  - Allow wrapping another strategy (filter + delegate)
  - Example: Geo filter → Performance-based selection

**Checkpoint**: Geo-targeted strategy functional with fallback and composition support

---

## Phase 9: Strategy Composition & Advanced Features

**Goal**: Implement strategy composition, hot-swapping, and plugin architecture

### Tests for Advanced Features (TDD - Write FIRST, ensure they FAIL)

- [ ] T065 [P] Integration test for strategy composition in `tests/integration/test_rotation_strategies.py`:
  - Test geo-filter + performance-based
  - Test geo-filter + least-used
  - Verify combined strategies work correctly
- [ ] T066 [P] Integration test for hot-swapping in `tests/integration/test_rotation_strategies.py`:
  - Verify SC-009: <100ms hot-swap for new requests
  - Test in-flight requests complete with original strategy
  - Test no dropped requests during swap
- [ ] T067 [P] Unit test for plugin architecture in `tests/unit/test_strategies.py`:
  - Test custom strategy registration
  - Test custom strategy loading
  - Verify SC-010: Custom plugin loads within 1 second

### Implementation for Advanced Features

- [ ] T068 Create `CompositeStrategy` class in `proxywhirl/strategies.py`:
  - Accept list of strategies to apply in sequence
  - First strategy filters pool, subsequent strategies select from filtered set
  - Implement validation that all component strategies are compatible
- [ ] T069 Implement strategy hot-swapping in `ProxyRotator`:
  - Add `set_strategy(strategy: RotationStrategy)` method
  - Use atomic reference swap for thread-safety
  - Track strategy version for in-flight request isolation
  - Add logging for strategy changes
- [ ] T070 Implement plugin architecture:
  - Create `StrategyRegistry` singleton
  - Add `register_strategy(name: str, strategy_class: Type[RotationStrategy])`
  - Add `get_strategy(name: str) -> RotationStrategy`
  - Support dynamic loading from entry points or module imports
- [ ] T071 Add `ComposedStrategy.from_config(config: dict) -> CompositeStrategy` factory method
- [ ] T072 Update `ProxyRotator` to support strategy names (string) in addition to strategy objects

**Checkpoint**: Strategy composition, hot-swapping, and plugin system all functional

---

## Phase 10: Cross-Cutting Concerns & Polish

**Purpose**: Improvements that affect multiple user stories and finalize implementation

### Documentation & Examples

- [ ] T073 [P] Create comprehensive examples in `examples/rotation_strategies_example.py`:
  - Example for each strategy (US1-US6)
  - Example of strategy composition
  - Example of session persistence
  - Example of custom strategy plugin
- [ ] T074 [P] Update `README.md` with rotation strategies section
- [ ] T075 [P] Create rotation strategies quickstart guide
- [ ] T076 [P] Add docstrings to all new/updated classes and methods
- [ ] T077 [P] Update API documentation for strategy configuration

### Performance & Optimization

- [ ] T078 Run benchmark suite and document results:
  - Verify all SC metrics are met
  - Profile strategy selection performance
  - Test concurrent load (10,000 requests)
- [ ] T079 Optimize hot paths identified in profiling:
  - Minimize lock contention
  - Cache healthy proxy list if performance issue
  - Optimize EMA calculation if needed
- [ ] T080 Validate memory usage under load (no leaks over 10,000+ cycles)

### Security & Validation

- [ ] T081 [P] Security audit of credential handling in strategies:
  - Verify no credentials in logs
  - Verify SecretStr usage throughout
  - Run Bandit static analysis
- [ ] T082 [P] Add input validation for all strategy configurations:
  - Validate alpha parameter (0 < alpha < 1)
  - Validate window duration (> 0)
  - Validate timeout values (> 0)
  - Validate country codes (ISO 3166-1 format)
- [ ] T083 [P] Add edge case handling:
  - Empty pools
  - All proxies unhealthy
  - Zero/negative weights
  - Missing metadata
  - Concurrent pool modifications

### Type Safety & Code Quality

- [ ] T084 Run `mypy --strict` on all strategy code and fix any issues
- [ ] T085 Run `ruff check` and fix any linting issues
- [ ] T086 Ensure 85%+ code coverage across all new code
- [ ] T087 Add missing type hints to any untyped code

### Integration & Testing

- [ ] T088 Run full integration test suite end-to-end
- [ ] T089 Validate all 6 user stories work independently
- [ ] T090 Validate cross-story integration (composition, hot-swap, etc.)
- [ ] T091 Run property tests with increased iteration counts (10,000+ examples)
- [ ] T092 Validate thread-safety with concurrent test harness

### Final Validation

- [ ] T093 Run quickstart.md validation guide
- [ ] T094 Verify all FR requirements are implemented and tested
- [ ] T095 Verify all SC success criteria are met and documented
- [ ] T096 Create feature demo script showing all strategies in action
- [ ] T097 Final code review and refactoring pass
- [ ] T098 Update CHANGELOG with feature additions
- [ ] T099 Tag release candidate and run full CI/CD pipeline

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Stories (Phases 3-8)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed) OR
  - Sequentially in priority order: US1(P1) → US2(P2) → US3(P2) → US4(P2) → US5(P3) → US6(P3)
- **Strategy Composition (Phase 9)**: Depends on US4 and US6 completion (composition requires multiple strategies)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (Round-Robin)**: Foundation only - no dependencies on other stories
- **US2 (Random/Weighted)**: Foundation only - no dependencies on other stories
- **US3 (Least-Used)**: Foundation only - no dependencies on other stories
- **US4 (Performance-Based)**: Foundation only - no dependencies on other stories
- **US5 (Session Persistence)**: Foundation only - no dependencies on other stories
- **US6 (Geo-Targeted)**: Foundation only - no dependencies on other stories
- **Strategy Composition**: Requires at least US4 and US6 for meaningful composition examples

### Within Each User Story

1. **Tests FIRST** - Write and verify they FAIL
2. **Models** before services (if applicable)
3. **Core implementation** before enhancements
4. **Validation** before integration
5. **Story complete** before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: All tasks [P] can run in parallel
- **Phase 2 (Foundational)**: Many tasks marked [P] can run in parallel:
  - T004-T007: Model enhancements (different fields)
  - T008-T011: Method implementations (different methods)
  - T016-T019: Thread safety (different aspects)
- **Phases 3-8 (User Stories)**: ALL stories can be developed in parallel by different team members once Foundation is complete
- **Within Each Story**: All test tasks marked [P] can run in parallel
- **Phase 10 (Polish)**: Many tasks marked [P] can run in parallel

---

## Implementation Strategy

### MVP First (Phase 3: US1 Only)

1. Complete Phase 1: Setup ✓
2. Complete Phase 2: Foundational (CRITICAL) ✓
3. Complete Phase 3: User Story 1 (Round-Robin) ✓
4. **STOP and VALIDATE**: Test US1 independently, verify SC-001, SC-007, SC-008
5. Deploy/demo if ready (minimal viable rotation strategy)

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Test independently → **Deploy/Demo (MVP!)**
3. Add US2 → Test independently → Deploy/Demo
4. Add US3 → Test independently → Deploy/Demo
5. Add US4 → Test independently → Deploy/Demo
6. Add US5 → Test independently → Deploy/Demo
7. Add US6 → Test independently → Deploy/Demo
8. Add Composition (Phase 9) → Test → Deploy/Demo
9. Polish (Phase 10) → Final release

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With 3+ developers after Foundation complete:

- **Developer A**: US1 (Round-Robin) → US2 (Random)
- **Developer B**: US3 (Least-Used) → US4 (Performance-Based)
- **Developer C**: US5 (Session) → US6 (Geo-Targeted)
- **Team**: Phase 9 (Composition) together
- **Team**: Phase 10 (Polish) together

Stories complete and integrate independently.

---

## Estimated Effort

| Phase | Tasks | Estimated Hours | Priority |
|-------|-------|----------------|----------|
| Phase 1: Setup | 3 | 2h | Critical |
| Phase 2: Foundational | 17 | 16h | Critical |
| Phase 3: US1 (Round-Robin) | 8 | 8h | P1 - MVP |
| Phase 4: US2 (Random) | 8 | 8h | P2 |
| Phase 5: US3 (Least-Used) | 8 | 8h | P2 |
| Phase 6: US4 (Performance) | 11 | 12h | P2 |
| Phase 7: US5 (Session) | 7 | 10h | P3 |
| Phase 8: US6 (Geo-Targeted) | 6 | 8h | P3 |
| Phase 9: Composition | 8 | 8h | Enhancement |
| Phase 10: Polish | 27 | 16h | Final |
| **Total** | **103 tasks** | **~96h** | **2-3 weeks** |

**Notes**:

- MVP (Phase 1-3): ~26h → 3-4 days
- Full Feature (Phase 1-8): ~72h → 9-10 days
- Complete with Polish: ~96h → 12-15 days

---

## Notes

- **TDD is mandatory**: All tests written FIRST, must FAIL before implementation
- **[P] tasks**: Different files, no dependencies - safe to parallelize
- **[Story] label**: Maps task to specific user story for traceability
- **Each user story**: Independently completable and testable
- **Stop at checkpoints**: Validate story independently before proceeding
- **Constitution compliance**: All code must pass mypy --strict, maintain 85%+ coverage
- **Performance validation**: Benchmark tests must pass for all success criteria
- **Thread safety**: Critical for concurrent request handling (SC-008)
- **Avoid**: Vague tasks, same-file conflicts, cross-story dependencies that break independence

---

## Quick Reference: Success Criteria Mapping

| Success Criteria | Primary Tasks | Validation Method |
|------------------|---------------|-------------------|
| SC-001: Round-robin ±1 distribution | T021-T028 | Property test T022, Integration test T023 |
| SC-002: Random 10% variance | T029-T033 | Property test T031, Integration test T032 |
| SC-003: Least-used <20% variance | T037-T044 | Property test T038, Integration test T039 |
| SC-004: Performance 15-25% improvement | T045-T051 | Integration test T047 with baseline comparison |
| SC-005: Session 99.9% same-proxy | T052-T058 | Integration test T054 with statistical validation |
| SC-006: Geo-targeting 100% accuracy | T059-T064 | Integration test T060, Property test T061 |
| SC-007: <5ms selection overhead | T024, T033, T040, T048 | Benchmark tests in all strategies |
| SC-008: 10k concurrent requests | T024, T092 | Concurrent test harness |
| SC-009: <100ms hot-swap | T066, T069 | Integration test with timing |
| SC-010: <1s plugin load | T067, T070 | Unit test with timing |
