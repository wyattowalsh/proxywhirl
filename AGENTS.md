# AGENTS.md

> AI agent instructions for **proxywhirl**. Human docs: [README.md](./README.md)

Advanced Python proxy rotation library with auto-fetching, validation, and persistence.

## Project Overview
<!-- agents-md:auto -->

| Property | Value |
|----------|-------|
| **Type** | Python library |
| **Language** | Python 3.9+ (targeting 3.9, 3.10, 3.11, 3.12, 3.13) |
| **Package Manager** | uv |
| **Test Runner** | pytest + pytest-asyncio + hypothesis |
| **Linter** | ruff |
| **Type Checker** | ty (Astral) |
| **Formatter** | ruff |
| **Pre-commit** | pre-commit (ruff, commitizen) |
| **CI/CD** | GitHub Actions |
| **License** | MIT |

## Quick Reference
<!-- agents-md:auto -->

| Task | Command |
|------|---------|
| Install | `uv sync` |
| Test all | `make test` or `uv run pytest tests/ -q` |
| Test unit | `make test-unit` or `uv run pytest tests/unit/ -v` |
| Test integration | `make test-integration` |
| Test parallel | `make test-parallel` (uses pytest-xdist) |
| Test watch | `make test-watch` |
| Test property | `make test-property` (hypothesis) |
| Test benchmark | `make test-benchmark` |
| Coverage | `make coverage` |
| Lint | `make lint` or `uv run ruff check proxywhirl/ tests/` |
| Format | `make format` or `uv run ruff format proxywhirl/ tests/` |
| Type check | `make type-check` or `uv run ty check proxywhirl/` |
| Quality gates | `make quality-gates` (lint + type-check + test + coverage) |
| CLI help | `uv run proxywhirl --help` |
| Commit | `make commit` (interactive conventional commit) |
| Bump version | `make bump` |
| Pre-commit | `pre-commit run --all-files` |

## Parallel Dispatch
<!-- agents-md:auto -->

### Parallelization Strategy

| Level | Tasks | Max Parallel | Dependencies |
|-------|-------|--------------|--------------|
| 0 | `lint`, `format-check` | Unlimited | None |
| 1 | `type-check` | Unlimited | None |
| 2 | `test-unit` | 8 | lint, type-check |
| 3 | `test-integration`, `test-property` | 4 | test-unit |
| 4 | `test-benchmark` | 1 | test-unit |
| 5 | `coverage`, `build` | 1 | All tests |

### Task Definitions for Subagents

```json
{
  "tasks": [
    {"id": "lint", "command": "uv run ruff check proxywhirl/ tests/", "parallelizable": true, "timeout": 60},
    {"id": "format-check", "command": "uv run ruff format --check proxywhirl/ tests/", "parallelizable": true, "timeout": 60},
    {"id": "type-check", "command": "uv run ty check proxywhirl/", "parallelizable": true, "timeout": 120},
    {"id": "test-unit", "command": "uv run pytest tests/unit/ -v", "parallelizable": true, "timeout": 300},
    {"id": "test-integration", "command": "uv run pytest tests/integration/ -v", "parallelizable": true, "timeout": 300},
    {"id": "test-property", "command": "uv run pytest tests/property/ -v", "parallelizable": true, "timeout": 300},
    {"id": "test-benchmark", "command": "uv run pytest tests/benchmarks/ --benchmark-only", "parallelizable": false, "timeout": 600},
    {"id": "coverage", "command": "make coverage", "parallelizable": false, "timeout": 600}
  ]
}
```

### Shared Resources

| Resource | Type | Lock Required | Notes |
|----------|------|---------------|-------|
| `uv.lock` | Lockfile | Yes (write) | Auto-generated, never edit manually |
| `proxywhirl.db` | Database | Yes (write) | SQLite, tracked in git |
| `.venv/` | Environment | No | Read-only after `uv sync` |
| `logs/` | Output | No | Test outputs, coverage reports |
| `.benchmarks/` | Output | No | Benchmark results |

## Module Navigation
<!-- agents-md:auto -->

