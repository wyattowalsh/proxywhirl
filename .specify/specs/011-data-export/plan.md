# Implementation Plan: Data Export & Reporting

**Branch**: `011-data-export` | **Date**: 2025-11-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-data-export/spec.md`

## Summary

Implement comprehensive data export and import functionality for proxywhirl, enabling users to backup proxy configurations, export analytics data for external analysis, schedule automated exports, and generate health reports. The system will support multiple formats (CSV, JSON, Excel, PDF), configurable notification mechanisms (in-app, email, webhook), and secure credential handling with encryption. Core capabilities include asynchronous processing for large exports, configurable compression, and strict access control (creator + admins only).

## Technical Context

**Language/Version**: Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13)  
**Primary Dependencies**: 
- `pandas>=2.0.0` (data manipulation and Excel export)
- `openpyxl>=3.1.0` (Excel file generation)
- `reportlab>=4.0.0` or `weasyprint>=60.0` (PDF generation)
- `apscheduler>=3.10.0` (scheduled exports)
- Existing: `pydantic>=2.0.0`, `httpx>=0.25.0`, `loguru>=0.7.0`

**Storage**: SQLite (reuse existing storage.py infrastructure from 001-core-python-package), local filesystem for export files  
**Testing**: pytest with hypothesis for property-based tests, respx for HTTP mocking  
**Target Platform**: Linux/macOS/Windows servers (Python cross-platform)  
**Project Type**: Single library project (flat package structure per constitution)  
**Performance Goals**: 
- Export initiation <100ms
- Analytics export (100K records) <60 seconds
- Async export overhead <10% CPU/memory
- File compression 60%+ reduction for JSON/CSV

**Constraints**: 
- <10ms proxy request latency impact (FR-007)
- 100% credential protection (never plain text in exports)
- Creator-only + admin access control
- Compression enabled by default

**Scale/Scope**: 
- Support exports up to 1M records
- Concurrent export jobs (10+)
- Retention: 30 days default
- File sizes: Individual exports up to 1GB compressed

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### 1. Library-First Architecture ✅
- **Status**: PASS
- **Evidence**: All export functionality accessible via `from proxywhirl import ExportManager, ImportManager`
- **Public API**: `ExportManager.export()`, `ImportManager.import_pool()`, `ScheduledExportManager.schedule()`
- **No CLI/Web Dependencies**: Pure Python functions, optional REST API integration via 003-rest-api

### 2. Test-First Development ✅
- **Status**: PASS (enforcement in Phase 2)
- **Target Coverage**: 85%+ overall, 100% for credential handling
- **Test Strategy**: 
  - Unit tests for export/import logic (respx for HTTP if needed)
  - Integration tests for full export→compress→download→import cycles
  - Property tests for file format compliance and data integrity
- **TDD Checkpoint**: Tests written before implementation in tasks.md

### 3. Type Safety ✅
- **Status**: PASS
- **Enforcement**: Mypy --strict for all new modules
- **Pydantic Models**: ExportJob, ImportJob, ExportTemplate, ScheduledExport
- **SecretStr**: Credential encryption keys, user passwords

### 4. Independent User Stories ✅
- **Status**: PASS
- **US1** (P1): Export/import proxy pool - Standalone MVP
- **US2** (P1): Export analytics data - Independent of US1
- **US3** (P2): Scheduled exports - Builds on US1/US2
- **US4** (P2): Health reports - Independent PDF generation
- **US5** (P3): Dashboard exports - Optional enhancement

### 5. Performance Standards ✅
- **Status**: PASS
- **Export initiation**: <100ms (SC-002: 60s for 100K records)
- **Async processing**: <10% overhead (FR-007)
- **Compression**: 60%+ reduction (SC-010)
- **No proxy latency impact**: Async queue prevents blocking

### 6. Security-First ✅
- **Status**: PASS
- **Credential Protection**: 
  - FR-004: Three modes (full encrypted/sanitized/reference)
  - FR-003: Master key or password for decryption
  - FR-020: Creator + admin only access
  - 100% audit logging (FR-010, FR-022)
- **No Plain Text**: SC-009 enforced

### 7. Simplicity ✅
- **Status**: PASS
- **Module Count**: +3 new modules (export.py, import.py, scheduled_export.py)
- **Total**: 15 modules (within 10-20 acceptable range given feature count)
- **Flat Architecture**: No sub-packages, single responsibilities
- **Dependencies**: Minimal additions (pandas, openpyxl, reportlab, apscheduler)

**GATE RESULT**: ✅ **ALL CHECKS PASS** - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/011-data-export/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── export-api.yaml  # OpenAPI spec for REST endpoints
├── checklists/
│   └── requirements.md  # Spec quality checklist (already exists)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
proxywhirl/              # Flat package (no sub-packages)
├── __init__.py          # Add export/import exports
├── export.py            # NEW: ExportManager, format handlers
├── import.py            # NEW: ImportManager, validation
├── scheduled_export.py  # NEW: ScheduledExportManager
├── export_models.py     # NEW: Pydantic models (ExportJob, etc.)
├── api.py               # MODIFY: Add export endpoints (if 003-rest-api active)
├── api_models.py        # MODIFY: Add export API models
├── storage.py           # MODIFY: Add export job tables
├── models.py            # Existing (may add export-related models)
├── rotator.py           # Existing (export uses this)
├── cache.py             # Existing (from 005-caching)
└── py.typed             # Existing

tests/
├── unit/
│   ├── test_export.py         # NEW: Export logic tests
│   ├── test_import.py         # NEW: Import validation tests
│   └── test_scheduled_export.py  # NEW: Scheduling tests
├── integration/
│   ├── test_export_import_cycle.py  # NEW: Full roundtrip
│   ├── test_export_formats.py      # NEW: CSV/JSON/Excel/PDF
│   └── test_export_compression.py  # NEW: Compression tests
└── property/
    └── test_export_integrity.py    # NEW: Data integrity properties

examples/
└── export_examples.py   # NEW: Usage examples
```

