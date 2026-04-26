---
title: Automation & CI/CD Runbook
---

# Automation & CI/CD Runbook

This guide covers everything you need to automate ProxyWhirl: local pre-flight checks, GitHub Actions CI pipelines, Docker deployment, cron-based proxy fetching, and integration testing patterns.

```{contents}
:local:
:depth: 2
```

---

## Pre-flight Checks

Run these commands before every commit or pull request to ensure your changes pass all quality gates:

```bash
# 1. Install / sync dependencies
uv sync --all-groups

# 2. Format and lint
uv run ruff format proxywhirl/ tests/
uv run ruff check proxywhirl/ tests/

# 3. Type-check (use ty, not mypy)
uv run ty check proxywhirl/

# 4. Run tests with coverage
uv run pytest tests/ -q --cov=proxywhirl --cov-report=term-missing

# 5. Build documentation (fails on warnings with nitpicky=True)
cd docs && uv run sphinx-build -W --keep-going -b html source build/html && cd ..

# 6. Check external links
cd docs && uv run sphinx-build -b linkcheck source build/linkcheck && cd ..
```

```{tip}
The ``Makefile`` wraps all of these into a single command: ``make quality-gates`` runs lint, type-check, tests, and coverage in sequence. Use ``make format`` for auto-fixing style issues before you lint.
```

### Makefile Targets Quick Reference

```{list-table}
:header-rows: 1
:widths: 30 70

* - Target
  - Description
* - ``make test``
  - Run all tests with pretty output
* - ``make test-unit``
  - Run unit tests only
* - ``make test-integration``
  - Run integration tests only
* - ``make test-parallel``
  - Run tests in parallel with ``pytest-xdist``
* - ``make test-fast``
  - Run tests excluding ``@pytest.mark.slow``
* - ``make lint``
  - Run Ruff linter
* - ``make format``
  - Auto-format with Ruff
* - ``make type-check``
  - Run ``ty`` type checker
* - ``make quality-gates``
  - Run lint + type-check + test + coverage
* - ``make docs-html``
  - Build HTML documentation
* - ``make docs-linkcheck``
  - Check documentation links
```

---

## GitHub Actions CI Pipeline

ProxyWhirl's CI is defined in ``.github/workflows/ci.yml``. It runs on every push to ``main``, ``develop``, and ``feature/**`` / ``fix/**`` branches, as well as on pull requests.

### Pipeline Architecture

```
                 ┌──────────────────┐
                 │    lint          │  ruff check + ruff format --check
                 └────────┬─────────┘
                          │
    ┌─────────────────────┼─────────────────────┐
    │                     │                     │
    v                     v                     v
┌──────────┐    ┌──────────────────┐    ┌──────────────────┐
│ typecheck │    │    commitlint    │    │   test (matrix)  │
│ (ty)     │    │ (PRs only)       │    │ 3.9-3.13         │
└────┬─────┘    └──────────────────┘    └────────┬─────────┘
     │                                           │
     └────────────────┬──────────────────────────┘
                      v
               ┌──────────────┐
               │    build     │  python -m build
               └──────┬───────┘
                      v
               ┌──────────────┐
               │    docs      │  sphinx-build + linkcheck
               └──────────────┘
```

### Full CI Workflow

Below is a production-ready workflow you can adapt for your own fork or downstream project:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop, "feature/**", "fix/**"]
  pull_request:
    branches: [main, develop]
  workflow_dispatch:

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
      - run: uv venv && uv pip install -e ".[dev]"
      - run: uv run ruff check .
      - run: uv run ruff format --check .

  typecheck:
    name: Type Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
      - run: uv venv && uv pip install -e ".[dev]"
      - run: uv run ty check proxywhirl

  test:
    name: Test - Python ${{ matrix.python-version }}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
      - run: uv venv && uv pip install -e ".[dev]"
      - run: |
          uv run pytest -m "not slow" \
            --cov=proxywhirl \
            --cov-report=xml \
            --cov-report=term-missing
      - uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.11'
        with:
          file: ./coverage.xml
          fail_ci_if_error: false
          token: ${{ secrets.CODECOV_TOKEN }}

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: [lint, typecheck, test]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
      - run: uv venv && uv pip install build
      - run: uv run python -m build
      - uses: actions/upload-artifact@v4
        with:
          name: python-package-distributions
          path: dist/

  docs:
    name: Documentation
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
      - run: uv venv && uv pip install -e ".[docs]"
      - run: cd docs && uv run sphinx-build -W --keep-going -b html source build/html
      - run: cd docs && uv run sphinx-build -b linkcheck source build/linkcheck
