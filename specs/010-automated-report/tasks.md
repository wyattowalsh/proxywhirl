# Tasks: 010-automated-report

**Feature**: Automated Reporting for Proxy Pool Metrics
**Input**: Design documents from `/specs/010-automated-report/`
**Generated**: 2025-11-02

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- File paths use proxywhirl flat package structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [ ] T001 Add reportlab>=4.0.0 dependency via `uv add reportlab`
- [ ] T002 [P] Add croniter>=2.0.0 dependency via `uv add croniter` (for cron expression parsing)
- [ ] T003 [P] Add python-multipart>=0.0.6 if not present (for file uploads in FastAPI)
- [ ] T004 Create proxywhirl/report_models.py for Pydantic entity definitions
- [ ] T005 Create proxywhirl/reporting.py for core report generation logic
- [ ] T006 Create proxywhirl/report_formatters.py for format-specific output
- [ ] T007 Create proxywhirl/report_scheduler.py for scheduled report management
- [ ] T008 Create proxywhirl/metrics_collector.py for metrics data abstraction
- [ ] T009 Update proxywhirl/__init__.py to export Report, ReportTemplate, ReportSchedule public API

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests (Write FIRST)

- [ ] T010 [P] Create tests/unit/test_report_models.py with test_report_validation_rules
- [ ] T011 [P] Create tests/unit/test_metrics_collector.py with test_abstract_interface
- [ ] T012 [P] Create tests/unit/test_report_formatters.py with test_base_formatter_interface
- [ ] T012b [P] Add test_source_breakdown_formatting to tests/unit/test_report_formatters.py for FR-009

### Core Models (proxywhirl/report_models.py)

- [ ] T013 [P] [FOUNDATION] Implement ReportMetric model (name, value, timestamp, proxy_url, source, labels)
- [ ] T014 [P] [FOUNDATION] Implement Report model (id, name, status, timestamps, file_path, metadata)
- [ ] T015 [P] [FOUNDATION] Implement ReportTemplate model (id, name, metrics, filters, thresholds)
- [ ] T016 [P] [FOUNDATION] Implement ReportSchedule model (id, name, cron_expression, enabled)
- [ ] T017 [P] [FOUNDATION] Implement ReportHistory model (id, report_id, schedule_id, status)
- [ ] T018 [FOUNDATION] Add validation: Report status transitions (generating → completed/failed only)
- [ ] T019 [FOUNDATION] Add validation: ReportTemplate slug name format (^[a-z0-9-]+$)
- [ ] T020 [FOUNDATION] Add validation: ReportSchedule cron expression syntax (using croniter)
- [ ] T021 [FOUNDATION] Add mypy --strict type hints to all models in proxywhirl/report_models.py

### Metrics Abstraction (proxywhirl/metrics_collector.py)

- [ ] T022 [FOUNDATION] Define MetricsDataStore abstract base class with ABC
- [ ] T023 [P] [FOUNDATION] Implement MetricsDataStore.get_proxy_metrics(start, end) -> Iterator[ReportMetric]
- [ ] T024 [P] [FOUNDATION] Implement MetricsDataStore.get_aggregate_stats(start, end) -> Dict
- [ ] T024b [P] [FOUNDATION] Implement MetricsDataStore.get_source_breakdown(start, end) -> Dict[str, Dict] for FR-009
- [ ] T025 [P] [FOUNDATION] Implement MetricsDataStore.get_available_metrics() -> List[str]
- [ ] T026 [FOUNDATION] Create MockMetricsCollector for unit testing (returns fake data)
- [ ] T027 [FOUNDATION] Create InMemoryMetricsCollector using ProxyRotator state (for feature independence)
- [ ] T028 [FOUNDATION] Add generator-based streaming to all metrics methods (<100MB memory)

### Base Formatter (proxywhirl/report_formatters.py)

- [ ] T029 [FOUNDATION] Define ReportFormatter abstract base class with ABC
- [ ] T030 [P] [FOUNDATION] Add ReportFormatter.format(metrics_stream) -> Iterator[bytes] abstract method
- [ ] T031 [P] [FOUNDATION] Add ReportFormatter.get_content_type() -> str abstract method
- [ ] T032 [FOUNDATION] Add ReportFormatter.validate_output(file_path) validation hook

### Database Schema (proxywhirl/storage.py extensions)

