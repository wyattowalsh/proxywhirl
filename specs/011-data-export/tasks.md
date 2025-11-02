---

description: "Task list for Data Export & Reporting implementation"
---

# Tasks: Data Export & Reporting

**Input**: Design documents from `/specs/011-data-export/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/export-api.yaml, quickstart.md

**Tests**: Test tasks are included for TDD workflow (constitution requirement)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `proxywhirl/`, `tests/` at repository root
- Flat package structure (constitutional requirement)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [ ] T001 Add export dependencies to pyproject.toml: `uv add pandas>=2.0.0 openpyxl>=3.1.0 reportlab>=4.0.0 apscheduler>=3.10.0`
- [ ] T002 [P] Create proxywhirl/export_models.py with Pydantic models for ExportJob, ExportTemplate, ImportJob, ExportManifest, ScheduledExport, ExportAuditLog
- [ ] T003 [P] Create proxywhirl/export.py with ExportManager class skeleton
- [ ] T004 [P] Create proxywhirl/import.py with ImportManager class skeleton
- [ ] T005 [P] Create proxywhirl/scheduled_export.py with ScheduledExportManager class skeleton
- [ ] T006 Create examples/export_examples.py file for usage demonstrations

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Extend proxywhirl/storage.py with export_jobs table schema and CRUD methods
- [ ] T008 Extend proxywhirl/storage.py with export_templates table schema and CRUD methods
- [ ] T009 Extend proxywhirl/storage.py with import_jobs table schema and CRUD methods
- [ ] T010 Extend proxywhirl/storage.py with scheduled_exports table schema and CRUD methods
- [ ] T011 Extend proxywhirl/storage.py with export_audit_logs table schema and CRUD methods
- [ ] T012 Create proxywhirl/cache_crypto.py with credential encryption/decryption functions (reuse SecretStr patterns from 001-core)
- [ ] T013 Implement file storage helpers in proxywhirl/export.py: create_export_directory(), generate_export_path(), cleanup_old_exports()
- [ ] T014 Implement access control function can_access_export() in proxywhirl/export.py
- [ ] T015 Configure NotificationSettings in proxywhirl/config.py: SMTP host, port, credentials, from_email
- [ ] T016 Update proxywhirl/__init__.py to export ExportManager, ImportManager, ScheduledExportManager

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Export/Import Proxy Pool Configuration (Priority: P1) 🎯 MVP

**Goal**: Enable users to export proxy pool configuration (with encrypted credentials) and import it for backup, migration, or sharing purposes.

**Independent Test**: Export a proxy pool with 10 proxies to JSON, then import it in a fresh environment and verify all proxies, credentials, and metadata are restored correctly.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T017 [P] [US1] Create tests/unit/test_export_pool.py with test cases for export_pool() method (JSON format, credential modes: full/sanitized/reference, compression)
- [ ] T018 [P] [US1] Create tests/unit/test_import_pool.py with test cases for import_pool() method (validation, duplicate detection, credential decryption)
- [ ] T019 [P] [US1] Create tests/integration/test_export_import_cycle.py with roundtrip test (export → save → load → import → verify)

### Implementation for User Story 1

- [ ] T020 [P] [US1] Implement ExportManager.export_pool() in proxywhirl/export.py: serialize pool to JSON, handle credential encryption modes
- [ ] T021 [P] [US1] Implement ExportManifest generation in proxywhirl/export.py: add metadata, version, checksum to exports
- [ ] T022 [US1] Implement compression logic in proxywhirl/export.py: gzip with configurable level (default 6)
- [ ] T023 [US1] Implement ImportManager.validate_import_file() in proxywhirl/import.py: Pydantic schema validation, checksum verification
- [ ] T024 [US1] Implement ImportManager.detect_duplicates() in proxywhirl/import.py: compare import URLs with existing pool
- [ ] T025 [US1] Implement ImportManager.import_pool() in proxywhirl/import.py: create/update proxies, handle duplicate strategies (skip/rename/merge)
- [ ] T026 [US1] Implement credential decryption in proxywhirl/import.py: use master key or user password to decrypt credentials from exports
- [ ] T027 [US1] Add audit logging to export and import operations in proxywhirl/export.py and proxywhirl/import.py
- [ ] T028 [US1] Update examples/export_examples.py with proxy pool export/import examples

**Checkpoint**: At this point, User Story 1 should be fully functional - users can backup and restore proxy pools

---

## Phase 4: User Story 2 - Export Analytics Data (Priority: P1)

**Goal**: Enable users to export historical analytics data in CSV, JSON, or Excel formats for external analysis.

**Independent Test**: Export 30 days of analytics data to CSV with specific columns, open in Excel, and verify all data is correctly formatted.

### Tests for User Story 2

- [ ] T029 [P] [US2] Create tests/unit/test_export_analytics.py with test cases for export_analytics() method (CSV, JSON, Excel formats, date range filtering, column selection)
- [ ] T030 [P] [US2] Create tests/integration/test_export_formats.py with tests for each format (CSV, JSON, Excel, PDF) and format validation

### Implementation for User Story 2

- [ ] T031 [P] [US2] Implement ExportManager.export_analytics() in proxywhirl/export.py: query analytics data from 009-analytics-engine-analysis
- [ ] T032 [P] [US2] Implement CSV export handler in proxywhirl/export.py: write_csv() with UTF-8 encoding, column selection
- [ ] T033 [P] [US2] Implement JSON export handler in proxywhirl/export.py: write_json() with ISO timestamp formatting
- [ ] T034 [US2] Implement Excel export handler in proxywhirl/export.py: write_excel() using pandas + openpyxl, support multiple sheets
- [ ] T035 [US2] Implement export size estimation in proxywhirl/export.py: calculate record count × average record size per format, display estimate to users
- [ ] T036 [US2] Implement async export processing in proxywhirl/export.py: background thread for exports >10MB, progress tracking
- [ ] T037 [US2] Add notification support in proxywhirl/export.py: send_email_notification(), send_webhook_notification(), create_inapp_notification()
- [ ] T038 [US2] Implement retry mechanism for failed exports in proxywhirl/export.py: exponential backoff, configurable max retries, log failures
- [ ] T039 [US2] Update examples/export_examples.py with analytics export examples

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - full backup and analytics export capabilities

---

## Phase 5: User Story 3 - Schedule Automated Exports (Priority: P2)

**Goal**: Enable users to schedule regular automated exports without manual intervention.

**Independent Test**: Configure a daily export schedule, wait for scheduled time, and verify export file is automatically generated with correct timestamp.

### Tests for User Story 3

- [ ] T040 [P] [US3] Create tests/unit/test_scheduled_export.py with test cases for schedule_export(), start(), stop(), and retry logic
- [ ] T041 [P] [US3] Create tests/integration/test_scheduled_export_execution.py with tests for scheduled job execution and failure recovery

### Implementation for User Story 3

- [ ] T042 [P] [US3] Implement ScheduledExportManager.__init__() in proxywhirl/scheduled_export.py: configure BackgroundScheduler with SQLAlchemyJobStore
- [ ] T043 [US3] Implement ScheduledExportManager.schedule_export() in proxywhirl/scheduled_export.py: add job with cron trigger
- [ ] T044 [US3] Implement ScheduledExportManager.execute_scheduled_export() in proxywhirl/scheduled_export.py: run export using template settings
- [ ] T045 [US3] Implement ScheduledExportManager.start() and stop() in proxywhirl/scheduled_export.py: scheduler lifecycle management
- [ ] T046 [US3] Implement failure handling in proxywhirl/scheduled_export.py: email admin on failure, exponential backoff retry
- [ ] T047 [US3] Implement ScheduledExportManager CRUD operations in proxywhirl/scheduled_export.py: list_schedules(), update_schedule(), delete_schedule()
- [ ] T048 [US3] Update examples/export_examples.py with scheduled export examples

**Checkpoint**: All automated export capabilities functional - users can set and forget

---

## Phase 6: User Story 4 - Export Health Check Reports (Priority: P2)

**Goal**: Enable users to export detailed health check reports as PDFs with charts and trend analysis.

**Independent Test**: Export a 7-day health report for all proxies, open PDF, and verify availability charts, failure patterns, and response time distributions are present.

### Tests for User Story 4

- [ ] T049 [P] [US4] Create tests/unit/test_export_health.py with test cases for export_health_report() method (PDF generation, chart rendering)
- [ ] T050 [P] [US4] Create tests/integration/test_pdf_generation.py with PDF validation tests (reportlab output, page count, chart presence)

### Implementation for User Story 4

- [ ] T051 [P] [US4] Implement ExportManager.export_health_report() in proxywhirl/export.py: query health data from 006-health-monitoring-continuous
- [ ] T052 [P] [US4] Implement PDF report generator in proxywhirl/export.py: create_pdf_document() using reportlab.platypus
- [ ] T053 [US4] Implement chart generators in proxywhirl/export.py: create_availability_chart(), create_response_time_chart(), create_failure_pattern_chart() using reportlab.graphics
- [ ] T054 [US4] Implement PDF styling in proxywhirl/export.py: apply branding (logo, colors, fonts) from config
- [ ] T055 [US4] Add PDF-specific metadata to ExportManifest in proxywhirl/export.py
- [ ] T056 [US4] Update examples/export_examples.py with health report PDF examples

**Checkpoint**: Health reporting capabilities complete - users can generate executive-ready reports

---

## Phase 7: User Story 5 - Export Custom Metric Dashboards (Priority: P3)

**Goal**: Enable users to export customized dashboard views as PDFs for presentations and executive briefings.

**Independent Test**: Create a custom dashboard with specific metrics and date ranges, export as PDF, and verify layout matches on-screen view.

### Tests for User Story 5

- [ ] T057 [P] [US5] Create tests/unit/test_export_dashboard.py with test cases for export_dashboard() method (custom filters, chart selections)
- [ ] T058 [P] [US5] Create tests/integration/test_dashboard_pdf.py with visual fidelity tests

### Implementation for User Story 5

- [ ] T059 [P] [US5] Implement ExportManager.export_dashboard() in proxywhirl/export.py: render custom dashboard to PDF
- [ ] T060 [US5] Implement dashboard chart rendering in proxywhirl/export.py: support pie charts, bar charts, line charts from dashboard config
- [ ] T061 [US5] Implement filter indicator rendering in proxywhirl/export.py: show applied filters in PDF header
- [ ] T062 [US5] Add branding to dashboard PDFs in proxywhirl/export.py: company logo, custom colors
- [ ] T063 [US5] Update examples/export_examples.py with dashboard export examples

**Checkpoint**: All user stories should now be independently functional - complete export/reporting suite

---

## Phase 8: REST API Integration (if 003-rest-api active)

**Purpose**: Expose export/import functionality via REST endpoints

- [ ] T064 [P] Extend proxywhirl/api_models.py with CreateExportRequest, ExportJobResponse, ImportFileRequest models
- [ ] T065 Create POST /api/v1/exports endpoint in proxywhirl/api.py: create export job
- [ ] T066 Create GET /api/v1/exports endpoint in proxywhirl/api.py: list export jobs with filters
- [ ] T067 Create GET /api/v1/exports/{export_id} endpoint in proxywhirl/api.py: get export job status
- [ ] T068 Create GET /api/v1/exports/{export_id}/download endpoint in proxywhirl/api.py: download export file with access control
- [ ] T069 Create DELETE /api/v1/exports/{export_id} endpoint in proxywhirl/api.py: delete export job
- [ ] T070 Create POST /api/v1/imports endpoint in proxywhirl/api.py: upload and import file (multipart/form-data)
- [ ] T071 Create GET /api/v1/imports/{import_id} endpoint in proxywhirl/api.py: get import job status
- [ ] T072 Create POST /api/v1/export-templates endpoint in proxywhirl/api.py: create template
- [ ] T073 Create GET /api/v1/export-templates endpoint in proxywhirl/api.py: list templates
- [ ] T074 Create GET /api/v1/export-templates/{template_id} endpoint in proxywhirl/api.py: get template
- [ ] T075 Create PUT /api/v1/export-templates/{template_id} endpoint in proxywhirl/api.py: update template
- [ ] T076 Create DELETE /api/v1/export-templates/{template_id} endpoint in proxywhirl/api.py: delete template
- [ ] T077 Create POST /api/v1/scheduled-exports endpoint in proxywhirl/api.py: create scheduled export
- [ ] T078 Create GET /api/v1/scheduled-exports endpoint in proxywhirl/api.py: list schedules
- [ ] T079 Create GET /api/v1/scheduled-exports/{schedule_id} endpoint in proxywhirl/api.py: get schedule
- [ ] T080 Create PUT /api/v1/scheduled-exports/{schedule_id} endpoint in proxywhirl/api.py: update schedule
- [ ] T081 Create DELETE /api/v1/scheduled-exports/{schedule_id} endpoint in proxywhirl/api.py: delete schedule
- [ ] T082 Create GET /api/v1/audit-logs endpoint in proxywhirl/api.py: query audit logs with filters
- [ ] T083 [P] Create tests/integration/test_export_api.py with API endpoint tests

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T084 [P] Add comprehensive docstrings to all export/import functions in proxywhirl/export.py, proxywhirl/import.py, proxywhirl/scheduled_export.py
- [ ] T085 [P] Create tests/unit/test_retention_policy.py with test cases for age-based cleanup, storage limit enforcement, and expired export deletion
- [ ] T086 [P] Create tests/property/test_export_integrity.py with hypothesis-based property tests for data integrity
- [ ] T087 [P] Create tests/integration/test_export_compression.py with compression ratio and performance tests
- [ ] T088 Run `uv run pytest tests/ --cov=proxywhirl` and verify 85%+ coverage (100% for credential handling)
- [ ] T089 Run `uv run mypy --strict proxywhirl/` and fix all type errors
- [ ] T090 Run `uv run ruff check proxywhirl/` and `uv run ruff format proxywhirl/` to ensure code quality
- [ ] T091 Update main README.md with export/import quickstart section
- [ ] T092 Validate all examples in examples/export_examples.py execute successfully
- [ ] T093 Performance benchmarks: verify export initiation <100ms, analytics export (100K records) <60s, measure CPU/memory overhead vs baseline
- [ ] T094 Security audit: verify 100% credential protection (no plain text in exports/logs/errors)
- [ ] T095 Run quickstart.md validation: execute all code examples and verify outputs

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (Export/Import Pool): Can start after Foundational - No dependencies on other stories
  - US2 (Export Analytics): Can start after Foundational - No dependencies on other stories (parallel with US1)
  - US3 (Scheduled Exports): Depends on US1 and US2 completion (reuses their export logic)
  - US4 (Health Reports): Can start after Foundational - No dependencies on other stories (parallel with US1/US2)
  - US5 (Dashboard Exports): Can start after Foundational - No dependencies on other stories (parallel with US1/US2/US4)
- **REST API Integration (Phase 8)**: Depends on at least US1 and US2 being complete (can proceed before US3/US4/US5)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

```
Foundational (Phase 2) [BLOCKING - Must complete first]
├── US1 (P1): Export/Import Pool [Independent - can start immediately after Foundational]
├── US2 (P1): Export Analytics [Independent - can start immediately after Foundational, parallel with US1]
├── US3 (P2): Scheduled Exports [Depends on US1 + US2 completion]
├── US4 (P2): Health Reports [Independent - can start immediately after Foundational, parallel with US1/US2]
└── US5 (P3): Dashboard Exports [Independent - can start immediately after Foundational, parallel with US1/US2/US4]
```

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD - constitutional requirement)
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

#### Setup Phase (Phase 1)
All tasks T002-T006 marked [P] can run in parallel

#### Foundational Phase (Phase 2)
- T007-T011 (database tables) can run in parallel
- T012 (crypto) can run in parallel with database work
- T013-T015 can run in parallel after T007-T011 complete
- T016 runs last (depends on all modules)

#### User Story Tests
Within each story, all test tasks marked [P] can run in parallel

#### User Story Implementation
Within each story, tasks marked [P] can run in parallel:
- US1: T020, T021 can run in parallel
- US2: T031, T032, T033 can run in parallel
- US4: T049, T050 can run in parallel
- US5: T057 can run in parallel with other US5 tasks

#### Cross-Story Parallelism
After Foundational phase:
- US1, US2, US4, US5 can all start in parallel (independent stories)
- US3 waits for US1 + US2 completion

#### REST API Phase (Phase 8)
- T062 can run in parallel with T063-T080
- T063-T080 (endpoint creation) can be split among developers (different files)
- T081 (tests) runs after endpoints complete

#### Polish Phase (Phase 9)
- T082, T083, T084 can run in parallel
- T085-T091 run sequentially (quality gates)
- T092 runs last (validation)

---

## Parallel Example: User Story 1

```bash
# Phase: Tests (run first, in parallel):
[T017] tests/unit/test_export_pool.py
[T018] tests/unit/test_import_pool.py  
[T019] tests/integration/test_export_import_cycle.py

