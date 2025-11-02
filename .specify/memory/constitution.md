# ProxyWhirl Constitution

## Core Principles

### I. Library-First Architecture

Every feature MUST start as a pure Python library with clean APIs:
- NO CLI/web dependencies required for core functionality
- Self-contained, independently testable, documented
- Clear purpose required - no organizational-only libraries
- Public API exported through `__init__.py`
- Type hints with `py.typed` marker (PEP 561)

### II. Test-First Development (NON-NEGOTIABLE)

TDD is MANDATORY for all code:
- Tests written BEFORE implementation
- Tests MUST fail before implementation begins
- Red-Green-Refactor cycle strictly enforced
- Minimum 85% coverage (100% for security code)
- All tests must pass before merge

### III. Type Safety & Runtime Validation

Strict type safety at compile-time and runtime:
- Full type hints for all public APIs
- mypy --strict compliance (0 errors)
- Pydantic v2 for runtime validation
- SecretStr for credentials (never log/expose)
- No `Any` types except where external APIs require

### IV. Independent User Stories

Each user story MUST be independently testable:
- No hidden dependencies between stories
- Each story delivers standalone value
- Can be implemented and tested in isolation
- Independent test scenarios defined upfront

### V. Performance Standards

Quantifiable performance requirements:
- <1ms proxy selection (all strategies)
- <50ms request overhead (p95)
- 1000+ concurrent requests support
- Benchmark tests for all critical paths

### VI. Security-First Design

100% credential protection:
- Credentials use SecretStr (Pydantic)
- NEVER log credentials (always `***` redaction)
- NEVER expose credentials in errors
- 100% test coverage for security code

### VII. Simplicity & Flat Architecture

Maximum 20 modules in flat package:
- Flat structure: `proxywhirl/*.py` (no sub-packages)
- Single responsibility per module
- Max 10 modules for new features
- Justify any complexity increases

## Development Workflow

### uv Package Manager (MANDATORY)

ALL Python commands MUST use `uv run` prefix:
- Add dependencies: `uv add <package>` (NEVER `pip install`)
- Add dev dependencies: `uv add --dev <package>`
- Run commands: `uv run pytest`, `uv run mypy`, etc.
- Rationale: Ensures consistent virtual environment activation

### Quality Gates

ALL must pass before merge:
- ✅ All tests passing (100%)
- ✅ Coverage ≥85% (100% for security)
- ✅ Mypy --strict (0 errors)
- ✅ Ruff checks (0 errors)
- ✅ Constitution compliance verified
- ✅ Independent user story testing

## Governance

Constitution supersedes all other practices:
- All PRs/reviews must verify compliance
- Violations require documented justification
- Amendments require explicit approval
- Use `.github/copilot-instructions.md` for agent guidance

**Version**: 1.0.0 | **Ratified**: 2025-10-22 | **Last Amended**: 2025-11-02