| Module | Purpose | Key Classes/Functions |
|--------|---------|----------------------|
| `proxywhirl/__init__.py` | Public API exports | All public symbols |
| `proxywhirl/models.py` | Pydantic data models | `Proxy`, `ProxyPool`, `ProxyCredentials`, `Session` |
| `proxywhirl/strategies.py` | Rotation strategies | `RoundRobinStrategy`, `WeightedStrategy`, `PerformanceBasedStrategy` |
| `proxywhirl/rotator.py` | Main rotator class | `ProxyRotator` |
| `proxywhirl/async_client.py` | Async client | `AsyncProxyRotator` |
| `proxywhirl/storage.py` | SQLite persistence | SQLModel ORM |
| `proxywhirl/fetchers.py` | Proxy list fetchers | `ProxyFetcher`, `ProxyValidator`, parsers |
| `proxywhirl/sources.py` | Built-in proxy sources | `ALL_SOURCES`, `RECOMMENDED_SOURCES` |
| `proxywhirl/cache/` | Multi-tier caching | `CacheManager`, `CacheConfig` |
| `proxywhirl/rate_limiting/` | Rate limiting | `RateLimiter` |
| `proxywhirl/mcp/` | MCP server integration | `MCPServer` |
| `proxywhirl/circuit_breaker.py` | Circuit breaker pattern | `CircuitBreaker`, `AsyncCircuitBreaker` |
| `proxywhirl/retry_executor.py` | Retry with backoff | `RetryExecutor`, `RetryPolicy` |
| `proxywhirl/cli.py` | Typer CLI | `proxywhirl` command |
| `proxywhirl/api.py` | FastAPI REST API | `/api/v1/*` endpoints |
| `proxywhirl/exceptions.py` | Custom exceptions | `ProxyWhirlError` hierarchy |
| `proxywhirl/config.py` | Configuration | `DataStorageConfig` |
| `proxywhirl/utils.py` | Utilities | URL parsing, encryption, logging |

## Project Structure
<!-- agents-md:auto -->

```
proxywhirl/                    # Core library
├── __init__.py                # Public API exports (~250 symbols)
├── models.py                  # Pydantic data models (Proxy, ProxyPool, etc.)
├── strategies.py              # Rotation strategies (10+ strategies)
├── rotator.py                 # Main ProxyRotator class
├── async_client.py            # AsyncProxyRotator for async workflows
├── storage.py                 # SQLite persistence with SQLModel
├── fetchers.py                # Proxy list fetchers and parsers
├── sources.py                 # Built-in proxy source definitions
├── exceptions.py              # Custom exception hierarchy
├── config.py                  # Configuration management
├── utils.py                   # Utilities (URL parsing, encryption)
├── cli.py                     # Typer CLI entry point
├── api.py                     # FastAPI REST API
├── api_models.py              # API request/response models
├── circuit_breaker.py         # Sync circuit breaker
├── circuit_breaker_async.py   # Async circuit breaker
├── retry_executor.py          # Retry with backoff logic
├── retry_policy.py            # Retry policy configuration
├── retry_metrics.py           # Retry metrics and analytics
├── browser.py                 # Playwright browser renderer
├── safe_regex.py              # ReDoS-safe regex utilities
├── rwlock.py                  # Read-write lock implementation
├── cache/                     # Cache subsystem
│   ├── __init__.py
│   ├── manager.py             # CacheManager
│   ├── tiers.py               # Multi-tier cache implementation
│   ├── crypto.py              # Cache encryption
│   └── models.py              # Cache data models
├── rate_limiting/             # Rate limiting subsystem
│   ├── __init__.py
│   ├── limiter.py             # RateLimiter implementation
│   └── models.py              # Rate limiting models
└── mcp/                       # MCP server integration
    ├── __init__.py
    ├── server.py              # MCP server implementation
    └── auth.py                # MCP authentication

tests/
├── unit/                      # Unit tests (~60 files)
├── integration/               # Integration tests (~15 files)
├── property/                  # Property-based tests (hypothesis)
├── benchmarks/                # Performance benchmarks
├── contract/                  # Contract tests
└── conftest.py                # Shared fixtures

docs/                          # Sphinx documentation
├── source/                    # Documentation source
└── Makefile                   # Docs build

examples/                      # Usage examples
├── notebooks/                 # Jupyter notebooks
└── python/                    # Python examples

.github/workflows/             # CI/CD
├── ci.yml                     # Main CI pipeline
├── cd.yml                     # Continuous deployment
├── security.yml               # Security scanning
└── generate-proxies.yml       # Proxy database update
```

## Testing

### Framework Stack

- **pytest** — Test runner with plugins
- **pytest-asyncio** — Async test support (mode: `auto`)
- **pytest-cov** — Coverage reporting
- **pytest-xdist** — Parallel test execution
- **pytest-benchmark** — Performance benchmarks
- **hypothesis** — Property-based testing
- **syrupy** — Snapshot testing
- **respx** — HTTP mocking for httpx
- **polyfactory** — Test data factories

### Test Patterns

