---
description: "Structured logging system implementation tasks for feature 007"
---

# Tasks: Structured Logging System

**Input**: Design documents from `.specify/specs/007-logging-system-structured/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Follow TDD — add or update tests before implementations and verify they fail prior to code changes.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5, US6)
- Include exact file paths in descriptions

## Path Conventions

- **Source**: `proxywhirl/` at repository root
- **Tests**: `tests/` at repository root
- **Examples**: `examples/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare repository scaffolding for structured logging outputs and artifacts.

- [ ] T001 Add ignore patterns for rotated logs and performance artifacts in `.gitignore`
- [ ] T002 Create `logs/.gitkeep` to ensure a writable directory for rotation tests

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish configuration models and shared fixtures required by all logging stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T003 Implement logging configuration models with validation in `proxywhirl/logging_config.py`
- [ ] T004 Add unit tests covering configuration validation scenarios in `tests/unit/test_logging_config.py`
- [ ] T005 Export logging configuration helpers from `proxywhirl/__init__.py`
- [ ] T006 Extend shared pytest fixtures with structured logging utilities in `tests/conftest.py`

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Structured Log Output (Priority: P1) 🎯 MVP

**Goal**: Produce schema-compliant structured logs (JSON and logfmt) with consistent metadata and redaction.

**Independent Test**: Generate logs and validate entries against `contracts/log-entry.schema.json` for both JSON and logfmt formats.

### Tests for User Story 1 ⚠️

- [ ] T007 [P] [US1] Add JSON schema contract test for structured logs in `tests/contract/test_logging_schema.py`
- [ ] T008 [P] [US1] Add formatter unit tests for JSON and logfmt outputs (including Unicode/special characters) in `tests/unit/test_logging_formatters.py`

### Implementation for User Story 1

- [ ] T009 [US1] Implement JSON/logfmt serializers with Unicode-safe redaction helpers in `proxywhirl/logging_formatters.py`
- [ ] T010 [US1] Integrate structured serializers into `configure_logging` in `proxywhirl/utils.py`
- [ ] T011 [US1] Harden sensitive data redaction logic for nested payloads in `proxywhirl/utils.py`

**Checkpoint**: Structured logging formats verified against schema with redaction guarantees.

---

## Phase 4: User Story 2 - Configurable Log Levels (Priority: P1)

**Goal**: Allow runtime control of log levels via environment variables and optional JSON config with live reload.

**Independent Test**: Change log level through env/config reload and confirm only permitted levels emit without restarting the process.

### Tests for User Story 2 ⚠️

- [ ] T012 [P] [US2] Add precedence unit tests for level resolution in `tests/unit/test_logging_levels.py`
- [ ] T013 [P] [US2] Add integration test covering live reload workflows in `tests/integration/test_logging_reload.py`

### Implementation for User Story 2

- [ ] T014 [US2] Implement configuration precedence and validation for levels in `proxywhirl/logging_config.py`
- [ ] T015 [US2] Add logging reload helper with atomic handler swaps in `proxywhirl/utils.py`
- [ ] T016 [US2] Wire CLI entrypoint to trigger logging reloads in `proxywhirl/cli.py`

**Checkpoint**: Log level changes apply within one second without requiring a restart.

---

## Phase 5: User Story 3 - Multiple Output Destinations (Priority: P2)

**Goal**: Support console, file, syslog, and HTTP handlers concurrently with fault tolerance.

**Independent Test**: Configure multiple handlers and confirm each destination receives logs, even when another fails.

### Tests for User Story 3 ⚠️

- [ ] T017 [P] [US3] Add integration test for multi-destination logging in `tests/integration/test_logging_multi_dest.py`
- [ ] T018 [P] [US3] Add handler fallback unit tests for syslog and HTTP sinks in `tests/unit/test_logging_handlers.py`
- [ ] T019 [P] [US3] Add component/module filter unit tests in `tests/unit/test_logging_handlers.py`
- [ ] T020 [P] [US3] Add sampling behavior test covering drop rates in `tests/property/test_logging_sampling.py`

### Implementation for User Story 3

- [ ] T021 [US3] Implement handler factory for console/file/syslog/http sinks in `proxywhirl/logging_handlers.py`
- [ ] T022 [US3] Map configuration-defined handlers into logger setup in `proxywhirl/utils.py`
- [ ] T023 [US3] Add failure fallback and warning instrumentation in `proxywhirl/logging_handlers.py`
- [ ] T024 [US3] Implement component/module filtering controls in `proxywhirl/logging_handlers.py`
- [ ] T025 [US3] Implement log sampling configuration and metrics in `proxywhirl/logging_handlers.py`

**Checkpoint**: Logs flow to all configured destinations with filtering, sampling, and graceful degradation.

---

## Phase 6: User Story 4 - Contextual Logging with Metadata (Priority: P2)

**Goal**: Attach request, proxy, and strategy metadata to log entries for correlation and debugging.

**Independent Test**: Emit logs during operations and verify contextual fields appear in structured output.

### Tests for User Story 4 ⚠️

- [ ] T026 [P] [US4] Add context binding unit tests using `contextvars` in `tests/unit/test_logging_context.py`
- [ ] T027 [P] [US4] Add integration test exercising metadata propagation in `tests/integration/test_logging_context.py`
- [ ] T028 [P] [US4] Add integration test validating structured health event logs in `tests/integration/test_logging_health.py`

