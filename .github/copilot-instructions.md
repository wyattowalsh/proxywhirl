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

**CRITICAL**: ALL Python commands MUST use `uv run` prefix without exception.

- Package manager: `uv` (ONLY uv commands allowed)
- Add dependencies: `uv add <package>` (NEVER `uv pip install` or `pip install`)
- Add dev dependencies: `uv add --dev <package>`
- Sync environment: `uv sync`
- Run ANY Python command: `uv run <command>` (e.g., `uv run pytest`, `uv run mypy`, `uv run python script.py`)
- Rationale: `uv add` keeps `pyproject.toml` in sync with installed packages, and `uv run` ensures consistent virtual environment activation

**Examples**:
```bash
# ✅ CORRECT
uv run pytest tests/
uv run python -m module
uv run python script.py

# ❌ WRONG (constitution violation)
pytest tests/
python script.py
pip install package
```

See `.specify/memory/AGENTS.md` for complete enforcement guidelines.

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

### REST API Dependencies (003-rest-api)
- `fastapi>=0.100.0` - Modern async web framework
- `uvicorn[standard]>=0.24.0` - ASGI server
- `slowapi>=0.1.9` - Rate limiting middleware
- `python-multipart>=0.0.6` - File upload support

## Project Structure

```
proxywhirl/              # Flat package (no sub-packages)
├── __init__.py          # Public API exports
├── api.py               # FastAPI REST API (003-rest-api)
├── api_models.py        # API-specific Pydantic models (003-rest-api)
├── browser.py           # Browser rendering support
├── cli.py               # Command-line interface
├── config.py            # Configuration management
├── exceptions.py        # Exception hierarchy
├── fetchers.py          # Proxy source fetchers
├── models.py            # Core Pydantic v2 models
├── rotator.py           # ProxyRotator class
├── sources.py           # Proxy source definitions
├── storage.py           # SQLite persistence
├── strategies.py        # Rotation strategies
├── utils.py             # Pure utility functions
└── py.typed             # PEP 561 type marker

tests/
├── unit/                # Fast, isolated tests (<10ms)
├── integration/         # End-to-end with HTTP mocking
├── property/            # Hypothesis property-based tests
└── benchmarks/          # Performance benchmarks

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

# REST API Server (003-rest-api)
uv run uvicorn proxywhirl.api:app --reload  # Development server
uv run uvicorn proxywhirl.api:app --host 0.0.0.0 --port 8000  # Production

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

### ✅ 003-rest-api (Implementation Complete)
**Status**: Implementation Complete (Tests Pending)

**User Stories Implemented**:
- US1 (P1): Proxied Requests - POST /api/v1/request endpoint with failover
- US2 (P2): Pool Management - CRUD operations for proxy pool
- US3 (P2): Monitoring - Health, readiness, status, metrics endpoints
- US4 (P3): Configuration - Runtime config updates via API

**Key Features**:
- 15 RESTful endpoints (OpenAPI/Swagger docs at /docs)
- Rate limiting (slowapi): 100 req/min default, 50 req/min for proxied requests
- Optional API key authentication (PROXYWHIRL_REQUIRE_AUTH env var)
- CORS support for cross-origin requests
- Graceful shutdown with resource cleanup
- Comprehensive error handling with structured responses

## Future Features (Planned)

- 002-cli-interface: Command-line tool
- 004-rotation-strategies-intelligent: ML-based strategies
- 005-caching-mechanisms-storage: Redis backends
- 006-health-monitoring-continuous: Background health checks
- 008-metrics-observability-performance: Metrics and observability
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

## Active Technologies
- Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13) (005-caching-mechanisms-storage)
- Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13) + httpx (HTTP client with proxy support), threading (background health checks), loguru (structured logging) (006-health-monitoring-continuous)
- Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13) (008-metrics-observability-performance)
- L3 SQLite cache tier for health state persistence (reuses 005-caching infrastructure) (006-health-monitoring-continuous)

## Recent Changes
- 005-caching-mechanisms-storage: Added Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13)
- 006-health-monitoring-continuous: Added Python 3.9+ with httpx, threading, loguru
- 008-metrics-observability-performance: Added Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13)