- [ ] T033 [FOUNDATION] Add report_history table schema (id, report_id, schedule_id, status, timestamps)
- [ ] T034 [FOUNDATION] Add report_schedules table schema (id, name, cron_expression, enabled, run_count)
- [ ] T035 [FOUNDATION] Add retention_expires_at index for cleanup queries
- [ ] T036 [FOUNDATION] Add schedule next_run_at index for scheduler queries

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Generate On-Demand Reports (Priority: P1) 🎯 MVP

**Goal**: Enable programmatic generation of reports with basic metrics in JSON format

**Independent Test**: Generate JSON report with proxy metrics, verify file creation and valid JSON

### Tests for User Story 1 (Write FIRST) ⚠️

- [ ] T037 [P] [US1] Contract test for POST /api/v1/reports/generate in tests/contract/test_api_reports.py
- [ ] T038 [P] [US1] Integration test for report_generator.generate() in tests/integration/test_report_generation.py
- [ ] T039 [P] [US1] Unit test for JSON formatter in tests/unit/test_json_formatter.py
- [ ] T040 [P] [US1] Property test for time range handling with hypothesis in tests/property/test_report_time_ranges.py

### Implementation for User Story 1

- [ ] T041 [P] [US1] Implement JSONFormatter class in proxywhirl/report_formatters.py
- [ ] T042 [P] [US1] Add JSONFormatter.format(metrics_stream) with streaming json.dumps
- [ ] T043 [US1] Create ReportGenerator class in proxywhirl/reporting.py
- [ ] T044 [US1] Implement ReportGenerator.generate(template, time_range, output_path) method
- [ ] T045 [US1] Add ReportGenerator._collect_metrics(time_range) -> Iterator[ReportMetric]
- [ ] T046 [US1] Add ReportGenerator._write_file(formatter, metrics_stream, output_path)
- [ ] T047 [US1] Add ReportGenerator._update_history(report_id, status, error=None)
- [ ] T048 [US1] Add error handling: insufficient data, invalid time range, IO errors
- [ ] T049 [US1] Add credential redaction in proxy URLs (strip auth before logging)
- [ ] T050 [US1] Add structured logging: generation_started, generation_completed events (loguru)
- [ ] T051 [US1] Verify tests pass: uv run pytest tests/integration/test_report_generation.py
- [ ] T051b [US1] Add integration test for rotation strategy metrics in tests/integration/test_strategy_metrics.py for FR-018

**Checkpoint**: At this point, User Story 1 should be fully functional - can generate JSON reports programmatically

---

## Phase 4: User Story 2 - Multiple Output Formats (Priority: P2)

**Goal**: Support CSV, HTML, and PDF output formats with same metrics data

**Independent Test**: Generate same report in all 4 formats (JSON, CSV, HTML, PDF), verify valid output

### Tests for User Story 2 (Write FIRST) ⚠️

- [ ] T052 [P] [US2] Unit test for CSVFormatter in tests/unit/test_csv_formatter.py
- [ ] T053 [P] [US2] Unit test for HTMLFormatter in tests/unit/test_html_formatter.py
- [ ] T054 [P] [US2] Unit test for PDFFormatter in tests/unit/test_pdf_formatter.py
- [ ] T055 [US2] Integration test for multi-format generation in tests/integration/test_multi_format.py

### Implementation for User Story 2

- [ ] T056 [P] [US2] Implement CSVFormatter class in proxywhirl/report_formatters.py
- [ ] T057 [P] [US2] Add CSVFormatter.format() using csv.DictWriter with streaming
- [ ] T058 [US2] Implement HTMLFormatter class in proxywhirl/report_formatters.py
- [ ] T059 [US2] Create Jinja2 HTML templates in templates/reports/ directory (repository root, not in package)
- [ ] T060 [US2] Add HTMLFormatter.format() with Jinja2 rendering and autoescaping
- [ ] T061 [US2] Implement PDFFormatter class in proxywhirl/report_formatters.py
- [ ] T062 [US2] Add PDFFormatter.format() using reportlab with streaming table generation
- [ ] T063 [US2] Add PDFFormatter._render_table(metrics_stream) for paginated tables
- [ ] T064 [US2] Update ReportGenerator to select formatter based on output_format parameter
- [ ] T065 [US2] Add MIME type detection in ReportGenerator._get_formatter(format)
- [ ] T066 [US2] Add format validation: reject unsupported formats with clear error
- [ ] T067 [US2] Verify tests pass: uv run pytest tests/integration/test_multi_format.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - all formats supported