### Implementation for User Story 4

- [ ] T029 [US4] Implement context binding utilities for log scopes in `proxywhirl/logging_context.py`
- [ ] T030 [P] [US4] Update proxy selection logging with context binding in `proxywhirl/rotator.py`
- [ ] T031 [P] [US4] Update API request logging to inject request metadata in `proxywhirl/api.py`
- [ ] T032 [P] [US4] Update strategy logging to include strategy identifiers in `proxywhirl/strategies.py`
- [ ] T033 [US4] Emit structured health check logs from `proxywhirl/health.py` with contextual metadata
- [ ] T034 [US4] Wire health logging configuration hooks into `proxywhirl/logging_handlers.py`

**Checkpoint**: Context metadata and health events are consistently attached to logs across proxy operations.

---

## Phase 7: User Story 5 - Log Rotation and Retention (Priority: P2)

**Goal**: Rotate log files by size/time and enforce retention policies without data loss.

**Independent Test**: Generate logs past rotation thresholds and confirm retention cleanup executes as configured.

### Tests for User Story 5 ⚠️

- [ ] T035 [P] [US5] Add rotation and retention integration test in `tests/integration/test_logging_rotation.py`
- [ ] T036 [P] [US5] Add unit tests for rotation scheduling and retention parsing in `tests/unit/test_logging_rotation.py`

### Implementation for User Story 5

- [ ] T037 [US5] Apply rotation and retention settings to file handlers in `proxywhirl/logging_handlers.py`
- [ ] T038 [US5] Implement retention cleanup helpers for rotated files in `proxywhirl/logging_handlers.py`
- [ ] T039 [US5] Extend configuration validation for rotation/retention fields in `proxywhirl/logging_config.py`

**Checkpoint**: File handlers enforce rotation/retention without interrupting logging flows.

---

## Phase 8: User Story 6 - Performance-Optimized Logging (Priority: P3)

**Goal**: Deliver high-throughput asynchronous logging with bounded queues and drop counters.

**Independent Test**: Stress logging at 10k entries/sec and confirm latency overhead stays under 5% with accurate drop metrics.

### Tests for User Story 6 ⚠️

- [ ] T040 [P] [US6] Add Hypothesis property tests for bounded queue behavior in `tests/property/test_logging_concurrency.py`
- [ ] T041 [P] [US6] Add benchmark test covering async logging throughput in `tests/benchmarks/test_logging_performance.py`

### Implementation for User Story 6

- [ ] T042 [US6] Implement bounded async queue with drop counter tracking in `proxywhirl/logging_handlers.py`
- [ ] T043 [US6] Expose logging performance metrics accessors in `proxywhirl/utils.py`

**Checkpoint**: Async logging meets performance targets with observable drop counters.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, samples, and changelog updates spanning all stories.

- [ ] T044 Document structured logging configuration in `README.md`
- [ ] T045 Add end-to-end configuration example script in `examples/structured_logging_demo.py`
- [ ] T046 Summarize structured logging release notes in `CHANGELOG.md`

---

## Dependencies & Execution Order

- **Setup → Foundational**: Complete Phase 1 before Phase 2; both must finish prior to any user story work.
- **User Story Ordering**: Execute user stories in priority sequence — US1 (P1) → US2 (P1) → US3 (P2) → US4 (P2) → US5 (P2) → US6 (P3). Later stories rely on configuration, formatters, and handler infrastructure delivered earlier.
- **Cross-Story Dependencies**:
  - US2 depends on configuration models from Phase 2 and formatters from US1.
  - US3 depends on handler factories built in US1/US2 foundations.
  - US4 builds on structured outputs and handler registration to carry context.
  - US5 extends file handler capabilities introduced in US3.
  - US6 optimizes the async pipeline introduced across US3–US5.
- **Polish Phase** starts after desired user stories reach their checkpoints.

---

## Parallel Execution Examples

- **US1**: After T007 and T008 exist, T009 can progress while a separate contributor prepares schema fixtures referenced in T007.
- **US2**: T012 and T013 can proceed in parallel once configuration helpers from T003–T005 are in place.
- **US3**: While T021 implements the handler factory, T017–T020 can proceed in parallel to lock in expectations.
- **US4**: Post T029, tasks T030–T034 can be tackled simultaneously across their respective modules.
- **US5**: T035 and T036 execute in parallel to validate rotation before T037 applies the handler changes.
- **US6**: T040 and T041 capture property and benchmark coverage concurrently prior to T042.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phases 1–2.
2. Deliver US1 tasks (T007–T011) to produce schema-compliant structured logs.
3. Validate against contract tests before proceeding.

### Incremental Delivery

1. US1 establishes structured outputs (MVP).
2. US2 adds runtime configurability and reloads.
3. US3 introduces multi-destination handlers.
4. US4 layers contextual metadata.
5. US5 enables production-ready rotation and retention.
6. US6 finalizes performance characteristics.

### Parallel Team Strategy

1. Team completes Setup and Foundational phases collectively.
2. Assign US1 and US2 to separate developers (after T003–T006).
3. Split US3–US5 among available engineers once preceding stories reach checkpoints.
4. Dedicate performance specialists to US6 while others handle polish tasks.
