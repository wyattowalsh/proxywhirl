# Tasks: Core Python Package

**Input**: Design documents from `/specs/001-core-python-package/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Following Constitution Principle II (Test-First Development), ALL tests are written BEFORE implementation. This is NON-NEGOTIABLE.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Package: `proxywhirl/` (flat structure, no sub-packages)
- Tests: `tests/unit/`, `tests/integration/`, `tests/property/`
- Docs: `.specify/specs/001-core-python-package/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Verify pyproject.toml has correct dependencies (httpx>=0.25.0, pydantic>=2.0.0, pydantic-settings>=2.0.0, tenacity>=8.2.0, loguru>=0.7.0)
- [x] T002 Verify pyproject.toml has correct dev dependencies (pytest>=7.4.0, pytest-cov>=4.1.0, hypothesis>=6.88.0, mypy>=1.5.0, ruff>=0.1.0)
- [x] T003 Verify pyproject.toml has correct optional dependencies ([js]: playwright>=1.40.0, [storage]: sqlmodel>=0.0.14, [security]: cryptography>=41.0.0)
- [x] T004 Create proxywhirl/__init__.py with empty __all__ list (will populate later)
- [x] T005 [P] Create proxywhirl/py.typed marker file for PEP 561 compliance
- [x] T006 [P] Configure ruff.toml for linting rules (using ruff for formatting too, not black)
- [x] T007 [P] Configure mypy.ini for --strict type checking
- [x] T008 [P] Create tests/conftest.py with pytest fixtures for mock proxies and pools

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundation (Test-First) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T009 [P] Create tests/unit/test_exceptions.py with tests for all exception types
- [x] T010 [P] Create tests/unit/test_models.py with Pydantic validation tests for Proxy model (URL+Port deduplication, SecretStr credentials, health states)
- [x] T011 [P] Create tests/unit/test_models.py tests for ProxyPool model (add/remove, max_pool_size, deduplication)
- [x] T012 [P] Create tests/unit/test_utils.py with tests for credential redaction (*** in logs), URL validation, logging setup

### Implementation for Foundation

- [x] T013 [P] Implement proxywhirl/exceptions.py with exception hierarchy (ProxyError, ProxyPoolEmptyError, ProxyValidationError, ProxyAuthError, ProxyFetchError, ProxyParsingError)
- [x] T014 Implement proxywhirl/models.py with Proxy model (Pydantic v2, SecretStr for credentials, URL+Port deduplication logic, health states: Healthy/Unhealthy/Dead, source tracking)
- [x] T015 Implement proxywhirl/models.py with ProxyPool model (add/remove/update methods, max_pool_size validation, thread-safe operations, statistics methods)
- [x] T016 Implement proxywhirl/models.py with ProxyCredentials model (SecretStr for username/password, never in JSON)
- [x] T017 Implement proxywhirl/models.py with ProxyConfiguration model (timeout settings, retry config, rate limiting config)
- [x] T018 Implement proxywhirl/models.py with enums (HealthStatus, ProxySource, ProxyFormat, ValidationLevel)
- [x] T019 [P] Implement proxywhirl/utils.py with URL validation helpers (parse, validate format, extract protocol)
- [x] T020 [P] Implement proxywhirl/utils.py with credential redaction for logging (ensure *** always shown, never actual values)
- [x] T021 [P] Implement proxywhirl/utils.py with logging setup (configurable DEBUG/INFO/WARNING/ERROR levels via loguru)
- [x] T022 Run tests: pytest tests/unit/test_exceptions.py tests/unit/test_models.py tests/unit/test_utils.py (all should pass)
- [x] T023 Verify mypy --strict proxywhirl/ passes with no warnings
- [x] T024 Verify coverage for security code (credential handling) is 100%

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Install and Use Basic Proxy Rotation (Priority: P1) 🎯 MVP

**Goal**: Developer can install package, provide proxy list, and rotate through proxies automatically with failover

**Independent Test**: Install via pip, create ProxyRotator with proxy list, make consecutive requests and verify different proxies used, simulate failure and verify automatic fallback

