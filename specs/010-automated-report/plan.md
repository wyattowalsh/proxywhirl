# Implementation Plan: Automated Reporting System

**Branch**: `010-automated-report` | **Date**: 2025-11-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/010-automated-report/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement automated reporting system for ProxyWhirl that generates on-demand and scheduled reports about proxy pool performance, health, and usage statistics. Reports support multiple formats (JSON, CSV, HTML, PDF) with streaming architecture for memory efficiency. The system includes custom report templates, concurrent generation with configurable limits, and automatic cleanup with configurable retention periods.

**Technical Approach**: Library-first architecture using standard library (csv, threading, queue, json) with minimal dependencies (reportlab for PDF, jinja2 already installed via FastAPI). Generator-based streaming ensures constant memory usage (<100MB) for datasets of any size. MetricsCollector abstraction layer enables feature independence from 008-metrics implementation.

## Technical Context

**Language/Version**: Python 3.9+ (target: 3.9, 3.10, 3.11, 3.12, 3.13)  
**Primary Dependencies**: 
- `reportlab>=4.0.0` - PDF generation (only new dependency)
- `jinja2>=3.1.0` - HTML templates (already installed via FastAPI)
- `tenacity>=8.2.0` - Retry logic (already installed)
- Standard library: `csv`, `threading`, `queue`, `json`, `pathlib`

**Storage**: 
- SQLite for report history and metrics data (via 008-metrics-observability-performance)
- Filesystem for generated report files (.json, .csv, .html, .pdf)
- JSON files for report template definitions

**Testing**: pytest with respx for HTTP mocking, hypothesis for property-based tests  
**Target Platform**: Cross-platform (Linux, macOS, Windows) - pure Python  
**Project Type**: Single project (library-first, extends existing proxywhirl package)  
**Performance Goals**: 
- Report generation: <5 seconds for 1000 proxies, 7 days data
- Memory usage: <100MB constant (streaming architecture)
- Concurrent reports: 3 simultaneous without degradation
- Schedule accuracy: ±1 minute (acceptable for reports)

**Constraints**: 
- Constitutional compliance: library-first, test-first, flat structure, security-first
- Memory efficiency: streaming required for large datasets (1M+ proxy requests)
- Feature independence: must work without 008-metrics (via abstraction layer)
- Backward compatibility: Python 3.9+ type hints (Union syntax, not |)

**Scale/Scope**: 
- Proxy pools: 1-10,000 proxies
- Time ranges: 1 hour - 90 days
- Report sizes: 1KB - 100MB
- Concurrent users: 1-100 simultaneous report requests
- Scheduled reports: 1-100 active schedules

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Library-First Architecture ✅

**Compliance**: PASS

- Pure Python API accessible via `from proxywhirl import ReportGenerator`
- No CLI/web dependencies required for core functionality
- All components independently importable and testable
- Example usage:
  ```python
  from proxywhirl import ReportGenerator, MetricsCollector
  generator = ReportGenerator(metrics_collector=collector)
  report = generator.generate_report(time_range="24h", format="json")
  ```

### Principle II: Test-First Development ✅

**Compliance**: PASS (to be validated during implementation)

- Test tasks will be written BEFORE implementation tasks
- Target: 85%+ coverage (100% for security code)
- Test organization:
  - Unit tests: Report generators, formatters, template validation
  - Integration tests: End-to-end report generation with mocked metrics
  - Property tests: Streaming correctness, memory bounds

### Principle III: Type Safety & Runtime Validation ✅

**Compliance**: PASS

- All functions will have complete type hints (mypy --strict)
- Pydantic models for all entities (Report, ReportTemplate, ReportSchedule, etc.)
- Runtime validation via Pydantic at API boundaries
- Python 3.9+ compatible type hints (using Union, not |)

### Principle IV: Independent User Stories ✅

**Compliance**: PASS