```python
import pytest
from proxywhirl import ProxyRotator, Proxy

@pytest.fixture
def rotator():
    """Sync fixture for ProxyRotator."""
    return ProxyRotator()

@pytest.fixture
async def async_rotator():
    """Async fixture - auto mode handles this."""
    from proxywhirl import AsyncProxyRotator
    return AsyncProxyRotator()

async def test_get_proxy(rotator):
    """Async tests work automatically with asyncio_mode=auto."""
    proxy = await rotator.get_proxy()
    assert proxy is not None
    assert isinstance(proxy, Proxy)

@pytest.mark.slow
def test_slow_operation():
    """Mark slow tests - skip with: pytest -m 'not slow'"""
    pass

@pytest.mark.integration
def test_external_service():
    """Mark integration tests."""
    pass
```

### Test Markers

| Marker | Purpose | Example |
|--------|---------|---------|
| `@pytest.mark.slow` | Slow tests | `pytest -m "not slow"` |
| `@pytest.mark.integration` | Integration tests | `pytest -m integration` |
| `@pytest.mark.unit` | Unit tests | `pytest -m unit` |
| `@pytest.mark.benchmark` | Benchmarks | `pytest --benchmark-only` |
| `@pytest.mark.snapshot` | Snapshot tests | `pytest -m snapshot` |
| `@pytest.mark.property` | Property tests | `pytest -m property` |
| `@pytest.mark.network` | Network-dependent | `pytest -m "not network"` |
| `@pytest.mark.flaky` | Flaky tests | Auto-rerun in CI |

## Code Style

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Classes | `PascalCase` | `ProxyRotator`, `CacheConfig` |
| Functions/methods | `snake_case` | `get_proxy`, `validate_proxy` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_TIMEOUT`, `MAX_RETRIES` |
| Private | `_leading_underscore` | `_internal_method`, `_cache` |
| Type aliases | `PascalCase` | `ProxyDict`, `StrategyFunc` |

### Ruff Configuration

- **Line length:** 100 characters
- **Quote style:** Double quotes
- **Indent:** Spaces (4)
- **Rules:** E, F, I, N, W, UP, B, C4, SIM
- **Ignored:** E501 (line length in some cases), B904, SIM105, B007

### Type Hints

```python
from __future__ import annotations
from typing import Optional, List, Dict, Any, Callable, TypeVar

# Always use type hints for public functions
async def get_proxy(
    self,
    protocol: Optional[str] = None,
    country: Optional[str] = None,
) -> Proxy:
    """Get a proxy with optional filters."""
    ...

# Use Pydantic models for data validation
from pydantic import BaseModel, Field

class ProxyConfig(BaseModel):
    timeout: float = Field(default=30.0, ge=0)
    retries: int = Field(default=3, ge=0)
