# ProxyWhirl Constitution
<!-- Python library for intelligent proxy rotation and management -->

## Core Principles

### I. Library-First Architecture
Every feature starts as a standalone library. Libraries must be self-contained, independently testable, and well-documented. Clear purpose required - no organizational-only libraries. All functionality must be usable via direct Python import without CLI/web dependencies. Full type hints with `py.typed` marker are mandatory.

### II. Test-First Development (NON-NEGOTIABLE)
TDD mandatory: Tests written → User approved → Tests fail → Then implement. Red-Green-Refactor cycle strictly enforced. Property-based tests with Hypothesis for invariants. Integration tests for all user stories. Coverage target: 85%+ (consistent with existing codebase: 88%+).

### III. Type Safety & Runtime Validation
Full type hints required for all public APIs. Pass `mypy --strict` without exceptions. Pydantic models for all data structures with runtime validation. Clear error messages for invalid inputs. No silent failures.

### IV. Independent User Stories
Each user story must deliver standalone value and be testable in isolation. No hidden dependencies between stories. Each story has independent acceptance scenarios. Stories can be implemented in any order.

### V. Performance Standards
Strategy selection: <5ms overhead. Support 10,000 concurrent requests without deadlocks. Hot-swap configuration: <100ms. Thread-safe with <1% lock contention overhead. Memory-bounded with sliding windows and auto-pruning.

### VI. Security-First Design
No credential exposure in logs or errors. Use `SecretStr` for sensitive data. Validate all user inputs to prevent injection. Thread-safe access prevents race conditions. Geo-location data from trusted sources only.

### VII. Simplicity & Flat Architecture
Prefer flat module structure over nested packages. Start simple, YAGNI principles. No circular dependencies. Single responsibility per module. Maximum 20 modules without strong justification.

## Development Environment

### Python Package Management (MANDATORY)

**CRITICAL**: ALL Python commands MUST use `uv run` prefix without exception:

```bash
# ✅ CORRECT - Always use uv run
uv run pytest tests/
uv run mypy --strict proxywhirl/
uv run ruff check proxywhirl/
uv run python -m module
uv run python script.py
uv run python -c "import sys; print(sys.version)"

# ❌ WRONG - Never run Python directly
pytest tests/
python -m pytest
python script.py
python -c "..."
```

**Package Management Commands**:
- Create virtual environment: `uv venv`
- Sync dependencies from lockfile: `uv sync`
- Add new package: `uv add <package>`
- Add dev dependency: `uv add --dev <package>`
- Run ANY Python command: `uv run <command>`
- NEVER use: `pip`, `pip install`, `python -m pip`, or bare `python`

**Rationale**: `uv run` ensures consistent virtual environment activation across all contexts. It provides significantly faster dependency resolution and installation compared to pip. It manages both the virtual environment and dependencies with a single tool, ensuring reproducible builds with lockfiles and eliminating environment activation issues.

**Enforcement**: Any Python command without `uv run` prefix is a constitution violation and must be corrected immediately.

### Python Version Support

Support Python 3.9+ with testing on 3.9, 3.10, 3.11, 3.12, and 3.13.

## Testing Standards

### Test Organization
- Unit tests: `tests/unit/` (fast, isolated, no I/O)
- Integration tests: `tests/integration/` (cross-component, realistic scenarios)
- Property tests: `tests/property/` (Hypothesis-based invariant testing)
- Benchmark tests: `tests/benchmarks/` (performance validation with pytest-benchmark)
- Contract tests: `tests/contract/` (API stability verification)

### Test Execution
All tests must pass before merge. Use `pytest` with coverage reporting. Parallel execution with `pytest-xdist` for speed.

## Code Quality Gates

### Pre-merge Requirements
1. All tests pass (unit, integration, property, contract)
2. `mypy --strict` passes with zero errors
3. `ruff check` passes (linting)
4. Test coverage ≥85%
5. Benchmark tests show no performance regression >10%
6. Constitution compliance verified

### Documentation Requirements
- Docstrings for all public APIs (Google style)
- Type hints for all parameters and returns
- Examples in docstrings for complex functions
- README with quick start and API overview
- Changelog updated for user-facing changes

## Governance

This constitution supersedes all other practices. Amendments require:
1. Documentation of the change and rationale
2. Review and approval from project maintainers
3. Migration plan for existing code if breaking

All PRs/reviews must verify compliance. Complexity must be justified. Constitution violations require explicit justification and acceptance.

**Version**: 1.1.0 | **Ratified**: 2025-06-13 | **Last Amended**: 2025-10-29

