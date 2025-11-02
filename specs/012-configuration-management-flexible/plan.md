# Implementation Plan: Configuration Management

**Branch**: `012-configuration-management-flexible` | **Date**: 2025-11-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/012-configuration-management-flexible/spec.md`

## Summary

Implement comprehensive configuration management for proxywhirl, enabling flexible multi-source configuration loading (environment variables, YAML files, CLI arguments), runtime configuration updates with zero downtime, validation with schema enforcement, hot reload capabilities, and configuration export/backup functionality. The system will use pydantic-settings for schema definition and validation, support role-based authorization for configuration updates (admin-only write), and handle concurrent updates with last-write-wins semantics and conflict notification.

## Technical Context

**Language/Version**: Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13)  
**Primary Dependencies**: 
- `pydantic-settings>=2.0.0` (multi-source configuration with validation)
- `pyyaml>=6.0` (YAML file parsing)
- `watchdog>=3.0.0` (filesystem events for config file watching)
- Existing: `pydantic>=2.0.0`, `loguru>=0.7.0`

**Storage**: SQLite (optional - for configuration change audit logs), filesystem (YAML config files)  
**Testing**: pytest with hypothesis for property-based validation tests  
**Target Platform**: Linux/macOS/Windows servers (Python cross-platform)  
**Project Type**: Single library project (flat package structure per constitution)  
**Performance Goals**: 
- Configuration loading <500ms for 100 settings
- Runtime updates take effect <1 second
- Hot reload from file <2 seconds
- Config validation <100ms

**Constraints**: 
- Admin-only authorization for runtime updates
- Concurrent update handling with last-write-wins + notification
- 100% credential redaction in logs and exports
- Hot-reloadable vs restart-required distinction clear

**Scale/Scope**: 
- Support 100+ configuration settings
- Handle concurrent configuration changes
- Multi-source precedence (CLI > ENV > File > Defaults)
- File watching for automatic reload

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### 1. Library-First Architecture ✅
- **Status**: PASS
- **Evidence**: All configuration functionality accessible via `from proxywhirl.config import ConfigurationManager`
- **Public API**: `ConfigurationManager.load()`, `ConfigurationManager.update()`, `ConfigurationManager.reload()`, `ConfigurationManager.export()`
- **No CLI/Web Dependencies**: Pure Python functions, configuration can be loaded programmatically

### 2. Test-First Development ✅
- **Status**: PASS (enforcement in Phase 2)
- **Target Coverage**: 85%+ overall, 100% for validation and credential redaction
- **Test Strategy**: 
  - Unit tests for multi-source loading, precedence, validation
  - Integration tests for hot reload, file watching, export/import
  - Property tests for configuration merging and conflict detection
- **TDD Checkpoint**: Tests written before implementation in tasks.md

### 3. Type Safety ✅
- **Status**: PASS
- **Enforcement**: Mypy --strict for all new modules
- **Pydantic Models**: ConfigurationSchema, ConfigurationSource, ConfigurationSnapshot, ConfigurationUpdate, ValidationResult
- **SecretStr**: Configuration values containing credentials (API keys, passwords)

### 4. Independent User Stories ✅
- **Status**: PASS
- **US1** (P1): Multi-source configuration loading - Standalone MVP
- **US2** (P1): Runtime configuration updates - Independent of US3/US4/US5
- **US3** (P2): Configuration validation - Independent of US4/US5
- **US4** (P2): Hot reload from files - Builds on US1 but independent of US3/US5
- **US5** (P3): Configuration export - Independent enhancement

### 5. Performance Standards ✅
- **Status**: PASS
- **Configuration loading**: <500ms for 100 settings (SC-006)
- **Runtime updates**: <1 second to take effect (SC-003)
- **Hot reload**: <2 seconds (SC-004)
- **Validation**: <100ms for typical configs

### 6. Security-First ✅
- **Status**: PASS
- **Credential Protection**: 
  - SecretStr for sensitive config values
  - 100% redaction in logs and error messages (SC-008)
  - Admin-only authorization for runtime updates (clarification: role-based)
  - Credentials encrypted or redacted in exports
  - Audit logging for all config changes (FR-013, FR-014)

### 7. Simplicity ✅
- **Status**: PASS
- **Module Count**: +2 new modules (config.py, config_models.py)
- **Total**: 8 core modules + 2 config = 10 modules (at acceptable limit)
- **Flat Architecture**: No sub-packages, single responsibilities
- **Dependencies**: Minimal additions (pydantic-settings, pyyaml, watchdog)

**GATE RESULT**: ✅ **ALL CHECKS PASS** - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/012-configuration-management-flexible/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── config-api.yaml  # REST API endpoints for runtime config (if 003-rest-api active)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
proxywhirl/              # Flat package (no sub-packages)
├── __init__.py          # Add config exports
├── config.py            # NEW: ConfigurationManager class
├── config_models.py     # NEW: Pydantic models (ConfigurationSchema, etc.)
├── models.py            # Existing (may extend for User model with is_admin)
├── api.py               # MODIFY: Add config endpoints (if 003-rest-api active)
├── api_models.py        # MODIFY: Add config API models
└── py.typed             # Existing

tests/
├── unit/
│   ├── test_config_loading.py          # NEW: Multi-source loading tests
│   ├── test_config_precedence.py       # NEW: Precedence rule tests
│   ├── test_config_validation.py       # NEW: Schema validation tests
│   └── test_config_updates.py          # NEW: Runtime update tests
├── integration/
│   ├── test_config_hot_reload.py       # NEW: File reload tests
│   ├── test_config_file_watching.py    # NEW: Automatic reload tests
│   └── test_config_export_import.py    # NEW: Export/import cycle tests
└── property/
    └── test_config_merging.py          # NEW: Property-based merge tests

examples/
└── config_examples.py   # NEW: Usage demonstrations
```