### Tests for User Story 1 (Test-First) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T025 [P] [US1] Create tests/unit/test_strategies.py with tests for RoundRobinStrategy (sequential selection, O(1) performance <1ms)
- [x] T026 [P] [US1] Create tests/unit/test_strategies.py with tests for RandomStrategy (uniform distribution, O(1) performance <1ms)
- [x] T027 [P] [US1] Create tests/property/test_rotation_properties.py with Hypothesis property-based tests for round-robin (sequential order maintained over 1000 iterations)
- [x] T028 [P] [US1] Create tests/property/test_rotation_properties.py with Hypothesis tests for random (uniform distribution over large samples)
- [x] T029 [P] [US1] Create tests/integration/test_basic_rotation.py for acceptance scenario 1 (pip install successful with all dependencies)
- [x] T030 [P] [US1] Create tests/integration/test_basic_rotation.py for acceptance scenario 2 (initialize rotator with proxy list, validates and loads all proxies)
- [x] T031 [P] [US1] Create tests/integration/test_basic_rotation.py for acceptance scenario 3 (multiple requests use different proxies automatically)
- [x] T032 [P] [US1] Create tests/integration/test_failover.py for acceptance scenario 4 (proxy failure triggers automatic fallback <100ms)

### Implementation for User Story 1

- [x] T033 [P] [US1] Implement proxywhirl/strategies.py with RotationStrategy Protocol (interface for pluggable strategies)
- [x] T034 [P] [US1] Implement proxywhirl/strategies.py with RoundRobinStrategy (sequential O(1) selection, <1ms guarantee)
- [x] T035 [P] [US1] Implement proxywhirl/strategies.py with RandomStrategy (random O(1) selection, <1ms guarantee)
- [x] T036 [US1] Implement proxywhirl/rotator.py with ProxyRotator class (pool management, strategy injection, context manager support)
- [x] T037 [US1] Implement proxywhirl/rotator.py with add_proxy/remove_proxy methods (thread-safe, <100ms completion, FR-015, FR-017)
- [x] T038 [US1] Implement proxywhirl/rotator.py with get_next_proxy method (uses strategy, updates stats, <1ms selection, FR-030)
- [x] T039 [US1] Implement proxywhirl/rotator.py with automatic failover logic (switch on proxy failure, <100ms, FR-016)
- [x] T040 [US1] Implement proxywhirl/rotator.py with retry logic using tenacity (exponential backoff, FR-027)
- [x] T041 [US1] Implement proxywhirl/rotator.py with empty pool handling (clear exception, FR-029)
- [x] T042 [US1] Update proxywhirl/__init__.py to export ProxyRotator, Proxy, ProxyPool, RoundRobinStrategy, RandomStrategy
- [x] T043 [US1] Run tests: pytest tests/unit/test_strategies.py tests/property/test_rotation_properties.py tests/integration/test_basic_rotation.py tests/integration/test_failover.py
- [x] T044 [US1] Verify performance: Proxy selection <1ms benchmark (SC-005)
- [x] T045 [US1] Verify performance: Failover <100ms benchmark (SC-013)
- [x] T046 [US1] Verify performance: Runtime updates <100ms benchmark (SC-009)

**Checkpoint**: At this point, User Story 1 should be fully functional - install, rotate, failover working

---

## Phase 4: User Story 2 - Handle Authenticated Proxies (Priority: P2)

**Goal**: Developer can provide credentials with proxies, system applies authentication automatically without exposing credentials in logs/errors

**Independent Test**: Configure proxies with username/password, verify authenticated requests succeed, verify credentials never appear in logs or error messages

### Tests for User Story 2 (Test-First) ⚠️

- [x] T047 [P] [US2] Create tests/unit/test_credentials.py with tests for credential storage (SecretStr used, never exposed)
- [x] T048 [P] [US2] Create tests/unit/test_credentials.py with tests for credential redaction in logs (always show ***)
- [x] T049 [P] [US2] Create tests/unit/test_credentials.py with tests for credential redaction in errors (never in exception messages)
- [x] T050 [P] [US2] Create tests/integration/test_authentication.py for acceptance scenario 1 (credentials securely stored and applied to connections)
- [x] T051 [P] [US2] Create tests/integration/test_authentication.py for acceptance scenario 2 (authentication headers automatically included)
- [x] T052 [P] [US2] Create tests/integration/test_auth_rotation.py for acceptance scenario 3 (correct credentials applied per proxy during rotation)

### Implementation for User Story 2

