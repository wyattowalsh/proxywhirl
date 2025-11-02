# Tasks: Configuration Management

**Input**: Design documents from `/specs/012-configuration-management-flexible/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-endpoints.md, quickstart.md

**Tests**: This feature follows Test-First Development (TDD). All test tasks must be completed and verified to FAIL before implementation tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and configuration management structure

- [ ] T001 Add pydantic-settings>=2.0.0 dependency to pyproject.toml
- [ ] T002 Add pyyaml>=6.0 dependency to pyproject.toml
- [ ] T003 Add watchdog>=3.0.0 dependency to pyproject.toml
- [ ] T004 Run `uv sync` to install new dependencies
- [ ] T005 Create proxywhirl/config_models.py for configuration data models
- [ ] T006 Create proxywhirl/config.py for ConfigurationManager implementation
- [ ] T007 Update proxywhirl/__init__.py to export configuration management classes

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configuration data models and validation infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 [P] Define ConfigurationSource enum in proxywhirl/config_models.py (DEFAULT, YAML_FILE, ENV_FILE, ENVIRONMENT, CLI_ARGUMENT, RUNTIME_UPDATE)
- [ ] T009 [P] Create User model in proxywhirl/config_models.py with id, username, is_admin, email fields (Pydantic model)
- [ ] T010 [P] Create ValidationError model in proxywhirl/config_models.py with field, message, value fields (Pydantic model)
- [ ] T011 Create ValidationResult model in proxywhirl/config_models.py with valid, errors, warnings fields and helper methods
- [ ] T012 Create ProxyWhirlSettings base configuration model in proxywhirl/config_models.py extending pydantic BaseSettings with SettingsConfigDict
- [ ] T013 Add core configuration fields to ProxyWhirlSettings: timeout (1-300s, hot_reloadable=True), max_retries (0-10, hot_reloadable=True), log_level (Literal enum, hot_reloadable=True)
- [ ] T014 Add proxy configuration fields to ProxyWhirlSettings: proxy_url (SecretStr, hot_reloadable=False), database_path (str, hot_reloadable=False)
- [ ] T015 Add server configuration fields to ProxyWhirlSettings: server_host (str, hot_reloadable=False), server_port (int 1024-65535, hot_reloadable=False), rate_limit_requests (int, hot_reloadable=True)
- [ ] T016 Add field validators to ProxyWhirlSettings: validate_log_level (uppercase), validate_database_path (.db extension)
- [ ] T017 Add helper methods to ProxyWhirlSettings: is_hot_reloadable(field_name), get_restart_required_fields()
- [ ] T018 [P] Create ConfigUpdate dataclass in proxywhirl/config_models.py (frozen) with user_id, username, timestamp, changes, version, source fields
- [ ] T019 Add helper methods to ConfigUpdate: get_changed_keys(), conflicts_with(other)
- [ ] T020 [P] Create ConfigurationSnapshot model in proxywhirl/config_models.py with settings, sources, timestamp, metadata fields
- [ ] T021 Add from_config() class method to ConfigurationSnapshot for creating snapshots with credential redaction
- [ ] T022 Add to_yaml() method to ConfigurationSnapshot for exporting to YAML format with source attribution

**Checkpoint**: Foundation ready - all data models defined with validation, user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Multi-Source Configuration Loading (Priority: P1) 🎯 MVP

**Goal**: Load configuration from environment variables, YAML files, and CLI arguments with correct precedence (CLI > ENV > File > Defaults)

**Independent Test**: Start proxywhirl with a mix of environment variables, a YAML config file, and command-line arguments, then verify that the configuration is loaded correctly with proper precedence

### Tests for User Story 1 (TDD)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T023 [P] [US1] Create tests/unit/test_config_models.py for ProxyWhirlSettings validation tests (test field validators, hot_reloadable checks, type coercion)
- [ ] T024 [P] [US1] Create tests/unit/test_config_loading.py for multi-source loading tests (test YAML loading, environment variable loading, precedence rules)
- [ ] T025 [P] [US1] Create tests/integration/test_multi_source_config.py for end-to-end configuration loading scenarios (test CLI overrides ENV overrides File overrides Defaults)
- [ ] T026 [P] [US1] Create tests/property/test_config_merging.py for property-based tests of configuration merging using Hypothesis
- [ ] T027 [US1] Run `uv run pytest tests/unit/test_config_models.py tests/unit/test_config_loading.py tests/integration/test_multi_source_config.py tests/property/test_config_merging.py -v` and verify all tests FAIL

### Implementation for User Story 1

- [ ] T028 [US1] Implement ConfigurationManager.__init__() in proxywhirl/config.py with _config, _config_lock, _previous_config, _sources attributes
- [ ] T029 [US1] Implement load_yaml_config(path) function in proxywhirl/config.py using yaml.safe_load() with error handling
- [ ] T030 [US1] Implement parse_cli_args() function in proxywhirl/config.py using argparse with type coercion for all config fields
- [ ] T031 [US1] Implement _load_config_from_sources() method in ConfigurationManager to merge YAML + ENV + CLI with correct precedence
- [ ] T032 [US1] Implement settings_customise_sources() class method in ProxyWhirlSettings to define source priority order
- [ ] T033 [US1] Implement get_config() method in ConfigurationManager for thread-safe configuration retrieval
- [ ] T034 [US1] Implement get_sources() method in ConfigurationManager to return dict mapping field names to ConfigurationSource
- [ ] T035 [US1] Add comprehensive logging for configuration loading: source, timestamp, loaded fields in ConfigurationManager
- [ ] T036 [US1] Run `uv run pytest tests/unit/test_config_models.py tests/unit/test_config_loading.py tests/integration/test_multi_source_config.py tests/property/test_config_merging.py -v` and verify all tests PASS
- [ ] T037 [US1] Run `uv run mypy --strict proxywhirl/config_models.py proxywhirl/config.py` and verify 0 errors

**Checkpoint**: User Story 1 complete - multi-source configuration loading works independently with proper precedence

---

## Phase 4: User Story 2 - Runtime Configuration Updates (Priority: P1)

**Goal**: Update configuration settings at runtime without restarting the application (admin-only, hot-reloadable fields only)

**Independent Test**: While proxywhirl is running and handling requests, update a configuration setting (e.g., request timeout) via API and verify that new requests immediately use the updated value without application restart

### Tests for User Story 2 (TDD)

- [ ] T038 [P] [US2] Create tests/unit/test_runtime_updates.py for runtime update tests (test update_runtime_config, authorization checks, hot-reloadable vs restart-required distinction)
- [ ] T039 [P] [US2] Create tests/unit/test_config_rollback.py for rollback functionality tests (test rollback() method, previous config preservation)
- [ ] T040 [P] [US2] Create tests/integration/test_runtime_config_api.py for API endpoint tests if 003-rest-api active (test PATCH /api/v1/config endpoint with admin auth)
- [ ] T041 [US2] Run `uv run pytest tests/unit/test_runtime_updates.py tests/unit/test_config_rollback.py tests/integration/test_runtime_config_api.py -v` and verify all tests FAIL

### Implementation for User Story 2

- [ ] T042 [US2] Implement require_admin(user) function in proxywhirl/config.py to check User.is_admin and raise PermissionError if not admin
- [ ] T043 [US2] Implement _validate_updates(updates) method in ConfigurationManager to check if fields are hot-reloadable and validate new values
- [ ] T044 [US2] Implement update_runtime_config(updates, user) method in ConfigurationManager with admin authorization, validation, atomic swap using threading.Lock
- [ ] T045 [US2] Implement rollback() method in ConfigurationManager to restore _previous_config with thread-safe swap
- [ ] T046 [US2] Add audit logging for runtime updates: user_id, username, changed fields, old/new values, timestamp in update_runtime_config()
- [ ] T047 [US2] Implement PATCH /api/v1/config endpoint in proxywhirl/api.py if 003-rest-api active (depends on T044, requires admin authorization)
- [ ] T048 [US2] Implement POST /api/v1/config/rollback endpoint in proxywhirl/api.py if 003-rest-api active (depends on T045, requires admin authorization)
- [ ] T049 [US2] Add ConfigUpdateRequest and ConfigUpdateResponse models to proxywhirl/api_models.py if 003-rest-api active
- [ ] T050 [US2] Run `uv run pytest tests/unit/test_runtime_updates.py tests/unit/test_config_rollback.py tests/integration/test_runtime_config_api.py -v` and verify all tests PASS
- [ ] T051 [US2] Run `uv run mypy --strict proxywhirl/config.py proxywhirl/api.py` and verify 0 errors

**Checkpoint**: User Story 2 complete - runtime configuration updates work with admin authorization and hot-reload distinction

---

## Phase 5: User Story 3 - Configuration Validation (Priority: P2)

**Goal**: Validate configuration files and settings against schema before deployment with clear error messages

**Independent Test**: Provide an invalid configuration file (e.g., timeout as string instead of integer) and verify that proxywhirl detects the error during startup with a clear, actionable error message

### Tests for User Story 3 (TDD)

- [ ] T052 [P] [US3] Create tests/unit/test_config_validation.py for validation tests (test field type validation, range validation, enum validation, cross-field validation)
- [ ] T053 [P] [US3] Create tests/integration/test_validation_startup.py for startup validation tests (test startup failure on invalid config with clear error messages)
- [ ] T054 [P] [US3] Create tests/integration/test_validation_api.py for validation endpoint tests if 003-rest-api active (test POST /api/v1/config/validate endpoint)
- [ ] T055 [US3] Run `uv run pytest tests/unit/test_config_validation.py tests/integration/test_validation_startup.py tests/integration/test_validation_api.py -v` and verify all tests FAIL

### Implementation for User Story 3

- [ ] T056 [US3] Implement validate_config(config_dict) function in proxywhirl/config.py to validate configuration dict and return ValidationResult
- [ ] T057 [US3] Add validation warnings for potentially problematic configurations (e.g., timeout=1s) in validate_config()
- [ ] T058 [US3] Implement validate_updates(updates) method in ConfigurationManager (already started in T043) to validate partial updates
- [ ] T059 [US3] Add startup validation in ConfigurationManager.__init__() or load() method to fail early with ValidationResult errors
- [ ] T060 [US3] Implement POST /api/v1/config/validate endpoint in proxywhirl/api.py if 003-rest-api active (any authenticated user, no admin required)
- [ ] T061 [US3] Implement GET /api/v1/config/schema endpoint in proxywhirl/api.py if 003-rest-api active to return JSON schema from ProxyWhirlSettings.model_json_schema()
- [ ] T062 [US3] Add ValidationRequest and ValidationResponse models to proxywhirl/api_models.py if 003-rest-api active
- [ ] T063 [US3] Run `uv run pytest tests/unit/test_config_validation.py tests/integration/test_validation_startup.py tests/integration/test_validation_api.py -v` and verify all tests PASS
- [ ] T064 [US3] Run `uv run mypy --strict proxywhirl/config.py proxywhirl/api.py` and verify 0 errors

**Checkpoint**: User Story 3 complete - configuration validation works at startup and via API with clear error messages

---

## Phase 6: User Story 4 - Configuration Hot Reload from Files (Priority: P2)

**Goal**: Update configuration by modifying config files and triggering reload (SIGHUP or API call) without restarting application

**Independent Test**: While proxywhirl is running, modify the configuration file and send a reload signal (SIGHUP or API call), then verify that the new configuration is loaded and applied without application restart

### Tests for User Story 4 (TDD)

- [ ] T065 [P] [US4] Create tests/unit/test_file_watching.py for file watching tests (test watchdog integration, debouncing, reload callback)
- [ ] T066 [P] [US4] Create tests/integration/test_hot_reload.py for hot reload tests (test file modification detection, reload with validation, rollback on invalid config)
- [ ] T067 [P] [US4] Create tests/integration/test_reload_api.py for reload endpoint tests if 003-rest-api active (test POST /api/v1/config/reload endpoint with admin auth)
- [ ] T068 [US4] Run `uv run pytest tests/unit/test_file_watching.py tests/integration/test_hot_reload.py tests/integration/test_reload_api.py -v` and verify all tests FAIL

### Implementation for User Story 4

- [ ] T069 [US4] Create ConfigFileHandler class in proxywhirl/config.py extending watchdog.events.FileSystemEventHandler with on_modified() method
- [ ] T070 [US4] Implement debouncing in ConfigFileHandler using time.time() to avoid rapid reloads (1-second debounce per research.md)
- [ ] T071 [US4] Implement reload() method in ConfigurationManager to reload config from all sources with validation and atomic swap
- [ ] T072 [US4] Implement enable_file_watching(config_path) method in ConfigurationManager to start watchdog Observer with ConfigFileHandler
- [ ] T073 [US4] Add reload callback support in ConfigurationManager.__init__() to allow custom actions after successful reload
- [ ] T074 [US4] Add logging for reload operations: trigger source, validation result, changed fields, timestamp in reload()
- [ ] T075 [US4] Implement POST /api/v1/config/reload endpoint in proxywhirl/api.py if 003-rest-api active (admin only, manually trigger reload)
- [ ] T076 [US4] Implement SIGHUP signal handler in proxywhirl/config.py to trigger reload() when signal received (optional, for Unix-like systems)
- [ ] T077 [US4] Run `uv run pytest tests/unit/test_file_watching.py tests/integration/test_hot_reload.py tests/integration/test_reload_api.py -v` and verify all tests PASS
- [ ] T078 [US4] Run `uv run mypy --strict proxywhirl/config.py proxywhirl/api.py` and verify 0 errors

**Checkpoint**: User Story 4 complete - hot reload from configuration files works with file watching and manual triggers

---

## Phase 7: User Story 5 - Configuration Export and Backup (Priority: P3)

**Goal**: Export current active configuration (all merged sources and computed defaults) to a file for backup, documentation, or sharing

**Independent Test**: With proxywhirl running with configuration from multiple sources, export the active configuration to a file and verify that the exported file contains all merged settings with credential redaction

### Tests for User Story 5 (TDD)

- [ ] T079 [P] [US5] Create tests/unit/test_config_export.py for export tests (test ConfigurationSnapshot creation, to_yaml() method, credential redaction)
- [ ] T080 [P] [US5] Create tests/integration/test_export_import.py for round-trip tests (test export → import produces same configuration)
- [ ] T081 [P] [US5] Create tests/integration/test_export_api.py for export endpoint tests if 003-rest-api active (test GET /api/v1/config/export endpoint)
- [ ] T082 [US5] Run `uv run pytest tests/unit/test_config_export.py tests/integration/test_export_import.py tests/integration/test_export_api.py -v` and verify all tests FAIL

### Implementation for User Story 5

- [ ] T083 [US5] Implement export_config() method in ConfigurationManager to create ConfigurationSnapshot and return YAML string
- [ ] T084 [US5] Implement export_config_to_file(path) method in ConfigurationManager to write snapshot to file
- [ ] T085 [US5] Ensure ConfigurationSnapshot.from_config() properly redacts SecretStr fields as "*** REDACTED ***"
- [ ] T086 [US5] Ensure ConfigurationSnapshot.to_yaml() includes source attribution comments for each field
- [ ] T087 [US5] Implement GET /api/v1/config/export endpoint in proxywhirl/api.py if 003-rest-api active (supports format=yaml or format=json query param)
- [ ] T088 [US5] Implement GET /api/v1/config endpoint in proxywhirl/api.py if 003-rest-api active (any authenticated user, returns current config with sources and hot_reloadable flags)
- [ ] T089 [US5] Run `uv run pytest tests/unit/test_config_export.py tests/integration/test_export_import.py tests/integration/test_export_api.py -v` and verify all tests PASS
- [ ] T090 [US5] Run `uv run mypy --strict proxywhirl/config.py proxywhirl/api.py` and verify 0 errors

**Checkpoint**: User Story 5 complete - configuration export works with credential redaction and source attribution

---

## Phase 8: Concurrent Update Handling (Additional Requirement from Clarifications)

**Goal**: Handle concurrent configuration update requests with last-write-wins semantics, conflict detection, and operator notification

**Independent Test**: Simulate concurrent configuration updates and verify that last-write-wins is applied, conflicts are logged, and operators are notified

### Tests for Concurrent Updates (TDD)

- [ ] T091 [P] Create tests/unit/test_concurrent_updates.py for concurrency tests (test last-write-wins, conflict detection, ConfigUpdate.conflicts_with())
- [ ] T092 [P] Create tests/integration/test_config_history.py for history tracking tests (test update history, conflict notifications)
- [ ] T093 [P] Create tests/integration/test_config_history_api.py for history endpoint tests if 003-rest-api active (test GET /api/v1/config/history endpoint)
- [ ] T094 Run `uv run pytest tests/unit/test_concurrent_updates.py tests/integration/test_config_history.py tests/integration/test_config_history_api.py -v` and verify all tests FAIL

### Implementation for Concurrent Updates

- [ ] T095 Add _config_version and _recent_updates attributes to ConfigurationManager.__init__()
- [ ] T096 Update update_runtime_config() in ConfigurationManager to create ConfigUpdate record with version, timestamp, user info
- [ ] T097 Implement conflict detection in update_runtime_config(): check _recent_updates for overlapping keys within 5-second window
- [ ] T098 Implement _notify_config_conflict(original, overwriting, overlapping_keys) method in ConfigurationManager to log conflict warnings
- [ ] T099 Implement _cleanup_old_updates() method in ConfigurationManager to remove updates older than 1 hour
- [ ] T100 Implement get_config_history(limit, since) method in ConfigurationManager to return recent ConfigUpdate records
- [ ] T101 Implement GET /api/v1/config/history endpoint in proxywhirl/api.py if 003-rest-api active (admin only, query params: limit, since)
- [ ] T102 Run `uv run pytest tests/unit/test_concurrent_updates.py tests/integration/test_config_history.py tests/integration/test_config_history_api.py -v` and verify all tests PASS
- [ ] T103 Run `uv run mypy --strict proxywhirl/config.py proxywhirl/api.py` and verify 0 errors

**Checkpoint**: Concurrent update handling complete - conflicts detected, logged, and operators notified

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, documentation, and final quality checks

- [ ] T104 [P] Add comprehensive docstrings to all public methods in proxywhirl/config.py and proxywhirl/config_models.py
- [ ] T105 [P] Update proxywhirl/__init__.py to export ConfigurationManager, ProxyWhirlSettings, User, ValidationResult, ConfigurationSnapshot
- [ ] T106 [P] Create example configuration file proxywhirl.yaml.example in repository root with all settings documented
- [ ] T107 [P] Add configuration management section to README.md with quickstart examples
- [ ] T108 Run complete test suite: `uv run pytest tests/ --cov=proxywhirl --cov-report=html --cov-report=term`
- [ ] T109 Verify coverage ≥85% overall, 100% for config_models.py credential handling and validation
- [ ] T110 Run `uv run mypy --strict proxywhirl/` and verify 0 errors across all modules
- [ ] T111 Run `uv run ruff check proxywhirl/` and verify 0 linting errors
- [ ] T112 Run `uv run ruff format proxywhirl/` to format all configuration management code
- [ ] T113 Validate all examples from specs/012-configuration-management-flexible/quickstart.md work correctly
- [ ] T114 Update CHANGELOG.md with configuration management feature description and all 5 user stories
- [ ] T115 Create migration guide for existing users in docs/configuration-migration-guide.md if breaking changes

**Checkpoint**: Configuration management feature complete, tested, documented, and ready for deployment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1): Multi-source loading - Can start after Foundational
  - User Story 2 (P1): Runtime updates - Can start after Foundational (builds on US1 but independently testable)
  - User Story 3 (P2): Validation - Can start after Foundational (enhances US1/US2 but independent)
  - User Story 4 (P2): Hot reload - Can start after US1 complete (needs multi-source loading)
  - User Story 5 (P3): Export - Can start after US1 complete (needs configuration to export)
- **Concurrent Updates (Phase 8)**: Depends on US2 completion (extends runtime updates)
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Foundation only - No other story dependencies (MVP)
- **US2 (P1)**: Foundation + US1 (uses configuration loading) - Independently testable
- **US3 (P2)**: Foundation only - Independent enhancement
- **US4 (P2)**: Foundation + US1 (needs multi-source loading for reload)
- **US5 (P3)**: Foundation + US1 (needs configuration to export)
- **Concurrent Updates**: US2 (extends runtime update logic)

### Within Each User Story

1. Tests MUST be written and verified to FAIL before implementation
2. Models/data structures before business logic
3. Core functionality before API endpoints
4. Unit tests before integration tests
5. Story complete and independently verified before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: All tasks can run in parallel (T001-T003 are independent dependency additions)
- **Phase 2 (Foundational)**: Tasks T008, T009, T010, T018, T020 can run in parallel (different model definitions)
- **Within User Stories**: All test tasks marked [P] can run in parallel, all model tasks marked [P] can run in parallel
- **User Stories**: Once Foundational complete, if team has capacity:
  - US1 and US3 can start in parallel (both depend only on Foundation)
  - After US1 completes: US2, US4, US5 can all work in parallel
- **Phase 9 (Polish)**: Tasks T103, T104, T105, T106 can run in parallel (different files)

---

## Parallel Example: User Story 1

```bash
# After Foundational phase complete, launch all US1 tests in parallel:
Task T023: "tests/unit/test_config_models.py" 
Task T024: "tests/unit/test_config_loading.py"
Task T025: "tests/integration/test_multi_source_config.py"
Task T026: "tests/property/test_config_merging.py"

