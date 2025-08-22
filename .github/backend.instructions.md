---
applyTo: "proxywhirl/**/*.py"
---

# ProxyWhirl Backend Development Guide

ProxyWhirl is a Python 3.13+ library for managing rotating proxies with pluggable proxy source loaders, flexible caching, and comprehensive validation.

## Architecture Overview

### Core Components
- **ProxyWhirl**: Main orchestrator class in `proxywhirl/core.py` (lines 1-621)
- **ProxyCache**: Multi-backend cache system supporting memory, JSON file, and SQLite database storage
- **BaseLoader**: Abstract base class for proxy source loaders in `proxywhirl/loaders/base.py`
- **Pydantic Models**: Strict data validation and serialization in `proxywhirl/models.py`

### Key Design Patterns

#### Loader Plugin Architecture
All proxy sources implement `BaseLoader` with a minimal interface:
```python
class CustomLoader(BaseLoader):
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
    
    def load(self) -> DataFrame:
        # Return DataFrame with columns: host, port, schemes, etc.
        # Must include 'host', 'port' as minimum requirements
        pass
```

**Existing loaders**: FreshProxyList, TheSpeedX (HTTP/SOCKS), Clarketm, Monosans, ProxyScrape, ProxyNova, OpenProxySpace.

#### Pydantic-First Data Modeling
- All data structures use Pydantic v2 with strict validation
- `Proxy` model enforces IP validation, scheme enums, country codes
- Use `model_validator` and `field_validator` for complex validation rules
- **Key pattern**: Country codes auto-converted to uppercase via `AfterValidator`
- **Validation order**: field validators → model validators → serialization

#### Multi-Backend Caching Strategy
```python
# Three cache backends with unified interface
cache = ProxyCache(CacheType.MEMORY)  # Default, fastest
cache = ProxyCache(CacheType.JSON, Path("proxies.json"))  # Persistent, simple
cache = ProxyCache(CacheType.SQLITE, Path("proxies.db"))  # Persistent, queryable
```

## Development Workflows

### Testing Strategy
- **Primary command**: `uv run pytest` (uses `-n auto` for parallel execution)
- **Coverage reports**: Automatic HTML generation in `logs/coverage/`
- **Async testing**: All async functions require `@pytest.mark.asyncio` decorator
- **CLI E2E tests**: Use `os.environ.get("PYTEST_CURRENT_TEST")` to avoid side effects during testing
- **Integration tests**: Separate real proxy validation from unit tests with mocked responses

### Code Quality Pipeline
- **Formatting**: `uv run black proxywhirl tests` (100-character line length, not 79/88)
- **Import sorting**: `uv run isort proxywhirl tests` (black-compatible profile)
- **Linting**: `uv run ruff check` (fast) + `uv run pylint` (comprehensive)
- **Type checking**: `uv run mypy` (strict mode enabled in pyproject.toml)
- **Order**: black → isort → ruff → pylint → mypy → tests

### CLI Development Patterns
- Uses Typer framework with async support via custom `_run()` helper in `cli.py`
- **Commands**: `fetch` (load proxies), `list` (display cached), `validate` (test connectivity), `get` (single proxy)
- **Critical pattern**: Always validate `--cache-path` parameter for JSON/SQLite cache types
- **Error handling**: Return exit codes, not exceptions, for CLI failures

## Project-Specific Conventions

### Async Programming Patterns
- **HTTP client**: Use `httpx.AsyncClient` for all external requests (not requests/aiohttp)
- **Design principle**: Core operations are async, CLI provides sync wrappers
- **Concurrency**: Leverage `asyncio.gather()` for concurrent proxy validation
- **Error handling**: Continue processing even if individual proxies fail validation

### Logging and Error Handling
- **Logger**: Use `loguru` exclusively (not standard logging module)
- **Philosophy**: Graceful degradation over strict failure
- **Pattern**: Return counts/results rather than raising exceptions on empty results
- **Structured logging**: Include context (proxy host, operation, timing) in log messages

### Data Validation Standards
- **IP addresses**: Always validate using `ipaddress` module before storage
- **Country codes**: Exactly 2 characters, auto-uppercase, pattern `^[A-Z]{2}$`
- **Port range**: 1-65535 (validate with Pydantic `ge=1, le=65535`)
- **Schemes**: Use StrEnum with HTTP, HTTPS, SOCKS4, SOCKS5 values only
- **Response times**: Store as float seconds, validate positive values