- [x] T053 [P] [US2] Enhance proxywhirl/models.py Proxy model to extract credentials from URL and store as SecretStr
- [x] T054 [P] [US2] Enhance proxywhirl/utils.py to ensure credentials are redacted in all log statements (DEBUG/INFO/WARNING/ERROR)
- [x] T055 [US2] Enhance proxywhirl/rotator.py to apply credentials to httpx client connections automatically
- [x] T056 [US2] Enhance proxywhirl/exceptions.py to sanitize credentials from exception messages
- [x] T057 [US2] Run tests: pytest tests/unit/test_credentials.py tests/integration/test_authentication.py tests/integration/test_auth_rotation.py
- [x] T058 [US2] Verify security: Credentials never in logs (100% compliance, SC-016)
- [x] T059 [US2] Verify security: Credentials never in error messages (100% compliance, FR-021)
- [x] T060 [US2] Verify coverage: Credential handling code has 100% test coverage (SC-023)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - rotation + authentication

---

## Phase 5: User Story 3 - Manage Proxy Pool Lifecycle (Priority: P2)

**Goal**: Developer can add/remove/update proxies at runtime without restarting application, pool updates complete without blocking requests

**Independent Test**: Start rotator with initial pool, add new proxies while requests are running, remove proxies, update proxy config, verify all changes take effect immediately without service interruption

### Tests for User Story 3 (Test-First) ⚠️

- [x] T061 [P] [US3] Create tests/unit/test_pool_lifecycle.py with tests for thread-safe add/remove operations
- [x] T062 [P] [US3] Create tests/unit/test_pool_lifecycle.py with tests for non-blocking pool updates during active requests
- [x] T063 [P] [US3] Create tests/integration/test_runtime_updates.py for acceptance scenario 1 (add new proxies, immediately available)
- [x] T064 [P] [US3] Create tests/integration/test_runtime_updates.py for acceptance scenario 2 (remove proxy, no longer used for new requests)
- [x] T065 [P] [US3] Create tests/integration/test_runtime_updates.py for acceptance scenario 3 (update proxy config, changes take effect for subsequent requests)

### Implementation for User Story 3

- [x] T066 [P] [US3] Enhance proxywhirl/models.py ProxyPool to use threading.Lock for thread-safe operations (FR-032)
- [x] T067 [US3] Enhance proxywhirl/rotator.py add_proxy to be non-blocking, complete <100ms (FR-017, SC-009)
- [x] T068 [US3] Enhance proxywhirl/rotator.py remove_proxy to be non-blocking, handle active requests gracefully
- [x] T069 [US3] Implement proxywhirl/rotator.py update_proxy method for updating credentials/timeouts at runtime
- [x] T070 [US3] Run tests: pytest tests/unit/test_pool_lifecycle.py tests/integration/test_runtime_updates.py
- [x] T071 [US3] Verify performance: Pool updates <100ms with 50 concurrent requests (SC-009)
- [x] T072 [US3] Verify concurrency: 1000+ concurrent requests without degradation (SC-007)

**Checkpoint**: All runtime pool management should work - add/remove/update during active use

---

## Phase 6: User Story 4 - Configure Rotation Behavior (Priority: P3)

**Goal**: Developer can customize rotation strategy (round-robin, random, weighted, least-used) and switch strategies at runtime

**Independent Test**: Create rotator, test each strategy produces expected selection pattern, switch strategy at runtime and verify new pattern takes effect

### Tests for User Story 4 (Test-First) ⚠️

- [x] T073 [P] [US4] Create tests/unit/test_strategies.py tests for WeightedStrategy (distribution matches weights, O(log n) performance)
- [x] T074 [P] [US4] Create tests/unit/test_strategies.py tests for LeastUsedStrategy (always selects minimum usage proxy, O(log n) performance)
- [x] T075 [P] [US4] Create tests/property/test_rotation_properties.py Hypothesis tests for weighted (distribution matches weights over 10000 samples)
- [x] T076 [P] [US4] Create tests/property/test_rotation_properties.py Hypothesis tests for least-used (always selects minimum usage)
- [x] T077 [P] [US4] Create tests/integration/test_strategy_switching.py for acceptance scenario 1 (round-robin produces sequential order)
- [x] T078 [P] [US4] Create tests/integration/test_strategy_switching.py for acceptance scenario 2 (random produces uniform distribution)
- [x] T079 [P] [US4] Create tests/integration/test_strategy_switching.py for acceptance scenario 3 (weighted prefers higher-weighted proxies)

### Implementation for User Story 4

