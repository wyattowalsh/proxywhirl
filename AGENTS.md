# AGENTS.md

> AI agent instructions for **proxywhirl** — Python proxy rotation library. Human docs: [README.md](./README.md)

## Overview

| Property | Value |
|----------|-------|
| **Language** | Python 3.9+ (uv package manager) |
| **Stack** | pytest, ruff, ty (Astral), pre-commit, GitHub Actions |
| **Key Libs** | httpx, pydantic, sqlmodel, loguru, tenacity, typer, fastapi |

## Commands

| Task | Command |
|------|---------|
| Install | `uv sync` |
| Test | `make test` / `uv run pytest tests/ -q` |
| Lint | `make lint` / `uv run ruff check proxywhirl/ tests/` |
| Format | `make format` / `uv run ruff format proxywhirl/ tests/` |
| Type check | `make type-check` / `uv run ty check proxywhirl/` |
| Quality gates | `make quality-gates` |
| Commit | `make commit` (conventional) |

**Always prefix with `uv run`** — never bare `pytest`, `python`, or `pip`.

## Parallelization

| Level | Tasks | Dependencies |
|-------|-------|--------------|
| 0 | lint, format-check, type-check | None |
| 1 | test-unit | Level 0 |
| 2 | test-integration, test-property | test-unit |
| 3 | coverage, build | All tests |

**Locks required:** `uv.lock` (write), `proxywhirl.db` (write)

## Key Modules

| Module | Purpose |
|--------|---------|
| `models/` | Pydantic models: `Proxy`, `ProxyPool`, `Session`, `*Config` |
| `strategies/` | `RoundRobinStrategy`, `WeightedStrategy`, `PerformanceBasedStrategy` |
| `rotator/` | `ProxyRotator` (sync), `AsyncProxyRotator` (async) |
| `storage.py` | `SQLiteStorage`, `FileStorage`, `ProxyTable` (SQLModel) |
| `fetchers.py` | `ProxyFetcher`, `ProxyValidator`, parsers (`JSON/CSV/PlainText/HTMLTable`) |
| `sources.py` | `ALL_SOURCES`, `RECOMMENDED_SOURCES`, predefined proxy endpoints |
| `cache/` | `CacheManager`, multi-tier caching |
| `circuit_breaker/` | `CircuitBreaker`, `AsyncCircuitBreaker` |
| `retry/` | `RetryExecutor`, `RetryPolicy`, backoff logic |
| `rate_limiting/` | `RateLimiter` (token bucket) |
| `api/` | FastAPI `/api/v1/*` routes |
| `mcp/` | MCP server for AI assistants |
| `cli.py` | Typer CLI (`proxywhirl` command) |
| `tui.py` | Textual TUI dashboard |
| `browser.py` | Playwright for JS-rendered sources |
| `config.py` | TOML config, `CLIConfig`, `DataStorageConfig` |
| `exceptions.py` | `ProxyWhirlError` hierarchy |
| `safe_regex.py` | ReDoS-safe regex utilities |
| `geo.py` | IP geolocation enrichment |
| `utils.py` | Utility functions (encryption, URL parsing, logging config) |
| `logging_config.py` | Loguru logging configuration |
| `metrics_collector.py` | Prometheus metrics collection |
| `enrichment.py` | Proxy data enrichment |
| `premium_sources.py` | Premium proxy source definitions |
| `migrations.py` | SQLModel database migrations (Alembic) |
| `exports.py` | Data export utilities |
| `rwlock.py` | Read-write lock utilities |

**Structure:** `proxywhirl/` (core), `tests/` (unit/integration/property/benchmarks/contract), `docs/`, `examples/`

**Key Exports** (from `proxywhirl/__init__.py`):
- Rotators: `ProxyRotator`, `AsyncProxyRotator`
- Models: `Proxy`, `ProxyPool`, `Session`, `ProxySource`, `HealthStatus`, `ProxyChain`, `SelectionContext`, `ProxyCredentials`, `ProxySourceConfig`, `SourceStats`, `HealthMonitor`, `ProxyFormat`, `RenderMode`, `ValidationLevel`
- Config: `ProxyConfiguration`, `StrategyConfig`, `CircuitBreakerConfig`, `RetryPolicy`, `CacheConfig`, `DataStorageConfig`
- Components: `CacheManager`, `CircuitBreaker`, `AsyncCircuitBreaker`, `RetryExecutor`, `BrowserRenderer`, `ProxyFetcher`, `ProxyValidator`
- Strategies: `RotationStrategy` (protocol), `StrategyRegistry`, all 9 strategy classes
- Parsers: `JSONParser`, `CSVParser`, `PlainTextParser`, `HTMLTableParser`
- Sources: `ALL_SOURCES`, `RECOMMENDED_SOURCES`, `ALL_HTTP_SOURCES`, `ALL_SOCKS4_SOURCES`, `ALL_SOCKS5_SOURCES`, `API_SOURCES`
- Exceptions: `ProxyWhirlError`, `ProxyPoolEmptyError`, `ProxyValidationError`, `ProxyConnectionError`, `ProxyAuthenticationError`, `ProxyFetchError`, `ProxyStorageError`, `RetryableError`, `NonRetryableError`, `RegexTimeoutError`, `RegexComplexityError`, `CacheCorruptionError`, `CacheStorageError`, `CacheValidationError`, `RequestQueueFullError`
- Utils: `configure_logging`, `encrypt_credentials`, `decrypt_credentials`, `generate_encryption_key`, `deduplicate_proxies`, `is_valid_proxy_url`, `parse_proxy_url`, `validate_proxy_model`, `proxy_to_dict`, `create_proxy_from_url`

