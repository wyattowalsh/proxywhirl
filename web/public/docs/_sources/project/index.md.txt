---
title: Project
---

# Project

## Development Setup

Get a working development environment in under a minute.

### Prerequisites

- **Python 3.9+** (3.11+ recommended for best performance)
- **[uv](https://docs.astral.sh/uv/)** -- fast Python package manager from Astral
- **git** with pre-commit support

### Clone & Install

```bash
git clone https://github.com/wyattowalsh/proxywhirl.git
cd proxywhirl
uv sync
pre-commit install
```

### Verify Installation

```bash
# Run the test suite
uv run pytest tests/ -q

# Check linting
uv run ruff check proxywhirl/ tests/

# Check types
uv run ty check proxywhirl/
```

### Make Commands

All common operations are available via `make`:

```{list-table}
:header-rows: 1
:widths: 25 35 40

* - Command
  - Equivalent
  - Purpose
* - `make test`
  - `uv run pytest tests/ -q`
  - Run all tests
* - `make lint`
  - `uv run ruff check proxywhirl/ tests/`
  - Lint with ruff
* - `make format`
  - `uv run ruff format proxywhirl/ tests/`
  - Auto-format code
* - `make type-check`
  - `uv run ty check proxywhirl/`
  - Type check with ty (Astral)
* - `make quality-gates`
  - all of the above
  - Full pre-merge validation
* - `make commit`
  - conventional commit
  - Commitizen-guided commit
```

```{admonition} Always use uv run
:class: warning
Never run bare `pytest`, `python`, or `pip`. Always prefix with `uv run` to use the project's virtual environment.
```

## Contributing

### Workflow

1. **Fork & clone** the repository
2. **Create a branch** from `main`: `git checkout -b feature/my-feature` or `fix/my-fix`
3. **Write tests first** -- every new feature needs test coverage
4. **Implement** your changes
5. **Run quality gates**: `make quality-gates`
6. **Commit** using conventional commits: `<type>(<scope>): <description>`
7. **Open a PR** against `main`

### Branch Naming

| Pattern | Use |
|---------|-----|
| `feature/*` | New features |
| `fix/*` | Bug fixes |
| `claude/*` | AI-assisted changes |
| `develop` | Integration branch |

### Commit Convention

Commits follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(strategies): add failover chain support
fix(cache): handle L2 encryption key rotation
docs(guides): expand async client examples
test(rotator): add property tests for weighted selection
refactor(storage): simplify SQLite connection pooling
perf(strategies): reduce EMA calculation overhead
chore(deps): update httpx to 0.28
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`

### Code Style

- **Line length**: 100 characters
- **Quotes**: double quotes
- **Indent**: 4 spaces
- **Naming**: `PascalCase` (classes), `snake_case` (functions), `UPPER_SNAKE_CASE` (constants)
- **Imports**: sorted by ruff (isort-compatible)
- **Types**: always type-hint public functions; use `from __future__ import annotations`
- **Models**: Pydantic with `ConfigDict(frozen=True, extra="forbid")`
- **Logging**: use `loguru` (never `print`)

### Pre-commit Hooks

The following hooks run automatically on every commit:

- **ruff** -- lint and format check
- **commitizen** -- conventional commit message validation
- **private key detection** -- blocks accidental secret commits
- **large file check** -- prevents binary bloat

### Testing Guidelines

| Marker | Purpose | Example |
|--------|---------|---------|
| (none) | Unit tests | `tests/unit/test_strategies.py` |
| `@pytest.mark.slow` | Long-running tests | Large pool simulations |
| `@pytest.mark.integration` | Integration tests | `tests/integration/` |
| `@pytest.mark.network` | Requires network | Live proxy validation |

HTTP mocking uses `respx` (not `responses`). Async tests run with `asyncio_mode = "auto"`.

```bash
# Run specific test file
uv run pytest tests/unit/test_strategies.py -v

# Run tests matching a pattern
uv run pytest -k "test_weighted" -v

# Run with coverage
uv run pytest tests/ --cov=proxywhirl --cov-report=term-missing
```

### Extending with Custom Strategies

ProxyWhirl supports a plugin architecture via `StrategyRegistry`. Implement the `RotationStrategy` protocol and register your strategy:

```python
from proxywhirl import StrategyRegistry, RotationStrategy

class MyStrategy:
    def select(self, pool, context=None):
        return pool.get_healthy_proxies()[0]

    def record_result(self, proxy, success, response_time_ms):
        pass

registry = StrategyRegistry()
registry.register_strategy("my-strategy", MyStrategy)
```

See {doc}`/reference/python-api` for the full `RotationStrategy` protocol and {doc}`/guides/advanced-strategies` for composite strategy patterns.

## CI/CD Pipelines

All workflows live in `.github/workflows/`:

```{list-table}
:header-rows: 1
:widths: 25 20 55

* - Workflow
  - Trigger
  - Purpose
* - `ci.yml`
  - push / PR
  - Lint, type-check, test matrix (Python 3.9-3.13)
* - `security.yml`
  - push / schedule
  - Dependency audit, secret scanning
* - `generate-proxies.yml`
  - cron (every 6h)
  - Fetch proxies from all built-in sources, update `proxywhirl.db`
* - `validate-sources.yml`
  - push / PR
  - Verify proxy source URLs are reachable
* - `update-readme-stats.yml`
  - after proxy generation
  - Update README badge counts
* - `release.yml`
  - tag push
  - Build and publish to PyPI
* - `cd.yml`
  - release
  - Deploy docs and dashboard
```

### Quality Gate Pipeline

The CI pipeline enforces this dependency order:

```
Level 0: lint + format-check + type-check  (parallel, no deps)
    |
Level 1: unit tests  (depends on Level 0)
    |
Level 2: integration + property tests  (depends on Level 1)
    |
Level 3: coverage + build  (depends on all tests)
```

## Architecture

### Module Map

```{list-table}
:header-rows: 1
:widths: 22 78

* - Module
  - Purpose
* - `models/`
  - Pydantic models: `Proxy`, `ProxyPool`, `Session`, `SelectionContext`, `*Config`
* - `strategies/`
  - 9 rotation strategies + `RotationStrategy` protocol + `StrategyRegistry`
* - `rotator/`
  - `ProxyRotator` (sync) and `AsyncProxyRotator` (async) -- core HTTP clients
* - `storage.py`
  - `SQLiteStorage`, `FileStorage`, `ProxyTable` (SQLModel ORM)
* - `fetchers.py`
  - `ProxyFetcher`, `ProxyValidator`, parsers (`JSON`, `CSV`, `PlainText`, `HTMLTable`)
* - `sources.py`
  - Hundreds of pre-configured `ProxySourceConfig` instances (`ALL_SOURCES`, `RECOMMENDED_SOURCES`)
* - `cache/`
  - `CacheManager` with L1 in-memory, L2 encrypted disk, L3 SQLite tiers
* - `circuit_breaker/`
  - `CircuitBreaker`, `AsyncCircuitBreaker` with state machine
* - `retry/`
  - `RetryExecutor`, `RetryPolicy`, backoff strategies (exponential, linear)
* - `rate_limiting/`
  - `RateLimiter` (token bucket), sync and async variants
* - `api/`
  - FastAPI REST API (`/api/v1/*` routes) with OpenAPI
* - `mcp/`
  - MCP server for AI assistant integration (Claude, GPT)
* - `cli.py`
  - Typer CLI (`proxywhirl` command, 9 subcommands)
* - `config.py`
  - TOML config loader, `CLIConfig`, `DataStorageConfig`
* - `exceptions.py`
  - `ProxyWhirlError` hierarchy, `ProxyErrorCode` enum, URL redaction
* - `safe_regex.py`
  - ReDoS-safe regex utilities
* - `geo.py`
  - IP geolocation enrichment (GeoIP2)
```

For the full public API surface, see {doc}`/reference/python-api`.

### Key Exports

The top-level `proxywhirl` package exports:

- **Rotators**: `ProxyRotator`, `AsyncProxyRotator`
- **Models**: `Proxy`, `ProxyPool`, `Session`, `ProxySource`, `HealthStatus`, `SelectionContext`, `ProxyCredentials`, `ProxyConfiguration`
- **Strategies**: `RoundRobinStrategy`, `RandomStrategy`, `WeightedStrategy`, `LeastUsedStrategy`, `PerformanceBasedStrategy`, `SessionPersistenceStrategy`, `GeoTargetedStrategy`, `CostAwareStrategy`, `CompositeStrategy`
- **Config**: `StrategyConfig`, `CircuitBreakerConfig`, `RetryPolicy`, `CacheConfig`, `DataStorageConfig`
- **Components**: `CacheManager`, `CircuitBreaker`, `AsyncCircuitBreaker`, `RetryExecutor`, `ProxyFetcher`, `ProxyValidator`, `BrowserRenderer`
- **Sources**: `ALL_SOURCES`, `RECOMMENDED_SOURCES`, `ALL_HTTP_SOURCES`, `ALL_SOCKS4_SOURCES`, `ALL_SOCKS5_SOURCES`, `API_SOURCES`
- **Utilities**: `configure_logging`, `encrypt_credentials`, `decrypt_credentials`, `deduplicate_proxies`

## Environment Variables

```{list-table}
:header-rows: 1
:widths: 35 15 50

* - Variable
  - Component
  - Purpose
* - `PROXYWHIRL_KEY`
  - CLI/config
  - Master encryption key
* - `PROXYWHIRL_CACHE_ENCRYPTION_KEY`
  - cache
  - Fernet key for L2 cache
* - `PROXYWHIRL_STORAGE_PATH`
  - api
  - SQLite database path
* - `PROXYWHIRL_API_KEY`
  - api
  - API authentication key
* - `PROXYWHIRL_MCP_API_KEY`
  - mcp
  - MCP server auth key
* - `PROXYWHIRL_MCP_DB`
  - mcp
  - MCP database path
```

See {doc}`/reference/configuration` for the full TOML configuration reference and environment variable override behavior.

## Current Health

- **Tests**: 2700+ passing across unit, integration, property, contract, and benchmark suites
- **Performance**: All selection strategies operate within 2.8-26 us (<5 ms target)
- **Proxy sources**: Hundreds of sources, refreshed every 6 hours via CI
- **Python**: Tested on 3.9, 3.10, 3.11, 3.12, and 3.13

## Changelog Highlights

### Recent

- **Composite strategies** -- chain filters and selectors with <5 us overhead via `CompositeStrategy`
- **Cost-aware strategy** -- budget-optimize proxy selection with `CostAwareStrategy`
- **MCP server** -- Model Context Protocol integration for AI assistants
- **Free proxy lists** -- auto-updated every 6 hours from hundreds of sources
- **Interactive dashboard** -- browse and export at [proxywhirl.com](https://proxywhirl.com/)
- **Rate limiting API** -- token bucket algorithm, per-proxy and global limits
- **Cache encryption** -- Fernet-encrypted L2 cache tier

### Phase Completion Status

```{list-table}
:header-rows: 1
:widths: 18 20 62

* - Phase
  - Status
  - Notable wins
* - Phase 6 -- Performance-based strategy
  - {bdg-success}`Complete`
  - EMA-driven scoring delivers 15-25% faster selection with <26 us overhead.
* - Phase 7 -- Session persistence
  - {bdg-success}`Complete`
  - Sticky sessions with TTL cleanup and zero request leakage at 99.9% stickiness.
* - Phase 8 -- Geo-targeted routing
  - {bdg-success}`Complete`
  - Region-aware filtering validated against 100% accuracy in SC-006.
* - Phase 9 -- Strategy composition
  - {bdg-success}`Complete`
  - Composite pipelines, hot-swapping under load, and plugin registry (SC-009/010).
* - Phase 10 -- Polish & validation
  - {bdg-warning}`In progress`
  - Optional tasks: coverage uplift, large-scale property tests, release packaging.
```

## License

ProxyWhirl is open source software released under the [MIT License](https://github.com/wyattowalsh/proxywhirl/blob/main/LICENSE).

---

**Related:** {doc}`/guides/automation` for CI integration | {doc}`/reference/configuration` for config reference | {doc}`/getting-started/index` for quickstart

```{admonition} Historical reports
:class: info
Detailed phase completion reports live alongside the source tree under `docs/` (e.g., `PHASE_9_COMPLETION.md`) and capture acceptance criteria per milestone.
```