# Phase: Core implementation (after tests, in parallel):
[T020] ExportManager.export_pool()
[T021] ExportManifest generation

# Phase: Sequential (depends on T020-T021):
[T022] Compression logic
[T023] validate_import_file()
[T024] detect_duplicates()
[T025] import_pool()
[T026] Credential decryption
[T027] Audit logging
[T028] Examples
```

---

## Parallel Example: Cross-Story (After Foundational)

```bash
# All independent stories can start together:
Developer A: US1 (Export/Import Pool) - T017-T028
Developer B: US2 (Export Analytics) - T029-T037
Developer C: US4 (Health Reports) - T047-T054
Developer D: US5 (Dashboard Exports) - T055-T061

# Then when US1+US2 complete:
Developer A or B: US3 (Scheduled Exports) - T038-T046
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T016) - **CRITICAL BLOCKING PHASE**
3. Complete Phase 3: User Story 1 (T017-T028)
4. Complete Phase 4: User Story 2 (T029-T037)
5. **STOP and VALIDATE**: Test US1 and US2 independently
6. Deploy/demo if ready (core export/import + analytics export)

**MVP Scope**: Proxy pool backup/restore + analytics data export (addresses primary user needs)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T016)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP: Backup capability)
3. Add User Story 2 → Test independently → Deploy/Demo (MVP: Analytics export)
4. Add User Story 3 → Test independently → Deploy/Demo (Automation layer)
5. Add User Story 4 → Test independently → Deploy/Demo (Health reporting)
6. Add User Story 5 → Test independently → Deploy/Demo (Executive reports)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. **Week 1**: Team completes Setup + Foundational together (T001-T016)
2. **Week 2-3**: Once Foundational is done:
   - Developer A: User Story 1 (T017-T028)
   - Developer B: User Story 2 (T029-T037)
   - Developer C: User Story 4 (T047-T054)
   - Developer D: User Story 5 (T055-T061)