## Testing

`pytest` with `asyncio_mode=auto`. Markers: `@pytest.mark.slow`, `@pytest.mark.integration`, `@pytest.mark.network`. Fixtures in `tests/conftest.py`.

## Code Style

- **Naming:** `PascalCase` (classes), `snake_case` (functions), `UPPER_SNAKE_CASE` (constants), `_prefix` (private)
- **Ruff:** 100 char lines, double quotes, 4-space indent. Rules: E, F, I, N, W, UP, B, C4, SIM
- **Types:** Always type-hint public functions. Use `from __future__ import annotations`. Pydantic with `ConfigDict(frozen=True, extra="forbid")`

## Git

**Branches:** `main` (protected), `develop`, `feature/*`, `fix/*`, `claude/*`

**Commits:** `<type>(<scope>): <description>` — types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`

**Pre-commit:** ruff lint/format, commitizen, private key detection, large file check

**CI Workflows** (`.github/workflows/`): `ci.yml` (main), `security.yml`, `generate-proxies.yml` (6h cron), `validate-sources.yml`, `update-readme-stats.yml`, `release.yml`, `cd.yml`

## Boundaries

**Always:**
- Run `make lint` before commit
- Add tests for new features (test-first)
- Use type hints on public functions
- Use `loguru` for logging (never `print`)
- Prefix all Python commands with `uv run`
- Validate inputs at module boundaries

**Ask First:**
- New dependencies in `pyproject.toml`
- Schema changes (SQLModel models)
- Public API changes (`__init__.py`)
- CLI command changes
- CI/CD workflow modifications
- Changes affecting >5 files

**Never Touch:**
- `.env` files (secrets)
- `uv.lock` (auto-generated)
- `.venv/` directory
- `dist/`, `*.egg-info/`
- `*.backup`, `*.bak` files
- Files outside repo root

**Database:** `proxywhirl.db` tracked in git, CI auto-updates every 6h, local changes overwritten

## Environment Variables

| Variable | Component | Purpose |
|----------|-----------|---------|
| `PROXYWHIRL_KEY` | CLI/config | Master encryption key |
| `PROXYWHIRL_CACHE_ENCRYPTION_KEY` | cache | Fernet key for L2 cache |
| `PROXYWHIRL_STORAGE_PATH` | api | SQLite database path |
| `PROXYWHIRL_API_KEY` | api | API authentication key |
| `PROXYWHIRL_MCP_API_KEY` | mcp | MCP server auth key |
| `PROXYWHIRL_MCP_DB` | mcp | MCP database path |

See subsystem AGENTS.md files for complete environment variable lists.

## Security

| Category | Forbidden | Allowed |
|----------|-----------|---------|
| **Files** | `*.env*`, `*.pem`, `*.key`, `*secret*`, `*credential*`, `*.bak` | `proxywhirl/`, `tests/`, `docs/`, `examples/` |
| **Commands** | `rm -rf`, `curl \| sh`, `eval`, `chmod 777`, `sudo *` | `uv run *`, `make *`, `git *` |
| **Network** | Raw sockets, production APIs, external URLs not in codebase | httpx client, localhost, mocked fixtures |
| **Secrets** | Hardcoded creds, logging passwords, base64-encoded keys | `os.environ.get()`, `cryptography` lib |
| **Regex** | User-provided patterns without validation | `safe_regex.py` utilities only (ReDoS) |
| **Destructive** | Bulk deletes, schema drops, force pushes | Single-file ops, migrations, regular commits |

### Human Intervention Required

- Modifying `__init__.py` exports
- Database schema migrations
- CI/CD workflow changes
- New external dependencies
- Any operation on `main` branch

## Gotchas

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | `uv sync` |
| Async test errors | `asyncio_mode = "auto"` in pyproject.toml |
| Type errors | Use `uv run ty check` not `mypy` |
| Import errors | Use `uv run pytest` not bare `pytest` |
| HTTP mock not working | Use `respx` not `responses`; check `respx_mock` fixture |
| Pydantic validation | Use `ConfigDict(extra="forbid")` to catch typos |
| Credential exposure | Use `SecretStr`, check `redact_url()` in exceptions.py |
| MCP tests skip | MCP requires Python 3.10+; tests auto-skip on older |

## Setup

```bash
git clone https://github.com/wyattowalsh/proxywhirl.git && cd proxywhirl
uv sync && pre-commit install
```

## Subagents

**Scope:** `proxywhirl/**/*.py`, `tests/**/*.py` — **Forbidden:** `.env`, `uv.lock`, `.venv/`, `dist/`

**Context template:**
```
Working dir: /path/to/proxywhirl
Package manager: uv (ALWAYS `uv run` prefix)
Test command: uv run pytest tests/unit/test_<module>.py -v
Lint command: uv run ruff check proxywhirl/<module>.py
```

## Decision Tree

| Scenario | Action |
|----------|--------|
| Sync vs Async | `ProxyRotator` for scripts/CLI; `AsyncProxyRotator` for web/high-concurrency |
| Tests fail | 1) `uv run pytest path::test -v` 2) Check `conftest.py` 3) `uv sync` |
| Lint fails | 1) `make format` auto-fix 2) Manual fix remaining 3) Check ruff codes |
| Type errors | `uv run ty check` (not mypy) — check `ty.rules` in pyproject.toml |
| New strategy | Implement `RotationStrategy` protocol, register in `StrategyRegistry` |
| New exception | Inherit from `ProxyWhirlError`, add error code to `ProxyErrorCode` |
| HTTP mocking | Use `respx` (not `responses`), fixtures in `conftest.py` |