---

## Phase 5: User Story 3 - Scheduled Report Generation (Priority: P3)

**Goal**: Automate report generation on cron schedules with retry logic

**Independent Test**: Create schedule, trigger manually, verify report generated and next_run_at updated

### Tests for User Story 3 (Write FIRST) ⚠️

- [ ] T068 [P] [US3] Contract test for POST /api/v1/reports/schedules in tests/contract/test_api_schedules.py
- [ ] T069 [P] [US3] Integration test for schedule execution in tests/integration/test_schedule_execution.py
- [ ] T070 [P] [US3] Unit test for cron expression parsing in tests/unit/test_schedule_cron.py
- [ ] T071 [US3] Property test for retry logic with hypothesis in tests/property/test_schedule_retry.py

### Implementation for User Story 3

- [ ] T072 [US3] Create ReportScheduler class in proxywhirl/report_scheduler.py
- [ ] T073 [US3] Implement ReportScheduler._schedule_loop() background thread with threading.Timer
- [ ] T074 [US3] Add ReportScheduler.start() to initialize scheduler thread
- [ ] T075 [US3] Add ReportScheduler.stop() with graceful shutdown (join threads)
- [ ] T076 [US3] Add ReportScheduler._fetch_due_schedules() query from report_schedules table
- [ ] T077 [US3] Add ReportScheduler._execute_schedule(schedule) -> Report method
- [ ] T078 [US3] Add ReportScheduler._calculate_next_run(cron_expression) using croniter
- [ ] T079 [US3] Add ReportScheduler._update_schedule_state(schedule_id, last_run, next_run)
- [ ] T080 [US3] Add retry logic: exponential backoff with max_retries from schedule config
- [ ] T081 [US3] Add retry logic: increment failure_count, disable schedule if max_retries exceeded
- [ ] T082 [US3] Add schedule persistence: save schedules to report_schedules table (SQLite)
- [ ] T083 [US3] Add schedule CRUD operations: create, read, update, delete, list
- [ ] T084 [US3] Add manual trigger: ReportScheduler.trigger_now(schedule_id) method
- [ ] T085 [US3] Add structured logging: schedule_executed, schedule_failed, schedule_disabled events
- [ ] T086 [US3] Add concurrency control: ThreadPoolExecutor with max_workers=3
- [ ] T087 [US3] Verify tests pass: uv run pytest tests/integration/test_schedule_execution.py

**Checkpoint**: At this point, all three user stories (1, 2, 3) should work independently - scheduling operational

---

## Phase 6: User Story 4 - Custom Report Templates (Priority: P3)

**Goal**: Allow users to create custom templates with specific metrics and filters

**Independent Test**: Create template, generate report from it, verify custom metrics included

### Tests for User Story 4 (Write FIRST) ⚠️

- [ ] T088 [P] [US4] Contract test for POST /api/v1/reports/templates in tests/contract/test_api_templates.py
- [ ] T089 [P] [US4] Integration test for template validation in tests/integration/test_template_validation.py
- [ ] T090 [P] [US4] Unit test for template manager in tests/unit/test_template_manager.py

### Implementation for User Story 4

- [ ] T091 [P] [US4] Create TemplateManager class in proxywhirl/reporting.py
- [ ] T092 [US4] Add TemplateManager.create_template(template_spec) with validation
- [ ] T093 [US4] Add TemplateManager._validate_metrics(metrics) - check metric existence
- [ ] T094 [US4] Add TemplateManager._validate_filters(filters) - validate filter keys
- [ ] T095 [US4] Add TemplateManager._validate_thresholds(thresholds) - numeric validation
- [ ] T096 [US4] Add template storage: save to templates/user/ directory as JSON files
- [ ] T097 [US4] Add template CRUD: get_template(name), list_templates(), delete_template(name)
- [ ] T098 [US4] Add system template protection: prevent modification/deletion of system templates
- [ ] T099 [US4] Create 3 built-in system templates in templates/system/:
- [ ] T100 [P] [US4] System template: basic-performance.json (requests_total, success_rate, avg_response_time)
- [ ] T101 [P] [US4] System template: detailed-health.json (health_status, consecutive_failures, last_check)
- [ ] T102 [P] [US4] System template: aggregate-stats.json (total_proxies, active_count, avg_success_rate)
- [ ] T103 [US4] Update ReportGenerator to load template from TemplateManager
- [ ] T104 [US4] Add template filter application in ReportGenerator._collect_metrics()
- [ ] T105 [US4] Add threshold validation in ReportGenerator._validate_thresholds()
- [ ] T106 [US4] Verify tests pass: uv run pytest tests/integration/test_template_validation.py

