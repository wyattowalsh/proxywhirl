# Implementation Plan: CLI Interface

**Branch**: `002-cli-interface` | **Date**: 2025-10-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-cli-interface/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

The CLI Interface feature provides a command-line tool for managing and using proxies, built on top of the core ProxyWhirl library. Users can make HTTP requests through rotating proxies, manage proxy pools, configure persistent settings, and format output for automation workflows. The implementation uses Typer for command structure, Rich for progress bars and formatting, TOML for configuration (pyproject.toml), Fernet encryption for credentials (reusing Phase 2 implementation), and file-based locking for concurrency safety.

## Technical Context

**Language/Version**: Python 3.9+ (target: 3.9, 3.10, 3.11, 3.12, 3.13)

**Primary Dependencies**:

- `typer>=0.9.0` - Modern CLI framework with automatic help generation and rich integration
- `rich>=13.0.0` - Progress bars, tables, and formatted output (built-in Typer integration)
- `toml>=0.10.2` - TOML parsing (Python 3.9-3.10) or `tomllib` (built-in Python 3.11+)
- `tomli-w>=1.0.0` - TOML writing (all Python versions)
- Core ProxyWhirl library - Proxy rotation, validation, storage (Phase 1 & 2)

**Storage**:

- Configuration: TOML files (`pyproject.toml` or `~/.config/proxywhirl/config.toml`)
- Proxy pool: Reuses Phase 2 storage backends (FileStorage, SQLiteStorage)
- Lock files: `.proxywhirl.lock` with PID tracking (platform-specific paths)

**Testing**: pytest with Typer's testing utilities for command invocation testing

**Target Platform**: Cross-platform CLI (Linux, macOS, Windows) - terminal-based interaction

**Project Type**: Single project - CLI module added to existing `proxywhirl/` package

**Performance Goals**:

- CLI startup time: <500ms from invocation to first output
- Simple request execution: <2 seconds (SC-004)
- Progress bar update frequency: 10 updates/second minimum

**Constraints**:

- Binary size: <10MB when packaged (SC-008)
- Cross-platform compatibility: identical behavior on Linux/macOS/Windows (SC-006)
- Graceful degradation: disable ANSI colors, progress bars when not TTY
- File permissions: config files MUST have 600 permissions (read/write owner only)

**Scale/Scope**:

- Command count: ~15 commands/subcommands (get, post, pool list/add/remove/test, config init/set/get)
- Configuration keys: ~20 settings (proxies, rotation strategy, timeouts, defaults)
- Output formats: 4 (human-readable, JSON, table, CSV)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Library-First Architecture ✅ PASS

- CLI built as thin wrapper over core `proxywhirl` library
- All functionality (rotation, validation, storage) accessible via Python API
- CLI imports and composes library functions - no duplicate logic
- Users can use library directly without CLI dependency
- Typer provides zero-cost abstraction over library API

### II. Test-First Development ✅ PASS

- Tests will be written BEFORE CLI implementation (per tasks.md workflow)
- Typer's testing utilities enable testing commands as black boxes
- Coverage target: 85%+ (consistent with Phase 1 & 2)
- Integration tests will validate end-to-end user stories

### III. Type Safety & Runtime Validation ✅ PASS

- All CLI functions will have complete type hints
- Configuration loaded via Pydantic models (reuse existing models)
- Input validation for URLs, proxy formats, file paths
- Pass `mypy --strict` (constitutional requirement)

### IV. Independent User Stories ✅ PASS

- US1 (Make Request): Independent - requires only core library
- US2 (Manage Pool): Independent - requires only pool management
- US3 (Configure Settings): Independent - requires only config module
- US4 (Output Formatting): Independent - orthogonal concern, can develop separately
- Each story has standalone value and can be tested in isolation

### V. Performance Standards ✅ PASS

- CLI startup: <500ms (library import + Typer initialization)
- Request execution: <2s for simple requests (SC-004)
- No performance regression to core library (CLI adds minimal overhead)
- Progress bars update asynchronously - no blocking

### VI. Security-First Design ✅ PASS

- Credentials use Fernet encryption (reuse Phase 2 FileStorage implementation)
- Config files created with 600 permissions (owner read/write only)
- Warning when credentials passed via CLI args (visible in process list)
- SecretStr used for all credential types (Pydantic)

### VII. Simplicity & Flat Architecture ✅ PASS

- Single new module: `proxywhirl/cli.py` (Typer command definitions)
- Optional new module: `proxywhirl/config.py` (TOML configuration management)
- No sub-packages - stays within flat structure
- Total modules after CLI: 11 (<10 threshold - requires justification, see Complexity Tracking)

**Overall: ✅ PASS** (1 complexity tracking item: module count)

## Project Structure

### Documentation (this feature)

```text
specs/002-cli-interface/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── cli-schema.md    # CLI command structure and options
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
proxywhirl/                      # Existing package (flat structure maintained)
├── __init__.py                  # Public API exports
├── models.py                    # Pydantic models (existing)
├── rotator.py                   # ProxyRotator class (existing)
├── strategies.py                # Rotation strategies (existing)
├── fetchers.py                  # Proxy fetching (Phase 2)
├── storage.py                   # Storage backends (Phase 2)
├── browser.py                   # Browser rendering (Phase 2)
├── utils.py                     # Utilities (existing)
├── exceptions.py                # Custom exceptions (existing)
├── cli.py                       # NEW: Typer CLI commands and groups
├── config.py                    # NEW: TOML configuration management
└── py.typed                     # Type marker (existing)

tests/
├── unit/
│   ├── test_cli.py              # NEW: CLI unit tests (Typer testing)
│   └── test_config.py           # NEW: Configuration tests
├── integration/
│   ├── test_cli_requests.py     # NEW: End-to-end request tests
│   ├── test_cli_pool.py         # NEW: Pool management tests
│   └── test_cli_config.py       # NEW: Config persistence tests
└── property/                    # (existing property tests)

examples/
└── cli_examples.sh              # NEW: CLI usage examples (bash script)
```

**Structure Decision**: Single project structure maintained. CLI added as two new modules (`cli.py`, `config.py`) to existing flat `proxywhirl/` package. This violates the "maximum 10 modules" principle (now 11), but is justified because CLI is a distinct user interface layer that cannot be folded into existing modules without breaking single responsibility. Typer is chosen over Click for its native type safety, automatic validation, and built-in Rich integration.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 11 modules (exceeds 10) | CLI is a distinct user interface layer requiring separate `cli.py` and `config.py` modules | Merging CLI into existing modules would violate single responsibility - `rotator.py` is for library logic, not command-line parsing. Config management is orthogonal to all existing modules. Typer provides better type safety and less boilerplate than Click. |
