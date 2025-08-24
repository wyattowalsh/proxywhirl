---
applyTo: "proxywhirl/**/*.py"
---

# ProxyWhirl Backend Development Instructions

Follow these instructions for Python 3.13+ backend development with AI assistance and MCP tool orchestration.

## Environment Setup Requirements

### Package Management (MANDATORY)
Always use `uv` exclusively for ProxyWhirl backend development:

```bash
# REQUIRED: Environment commands
uv sync --all-extras --dev        # Install all dependencies with dev tools
uv run python -m proxywhirl --help  # Execute via uv for environment isolation
uv run pytest tests/               # Test execution with proper environment
uv run make quality                # Complete quality pipeline
```

### SOTA 2025 Python Features
ProxyWhirl leverages cutting-edge Python 3.13+ features:

```python
# Enhanced Pydantic v2.10+ patterns with performance optimization
from pydantic import BaseModel, model_validator, field_validator

class Proxy(BaseModel):
    # Use model_validate_json() for 2x performance improvement
    @classmethod
    def from_json(cls, json_data: str) -> 'Proxy':
        return cls.model_validate_json(json_data)  # ✅ Faster
        # vs cls.model_validate(json.loads(json_data))  # ❌ Slower
    
    # Early validation termination with FailFast
    from typing import Annotated
    from pydantic import FailFast
    validation_results: Annotated[list[bool], FailFast()]

# HTTPX advanced patterns with connection pooling
import httpx
from contextlib import asynccontextmanager

@asynccontextmanager
async def proxy_http_session():
    limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
    async with httpx.AsyncClient(limits=limits, http2=True) as client:
        yield client

# Async streaming with performance optimization
async def validate_proxy_stream(proxy: Proxy) -> AsyncIterator[ValidationResult]:
    async with proxy_http_session() as client:
        async with client.stream('GET', f'http://{proxy.ip}:{proxy.port}') as response:
            async for chunk in response.aiter_bytes():
                yield process_validation_chunk(chunk)
```

### AI-Assisted Development Integration
GitHub Copilot understands ProxyWhirl's architecture patterns:

```python
# AI recognizes ProxyWhirl-specific patterns
class ProxyLoader(BaseLoader):
    """GitHub Copilot suggests optimal loader implementations."""
    
    async def load(self) -> DataFrame:
        # AI assists with proper async patterns and error handling
        async with self.get_http_session() as session:
            response = await session.get(self.source_url)
            response.raise_for_status()
            
            # AI suggests DataFrame transformation patterns
            return pd.DataFrame(self.parse_response(response.text))

# Circuit breaker pattern recognition
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def validate_proxy_with_backoff(proxy: Proxy) -> ValidationResult:
    # AI understands retry patterns and suggests optimal configurations
    pass
```

### MCP Tool Integration for Backend Development
Before implementing backend features, use MCP research pipeline:

```bash
# Version validation for Python dependencies  
mcp_package_versi_check_pyproject_versions({"dependencies": {"pydantic": "^2.10", "httpx": "^0.28"}})

# Documentation research for latest patterns
mcp_docfork_get-library-docs("pydantic/pydantic", "v2 performance validation patterns")
mcp_docfork_get-library-docs("encode/httpx", "async streaming connection pooling")
mcp_docfork_get-library-docs("jd/tenacity", "circuit breaker retry patterns")

# Community best practices research
mcp_brave_search_brave_web_search("Python 3.13 async performance patterns 2025")
mcp_brave_search_brave_web_search("Pydantic v2 advanced validation techniques")
```

## Architecture Overview

### Core Components
- **ProxyWhirl**: Main orchestrator class in `proxywhirl/proxywhirl.py` (1186 lines) - unified interface with smart sync/async handling
- **ProxyCache**: Multi-backend cache system in `proxywhirl/cache.py` supporting memory, JSON file, and SQLite database storage
- **ProxyRotator**: Rotation strategy implementation in `proxywhirl/rotator.py` with multiple algorithms
- **ProxyValidator**: Async validator in `proxywhirl/validator.py` with concurrency and circuit-breaker patterns
- **BaseLoader**: Abstract base class for proxy source loaders in `proxywhirl/loaders/base.py`
- **Pydantic Models**: Advanced data validation and serialization in `proxywhirl/models.py` with computed fields and context awareness
- **CLI Interface**: Rich terminal interface in `proxywhirl/cli.py` with Typer framework
- **TUI Application**: Interactive terminal UI in `proxywhirl/tui.py` for real-time proxy management
- **Export System**: Multi-format data export in `proxywhirl/exporter.py` and `proxywhirl/export_models.py`
- **Configuration**: Settings management in `proxywhirl/config.py`

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

**Existing loaders**: TheSpeedX (HTTP/SOCKS), Clarketm, Monosans, ProxyScrape, Proxifly, VakhovFresh, JetkaiProxyList, UserProvided.

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
- **Commands**: `fetch` (load proxies), `list` (display cached), `validate` (test connectivity), `get` (single proxy), `health-report` (diagnostic report), `export` (multi-format export), `tui` (interactive terminal UI)
- **Critical pattern**: Always validate `--cache-path` parameter for JSON/SQLite cache types
- **Error handling**: Return exit codes, not exceptions, for CLI failures
- **Rich integration**: Uses Rich library for progress bars, tables, and styled output

## Project-Specific Conventions

### Async Programming Patterns
- **HTTP clients**: Use both `httpx.AsyncClient` and `aiohttp` for external requests depending on context
- **Design principle**: Core operations are async with sync wrappers for CLI and compatibility
- **Concurrency**: Leverage `asyncio.gather()` for concurrent proxy validation and loading
- **Error handling**: Continue processing even if individual proxies fail validation
- **Target-based validation**: Support for validating proxies against specific target URLs with health tracking
- **Session stickiness**: Proxy assignment persistence with TTL-based expiration

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
4. Add loader import to `proxywhirl/proxywhirl.py` in the `_default_loaders` list
5. Create corresponding test file in `tests/test_[source_name].py`
6. Update loader list in documentation

### Extending Core Functionality
- **Cache modifications**: Extend `ProxyCache` class methods in `proxywhirl/cache.py`
- **Data models**: Add new fields to `Proxy` model in `proxywhirl/models.py` with computed fields and validators
- **CLI commands**: Add new Typer commands to `proxywhirl/cli.py` with Rich integration
- **TUI features**: Extend interactive interface in `proxywhirl/tui.py` using Textual framework
- **Export formats**: Add new export formats in `proxywhirl/exporter.py` and update `proxywhirl/export_models.py`
- **Validation logic**: Extend validator functions in `proxywhirl/validator.py` with circuit-breaker patterns
- **Rotation strategies**: Add new algorithms in `proxywhirl/rotator.py`

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