**Checkpoint**: All 4 user stories should now be independently functional - custom templates working

---

## Phase 7: REST API Integration

**Purpose**: Expose reporting functionality via REST API (maps to all user stories)

### Tests for REST API (Write FIRST) ⚠️

- [ ] T107 [P] [US1,US2] Contract test for GET /api/v1/reports/{id}/status in tests/contract/test_api_reports.py
- [ ] T108 [P] [US1,US2] Contract test for GET /api/v1/reports/{id}/download in tests/contract/test_api_reports.py
- [ ] T109 [P] [US1] Contract test for GET /api/v1/reports (list) in tests/contract/test_api_reports.py
- [ ] T110 [P] [US1] Contract test for DELETE /api/v1/reports/{id} in tests/contract/test_api_reports.py
- [ ] T111 [P] [US4] Contract test for GET /api/v1/reports/templates in tests/contract/test_api_templates.py
- [ ] T112 [P] [US4] Contract test for GET /api/v1/reports/templates/{id} in tests/contract/test_api_templates.py
- [ ] T113 [P] [US4] Contract test for PUT /api/v1/reports/templates/{id} in tests/contract/test_api_templates.py
- [ ] T114 [P] [US4] Contract test for DELETE /api/v1/reports/templates/{id} in tests/contract/test_api_templates.py
- [ ] T115 [P] [US3] Contract test for GET /api/v1/reports/schedules in tests/contract/test_api_schedules.py
- [ ] T116 [P] [US3] Contract test for GET /api/v1/reports/schedules/{id} in tests/contract/test_api_schedules.py
- [ ] T117 [P] [US3] Contract test for PUT /api/v1/reports/schedules/{id} in tests/contract/test_api_schedules.py
- [ ] T118 [P] [US3] Contract test for DELETE /api/v1/reports/schedules/{id} in tests/contract/test_api_schedules.py
- [ ] T119 [P] [US3] Contract test for POST /api/v1/reports/schedules/{id}/trigger in tests/contract/test_api_schedules.py
- [ ] T120 [P] [US1] Contract test for GET /api/v1/reports/metrics in tests/contract/test_api_reports.py

### Implementation for REST API

- [ ] T121 Create proxywhirl/api_reports.py for report API endpoints (extends api.py)
- [ ] T122 [P] [US1] Implement POST /api/v1/reports/generate endpoint (returns 202 Accepted)
- [ ] T123 [P] [US1] Implement GET /api/v1/reports/{id}/status endpoint (returns Report status)
- [ ] T124 [P] [US1,US2] Implement GET /api/v1/reports/{id}/download endpoint (FileResponse with streaming)
- [ ] T125 [P] [US1] Implement GET /api/v1/reports endpoint (list with pagination, filters)
- [ ] T126 [P] [US1] Implement DELETE /api/v1/reports/{id} endpoint (204 No Content)
- [ ] T127 [P] [US4] Implement POST /api/v1/reports/templates endpoint (create template)
- [ ] T128 [P] [US4] Implement GET /api/v1/reports/templates endpoint (list templates)
- [ ] T129 [P] [US4] Implement GET /api/v1/reports/templates/{id} endpoint (get template)
- [ ] T130 [P] [US4] Implement PUT /api/v1/reports/templates/{id} endpoint (update template)
- [ ] T131 [P] [US4] Implement DELETE /api/v1/reports/templates/{id} endpoint (delete template)
- [ ] T132 [P] [US3] Implement POST /api/v1/reports/schedules endpoint (create schedule)
- [ ] T133 [P] [US3] Implement GET /api/v1/reports/schedules endpoint (list schedules)
- [ ] T134 [P] [US3] Implement GET /api/v1/reports/schedules/{id} endpoint (get schedule)
- [ ] T135 [P] [US3] Implement PUT /api/v1/reports/schedules/{id} endpoint (update schedule)
- [ ] T136 [P] [US3] Implement DELETE /api/v1/reports/schedules/{id} endpoint (delete schedule)
- [ ] T137 [P] [US3] Implement POST /api/v1/reports/schedules/{id}/trigger endpoint (manual trigger)
- [ ] T138 [P] [US1] Implement GET /api/v1/reports/metrics endpoint (list available metrics)
- [ ] T139 Update proxywhirl/api.py to mount report router from api_reports.py
- [ ] T140 Add rate limiting: 50 req/min for report generation (slowapi)
- [ ] T141 Add rate limiting: 20 req/min for template/schedule writes (slowapi)
- [ ] T142 Add OpenAPI tags: "Reports", "Templates", "Schedules", "Metrics"
- [ ] T143 Add API error responses with structured format (error code, message, details)
- [ ] T144 Verify tests pass: uv run pytest tests/contract/test_api_reports.py
- [ ] T145 Verify tests pass: uv run pytest tests/contract/test_api_templates.py
- [ ] T146 Verify tests pass: uv run pytest tests/contract/test_api_schedules.py

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Documentation