```

```{note}
The ``astral-sh/setup-uv@v5`` action installs ``uv`` for fast, reproducible dependency management. Pin to ``version: "latest"`` or a specific version for stability.
```

---

## Cron-Based Proxy Fetching

ProxyWhirl's proxy lists are refreshed automatically every 2 hours via ``.github/workflows/generate-proxies.yml``. The workflow:

1. Re-validates existing proxies in the database
2. Fetches new proxies from 60+ sources
3. Cleans up dead (failed validation) proxies
4. Compacts the SQLite database (VACUUM)
5. Exports proxy lists for the web dashboard
6. Commits and pushes changes

### Proxy Generation Workflow

```yaml
# .github/workflows/generate-proxies.yml
name: Generate Proxy Lists

on:
  schedule:
    - cron: '0 */2 * * *'  # Every 2 hours
  workflow_dispatch:

concurrency:
  group: proxy-generation
  cancel-in-progress: true

jobs:
  generate:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - uses: astral-sh/setup-uv@v5
        with:
          version: "latest"

      - run: uv venv && uv pip install -e .

      # Install Playwright for JS-rendered sources
      - run: uv run python -m playwright install chromium

      # Re-validate existing proxies
      - run: uv run proxywhirl fetch --revalidate --timeout 5 --concurrency 2000 --no-export
        timeout-minutes: 60

      # Fetch new proxies from all sources
      - run: uv run proxywhirl fetch --timeout 5 --concurrency 2000 --no-export
        timeout-minutes: 60

      # Remove dead proxies before export
      - run: uv run proxywhirl cleanup --stale-days 0 --execute

      # Compact the database
      - run: sqlite3 proxywhirl.db "VACUUM;"

      # Export proxy lists
      - run: uv run proxywhirl export

      # Commit and push
      - run: |
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git config user.name "github-actions[bot]"
          git add docs/proxy-lists/ proxywhirl.db
          git diff --staged --quiet || \
            git commit -m "chore: Update proxy lists and database - $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
          git pull --rebase origin main || true
          git push
```

```{warning}
The ``concurrency`` block with ``cancel-in-progress: true`` prevents job stacking if a fetch takes longer than the 2-hour interval. Without this, multiple fetch jobs could run in parallel and corrupt the database.
```

### Running Locally

You can run the same fetch pipeline locally:

```bash
# Fetch, validate, and export (full pipeline)
uv run proxywhirl fetch

# Re-validate existing proxies only
uv run proxywhirl fetch --revalidate --no-export

# Fetch without validation (raw proxies)
uv run proxywhirl fetch --no-validate

# High-concurrency validation
uv run proxywhirl fetch --concurrency 2000

# Export proxy lists for web dashboard
uv run proxywhirl export
```

See {doc}`cli-reference` for the full ``fetch`` and ``export`` command reference.

### Setting Up a Local Cron Job

For self-hosted setups, use a system cron job:

```bash
# Edit crontab
crontab -e

# Add this line to fetch proxies every 2 hours
0 */2 * * * cd /path/to/proxywhirl && uv run proxywhirl fetch --concurrency 1000 >> /var/log/proxywhirl-fetch.log 2>&1
```

```{tip}
On macOS, use ``launchd`` instead of cron for more reliable scheduling. Create a plist in ``~/Library/LaunchAgents/`` with a ``StartInterval`` of 7200.
```

---

## Docker Deployment

ProxyWhirl ships with a multi-stage ``Dockerfile`` and a ``docker-compose.yml`` for the REST API server.

### Building the Image

```bash
# Build the image
docker build -t proxywhirl-api:latest .