# Verify all fail with: uv run pytest <all-test-files> -v

# Then implement in sequence (dependencies on previous tasks)
# Then verify all pass with: uv run pytest <all-test-files> -v
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2 Only)

1. Complete Phase 1: Setup (T001-T007) - ~1 hour
2. Complete Phase 2: Foundational (T008-T022) - ~4 hours
3. Complete Phase 3: User Story 1 (T023-T037) - ~6 hours
4. Complete Phase 4: User Story 2 (T038-T051) - ~6 hours
5. **STOP and VALIDATE**: Test US1+US2 independently
6. Deploy/demo if ready - Core configuration management functional

**MVP Scope**: Multi-source configuration loading + runtime updates (admin-only) = production-ready configuration management

### Incremental Delivery

1. **Foundation Ready** (Phase 1-2): All data models defined → ~5 hours
2. **MVP** (Add US1+US2): Multi-source loading + runtime updates → +12 hours = ~17 hours total
3. **Validation Enhanced** (Add US3): Configuration validation → +6 hours = ~23 hours total
4. **Hot Reload** (Add US4): File watching and reload → +6 hours = ~29 hours total
5. **Complete** (Add US5 + Concurrent + Polish): Export + conflict handling + polish → +8 hours = ~37 hours total

### Parallel Team Strategy