**Structure Decision**: Maintaining flat proxywhirl/ package per constitution. New modules follow single-responsibility principle:
- `config.py`: Configuration management and orchestration
- `config_models.py`: Pydantic models for configuration domain

REST API integration (if needed) extends existing `api.py` from 003-rest-api.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations** - All constitutional principles satisfied. Module count increase justified by:
1. Configuration management is a distinct responsibility (not mergeable with existing modules)
2. Configuration models warrant separate file for clarity
3. Total modules (10) still at acceptable limit
4. Flat architecture maintained

---

## Phase 0: Research & Technical Decisions

**Status**: In Progress

### Research Tasks

1. **pydantic-settings Multi-Source Configuration**
   - **Question**: How to implement multi-source loading with pydantic-settings BaseSettings?
   - **Requirements**: Environment variables, YAML files, CLI args with clear precedence
   - **Deliverable**: Configuration loading pattern with precedence implementation in research.md

2. **YAML File Parsing Strategy**
   - **Question**: PyYAML vs ruamel.yaml for YAML configuration files?
   - **Requirements**: Python 3.9+ compatibility, hierarchical structure support, comments preservation
   - **Deliverable**: Library choice and usage patterns in research.md

3. **Filesystem Watching Implementation**
   - **Question**: watchdog library usage patterns for automatic config reload?
   - **Requirements**: Cross-platform (Linux/macOS/Windows), low overhead, reliable event detection
   - **Deliverable**: File watching implementation approach in research.md

4. **CLI Argument Parsing**
   - **Question**: argparse vs click vs typer for configuration CLI arguments?
   - **Requirements**: Integration with pydantic-settings, type coercion, help generation
   - **Deliverable**: CLI parsing strategy in research.md

5. **Hot Reload Implementation**
   - **Question**: Thread-safe configuration update mechanism?
   - **Requirements**: Atomic updates, rollback on failure, in-flight operation preservation
   - **Deliverable**: Hot reload patterns and thread safety approach in research.md

6. **Configuration Export Format**
   - **Question**: YAML comments annotation for export indicating sources?
   - **Requirements**: Human-readable, source attribution, sensitive value redaction
   - **Deliverable**: Export format and annotation strategy in research.md

7. **Authorization Integration**
   - **Question**: How to integrate admin-only authorization for runtime updates?
   - **Requirements**: Role-based access control, compatible with existing auth (if any)
   - **Deliverable**: Authorization model integration in research.md

8. **Concurrent Update Handling**
   - **Question**: Implementation of last-write-wins with conflict detection?
   - **Requirements**: Conflict logging, operator notification, no blocking/deadlocks
   - **Deliverable**: Concurrency strategy and notification patterns in research.md

### Unknowns to Resolve

