# AGENTS.md

> AI agent instructions for **proxywhirl** — Python proxy rotation library. Human docs: [README.md](./README.md)

## Overview

| Property     | Value                                                             |
| ------------ | ----------------------------------------------------------------- |
| **Language** | Python 3.10+ (uv package manager)                                 |
| **Stack**    | pytest, ruff, ty (Astral), pre-commit, GitHub Actions             |
| **Docs**     | Fumadocs + Next.js in `web/`; legacy Sphinx sources remain under `docs/source/` |
| **Key Libs** | httpx, pydantic, sqlmodel, loguru, tenacity, typer, fastapi       |

## Commands

| Task          | Command                                                                               |
| ------------- | ------------------------------------------------------------------------------------- |
| Install       | `uv sync`                                                                             |
| Test          | `task test-fast` / `uv run pytest tests/unit/ tests/integration/ -m "not slow" --timeout=120 -q` |
| Lint          | `task lint` / `uv run ruff check proxywhirl/ tests/`                                  |
| Format        | `task format` / `uv run ruff format proxywhirl/ tests/`                               |
| Type check    | `task type-check` / `uv run ty check proxywhirl/`                                     |
| Quality gates | `task quality-gates`                                                                  |
| Docs generate | `pnpm --dir web run docs:generate`                                                    |
| Docs build    | `task docs-html` / `pnpm --dir web run build`                                         |
| Source gate   | `uv run proxywhirl sources --validate --fail-on-unhealthy --timeout 5 --concurrency 5` |

**Always prefix with `uv run`** — never bare `pytest`, `python`, or `pip`.
Use `uvx` only for intentionally isolated tools such as `uvx pip-audit` or `uvx bandit`.

## Parallelization

| Level | Tasks                           | Dependencies |
| ----- | ------------------------------- | ------------ |
| 0     | lint, format-check, type-check  | None         |
| 1     | test-unit                       | Level 0      |
| 2     | test-integration, test-property | test-unit    |
| 3     | coverage, build                 | All tests    |

**Locks required:** `uv.lock` (write), `proxywhirl.db` (write)

## Key Modules

| Module                 | Purpose                                                                    |
| ---------------------- | -------------------------------------------------------------------------- |
| `models/`              | Pydantic models: `Proxy`, `ProxyPool`, `Session`, `*Config`                |
| `strategies/`          | `RoundRobinStrategy`, `WeightedStrategy`, `PerformanceBasedStrategy`       |
| `rotator/`             | `ProxyWhirl` (sync), `AsyncProxyWhirl` (async)                             |
| `storage.py`           | `SQLiteStorage`, `FileStorage`, `ProxyTable` (SQLModel)                    |
| `fetchers.py`          | `ProxyFetcher`, `ProxyValidator`, parsers (`JSON/CSV/PlainText/HTMLTable`) |
| `sources.py`           | `ALL_SOURCES`, `RECOMMENDED_SOURCES`, predefined proxy endpoints           |
| `cache/`               | `CacheManager`, multi-tier caching                                         |
| `circuit_breaker/`     | `CircuitBreaker`, `AsyncCircuitBreaker`                                    |
| `retry/`               | `RetryExecutor`, `RetryPolicy`, backoff logic                              |
| `rate_limiting/`       | `RateLimiter` (token bucket)                                               |
| `api/`                 | FastAPI canonical `/api/*` routes                                          |
| `mcp/`                 | MCP server for AI assistants                                               |
| `cli.py`               | Typer CLI (`proxywhirl` command)                                           |
| `tui.py`               | Textual TUI dashboard                                                      |
| `browser.py`           | Playwright for JS-rendered sources                                         |
| `config.py`            | TOML config, `CLIConfig`, `DataStorageConfig`                              |
| `exceptions.py`        | `ProxyWhirlError` hierarchy                                                |
| `safe_regex.py`        | ReDoS-safe regex utilities                                                 |
| `geo.py`               | IP geolocation enrichment                                                  |
| `utils.py`             | Utility functions (encryption, URL parsing, logging config)                |
| `logging_config.py`    | Loguru logging configuration                                               |
| `metrics_collector.py` | Prometheus metrics collection                                              |
| `enrichment.py`        | Proxy data enrichment                                                      |
| `premium_sources.py`   | Premium proxy source definitions                                           |
| `migrations.py`        | SQLModel database migrations (Alembic)                                     |
| `exports.py`           | Data export utilities                                                      |
| `rwlock.py`            | Read-write lock utilities                                                  |

**Structure:** `proxywhirl/` (core), `tests/` (unit/integration/property/benchmarks/contract), `web/content/docs/` (active Fumadocs docs), `docs/` (legacy/generated assets), `examples/`

**Key Exports** (from `proxywhirl/__init__.py`):