- [ ] T147 [P] Create docs/guides/reporting.md with usage examples for all 4 user stories
- [ ] T148 [P] Update README.md to mention automated reporting feature
- [ ] T149 [P] Add docstrings to all public classes/methods in reporting modules
- [ ] T150 Update docs/source/reference/ with API documentation for reporting

### Testing & Quality

- [ ] T151 Add unit tests for credential redaction in tests/unit/test_report_security.py
- [ ] T152 Add property tests for concurrent report generation in tests/property/test_concurrent_reports.py
- [ ] T153 Add benchmark for report generation performance in tests/benchmarks/test_report_performance.py
- [ ] T154 Add integration test for 008-metrics SQLite integration in tests/integration/test_metrics_integration.py
- [ ] T155 Run full test suite: uv run pytest tests/ --cov=proxywhirl
- [ ] T156 Verify coverage ≥85% for all reporting modules
- [ ] T157 Verify mypy --strict passes: uv run mypy --strict proxywhirl/report*.py

### Security & Performance

- [ ] T158 Add path traversal validation for output_directory in ReportSchedule
- [ ] T159 Add file permission validation: reports created with 0600 (owner only)
- [ ] T160 Add memory profiling test: verify <100MB for 1M+ metrics (streaming validation)
- [ ] T161 Add security audit: ensure no credentials in log output
- [ ] T162 Add Jinja2 autoescaping verification for HTML formatter

### CLI Integration (Optional)

- [ ] T163 Add `proxywhirl report generate` CLI command in proxywhirl/cli.py
- [ ] T164 Add `proxywhirl report list` CLI command in proxywhirl/cli.py
- [ ] T165 Add `proxywhirl schedule create` CLI command in proxywhirl/cli.py
- [ ] T166 Add `proxywhirl schedule list` CLI command in proxywhirl/cli.py

### Final Validation

- [ ] T167 Run quickstart.md validation: follow all examples and verify they work
- [ ] T168 Verify all 4 user stories independently testable and functional
- [ ] T169 Verify constitution compliance: all 7 principles satisfied
- [ ] T170 Code cleanup: remove debug prints, commented code, TODO markers
- [ ] T171 Final commit: update IMPLEMENTATION_STATUS.md and CHANGELOG.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - **BLOCKS all user stories**
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in **parallel** (if staffed)
  - Or sequentially in priority order: **US1 (P1) → US2 (P2) → US3 (P3) → US4 (P3)**
- **REST API (Phase 7)**: Can proceed after relevant user story completes (or in parallel if implementation coordinates)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - **No dependencies on other stories**
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 formatters but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses US1 report generation but independently testable
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Extends US1 templates but independently testable

### Within Each User Story

- Tests (included) **MUST** be written and **FAIL** before implementation
- Models before services (Pydantic models define contracts)
- Services before endpoints (business logic before API)
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **All Setup tasks** (T001-T009) can run in parallel
- **All Foundational tasks marked [P]** (T010-T032) can run in parallel within Phase 2
- **Once Foundational phase completes**, all user stories can start in parallel (if team capacity allows):
  - Developer A: User Story 1 (T037-T051)
  - Developer B: User Story 2 (T052-T067)
  - Developer C: User Story 3 (T068-T087)
  - Developer D: User Story 4 (T088-T106)
- **All REST API tests** (T107-T120) can run in parallel
- **All REST API endpoint implementations marked [P]** (T122-T138) can run in parallel
- **Documentation tasks** (T147-T150) can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch all foundational tests together:
Task T010: "tests/unit/test_report_models.py"
Task T011: "tests/unit/test_metrics_collector.py"
Task T012: "tests/unit/test_report_formatters.py"