3. **Week 4**: 
   - Developer A or B: User Story 3 (T038-T046) - after US1+US2 complete
   - Others: Start REST API integration (T062-T081)
4. **Week 5**: Polish phase (T082-T092)

### Quality Gates

After each user story completion, run:
```bash
uv run pytest tests/unit/test_[story]*.py tests/integration/test_[story]*.py
uv run mypy --strict proxywhirl/
uv run ruff check proxywhirl/
```

After all stories complete, run full quality gate:
```bash
uv run pytest tests/ --cov=proxywhirl  # Target: 85%+ overall, 100% credential
uv run mypy --strict proxywhirl/       # Target: 0 errors
uv run ruff check proxywhirl/          # Target: 0 errors
uv run ruff format proxywhirl/         # Auto-format
```

---

## Task Count Summary

- **Phase 1 (Setup)**: 6 tasks
- **Phase 2 (Foundational)**: 10 tasks (BLOCKING)
- **Phase 3 (US1 - P1)**: 12 tasks (MVP - Export/Import Pool)
- **Phase 4 (US2 - P1)**: 10 tasks (MVP - Export Analytics, includes size estimation and retry logic)
- **Phase 5 (US3 - P2)**: 9 tasks (Scheduled Exports)
- **Phase 6 (US4 - P2)**: 8 tasks (Health Reports)
- **Phase 7 (US5 - P3)**: 7 tasks (Dashboard Exports)
- **Phase 8 (REST API)**: 20 tasks (API integration)
- **Phase 9 (Polish)**: 12 tasks (Quality & docs, includes retention tests)

**Total**: 94 tasks

**MVP Scope (US1 + US2)**: 38 tasks (Phase 1 + Phase 2 + Phase 3 + Phase 4)

**Parallel Opportunities**: 
- 5 tasks in Setup
- 5 tasks in Foundational
- 9 test tasks across user stories
- 16 implementation tasks across user stories
- 4 independent user stories (US1, US2, US4, US5) can proceed in parallel after Foundational

---

## Notes

- **[P] tasks** = different files, no dependencies - can run in parallel
- **[Story] label** maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD Required**: Verify tests fail before implementing (constitutional requirement)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **All Python commands MUST use `uv run` prefix** (constitutional requirement)
- **Mypy --strict** must pass with 0 errors (constitutional requirement)
- **Credential security** requires 100% test coverage (constitutional requirement)
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