# Run the container
docker run -d \
  --name proxywhirl \
  -p 8000:8000 \
  -e PROXYWHIRL_STRATEGY=round-robin \
  -e PROXYWHIRL_TIMEOUT=30 \
  proxywhirl-api:latest
```

### docker-compose.yml

The included ``docker-compose.yml`` runs the API server with persistent storage, health checks, and resource limits:

```yaml
version: '3.8'

services:
  proxywhirl-api:
    build:
      context: .
      dockerfile: Dockerfile
    image: proxywhirl-api:latest
    container_name: proxywhirl-api
    ports:
      - "8000:8000"
    environment:
      - PROXYWHIRL_STRATEGY=round-robin
      - PROXYWHIRL_TIMEOUT=30
      - PROXYWHIRL_MAX_RETRIES=3
      - PROXYWHIRL_REQUIRE_AUTH=false
      # - PROXYWHIRL_API_KEY=your-secret-api-key-here
      - PROXYWHIRL_CORS_ORIGINS=*
      # - PROXYWHIRL_STORAGE_PATH=/data/proxies.db
    volumes:
      - proxywhirl-data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"]
      interval: 30s
      timeout: 10s
      start_period: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M

volumes:
  proxywhirl-data:
    driver: local
```

```bash
# Start the stack
docker compose up -d

# Check health
curl http://localhost:8000/api/v1/health

# View logs
docker compose logs -f proxywhirl-api

# Stop the stack
docker compose down
```

### Production Docker with Reverse Proxy

For production deployments, place ProxyWhirl behind a reverse proxy (Nginx, Caddy, etc.) to handle TLS termination and client IP forwarding. See {doc}`deployment-security` for secure configurations with Nginx, Caddy, HAProxy, and Traefik.

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - proxywhirl-api

  proxywhirl-api:
    image: proxywhirl-api:latest
    environment:
      PROXYWHIRL_STRATEGY: round-robin
      PROXYWHIRL_STORAGE_PATH: /data/proxies.db
      PROXYWHIRL_CLIENT_IP_HEADER: "X-Real-IP"
      PROXYWHIRL_TRUSTED_PROXIES: "10.0.0.0/8"
      PROXYWHIRL_REQUIRE_AUTH: "true"
      PROXYWHIRL_API_KEY: "${PROXYWHIRL_API_KEY}"
    volumes:
      - proxywhirl-data:/data
    expose:
      - 8000

volumes:
  proxywhirl-data:
```

```{warning}
Never expose port 8000 directly to the internet without a reverse proxy. The API server does not handle TLS or header sanitization on its own.
```

---

## Integration Testing Patterns

### Testing with Mocked Proxies

ProxyWhirl uses ``respx`` (not ``responses``) for HTTP mocking in tests. Use the ``respx_mock`` fixture provided by ``conftest.py``:

```python
import pytest
import respx
from httpx import Response
from proxywhirl import ProxyWhirl

@respx.mock
def test_rotator_basic_request():
    """Test that the rotator makes a request through a proxy."""
    # Mock the target URL
    respx.get("https://httpbin.org/ip").mock(
        return_value=Response(200, json={"origin": "1.2.3.4"})
    )

    rotator = ProxyWhirl(proxies=["http://proxy1:8080"])
    response = rotator.get("https://httpbin.org/ip")

    assert response.status_code == 200
    assert response.json()["origin"] == "1.2.3.4"
```

### Async Test Patterns

ProxyWhirl's test suite uses ``asyncio_mode = "auto"`` so async tests do not need explicit event loop management:

```python
import pytest
from proxywhirl import AsyncProxyWhirl

@pytest.mark.asyncio
async def test_async_rotator():
    rotator = AsyncProxyWhirl(proxies=["http://proxy1:8080"])
    # ... test async operations
```