# Launch all foundational models together:
Task T013: "ReportMetric model"
Task T014: "Report model"
Task T015: "ReportTemplate model"
Task T016: "ReportSchedule model"
Task T017: "ReportHistory model"

# Launch all metrics abstraction methods together:
Task T023: "get_proxy_metrics() method"
Task T024: "get_aggregate_stats() method"
Task T025: "get_available_metrics() method"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) - Recommended ✅

1. Complete Phase 1: Setup (T001-T009)
2. Complete Phase 2: Foundational (T010-T036) **CRITICAL - blocks all stories**
3. Complete Phase 3: User Story 1 (T037-T051) **MVP: Generate JSON reports**
4. **STOP and VALIDATE**: Test US1 independently, generate sample report, verify output
5. Deploy/demo if ready (core reporting functional!)

**Result**: Minimum viable product with programmatic report generation in JSON format

### Incremental Delivery (Add Features Progressively)

1. Complete Setup + Foundational → Foundation ready (T001-T036)
2. Add User Story 1 → Test independently → Deploy/Demo (T037-T051) **MVP!**
3. Add User Story 2 → Test independently → Deploy/Demo (T052-T067) **Multi-format support!**
4. Add User Story 3 → Test independently → Deploy/Demo (T068-T087) **Automation!**
5. Add User Story 4 → Test independently → Deploy/Demo (T088-T106) **Customization!**
6. Add REST API → Test endpoints → Deploy/Demo (T107-T146) **Remote access!**
7. Polish → Final validation (T147-T171) **Production ready!**

**Result**: Each story adds value without breaking previous stories, continuous delivery

### Parallel Team Strategy (4+ Developers)

With multiple developers:

1. **Team completes Setup + Foundational together** (T001-T036)
2. Once Foundational is done (**checkpoint!**):
   - **Developer A**: User Story 1 (T037-T051) - JSON reports
   - **Developer B**: User Story 2 (T052-T067) - Multi-format
   - **Developer C**: User Story 3 (T068-T087) - Scheduling
   - **Developer D**: User Story 4 (T088-T106) - Templates
3. Stories complete and integrate independently
4. **All developers**: REST API (T107-T146) - Can parallelize endpoints
5. **All developers**: Polish (T147-T171) - Split documentation/testing

**Result**: Fastest time to completion with parallel work streams

---

## Notes

- **[P] tasks** = different files/modules, no dependencies, safe to parallelize
- **[Story] label** maps task to specific user story for traceability
- Each user story should be **independently completable and testable**
- **Verify tests fail** before implementing (TDD enforcement)
- **Commit after each task** or logical group for granular history
- **Stop at any checkpoint** to validate story independently before proceeding
- **Avoid**: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Quality Gates (ALL must pass before merge)

- ✅ All tests passing (100%): `uv run pytest tests/`
- ✅ Coverage ≥85%: `uv run pytest tests/ --cov=proxywhirl`
- ✅ Mypy --strict (0 errors): `uv run mypy --strict proxywhirl/report*.py`
- ✅ Ruff checks (0 errors): `uv run ruff check proxywhirl/`
- ✅ Constitution compliance verified (all 7 principles satisfied)
- ✅ Independent user story testing (each story works standalone)
- ✅ Quickstart validation (all examples executable)
- ✅ Security audit passed (no credentials in logs/errors)
- ✅ Memory profiling passed (<100MB for streaming)

---

## Task Count Summary

- **Phase 1 (Setup)**: 9 tasks
- **Phase 2 (Foundational)**: 29 tasks (BLOCKS all user stories) - added T012b, T024b for coverage
- **Phase 3 (US1 - P1 MVP)**: 16 tasks - added T051b for strategy metrics
- **Phase 4 (US2 - P2)**: 16 tasks
- **Phase 5 (US3 - P3)**: 20 tasks
- **Phase 6 (US4 - P3)**: 19 tasks
- **Phase 7 (REST API)**: 26 tasks
- **Phase 8 (Polish)**: 25 tasks
- **Total**: 174 tasks

**Minimum MVP**: 54 tasks (Phase 1 + Phase 2 + Phase 3) for basic JSON reporting
**Full Feature**: 174 tasks for complete implementation with all user stories