- [x] T080 [P] [US4] Implement proxywhirl/strategies.py with WeightedStrategy (weighted random selection, O(log n), <1ms)
- [x] T081 [P] [US4] Implement proxywhirl/strategies.py with LeastUsedStrategy (min-heap priority queue, O(log n), <1ms)
- [x] T082 [US4] Implement proxywhirl/rotator.py set_strategy method for runtime strategy switching (<5ms, FR-008, SC-008)
- [x] T083 [US4] Add weight parameter to Proxy model for weighted rotation
- [x] T084 [US4] Update proxywhirl/__init__.py to export WeightedStrategy, LeastUsedStrategy
- [x] T085 [US4] Run tests: pytest tests/unit/test_strategies.py tests/property/test_rotation_properties.py tests/integration/test_strategy_switching.py
- [x] T086 [US4] Verify performance: All strategies <1ms selection time (SC-005)
- [x] T087 [US4] Verify performance: Strategy switching <5ms (SC-008)

**Checkpoint**: All rotation strategies working and switchable at runtime

---

## Phase 7: User Story 5 - Fetch Proxies from Free Public Sources (Priority: P1)

**Goal**: Developer can configure fetcher to automatically retrieve and validate proxies from free proxy list URLs, with deduplication by URL+Port

**Independent Test**: Configure fetcher with free proxy source URL, verify proxies fetched and validated, verify deduplication works (same URL+Port = duplicate), verify periodic refresh, verify only working proxies added to pool

### Tests for User Story 5 (Test-First) ⚠️

- [ ] T088 [P] [US5] Create tests/unit/test_fetchers.py with tests for JSON parser (valid/invalid JSON, schema validation)
- [ ] T089 [P] [US5] Create tests/unit/test_fetchers.py with tests for CSV parser (headers, malformed rows)
- [ ] T090 [P] [US5] Create tests/unit/test_fetchers.py with tests for plain text parser (one proxy per line)
- [ ] T091 [P] [US5] Create tests/unit/test_fetchers.py with tests for HTML table parser (extract from <table> tags)
- [ ] T092 [P] [US5] Create tests/unit/test_fetchers.py with tests for URL+Port deduplication (same URL+port = duplicate, different ports = unique)
- [ ] T093 [P] [US5] Create tests/unit/test_fetchers.py with tests for ProxyValidator (connectivity checks, timeout handling)
- [ ] T094 [P] [US5] Create tests/integration/test_proxy_fetching.py for acceptance scenario 1 (retrieve proxies from source URL)
- [ ] T095 [P] [US5] Create tests/integration/test_proxy_fetching.py for acceptance scenario 2 (validate proxies before adding to pool)
- [ ] T096 [P] [US5] Create tests/integration/test_proxy_fetching.py for acceptance scenario 3 (aggregate and deduplicate from multiple sources)
- [ ] T097 [P] [US5] Create tests/integration/test_proxy_fetching.py for acceptance scenario 4 (periodic refresh on configured interval)
- [ ] T098 [P] [US5] Create tests/integration/test_proxy_fetching.py for acceptance scenario 5 (only working proxies added after validation)

### Implementation for User Story 5

- [ ] T099 [P] [US5] Implement proxywhirl/fetchers.py with ProxySourceConfig model (URL, format, refresh_interval, custom_parser)
- [ ] T100 [P] [US5] Implement proxywhirl/fetchers.py with JSONParser for parsing JSON proxy lists
- [ ] T101 [P] [US5] Implement proxywhirl/fetchers.py with CSVParser for parsing CSV proxy lists
- [ ] T102 [P] [US5] Implement proxywhirl/fetchers.py with PlainTextParser for parsing plain text lists
- [ ] T103 [P] [US5] Implement proxywhirl/fetchers.py with HTMLTableParser for extracting from HTML tables
- [ ] T104 [US5] Implement proxywhirl/fetchers.py with ProxyFetcher class (fetch from URLs, handle network failures with tenacity retry)
- [ ] T105 [US5] Implement proxywhirl/fetchers.py with deduplication logic (URL+Port combination, FR-038)
- [ ] T106 [US5] Implement proxywhirl/fetchers.py with ProxyValidator (test connectivity, filter dead proxies, parallel validation 100+/sec, SC-011)
- [ ] T107 [US5] Implement proxywhirl/fetchers.py with source tagging (user-provided vs fetched vs source URL, FR-040)
- [ ] T108 [US5] Implement proxywhirl/fetchers.py with periodic refresh logic (auto-refresh on interval, FR-039)
- [ ] T109 [US5] Implement proxywhirl/rotator.py integration with ProxyFetcher (add_source method)
- [ ] T110 [US5] Update proxywhirl/__init__.py to export ProxyFetcher, ProxyValidator, ProxySourceConfig, parsers
- [ ] T111 [US5] Run tests: pytest tests/unit/test_fetchers.py tests/integration/test_proxy_fetching.py
- [ ] T112 [US5] Verify performance: Validation 100+ proxies per second (SC-011)
- [ ] T113 [US5] Verify deduplication: Same URL+Port correctly identified as duplicates