- ⚠️ pydantic-settings multi-source patterns (Research needed)
- ⚠️ YAML library choice and features (Research needed)
- ⚠️ watchdog configuration and best practices (Research needed)
- ⚠️ CLI argument integration with pydantic-settings (Research needed)
- ⚠️ Thread-safe hot reload mechanism (Research needed)
- ⚠️ Export format and source attribution (Research needed)
- ⚠️ Admin authorization integration (Research needed)
- ⚠️ Concurrent update conflict notification (Research needed)

**Next**: Generate research.md addressing all unknowns above.

---

## Phase 1: Design & Modeling

✅ **COMPLETE**: All design documents generated based on research outcomes.

### Design Documents

1. ✅ **research.md**: All technical unknowns resolved
   - pydantic-settings with custom SettingsConfigDict for multi-source loading
   - PyYAML with safe_load for configuration files
   - watchdog for cross-platform file watching with 1s debounce
   - argparse (stdlib) for CLI argument parsing
   - Threading lock with atomic configuration swap for hot reload
   - YAML export format with inline source comments
   - Simple User model with is_admin flag for authorization
   - Last-write-wins with conflict logging and notification for concurrent updates

2. ✅ **data-model.md**: Entity definitions and relationships
   - 6 entities defined: ProxyWhirlSettings, ConfigurationSource, ConfigUpdate, User, ValidationResult, ConfigurationSnapshot
   - Complete type safety with Pydantic v2 models
   - 100% mypy --strict compatible
   - Security: SecretStr for credentials, admin authorization model
   - All validation rules documented (ranges, enums, cross-field checks)

3. ✅ **contracts/api-endpoints.md**: REST API specifications (003-rest-api integration)
   - 8 endpoints: GET /config, PATCH /config, POST /validate, GET /export, POST /reload, POST /rollback, GET /history, GET /schema
   - 4 admin-only endpoints (PATCH, POST reload, POST rollback, GET history)
   - Complete request/response schemas with error handling
   - Rate limiting: 100 req/min default, 50 req/min for writes, 20 req/min for exports
   - Integration with existing auth and metrics systems
   - WebSocket support documented for future enhancement

4. ✅ **quickstart.md**: Developer guide with usage examples
   - All 5 user stories demonstrated with working code examples
   - Complete examples for multi-source loading, runtime updates, validation, hot reload, export
   - Integration patterns, testing examples, performance tips
   - Full application example combining all features
   - cURL examples for REST API testing

### Unknowns Resolved

- ✅ pydantic-settings multi-source patterns → Custom SettingsConfigDict with priority-based sources
- ✅ YAML library choice → PyYAML with safe_load (mature, secure, lightweight)
- ✅ watchdog configuration → Cross-platform file watching with 1s debounce
- ✅ CLI argument integration → argparse (stdlib) with type coercion
- ✅ Thread-safe hot reload → Threading lock with atomic configuration swap
- ✅ Export format → YAML with inline source comments and credential redaction
- ✅ Admin authorization → Simple User model with is_admin flag
- ✅ Concurrent updates → Last-write-wins with conflict logging and notification

### Ready for Phase 2

All design documents complete. Next step: Generate tasks.md using `/speckit.tasks` command.

---

## Summary

**Feature**: 012-configuration-management-flexible (Configuration Management)

**Status**: Planning Complete (Phases 0-1 finished)

**Constitutional Compliance**: ✅ All 7 principles passed

**Documents Generated**:
- ✅ spec.md (21 FR, 10 SC, 5 US, 2 clarifications)
- ✅ checklists/requirements.md (all items passed)
- ✅ plan.md (this document)
- ✅ research.md (8 technical decisions resolved)
- ✅ data-model.md (6 entities defined)
- ✅ contracts/api-endpoints.md (8 REST API endpoints)
- ✅ quickstart.md (all 5 user stories with examples)

**Next Action**: Run `/speckit.tasks` to generate implementation tasks (tasks.md)

**Module Impact**: +2 modules (config.py, config_models.py), total 10 modules

**Dependencies**:
- New: pydantic-settings>=2.0.0, pyyaml>=6.0, watchdog>=3.0.0
- Reused: pydantic>=2.0.0, loguru>=0.7.0 (from 001-core-python-package)

**Performance Targets**:
- Configuration loading: <500ms
- Runtime updates: <1s
- Hot reload: <2s
- Validation: <100ms

**Security Requirements**:
- Admin-only write access
- 100% credential redaction (SecretStr)
- Complete audit logging
- Conflict detection and notification