```

## Key Libraries

| Library | Purpose | Usage |
|---------|---------|-------|
| `httpx` | HTTP client | Proxy requests, async support |
| `pydantic` | Data validation | Models, settings, serialization |
| `sqlmodel` | Database ORM | SQLite persistence |
| `loguru` | Logging | Structured logging (use instead of `print()`) |
| `tenacity` | Retry logic | Exponential backoff, circuit breaker |
| `typer` | CLI | Command-line interface |
| `fastapi` | REST API | `/api/v1/*` endpoints |
| `rich` | Terminal output | Tables, progress bars |
| `playwright` | Browser automation | JS-rendered proxy sources |
| `cryptography` | Encryption | Credential encryption |

## Git Workflow

### Branches

| Branch | Purpose |
|--------|---------|
| `main` | Production, protected |
| `develop` | Integration branch |
| `feature/*` | New features |
| `fix/*` | Bug fixes |
| `claude/*` | AI agent branches |

### Conventional Commits

```bash
# Format: <type>(<scope>): <description>

feat(rotator): add circuit breaker support
fix(cache): handle TTL expiration edge case
docs(api): update REST API reference
chore(deps): update httpx to 0.26.0
refactor(strategies): extract base strategy class
test(unit): add property tests for ProxyPool
perf(storage): optimize batch insert queries
```

**Types:** `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `ci`, `style`, `build`

### Pre-commit Hooks

Automatically runs on commit:
1. Trailing whitespace removal
2. End-of-file fixer
3. YAML/JSON/TOML syntax check
4. Large file check (max 1MB)
5. Private key detection
6. Ruff linter (with auto-fix)
7. Ruff formatter
8. Commitizen (commit message validation)

## CI/CD Pipeline

### GitHub Actions Jobs

| Job | Trigger | Python Versions |
|-----|---------|-----------------|
| `lint` | push, PR | 3.11 |
| `typecheck` | push, PR | 3.11 |
| `commitlint` | PR only | 3.11 |
| `test` | push, PR | 3.9, 3.10, 3.11, 3.12, 3.13 |
| `test-all-extras` | push, PR | 3.11 |
| `benchmark` | push, PR | 3.11 |
| `build` | after tests pass | 3.11 |

### Quality Gates

All must pass before merge:
- `uv run ruff check .` — Zero lint errors
- `uv run ruff format --check .` — Formatting compliant
- `uv run ty check proxywhirl/` — Zero type errors
- `uv run pytest` — All tests passing
- Benchmark regression < 10%

## Boundaries

### Always Do

- Run `make lint` before committing
- Add tests for new features (test-first preferred)
- Use type hints for all public functions
- Use existing Pydantic models from `models.py`
- Use `loguru` for logging, never `print()`
- Use `uv run` prefix for all Python commands
- Follow conventional commits format

### Ask First

- Adding new dependencies to `pyproject.toml`
- Changing database schema (SQLModel models)
- Modifying public API in `__init__.py`
- Changing CLI command structure
- Adding new optional dependency groups
- Modifying CI/CD workflows

### Never Touch

- `.env` files (secrets, API keys)
- `uv.lock` (auto-generated by uv)
- `.venv/` (virtual environment)
- `dist/` (build outputs)
- `logs/htmlcov/` (coverage reports)
- `*.egg-info/` (package metadata)
- `*.backup`, `*.bak` files

### Database Strategy

- `proxywhirl.db` is **tracked in git** for analytics continuity
- Updated automatically by CI/CD workflow every 6 hours
- Uses DELETE journal mode (not WAL) for git compatibility
- Local modifications will be overwritten by CI
- Use aggregation script for local updates:
  ```bash
  uv run python scripts/aggregate_proxies.py
  ```

## Gotchas

### Common Pitfalls

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `uv sync` first |
| Tests fail with async errors | Ensure `asyncio_mode = "auto"` in pyproject.toml |
| Type checker errors | Run `uv run ty check proxywhirl/` not `mypy` |
| Pre-commit fails | Run `pre-commit install` after clone |
| Import errors in tests | Use `uv run pytest`, not bare `pytest` |
| Database locked | Ensure no other process has `proxywhirl.db` open |

### Python Command Rules

**ALWAYS use `uv run` prefix:**

```bash
# ✅ CORRECT
uv run pytest tests/
uv run python script.py
uv run ruff check .

# ❌ WRONG
pytest tests/
python script.py
pip install package
```

### Async Testing

```python
# No need for @pytest.mark.asyncio - auto mode handles it
async def test_async_operation():
    result = await some_async_function()
    assert result is not None

# Fixtures can be async too
@pytest.fixture
async def async_client():
    client = await create_async_client()
    yield client
    await client.close()
```

### Pydantic v2 Patterns

```python
from pydantic import BaseModel, Field, ConfigDict

class MyModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,  # Immutable
        extra="forbid",  # No extra fields
    )

    name: str = Field(..., min_length=1)
    value: int = Field(default=0, ge=0)
```

## Environment Setup

### Prerequisites

- Python 3.9+ (3.11 recommended)
- uv package manager
- git

### Quick Start

```bash
# Clone repository
git clone https://github.com/wyattowalsh/proxywhirl.git
cd proxywhirl

# Install dependencies
uv sync

# Install pre-commit hooks
pre-commit install

# Verify installation
uv run pytest tests/unit/ -v --tb=short

# Run CLI
uv run proxywhirl --help
```

### Optional Dependencies

```bash
# Install with all extras
uv sync --all-extras

# Or specific extras
uv pip install -e ".[storage]"     # SQLModel storage
uv pip install -e ".[security]"    # Cryptography
uv pip install -e ".[js]"          # Playwright for JS rendering
uv pip install -e ".[analytics]"   # pandas, numpy, scikit-learn
uv pip install -e ".[mcp]"         # MCP server (Python 3.10+)
uv pip install -e ".[docs]"        # Sphinx documentation
uv pip install -e ".[dev]"         # Development tools
```

## Subagent Instructions

When spawning subagents for this project:

### Context to Provide

```markdown
## Task Context

**Working Directory**: /path/to/proxywhirl
**Package Manager**: uv (ALWAYS use `uv run` prefix)

**Scope**:
- Allowed: `proxywhirl/**/*.py`, `tests/**/*.py`
- Forbidden: `.env`, `uv.lock`, `.venv/`, `dist/`

**AGENTS.md files** (read first):
1. `AGENTS.md` (this file)
2. `.specify/memory/AGENTS.md` (constitution compliance)
```

### Scoped Task Example

```json
{
  "task": "Add retry logic to ProxyFetcher",
  "scope": {
    "allowed_files": ["proxywhirl/fetchers.py", "tests/unit/test_fetchers.py"],
    "forbidden_files": ["proxywhirl/__init__.py"],
    "max_files_to_modify": 5
  },
  "commands": {
    "test": "uv run pytest tests/unit/test_fetchers.py -v",
    "lint": "uv run ruff check proxywhirl/fetchers.py"
  }
}
```
