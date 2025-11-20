# Implementation Plan: Structured Logging System

**Branch**: `007-logging-system-structured` | **Date**: 2025-11-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `.specify/specs/007-logging-system-structured/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Extend proxywhirl's existing loguru-based logging with structured output formats (JSON, logfmt), configurable handlers (console, file, syslog, HTTP remote), and operational features (rotation, retention, async buffering, contextual metadata, component filtering, log sampling). Configuration via environment variables + optional config file using pydantic-settings. Single background thread for async logging with bounded queue and drop counter metrics. Graceful failure handling with fallback to stderr/console, plus instrumentation for health events.

## Technical Context

**Language/Version**: Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13)
**Primary Dependencies**: 
- loguru>=0.7.0 (already in dependencies - extend configuration)
- pydantic-settings>=2.0.0 (already in dependencies - for config management)
- No additional JSON logging libraries; rely on Loguru’s native serialization per research decision.

**Storage**: File system (rotated log files), optional remote endpoints (syslog, HTTP)
**Testing**: pytest (unit, integration, property tests with Hypothesis), pytest-benchmark for performance validation
**Target Platform**: Linux/macOS/Windows servers (cross-platform file handling)
**Project Type**: Single project (library extension)
**Performance Goals**: 
- <5% logging overhead on proxy requests (SC-003)
- 10,000 log entries/second without blocking (SC-005)
- <1 second configuration reload (SC-002)
- Log rotation <1 minute of threshold (SC-008)

**Constraints**:
- Must extend existing loguru usage (not replace)
- Async logging with bounded queue (prevent OOM)
- Thread-safe for concurrent proxy operations
- No credential exposure in logs (100% redaction, SC-007)
- Graceful degradation on destination failures

**Scale/Scope**:
- Support high-volume production logging (10k+ entries/sec)
- Multiple simultaneous output destinations (4+ handlers)
- Large log files with rotation (100MB+ files, daily rotation)
- 24/7 operation with automatic retention cleanup

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. Library-First Architecture** | ✅ PASS | Extends existing loguru library configuration. All functionality usable via Python import. No CLI/web dependencies required. Type hints with `py.typed` marker. |
| **II. Test-First Development** | ✅ PASS | TDD workflow enforced in tasks.md (to be created). Unit tests for formatters, handlers, config. Integration tests for multi-destination logging. Property tests for concurrent logging. Target 85%+ coverage. |
| **III. Type Safety & Runtime Validation** | ✅ PASS | Pydantic models for LogConfiguration. Full type hints for all public APIs. mypy --strict compliance. Pydantic-settings for config validation. |
| **IV. Independent User Stories** | ✅ PASS | 6 user stories (US1-US6) each independently testable. US1 (structured output) can be implemented without US2-US6. No hidden dependencies between stories. |
| **V. Performance Standards** | ✅ PASS | Success criteria defined: <5% overhead (SC-003), 10k entries/sec (SC-005). Async logging with bounded queue prevents blocking. Benchmark tests required for validation. |
| **VI. Security-First Design** | ✅ PASS | FR-017 requires 100% credential redaction (SC-007). Use SecretStr for sensitive config. No credential exposure in structured logs. Thread-safe async queue. |
| **VII. Simplicity & Flat Architecture** | ✅ PASS | Extends existing loguru in proxywhirl/ (no new package). Adds ~2-3 modules: logging_config.py, logging_formatters.py, logging_handlers.py. Total modules: 19/20 (within limit). |

**uv run Enforcement**: All Python commands will use `uv run` prefix per constitution (e.g., `uv run pytest tests/`).

## Project Structure

### Documentation (this feature)

```text
specs/007-logging-system-structured/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── logging-config-schema.json  # Pydantic model schema for configuration
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
proxywhirl/                    # Flat package structure (existing)
├── logging_config.py          # NEW: Pydantic-settings configuration models
├── logging_formatters.py      # NEW: JSON/logfmt structured formatters
├── logging_handlers.py        # NEW: Multi-destination handlers with fallback, sampling, filtering
├── logging_context.py         # NEW: Context binding helpers for correlation metadata
├── config.py                  # EXISTING: May extend with logging settings
├── rotator.py                 # EXISTING: Will use structured logging
├── health.py                  # EXISTING (006): Emit structured health events
└── ...                        # Other existing modules

tests/
├── unit/
│   ├── test_logging_config.py         # NEW: Config model validation
│   ├── test_logging_formatters.py     # NEW: JSON/logfmt formatting + Unicode safety
│   ├── test_logging_handlers.py       # NEW: Handler behavior, fallback, sampling
│   ├── test_logging_levels.py         # NEW: Level precedence validation
│   ├── test_logging_context.py        # NEW: Context binding utilities
│   └── test_logging_rotation.py       # NEW: Rotation parsing helpers
├── integration/
│   ├── test_logging_multi_dest.py     # NEW: Multiple outputs simultaneously
│   ├── test_logging_rotation.py       # NEW: File rotation + retention
│   ├── test_logging_context.py        # NEW: Context propagation
│   └── test_logging_health.py         # NEW: Health event logging coverage
├── contract/
│   └── test_logging_schema.py         # NEW: Structured log schema validation
├── property/
│   ├── test_logging_concurrency.py    # NEW: Hypothesis concurrent logging
│   └── test_logging_sampling.py       # NEW: Sampling behavior validation
└── benchmarks/
    └── test_logging_performance.py    # NEW: SC-003, SC-005 validation
```

**Structure Decision**: Flat module structure per Constitution VII. Adding focused logging modules (config, formatters, handlers, context) keeps total modules within the allowed limit and documents updates to existing components (rotator, health). No nested logging sub-package—architecture stays simple.

## Complexity Tracking

No constitution violations - all gates pass. Table not applicable.