**Structure Decision**: Maintaining flat proxywhirl/ package per constitution. New modules follow single-responsibility principle:
- `export.py`: Export logic and format handlers
- `import.py`: Import validation and restoration
- `scheduled_export.py`: APScheduler integration
- `export_models.py`: Pydantic models for export domain

REST API integration (if needed) extends existing `api.py` from 003-rest-api.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations** - All constitutional principles satisfied. Module count increase justified by:
1. Export/import are distinct responsibilities (not mergeable)
2. Scheduled exports require separate scheduler management
3. New models isolated to maintain clarity
4. Total modules (15) still within acceptable range for feature count

---

## Phase 0: Research & Technical Decisions

**Status**: In Progress

### Research Tasks

1. **PDF Generation Library Selection**
   - **Question**: ReportLab vs WeasyPrint vs matplotlib for health reports and dashboards?
   - **Requirements**: Charts, tables, branding support, Python 3.9+ compatibility
   - **Deliverable**: Decision with rationale in research.md

2. **Excel Export Strategy**
   - **Question**: pandas + openpyxl vs xlsxwriter for XLSX generation?
   - **Requirements**: Formatting preservation, formula support, memory efficiency
   - **Deliverable**: Library choice and usage patterns in research.md

3. **APScheduler Configuration**
   - **Question**: BackgroundScheduler vs AsyncIOScheduler for scheduled exports?
   - **Requirements**: Thread-safe, persistent jobs, cron expressions
   - **Deliverable**: Scheduler configuration approach in research.md

4. **Compression Algorithm**
   - **Question**: gzip level (1-9) vs lzma for export compression?
   - **Requirements**: 60%+ reduction, <5s overhead for 100MB files
   - **Deliverable**: Algorithm choice and compression level in research.md

5. **Notification Infrastructure**
   - **Question**: Email sending (SMTP vs sendgrid) and webhook patterns?
   - **Requirements**: Configurable, async, error handling
   - **Deliverable**: Notification implementation approach in research.md

6. **Access Control Integration**
   - **Question**: How to integrate with existing auth (if any) or implement simple user/admin model?
   - **Requirements**: Creator + admin check, audit logging
   - **Deliverable**: Access control strategy in research.md

7. **File Storage Management**
   - **Question**: Directory structure, retention policy implementation, cleanup strategy?
   - **Requirements**: Organized by user/date, atomic cleanup, size limits
   - **Deliverable**: Storage patterns in research.md

8. **Import Validation Patterns**
   - **Question**: JSON Schema validation vs Pydantic vs custom validators?
   - **Requirements**: Schema versioning, helpful error messages
   - **Deliverable**: Validation approach in research.md

### Unknowns to Resolve

- ✅ Notification mechanisms (Clarified: in-app, email, webhook - all supported)
- ✅ Access control model (Clarified: creator + admin only)
- ✅ Compression strategy (Clarified: default on, user can disable)
- ✅ Credential restoration (Clarified: master key or user password required)
- ✅ Failure notifications (Clarified: email + system log)
- ⚠️ PDF library choice (Research needed)
- ⚠️ Excel library approach (Research needed)
- ⚠️ Scheduler type (Research needed)
- ⚠️ Compression algorithm details (Research needed)
- ⚠️ Email/webhook implementation (Research needed)
- ⚠️ File storage patterns (Research needed)
- ⚠️ Import validation approach (Research needed)

**Next**: Generate research.md addressing all unknowns above.

---

*Plan continues with Phase 1 after research.md completion...*