**Checkpoint**: Proxy fetching, parsing, validation, deduplication all working

---

## Phase 8: User Story 6 - Mix User-Provided and Fetched Proxies (Priority: P2)

**Goal**: Developer can combine user-provided proxies with auto-fetched proxies, control priority via weighted rotation, view pool statistics showing source tags

**Independent Test**: Add user-provided proxies and configure auto-fetch, verify pool contains both with distinct tags, verify weighted rotation prefers user proxies, verify statistics show source breakdown

### Tests for User Story 6 (Test-First) ⚠️

- [ ] T114 [P] [US6] Create tests/integration/test_mixed_sources.py for acceptance scenario 1 (pool contains user + fetched with distinct tags)
- [ ] T115 [P] [US6] Create tests/integration/test_mixed_sources.py for acceptance scenario 2 (weighted rotation prefers user-defined proxies)
- [ ] T116 [P] [US6] Create tests/integration/test_mixed_sources.py for acceptance scenario 3 (statistics indicate source for each proxy)

### Implementation for User Story 6

- [ ] T117 [P] [US6] Enhance proxywhirl/models.py Proxy model to set source=USER for manually added proxies, source=FETCHED for auto-fetched
- [ ] T118 [US6] Enhance proxywhirl/rotator.py to apply higher weights to user-provided proxies when using WeightedStrategy
- [ ] T119 [US6] Implement proxywhirl/rotator.py get_statistics method (total, healthy count, success rates, source breakdown, FR-050)
- [ ] T120 [US6] Run tests: pytest tests/integration/test_mixed_sources.py
- [ ] T121 [US6] Verify statistics API returns source tags correctly

**Checkpoint**: User and fetched proxies can be mixed with priority control and source visibility

---

## Phase 9: User Story 7 - Programmatic Error Handling (Priority: P2)

**Goal**: Developer can handle proxy failures gracefully with clear exceptions, error messages identify failed proxy and reason, retry recommendations provided

**Independent Test**: Simulate various failure modes (proxy down, auth fail, timeout), verify appropriate exceptions raised, verify exception messages are clear and actionable, verify no credential exposure

### Tests for User Story 7 (Test-First) ⚠️

- [ ] T122 [P] [US7] Create tests/integration/test_error_handling.py for acceptance scenario 1 (unavailable proxy raises clear exception with proxy details)
- [ ] T123 [P] [US7] Create tests/integration/test_error_handling.py for acceptance scenario 2 (all proxies failed raises ProxyPoolEmptyError)
- [ ] T124 [P] [US7] Create tests/integration/test_error_handling.py for acceptance scenario 3 (exceptions contain proxy details, error type, retry recommendations)
- [ ] T125 [P] [US7] Create tests/unit/test_utils_coverage.py with edge case tests (EC-001 through EC-017 from spec.md: all proxies fail, invalid URLs, missing auth, slow proxies, empty pool, bad credentials, concurrent updates, unreachable sources, rate limiting, duplicates, dead proxy removal, SOCKS/HTTP mixing, JS timeout, missing Playwright, DOM changes, custom parser errors, variable performance)

### Implementation for User Story 7

- [ ] T126 [P] [US7] Enhance proxywhirl/exceptions.py to include proxy details in exception messages (without credentials)
- [ ] T127 [P] [US7] Enhance proxywhirl/exceptions.py to include retry recommendations in exception metadata
- [ ] T128 [US7] Enhance proxywhirl/rotator.py to raise specific exceptions for different failure modes (FR-026)
- [ ] T129 [US7] Enhance proxywhirl/rotator.py to provide clear, actionable error messages (FR-025, SC-015)
- [ ] T130 [US7] Run tests: pytest tests/integration/test_error_handling.py tests/unit/test_utils_coverage.py
- [ ] T131 [US7] Verify error messages identify failed proxy 95%+ of time (SC-015)

**Checkpoint**: All error handling working with clear, actionable messages