- US1 (P1): Generate On-Demand Reports - Independently testable, delivers core value
- US2 (P2): Export Multiple Formats - Independent from US1, adds format flexibility
- US3 (P3): Schedule Automated Reports - Independent from US1/US2, adds automation
- US4 (P3): Customize Report Content - Independent from all others, adds power user features

Each story can be implemented, tested, and shipped independently.

### Principle V: Performance Standards ✅

**Compliance**: PASS

- Report generation: <5 seconds (streaming architecture)
- Memory usage: <100MB constant (generator-based streaming)
- Concurrent reports: 3 simultaneous (ThreadPoolExecutor with limits)
- Algorithms: O(1) or O(n) with streaming (no quadratic complexity)

### Principle VI: Security-First Design ✅

**Compliance**: PASS

- Credentials never in reports (proxy URLs use redacted format from models.py)
- XSS prevention (jinja2 autoescaping for HTML reports)
- Path validation (prevent directory traversal in template/report paths)
- File permissions (reports created with 0600, owner read/write only)
- No SQL injection (parameterized queries for metrics access)

### Principle VII: Simplicity & Flat Architecture ✅

**Compliance**: PASS

- Flat module structure within proxywhirl/ package:
  - `reporting.py` - ReportGenerator class
  - `report_models.py` - Pydantic models (Report, ReportTemplate, etc.)
  - `report_formatters.py` - Format-specific generators (JSON, CSV, HTML, PDF)
  - `report_scheduler.py` - Scheduled report management
  - `metrics_collector.py` - Abstraction for metrics data access
- Total: 5 modules (well under 10-module limit)
- Single responsibility: Each module has one clear purpose
- No circular dependencies: reporting → formatters → models

**GATE RESULT**: ✅ **PASSED** - All constitutional principles satisfied, no violations to justify

## Project Structure

### Documentation (this feature)

```text
specs/010-automated-report/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (COMPLETE)
├── data-model.md        # Phase 1 output (THIS DOCUMENT)
├── quickstart.md        # Phase 1 output (THIS DOCUMENT)
├── contracts/           # Phase 1 output (THIS DOCUMENT)
│   └── api-contracts.md # REST API endpoints for reports
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created yet)
```

### Source Code (repository root)

```text
proxywhirl/                       # Single package (flat architecture)
├── __init__.py                   # Public API exports (add reporting exports)
├── reporting.py                  # NEW: ReportGenerator class
├── report_models.py              # NEW: Pydantic models for reports
├── report_formatters.py          # NEW: JSON/CSV/HTML/PDF formatters
├── report_scheduler.py           # NEW: Scheduled report management
├── metrics_collector.py          # NEW: Metrics data abstraction
├── [existing modules...]         # Models, rotator, strategies, etc.
└── py.typed                      # PEP 561 type marker

templates/                        # NEW: Jinja2 templates (repository root, NOT in package)
└── reports/
    ├── base.html                 # HTML report base template
    ├── performance.html          # Performance report template
    └── health.html               # Health report template

Note: templates/ directory lives at repository root alongside proxywhirl/ package.
Templates are NOT distributed in the Python wheel (external resources).
Load via: Path(__file__).parent.parent / 'templates' / 'reports'

tests/
├── unit/
│   ├── test_report_generator.py      # NEW: Report generation logic
│   ├── test_report_formatters.py     # NEW: Format-specific tests
│   ├── test_report_templates.py      # NEW: Template validation
│   └── test_metrics_collector.py     # NEW: Metrics abstraction tests
├── integration/
│   ├── test_report_generation.py     # NEW: End-to-end report tests
│   ├── test_scheduled_reports.py     # NEW: Scheduling tests
│   └── test_report_api.py            # NEW: REST API tests
└── property/
    └── test_report_streaming.py      # NEW: Hypothesis streaming tests
```

**Structure Decision**: Single project (library-first) with flat module structure. All new reporting modules added directly to `proxywhirl/` package alongside existing modules. This maintains constitutional principle VII (flat architecture, no sub-packages). Templates stored in top-level `templates/` directory (external to package, not distributed in wheel).