- Rotators: `ProxyWhirl`, `AsyncProxyWhirl`
- Models: `Proxy`, `ProxyPool`, `Session`, `ProxySource`, `HealthStatus`, `ProxyChain`, `SelectionContext`, `ProxyCredentials`, `ProxySourceConfig`, `SourceStats`, `HealthMonitor`, `ProxyFormat`, `RenderMode`, `ValidationLevel`
- Config: `ProxyConfiguration`, `StrategyConfig`, `CircuitBreakerConfig`, `RetryPolicy`, `CacheConfig`, `DataStorageConfig`
- Components: `CacheManager`, `CircuitBreaker`, `AsyncCircuitBreaker`, `RetryExecutor`, `BrowserRenderer`, `ProxyFetcher`, `ProxyValidator`
- Strategies: `RotationStrategy` (protocol), `StrategyRegistry`, all 9 strategy classes
- Parsers: `JSONParser`, `CSVParser`, `PlainTextParser`, `HTMLTableParser`
- Sources: `ALL_SOURCES`, `RECOMMENDED_SOURCES`, `ALL_HTTP_SOURCES`, `ALL_SOCKS4_SOURCES`, `ALL_SOCKS5_SOURCES`, `API_SOURCES`
- Exceptions: `ProxyWhirlError`, `ProxyPoolEmptyError`, `ProxyValidationError`, `ProxyConnectionError`, `ProxyAuthenticationError`, `ProxyFetchError`, `ProxyStorageError`, `RetryableError`, `NonRetryableError`, `RegexTimeoutError`, `RegexComplexityError`, `CacheCorruptionError`, `CacheStorageError`, `CacheValidationError`, `RequestQueueFullError`
- Utils: `configure_logging`, `encrypt_credentials`, `decrypt_credentials`, `generate_encryption_key`, `deduplicate_proxies`, `is_valid_proxy_url`, `parse_proxy_url`, `validate_proxy_model`, `proxy_to_dict`, `create_proxy_from_url`

## Testing

`pytest` with `asyncio_mode=auto`. Markers: `slow`, `integration`, `unit`, `benchmark`, `snapshot`, `property`, `flaky`, `network`, `stress`. Fixtures in `tests/conftest.py`.

Use the same tiers as CI:

| Scope | Command | Notes |
| ----- | ------- | ----- |
| Focused regression | `uv run pytest tests/unit/test_<module>.py -q --no-cov -n0` | Keeps local probes free of coverage/xdist noise. |
| CI parity | `task quality-gates` | Runs lint, type check, non-slow unit/integration tests, and coverage. |
| Expanded non-slow | `uv run pytest tests/ -q -m "not slow" --ignore=tests/benchmarks --timeout=120` | Covers API, contract, property, unit, and integration surfaces without real-network slow/browser tests or benchmarks. |
| Full raw suite | `uv run pytest tests/ -q` | Intentional stress run only; includes slow real-browser/network tests and benchmarks that are not the CI parity gate. |

When manually testing CLI fixes, use `uv run proxywhirl --no-lock --help` plus a temporary config path and cover `pool add/list/remove`, `config set/get`, `import-proxies`, `validate-proxy`, strict `sources --validate`, and credential redaction. When API/runtime behavior changes, start `uv run uvicorn proxywhirl.api:app --host 127.0.0.1 --port <port>` with a temporary `PROXYWHIRL_STORAGE_PATH` and verify `/api/health` plus `/api/ready`.

## Code Style

- **Naming:** `PascalCase` (classes), `snake_case` (functions), `UPPER_SNAKE_CASE` (constants), `_prefix` (private)
- **Ruff:** 100 char lines, double quotes, 4-space indent. Rules: E, F, I, N, W, UP, B, C4, SIM
- **Types:** Always type-hint public functions. Use `from __future__ import annotations`. Pydantic with `ConfigDict(frozen=True, extra="forbid")`

## Git

**Branches:** `main` (protected), `develop`, `feature/*`, `fix/*`, `claude/*`

**Commits:** `<type>(<scope>): <description>` — types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`

**Pre-commit:** ruff lint/format, commitizen, private key detection, large file check

**CI Workflows** (`.github/workflows/`): `ci.yml` (main), `security.yml`, `generate-proxies.yml` (6h cron), `validate-sources.yml`, `update-readme-stats.yml`, `release.yml`, `cd.yml`

For remote assurance, monitor at least `CI`, `Security Scan`, and manually dispatched `Validate Proxy Sources` on the pushed SHA. Treat GitHub log markers as actionable if they include `##[warning]`, `##[error]`, `::warning::`, `::error::`, Python warning classes, tracebacks, or Codecov upload token errors. Literal environment assignments such as `PYTHONWARNINGS="ignore::UserWarning"` are not emitted warnings.

Codecov upload in `ci.yml` is optional and gated by `CODECOV_TOKEN_PRESENT`; coverage threshold enforcement and coverage artifact upload must continue even when Codecov is skipped.

## Documentation

The active docs framework is Fumadocs on Next.js in `web/`.

- Source pages live in `web/content/docs/**/*.mdx`.
- Generated reference pages live in `web/content/docs/generated/` and are regenerated by `web/scripts/generate-docs.mjs`.
- Proxy-list web assets are copied from `docs/proxy-lists/` into `web/public/proxy-lists/` by `pnpm --dir web run docs:generate`.
- After docs, README, AGENTS, public API surface, file-structure, agent, or skill-definition changes, invoke the docs-steward workflow and run the relevant docs checks.
- Use `shieldcn` badges in `README.md`; keep the top badge row to 3–6 clickable SVG badges and do not leave placeholder owner/repo/package values.

