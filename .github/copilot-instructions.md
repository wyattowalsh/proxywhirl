# ProxyWhirl Development Guide

ProxyWhirl is a Python 3.13+ library for managing rotating proxies with pluggable proxy source loaders, flexible caching, and comprehensive validation.

## Architecture Overview

### Core Components
- **ProxyWhirl**: Main orchestrator class in `proxywhirl/core.py` (lines 1-621)
- **ProxyCache**: Multi-backend cache system (memory, JSON, SQLite) 
- **BaseLoader**: Abstract base class for proxy source loaders in `proxywhirl/loaders/base.py`
- **Pydantic Models**: Strict data validation in `proxywhirl/models.py`

### Key Design Patterns

#### Loader Plugin Architecture
All proxy sources implement `BaseLoader` with a simple interface:
```python
class CustomLoader(BaseLoader):
    def load(self) -> DataFrame:
        # Return DataFrame with proxy data
```
Existing loaders: FreshProxyList, TheSpeedX, Clarketm, Monosans, ProxyScrape, ProxyNova, OpenProxySpace.

#### Pydantic-First Data Modeling
- All data structures use Pydantic with strict validation
- `Proxy` model with IP validation, scheme enums, country codes
- Use `model_validator` and `field_validator` for complex validation
- Example: Country codes auto-converted to uppercase

#### Multi-Backend Caching
```python
# Memory (default), JSON file, or SQLite database
cache = ProxyCache(CacheType.SQLITE, Path("proxies.db"))
```

## Development Workflows

### Testing
- **Run tests**: `make test` (uses `-n auto` for parallel execution)
- **Coverage**: Automatic HTML reports in `logs/coverage/`
- **Async testing**: All async functions use `@pytest.mark.asyncio`
- **E2E CLI tests**: Use `os.environ.get("PYTEST_CURRENT_TEST")` checks to avoid side effects

### Code Quality
- **Complete pipeline**: `make quality` (format → lint → test)
- **Formatting**: `make format` (black + isort, 100 char line length)
- **Linting**: `make lint` (ruff + pylint + mypy in sequence)
- **Environment**: `make setup` (creates venv, syncs all dependencies)

### CLI Development
- Uses Typer with async support via `_run()` helper in `cli.py`
- Commands: `fetch`, `list`, `validate`, `get`
- Always add `--cache-path` validation for JSON/SQLite cache types

## Project-Specific Conventions

### Async Patterns
- Use `httpx.AsyncClient` for HTTP requests
- All core operations are async with sync CLI wrappers
- Leverage `asyncio.gather()` for concurrent proxy validation

### Error Handling
- Use `loguru` for structured logging (not standard logging)
- Graceful degradation: continue processing even if some proxies fail validation
- Return counts/results rather than raising on empty results

### Data Validation
- Always validate IP addresses using `ipaddress` module
- Country codes: 2-char uppercase (auto-converted)
- Port range: 1-65535
- Schemes: HTTP, HTTPS, SOCKS4, SOCKS5 (StrEnum)

### Testing Patterns
- Async test functions for all core functionality
- Use `pytest.fixture` for ProxyWhirl instances
- Mock external HTTP requests in unit tests
- Separate integration tests for real proxy validation

## Key Files for New Features

- **New proxy source**: Add loader to `proxywhirl/loaders/`
- **Core logic changes**: Modify `proxywhirl/core.py` (ProxyWhirl/ProxyCache classes)
- **Data models**: Extend `proxywhirl/models.py`
- **CLI commands**: Add to `proxywhirl/cli.py`
- **Tests**: Create corresponding test file in `tests/`

## Build System

- **Package manager**: `uv` (not pip/poetry)
- **Python version**: 3.13+ required
- **Dependencies**: Grouped by purpose (test, lint, format, notebook)
- **Entry point**: CLI available as `proxywhirl` command after install
- **Build tool**: Makefile with all development targets

## CI/CD Pipeline

### GitHub Actions Workflows
- **CI Pipeline** (`.github/workflows/ci.yml`): Runs on every push/PR
  - Quality checks: `make quality` (format → lint → test)
  - Security audit with pip-audit
  - Integration tests (optional, triggered by label)
  - Coverage reports uploaded as artifacts

- **Documentation** (`.github/workflows/docs.yml`): Auto-deploy docs
  - API docs generation from Python docstrings
  - GitHub Pages deployment on main branch
  - Link checking on PRs

- **Release** (`.github/workflows/release.yml`): Automated releases
  - Version validation and pre-release testing
  - PyPI publishing with trusted publishing
  - GitHub releases with auto-generated changelog
  - Post-release documentation updates

- **Dependabot** (`.github/dependabot.yml`): Automated dependency updates
  - Python dependencies (weekly, targets dev branch)
  - Node.js dependencies (weekly, targets dev branch)
  - GitHub Actions (monthly, targets dev branch)

### Development Workflow
1. Create feature branch from `dev`
2. Make changes, commit, push
3. CI automatically runs quality checks
4. Create PR to `dev` branch
5. CI runs full test suite
6. After merge, dev branch tested
7. Release by creating version tag

## Documentation

Separate Next.js documentation site in `docs/` using Fumadocs:
- Run: `make docs-dev` or `make dev`
- Content: `docs/content/docs/`
- API docs generation: `docs/scripts/generate-api-docs.mjs`
- Auto-deploy: GitHub Pages on main branch pushes