### Testing Patterns and Fixtures
- **Async tests**: All core functionality tests must be async with proper `await` usage
- **Fixtures**: Use `pytest.fixture` for ProxyWhirl instances, avoid global state
- **Mocking strategy**: Mock external HTTP requests in unit tests, separate integration tests
- **Test isolation**: Each test should create its own cache instance to avoid conflicts
- **Property-based testing**: Use Hypothesis for testing with random proxy data

## Implementation Guidelines

### Adding New Proxy Sources
1. Create new loader in `proxywhirl/loaders/[source_name].py`
2. Inherit from `BaseLoader` and implement `load() -> DataFrame`
3. Ensure DataFrame has required columns: `host`, `port`, `schemes`
4. Add loader import to `proxywhirl/core.py`
5. Create corresponding test file in `tests/test_[source_name].py`
6. Update loader list in documentation

### Extending Core Functionality
- **Cache modifications**: Extend `ProxyCache` class methods in `proxywhirl/core.py`
- **Data models**: Add new fields to `Proxy` model in `proxywhirl/models.py`
- **CLI commands**: Add new Typer commands to `proxywhirl/cli.py`
- **Validation logic**: Extend validator functions in core validation pipeline

### Performance Considerations
- **Database queries**: Use SQLite efficiently with proper indexing on host+port
- **Memory usage**: Stream large proxy lists instead of loading all into memory
- **Network timeouts**: Set appropriate timeouts for proxy validation (default: 5s)
- **Caching strategy**: Use memory cache for hot paths, persistent cache for cold storage

## Build System and Dependencies

### Package Management
- **Tool**: `uv` exclusively (not pip, poetry, or conda)
- **Python version**: 3.13+ required (uses latest async features)
- **Dependency groups**: `test`, `lint`, `format`, `notebook` for different workflows
- **Lock file**: `uv.lock` should be committed to ensure reproducible builds

### Entry Points and Installation
- **CLI availability**: `proxywhirl` command available after `uv pip install .`
- **Package structure**: Standard `pyproject.toml` with proper metadata
- **Dependencies**: Core dependencies minimal, development dependencies comprehensive

### Development Environment Setup
```bash
# Initial setup
make setup      # Creates venv, syncs all dependencies
make test       # Verify installation

# Daily workflow
make format     # Runs black + isort
make lint       # Runs ruff + pylint + mypy  
make test       # Runs pytest with coverage
make quality    # Complete pipeline: format → lint → test

# Alternative: Direct uv commands (if needed)
uv run black proxywhirl tests
uv run isort proxywhirl tests  
uv run ruff check
uv run pylint proxywhirl
uv run mypy proxywhirl
uv run pytest
```

## CI/CD Integration

### Automated Testing
- **GitHub Actions**: All code changes trigger automated testing via `.github/workflows/ci.yml`
- **Quality Gate**: Must pass `make quality` pipeline before merge
- **Coverage Reports**: Automatically generated and uploaded as artifacts
- **Security Scanning**: pip-audit runs on all dependencies

### Release Process
- **Automated Releases**: Create version tag to trigger `.github/workflows/release.yml`
- **PyPI Publishing**: Automatic publication to PyPI with trusted publishing
- **Documentation Updates**: API docs automatically regenerated and deployed
- **Changelog**: Auto-generated from commit history

### Branch Strategy
- **Main Branch**: Production-ready code, protected, requires PR approval
- **Dev Branch**: Integration branch for feature development
- **Feature Branches**: Created from `dev`, merged back via PR
- **Release Tags**: `v*` tags trigger automated release pipeline

## Common Patterns and Anti-Patterns

### ✅ Do This
- Use async/await for all I/O operations
- Validate data at boundaries (API responses, user input)
- Return structured results with counts and success indicators
- Log operations with context for debugging
- Use type hints on all function signatures

### ❌ Avoid This
- Blocking synchronous HTTP calls in core logic
- Silent failures without logging or error indication
- Direct database access without going through cache layer
- Hardcoded timeouts or retry logic
- Using standard logging instead of loguru