Docs validation sequence:

```bash
pnpm --dir web run docs:generate
pnpm --dir web run lint
pnpm --dir web run test:run
pnpm --dir web run build
```

Run `pnpm --dir web run test:e2e` only when browser dependencies are installed and the change affects rendered docs behavior.

## Boundaries

**Always:**

- Run `task lint` before commit
- Run `task quality-gates` before production-readiness commits when Python behavior changed
- Add tests for new features (test-first)
- Use type hints on public functions
- Use `loguru` for logging (never `print`)
- Prefix all Python commands with `uv run`
- Validate inputs at module boundaries
- Keep docs generated from source: edit generator scripts or source docs, then run `pnpm --dir web run docs:generate`

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

| Variable                                      | Component  | Purpose                                       |
| --------------------------------------------- | ---------- | --------------------------------------------- |
| `PROXYWHIRL_KEY`                              | CLI/config | Master encryption key                         |
| `PROXYWHIRL_CACHE_ENCRYPTION_KEY`             | cache      | Fernet key for L2 cache                       |
| `PROXYWHIRL_STORAGE_PATH`                     | api        | SQLite database path                          |
| `PROXYWHIRL_API_KEY`                          | api        | API authentication key                        |
| `PROXYWHIRL_MCP_API_KEY`                      | mcp        | MCP server auth key                           |
| `PROXYWHIRL_MCP_ALLOW_UNAUTHENTICATED_WRITES` | mcp        | Local-dev/test override for MCP write actions |
| `PROXYWHIRL_MCP_DB`                           | mcp        | MCP database path                             |

See subsystem AGENTS.md files for complete environment variable lists.

## Security

| Category        | Forbidden                                                       | Allowed                                       |
| --------------- | --------------------------------------------------------------- | --------------------------------------------- |
| **Files**       | `*.env*`, `*.pem`, `*.key`, `*secret*`, `*credential*`, `*.bak` | `proxywhirl/`, `tests/`, `docs/`, `examples/` |
| **Commands**    | `rm -rf`, `curl \| sh`, `eval`, `chmod 777`, `sudo *`           | `uv run *`, `task *`, `git *`                 |
| **Network**     | Raw sockets, production APIs, external URLs not in codebase     | httpx client, localhost, mocked fixtures      |
| **Secrets**     | Hardcoded creds, logging passwords, base64-encoded keys         | `os.environ.get()`, `cryptography` lib        |
| **Regex**       | User-provided patterns without validation                       | `safe_regex.py` utilities only (ReDoS)        |
| **Destructive** | Bulk deletes, schema drops, force pushes                        | Single-file ops, migrations, regular commits  |

### Human Intervention Required

- Modifying `__init__.py` exports
- Database schema migrations
- CI/CD workflow changes
- New external dependencies
- Any operation on `main` branch

## Gotchas

| Issue                 | Fix                                                     |
| --------------------- | ------------------------------------------------------- |
| `ModuleNotFoundError` | `uv sync`                                               |
| Async test errors     | `asyncio_mode = "auto"` in pyproject.toml               |
| Type errors           | Use `uv run ty check` not `mypy`                        |
| Import errors         | Use `uv run pytest` not bare `pytest`                   |
| Raw full suite hangs  | Use CI parity gates; slow browser/benchmark tests are intentional stress surfaces |
| HTTP mock not working | Use `respx` not `responses`; check `respx_mock` fixture |
| Pydantic validation   | Use `ConfigDict(extra="forbid")` to catch typos         |
| Credential exposure   | Use `SecretStr`, check `redact_url()` in exceptions.py  |
| MCP tests skip        | MCP requires Python 3.10+; tests auto-skip on older     |

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
Docs command: pnpm --dir web run docs:generate && pnpm --dir web run build
```

## Decision Tree

| Scenario      | Action                                                                   |
| ------------- | ------------------------------------------------------------------------ |
| Sync vs Async | `ProxyWhirl` for scripts/CLI; `AsyncProxyWhirl` for web/high-concurrency |
| Tests fail    | 1) `uv run pytest path::test -v` 2) Check `conftest.py` 3) `uv sync`     |
| Lint fails    | 1) `task format` auto-fix 2) Manual fix remaining 3) Check ruff codes    |
| Type errors   | `uv run ty check` (not mypy) — check `ty.rules` in pyproject.toml        |
| Docs drift    | 1) `pnpm --dir web run docs:generate` 2) Inspect generated diff 3) `pnpm --dir web run build` |
| Source drift  | `uv run proxywhirl sources --validate --fail-on-unhealthy --timeout 5 --concurrency 5` |
| New strategy  | Implement `RotationStrategy` protocol, register in `StrategyRegistry`    |
| New exception | Inherit from `ProxyWhirlError`, add error code to `ProxyErrorCode`       |
| HTTP mocking  | Use `respx` (not `responses`), fixtures in `conftest.py`                 |
