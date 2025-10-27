# proxywhirl Development Guidelines

**Last Updated**: 2025-10-22  
**Constitution Version**: 1.0.0  
**Status**: Core Package (v0.1.0) - Production Ready

## Constitutional Principles (MANDATORY)

All development MUST follow the 7 core principles in `.specify/memory/constitution.md`:

1. **Library-First Architecture** - Pure Python API, no CLI/web dependencies required
2. **Test-First Development** - Tests written BEFORE implementation (NON-NEGOTIABLE)
3. **Type Safety** - Mypy --strict compliance + Pydantic runtime validation
4. **Independent User Stories** - Each story independently developable and testable
5. **Performance Standards** - <1ms selection, 1000+ concurrent requests
6. **Security-First** - 100% credential protection, never exposed in logs/errors
7. **Simplicity** - Flat architecture, single responsibilities, max 10 modules

## Technology Stack

### Language & Runtime
- Python 3.9+ (target: 3.9, 3.10, 3.11, 3.12, 3.13)
- Use `Union[X, Y]` syntax (not `X | Y`) for Python 3.9 compatibility
- Use `datetime.timezone.utc` (not `datetime.UTC`) for Python 3.9 compatibility

### Package Management (MANDATORY)
- Package manager: `uv` (ONLY uv commands allowed)
- Add dependencies: `uv add <package>` (NEVER `uv pip install` or `pip install`)
- Add dev dependencies: `uv add --dev <package>`
- Sync environment: `uv sync`
- Run commands: `uv run <command>` (e.g., `uv run pytest`, `uv run mypy`)
- Rationale: `uv add` keeps `pyproject.toml` in sync with installed packages

### Core Dependencies
- `httpx>=0.25.0` - HTTP client with proxy support
- `pydantic>=2.0.0` - Data validation (use SecretStr for credentials)
- `pydantic-settings>=2.0.0` - Configuration management
- `tenacity>=8.2.0` - Retry logic with exponential backoff
- `loguru>=0.7.0` - Structured logging

### Development Dependencies
- `pytest>=7.4.0` - Test framework
- `pytest-cov>=4.1.0` - Coverage reporting (target: 85%+)
- `hypothesis>=6.88.0` - Property-based testing
- `mypy>=1.5.0` - Type checking (--strict mode)
- `ruff>=0.1.0` - Linting AND formatting (NOT black)

## Project Structure

```
proxywhirl/              # Flat package (no sub-packages)
├── __init__.py          # Public API exports
├── exceptions.py        # Exception hierarchy
├── models.py            # Pydantic v2 models
├── rotator.py           # ProxyRotator class
├── strategies.py        # Rotation strategies
├── utils.py             # Pure utility functions
└── py.typed             # PEP 561 type marker

tests/
├── unit/                # Fast, isolated tests (<10ms)
├── integration/         # End-to-end with HTTP mocking
└── property/            # Hypothesis property-based tests

.specify/
├── memory/              # Constitution, compliance reports
├── specs/               # Feature specifications
└── templates/           # Spec-kit templates
```

## Development Commands

All Python commands MUST use `uv run` prefix:

```bash
# Testing
uv run pytest tests/ -q                    # Quick test run
uv run pytest tests/ --cov=proxywhirl      # With coverage
uv run pytest tests/unit/                  # Unit tests only

# Type Checking
uv run mypy --strict proxywhirl/           # Must pass with 0 errors

# Linting & Formatting
uv run ruff check proxywhirl/              # Linting
uv run ruff format proxywhirl/             # Formatting (NOT black)

# Quality Gates (all must pass)
uv run pytest tests/ && \
uv run mypy --strict proxywhirl/ && \
uv run ruff check proxywhirl/
```

## Code Style & Quality

### Type Hints (MANDATORY)
- All functions MUST have complete type hints
- Pass `mypy --strict` with 0 errors
- Use `Union[X, Y]` for Python 3.9 compatibility
- No `Any` types except where external APIs require it

### Security (CRITICAL)
- Credentials MUST use `SecretStr` from Pydantic
- Credentials MUST NEVER appear in logs (always `***`)
- Credentials MUST NEVER appear in error messages
- 100% test coverage required for credential handling

### Testing (NON-NEGOTIABLE)
- Write tests BEFORE implementation (TDD)
- Minimum 85% overall coverage (current: 88%)
- 100% coverage for security code
- Unit tests <10ms each
- Property-based tests for algorithms

### Formatting
- Ruff (line-length=100)
- NOT black (use ruff format instead)
- PEP 8 compliant
- Explicit over implicit

## Completed Features

### ✅ 001-core-python-package (v0.1.0)
**Status**: Production Ready (87 tasks, 239 tests passing, 88% coverage)

**User Stories Implemented**:
- US1 (P1): Basic Rotation - Round-robin, random strategies, automatic failover
- US2 (P2): Authentication - SecretStr credentials, redaction in logs/errors
- US3 (P2): Pool Lifecycle - Runtime add/remove/update, thread-safe operations
- US4 (P3): Rotation Strategies - Weighted, least-used strategies

**Key Metrics**:
- Tests: 239/239 passing
- Coverage: 88% (exceeds 85% target)
- Mypy: --strict, 0 errors
- Ruff: All checks passing
- Security: 100% credential coverage

## Future Features (Planned)

- 002-cli-interface: Command-line tool
- 003-rest-api: RESTful API server
- 004-rotation-strategies-intelligent: ML-based strategies
- 005-caching-mechanisms-storage: SQLite, Redis backends
- 006-health-monitoring-continuous: Background health checks
- 018-mcp-server-model: Model Context Protocol server

See `.specify/specs/` for full specifications.

## Development Workflow

### For New Features:
1. Create spec in `.specify/specs/###-feature-name/`
2. Run constitution check (must pass)
3. Write plan.md (technical design)
4. Write spec.md (user stories, acceptance criteria)
5. Write tasks.md (test-first phases)
6. Create feature branch: `###-feature-name`
7. Write tests FIRST (verify they fail)
8. Implement minimal code to pass tests
9. Refactor while maintaining green tests
10. Merge to main after quality gates pass

### Quality Gates (ALL must pass):
- ✅ All tests passing (100%)
- ✅ Coverage ≥85% (100% for security code)
- ✅ Mypy --strict (0 errors)
- ✅ Ruff checks (0 errors)
- ✅ Constitution compliance verified
- ✅ Independent user story testing

## Important Notes

### Use `uv run` for ALL Python commands
```bash
# ✅ Correct
uv run pytest tests/
uv run mypy --strict proxywhirl/

# ❌ Wrong
pytest tests/
python -m pytest tests/
```

### Security Reminders
- Never log credentials (use `***` redaction)
- Never expose credentials in errors
- Always use `SecretStr` for passwords/tokens
- Test credential security explicitly

### Performance Requirements
- Proxy selection: <1ms (all strategies)
- Request overhead: <50ms p95
- Strategy switching: <5ms
- 1000+ concurrent requests support

### Documentation
- Code docs: Inline (docstrings, comments)
- Feature docs: `.specify/specs/###-feature/`
- NO ad-hoc standalone `.md` files

## Resources

- Constitution: `.specify/memory/constitution.md`
- Compliance Report: `.specify/memory/constitution-compliance-report.md`
- Implementation Status: `IMPLEMENTATION_STATUS.md`
- Feature Specs: `.specify/specs/`

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