---

## Phase 10: Advanced Features - Logging, Rate Limiting, Circuit Breaker

**Goal**: Implement configurable logging levels, adaptive rate limiting, and optional Playwright support for JS-rendered proxy sources

**Independent Test**: Verify logging levels work (DEBUG/INFO/WARNING/ERROR), verify rate limiting adapts based on success/failure, verify Playwright optional dependency works, verify custom parser registration

### Tests for Advanced Features (Test-First) ⚠️

- [ ] T132 [P] Create tests/unit/test_logging.py with tests for all log levels (DEBUG: selections, INFO: lifecycle, WARNING: retries, ERROR: failures)
- [ ] T133 [P] Create tests/unit/test_rate_limiting.py with tests for adaptive rate limiting (start 10 req/min, increase on success)
- [ ] T133a [P] Create tests/unit/test_rate_limiting.py with tests for HTTP 429 rate limit response handling (retry headers, exponential backoff, adaptive adjustment, FR-048a)
- [ ] T134 [P] Create tests/unit/test_fetchers.py with tests for custom parser registration (user-provided functions)
- [ ] T135 [P] Create tests/unit/test_fetchers.py with tests for Playwright integration (JavaScript rendering, graceful degradation if not installed)

### Implementation for Advanced Features

- [ ] T136 [P] Implement proxywhirl/utils.py configurable logging (DEBUG/INFO/WARNING/ERROR levels, FR-047)
- [ ] T137 [P] Implement proxywhirl/rotator.py adaptive rate limiting using tenacity (start 10 req/min, increase on success, FR-048, FR-048a)
- [ ] T138 [P] Implement proxywhirl/rotator.py circuit breaker pattern for failing proxies (FR-049)
- [ ] T139 [P] Implement proxywhirl/rotator.py event hooks for custom monitoring (proxy selection, request completion, failures, FR-047a)
- [ ] T140 [P] Implement proxywhirl/fetchers.py custom parser registration API (user-provided functions, FR-037a)
- [ ] T141 [P] Implement proxywhirl/fetchers.py Playwright integration for JavaScript rendering (FR-043, optional dependency)
- [ ] T142 [P] Implement proxywhirl/fetchers.py graceful degradation if Playwright not installed (FR-044)
- [ ] T143 Run tests: pytest tests/unit/test_logging.py tests/unit/test_rate_limiting.py
- [ ] T144 Verify all logging levels produce correct output
- [ ] T145 Verify rate limiting adapts correctly based on proxy performance

---

## Phase 11: Storage Backends

**Goal**: Implement storage backends (in-memory by default, JSON file export/import, optional SQLite)

### Tests for Storage (Test-First) ⚠️

- [ ] T146 [P] Create tests/unit/test_storage.py with tests for MemoryStorage (default backend)
- [ ] T147 [P] Create tests/unit/test_storage.py with tests for FileStorage (JSON save/load, atomic writes, <50ms for 100 proxies)
- [ ] T148 [P] Create tests/unit/test_storage.py with tests for optional SQLModelStorage (requires sqlmodel extra)

### Implementation for Storage

- [ ] T149 [P] Implement proxywhirl/storage.py with StorageBackend Protocol
- [ ] T150 [P] Implement proxywhirl/storage.py with MemoryStorage (default)
- [ ] T151 [P] Implement proxywhirl/storage.py with FileStorage (JSON with atomic writes, FR-045, FR-046)
- [ ] T152 [P] Implement proxywhirl/storage.py with optional SQLModelStorage (requires sqlmodel extra - future feature)
- [ ] T153 [P] Integrate storage backends with ProxyRotator (save_pool, load_pool methods)
- [ ] T154 [P] Update proxywhirl/__init__.py to export storage backends
- [ ] T155 Run tests: pytest tests/unit/test_storage.py
- [ ] T156 Verify performance: File I/O <50ms for 100 proxies (SC-012)

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, performance validation, security audit, documentation