### Source Validation in CI

Validate that all proxy sources are reachable as part of your CI pipeline:

```bash
# Validate all sources (informational)
uv run proxywhirl sources --validate

# CI mode: exit with error code if any sources are unhealthy
uv run proxywhirl sources --validate --fail-on-unhealthy
```

Or use the Makefile target:

```bash
make validate-sources-ci
```

---

## Smoke Tests for Docs Examples

Whenever you update CLI examples or environment configuration, run the bundled validators:

```bash
uv run python validate_quickstart.py
```

Document new verification scripts in the docs and reference them from pull requests for traceability.

---

## Automating Releases

1. Bump the version using conventional commits:
   ```bash
   # Dry-run to preview the version bump
   make bump-dry

   # Apply the bump
   make bump
   ```

2. Generate the changelog:
   ```bash
   make changelog
   ```

3. Export proxy data for the release:
   ```bash
   uv run proxywhirl export --output-dir export/release-$(date -u +%Y%m%d)
   ```

4. Build distribution packages:
   ```bash
   uv run python -m build
   ```

5. Publish and deploy:
   - Upload to PyPI (via ``twine`` or CI workflow)
   - Deploy ``docs/build/html`` to your hosting target (GitHub Pages, S3, Vercel)

---

## DocSearch Credentials

Algolia DocSearch is opt-in. Export credentials before building to enable the hosted search UI:

```bash
export DOCSEARCH_APP_ID="..."
export DOCSEARCH_API_KEY="..."
export DOCSEARCH_INDEX_NAME="proxywhirl"
```

Without these variables, Sphinx builds cleanly but omits DocSearch assets to avoid failing local contributors.

---

## CI Stage Summary

```{list-table}
:header-rows: 1
:widths: 15 35 50

* - Stage
  - Commands
  - Purpose
* - ``lint``
  - ``make lint`` / ``uv run ruff check .``
  - Style enforcement and static analysis
* - ``typecheck``
  - ``uv run ty check proxywhirl/``
  - Type safety with Pydantic + SQLModel
* - ``test``
  - ``uv run pytest -m "not slow" --cov``
  - Test suite with coverage gates (Python 3.9--3.13 matrix)
* - ``build``
  - ``uv run python -m build``
  - Verify distribution packages build cleanly
* - ``docs``
  - ``sphinx-build -W -b html`` + ``-b linkcheck``
  - Documentation health and link integrity
* - ``benchmark``
  - ``uv run pytest tests/benchmarks/ --benchmark-only``
  - Performance regression detection (PRs and main only)
```

```{tip}
Cache the ``uv`` virtual environment per job to keep CI runtimes low. Pin to Python 3.11+ for the primary job, but test against the full 3.9--3.13 matrix.
```

---

## See Also

::::{grid} 2
:gutter: 3

:::{grid-item-card} CLI Reference
:link: /guides/cli-reference
:link-type: doc

Full CLI command reference for all ProxyWhirl commands including `fetch`, `export`, `cleanup`, and `sources`.
:::

:::{grid-item-card} Deployment Security
:link: /guides/deployment-security
:link-type: doc

Reverse proxy configuration and production security checklist for Docker and cloud deployments.
:::

:::{grid-item-card} Retry & Failover
:link: /guides/retry-failover
:link-type: doc

Retry policies and circuit breakers for robust automation and fault tolerance.
:::

:::{grid-item-card} Async Client
:link: /guides/async-client
:link-type: doc

Async patterns for high-concurrency proxy rotation in production applications.
:::

:::{grid-item-card} Caching Subsystem
:link: /guides/caching
:link-type: doc

Cache warming for faster startup and persistent proxy storage across restarts.
:::

:::{grid-item-card} MCP Server
:link: /guides/mcp-server
:link-type: doc

AI assistant integration for automated proxy management via MCP protocol.
:::
::::