With 3 developers after Foundation complete:

1. **Developer A**: User Story 1 (multi-source loading) - ~6 hours
2. **Developer B**: User Story 3 (validation) - ~6 hours (parallel with A, no dependencies)
3. **Developer C**: Setup documentation and examples - ~3 hours

After US1 complete:

4. **Developer A**: User Story 2 (runtime updates) - ~6 hours
5. **Developer B**: User Story 4 (hot reload) - ~6 hours (parallel with A)
6. **Developer C**: User Story 5 (export) - ~4 hours (parallel with A/B)

Then concurrent updates and polish together: ~6 hours

**Total Timeline with 3 Developers**: ~20 hours (vs 37 hours sequential)

---

## Task Summary

- **Total Tasks**: 115 (increased by 1 for SIGHUP signal handler)
- **Setup Tasks**: 7 (Phase 1)
- **Foundational Tasks**: 15 (Phase 2)
- **User Story 1**: 15 tasks (5 tests + 10 implementation)
- **User Story 2**: 14 tasks (4 tests + 10 implementation)
- **User Story 3**: 13 tasks (4 tests + 9 implementation)
- **User Story 4**: 14 tasks (4 tests + 10 implementation, including SIGHUP handler)
- **User Story 5**: 12 tasks (4 tests + 8 implementation)
- **Concurrent Updates**: 13 tasks (4 tests + 9 implementation)
- **Polish**: 12 tasks

**Test Coverage Target**: 85%+ overall, 100% for credential handling and validation  
**Type Safety Target**: mypy --strict with 0 errors  
**Parallel Opportunities**: ~35 tasks can run in parallel (marked with [P])

**Constitutional Compliance**: All tasks aligned with 7 principles (Library-First, Test-First, Type Safety, Independent Stories, Performance, Security, Simplicity)

---

## Notes

- All tasks include exact file paths for clarity
- [P] marker indicates tasks that can run in parallel (different files, no dependencies)
- [Story] label maps tasks to user stories for traceability and independent testing
- Each user story is independently completable and testable
- TDD enforced: Tests must FAIL before implementation, then PASS after
- Security: 100% credential redaction tested (SecretStr in exports, logs, errors)
- Performance: Configuration loading <500ms, runtime updates <1s, hot reload <2s, validation <100ms
- Stop at any checkpoint to validate story independently before proceeding
