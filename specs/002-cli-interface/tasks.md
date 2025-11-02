---

description: "Task list for CLI interface feature"
---

# Tasks: 002-cli-interface

**Input**: Design documents from `/specs/002-cli-interface/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are required per constitution (test-first). Every user story includes explicit test tasks that must be completed before implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Task can run in parallel (different files, no blocking dependencies)
- **[Story]**: Maps task to user story (US1-US4)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare dependencies and project configuration for the Typer-based CLI.

- [ ] T001 Update Typer/Rich/FileLock/Platformdirs runtime dependencies in `pyproject.toml`
- [ ] T002 Add `proxywhirl.cli:app` console entry point and Typer testing extras in `pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish reusable CLI infrastructure before any user story work begins.

- [ ] T003 Create Typer-aware configuration utilities (discover/load/save/encrypt) in `proxywhirl/config.py`
- [ ] T004 [P] Add CLI result and pool summary models (RequestResult, ProxyStatus, PoolSummary) to `proxywhirl/models.py`
- [ ] T005 Implement Typer `app` callback with shared `CommandContext`, global options, and renderer selection in `proxywhirl/cli.py`
- [ ] T006 [P] Introduce `CLILock` context manager with Typer-aware error handling in `proxywhirl/utils.py`

**Checkpoint**: Base CLI scaffolding, shared models, and locking utilities ready for story work.

---

## Phase 3: User Story 1 - Make Request Through Proxy via CLI (Priority: P1) 🎯 MVP

**Goal**: Allow users to make proxied HTTP requests from the CLI with rotation and failover.

**Independent Test**: Invoke `proxywhirl get <url>` with a proxy list file and verify the response uses rotating proxies with automatic retry on failure.

### Tests for User Story 1 (write first)

- [ ] T007 [P] [US1] Author Typer CLI unit tests for `get/post/put/delete` commands including multi-header scenarios in `tests/unit/test_cli.py`
- [ ] T008 [P] [US1] Add integration test covering proxied request workflow in `tests/integration/test_cli_requests.py`

### Implementation for User Story 1

- [ ] T009 [US1] Implement Typer HTTP verb commands (GET/POST/PUT/DELETE/PATCH/HEAD/OPTIONS) with argument validation in `proxywhirl/cli.py`
- [ ] T010 [US1] Wire request execution, retry/failover, and output serialization to RequestResult in `proxywhirl/cli.py`

**Checkpoint**: P1 CLI requests succeed with rotation, retries, and human-readable output.

---

## Phase 4: User Story 2 - Manage Proxy Pool from CLI (Priority: P2)

**Goal**: Provide Typer `pool` subcommands to inspect, add, remove, and test proxies with concurrency-safe updates.

**Independent Test**: Run `proxywhirl pool list/add/remove/test` on an isolated pool and verify statuses update without interfering commands.

### Tests for User Story 2 (write first)

- [ ] T011 [P] [US2] Extend unit tests for pool subcommands (list/add/remove/test) in `tests/unit/test_cli.py`
- [ ] T012 [P] [US2] Create integration workflow test for pool lifecycle in `tests/integration/test_cli_pool.py`

### Implementation for User Story 2

- [ ] T013 [US2] Implement Typer `pool` command group with CLILock protection in `proxywhirl/cli.py`
- [ ] T014 [US2] Connect pool commands to existing storage backends (FileStorage/SQLiteStorage) and wire health metrics from Phase 2 in `proxywhirl/cli.py`

**Checkpoint**: Pool management commands operate safely and report accurate health metrics.

---

## Phase 5: User Story 3 - Configure CLI Settings (Priority: P2)

**Goal**: Enable persistent configuration via Typer `config` subcommands with encryption and validation.

**Independent Test**: Use `proxywhirl config init/set/get/show` without extra flags and observe settings applied to subsequent CLI runs.

### Tests for User Story 3 (write first)

- [ ] T015 [P] [US3] Add configuration model tests covering discovery, load/save, and permissions in `tests/unit/test_config.py`
- [ ] T016 [P] [US3] Build integration tests for config CLI workflow in `tests/integration/test_cli_config.py`

### Implementation for User Story 3

- [ ] T017 [US3] Implement TOML discovery/load/save/encrypt helpers in `proxywhirl/config.py`
- [ ] T018 [US3] Implement Typer `config` subcommands (init/get/set/show) using CommandContext in `proxywhirl/cli.py`

**Checkpoint**: Configuration commands persist settings securely and affect later CLI sessions.

---

## Phase 6: User Story 4 - Output Formatting and Piping (Priority: P3)

**Goal**: Support multiple output formats (human, JSON, table, CSV) and TTY-aware behaviors for automation workflows.

**Independent Test**: Run any command with `--format json/table/csv` and pipe output to shell tools (e.g., `jq`) without loss of fidelity.

### Tests for User Story 4 (write first)

- [ ] T019 [P] [US4] Add renderer unit tests for human/json/table/csv outputs in `tests/unit/test_cli.py`
- [ ] T020 [P] [US4] Create integration tests demonstrating piping/TTY fallbacks in `tests/integration/test_cli_output.py`

### Implementation for User Story 4

- [ ] T021 [US4] Implement Rich-backed renderer strategy and CSV/JSON emitters in `proxywhirl/cli.py`
- [ ] T022 [US4] Apply format selection, quiet/verbose flags, and piping safeguards across commands in `proxywhirl/cli.py`

**Checkpoint**: CLI outputs honor format flags, TTY detection, and piping scenarios.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Finalize documentation, examples, and quality gates across the CLI feature.

- [ ] T023 [P] Update CLI quickstart examples in `examples/cli_examples.sh`
- [ ] T024 Refresh CLI sections in `README.md` with Typer usage and formatting guidance
- [ ] T025 Run quality gates (`uv run pytest`, `uv run mypy --strict proxywhirl/`, `uv run ruff check proxywhirl/`) and capture results in `docs/PHASE2_STATUS.md`
- [ ] T026 [P] Verify packaged CLI binary size <10MB per SC-008 using `uv build` and file size check

---

## Dependencies & Execution Order

1. **Setup** → Enables dependency availability for all other phases.
2. **Foundational** → Blocks every user story; ensures shared CLI infrastructure is stable.
3. **User Story 1 (P1)** → First deliverable (MVP). Must complete before any downstream demos.
4. **User Story 2 (P2)** and **User Story 3 (P2)** → Can proceed in parallel after Foundational but remain independently testable.
5. **User Story 4 (P3)** → Builds on prior stories for formatting flexibility.
6. **Polish** → Runs after all targeted stories meet acceptance.

## Parallel Execution Examples

- **US1**: T007 and T008 can run in parallel (unit vs integration tests in separate files).
- **US2**: T011 and T012 can proceed concurrently before implementation.
- **US3**: T015 and T016 can proceed in parallel (unit vs integration coverage).
- **US4**: T019 and T020 can execute simultaneously to cover renderer behavior.
- **Cross-Story**: After Phase 2, teams can assign US2 and US3 to different developers due to isolated file touch points.

## Implementation Strategy

1. **Deliver MVP first**: Complete Phases 1-3 to ship proxied requests quickly.
2. **Layer management**: Implement pool operations (Phase 4) once MVP proves stable.
3. **Add persistence**: Introduce configuration commands (Phase 5) to reduce flag usage.
4. **Polish with formatting**: Implement advanced output (Phase 6) for automation users.
5. **Finalize**: Execute Phase 7 to update docs, examples, and enforce quality gates before integration.