- [x] T157 Run full test suite: pytest tests/ --cov=proxywhirl --cov-report=html
- [x] T158 Verify coverage ≥85% (current: 88%+, must maintain)
- [x] T159 Verify 100% coverage for credential handling code
- [x] T160 Run mypy --strict proxywhirl/ (must pass with no warnings)
- [x] T161 Run ruff check proxywhirl/ (must pass with no errors)
- [x] T162 Run ruff format --check proxywhirl/ (must pass - using ruff for formatting, not black)
- [ ] T163 Verify all 24 success criteria from spec.md (SC-001 through SC-024)
- [ ] T164 Verify all 53 functional requirements implemented (FR-001 through FR-050)
- [ ] T165 Verify all 7 constitution principles complied with
- [ ] T166 Run performance benchmarks:
  - Package size <5MB (SC-004)
  - Proxy selection <1ms (SC-005)
  - Rotation overhead <50ms p95 (SC-006)
  - 1000+ concurrent requests (SC-007)
  - Strategy switching <5ms (SC-008)
  - Runtime updates <100ms (SC-009)
  - 100 proxies rotation without degradation (SC-010)
  - Validation 100+ proxies/sec (SC-011)
  - File I/O <50ms for 100 proxies (SC-012)
  - Failover <100ms (SC-013)
- [ ] T167 Security audit: Verify credentials never in logs/errors/stack traces (SC-016, SC-017)
- [ ] T168 Load test: 10,000+ request cycles without memory leaks
- [ ] T169 Update proxywhirl/__init__.py with complete __all__ list (all public exports)
- [ ] T170 Add docstrings to all public functions/methods/classes
- [ ] T171 Generate API documentation from docstrings
- [ ] T172 Update README.md with installation instructions and basic examples
- [ ] T173 Create examples/ directory with sample code for each user story
- [ ] T174 Final constitution check - all 7 principles verified
- [ ] T175 Create GitHub release with changelog

---

## Dependencies & Execution Strategy

### User Story Completion Order

```
Phase 1: Setup → Phase 2: Foundational (BLOCKS ALL)
                 ↓
Phase 3: US1 (P1) ← MVP - Ship this first!
                 ↓
Phase 7: US5 (P1) ← Can start in parallel with US1
                 ↓
┌────────────────┴────────────────┐
│                                 │
Phase 4: US2 (P2)         Phase 5: US3 (P2)
Phase 9: US7 (P2)         Phase 8: US6 (P2)
│                                 │
└────────────────┬────────────────┘
                 ↓
Phase 6: US4 (P3)
                 ↓
Phase 10-12: Advanced Features & Polish
```

### Parallel Execution Opportunities

**Within Phase 3 (US1):**
- T025-T032 (all tests) can run in parallel
- T033-T035 (strategies) can run in parallel
- After T036-T041 complete: T042-T046 can run in parallel

**Within Phase 4 (US2):**
- T047-T052 (all tests) can run in parallel
- T053-T054 can run in parallel
- After T055-T056: T057-T060 can run in parallel

**Within Phase 5 (US3):**
- T061-T065 (all tests) can run in parallel
- T066-T067 can run in parallel

**Within Phase 7 (US5):**
- T088-T098 (all tests) can run in parallel
- T099-T103 (all parsers) can run in parallel
- After T104-T109: T110-T113 can run in parallel

**Across Phases:**
- Phase 3 (US1) and Phase 7 (US5) can run in parallel after Phase 2
- Phase 4 (US2), Phase 5 (US3), Phase 8 (US6), Phase 9 (US7) can run in parallel after US1 complete

### MVP Scope (Recommended First Release)

**Minimum Viable Product = User Story 1 only:**
- Phase 1: Setup
- Phase 2: Foundational
- Phase 3: US1 - Basic rotation with failover
- Phase 12: Minimal polish (tests, docs, security audit)

This gives users immediate value: install, rotate, failover. Ship early, iterate based on feedback.

---

## Task Summary

**Total Tasks**: 175
- Phase 1 (Setup): 8 tasks
- Phase 2 (Foundational): 16 tasks
- Phase 3 (US1 - P1): 22 tasks
- Phase 4 (US2 - P2): 14 tasks
- Phase 5 (US3 - P2): 12 tasks
- Phase 6 (US4 - P3): 15 tasks
- Phase 7 (US5 - P1): 25 tasks
- Phase 8 (US6 - P2): 8 tasks
- Phase 9 (US7 - P2): 10 tasks
- Phase 10 (Advanced): 14 tasks
- Phase 11 (Storage): 11 tasks
- Phase 12 (Polish): 19 tasks

**Parallel Opportunities**: 87 tasks marked [P] (can run in parallel within phase)

**Test-First**: All tests written BEFORE implementation (Constitution Principle II)

**Independent Stories**: Each user story (US1-US7) can be tested independently

**Constitution Compliance**: All 7 principles verified in Phase 12
