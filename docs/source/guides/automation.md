---
title: Automation & CI Runbook
---

# Automation & CI Runbook

ProxyWhirl ships without hosted CI, so local automation must mimic the pipeline we expect to add later. Use this guide to standardize verification, documentation publishing, and search integration.

## Pre-flight checks

```bash
uv sync --all-groups
make format
make lint
uv run mypy proxywhirl/
make test-cov
make docs
uv run sphinx-build -b linkcheck docs/source docs/build/linkcheck
```

- `make docs` fails on warnings (`nitpicky = True`), surfacing broken references immediately.
- Link checking guarantees external resources stay reachable; add to `linkcheck_ignore` only when a domain blocks bots.

## Smoke tests for docs examples

Run bundled validators whenever you update CLI examples or environment configuration:

```bash
uv run python validate_quickstart.py
```

Document new verification scripts in the docs and reference them from pull requests for traceability.

## DocSearch credentials

Algolia DocSearch is opt-in. Export credentials before building to enable the hosted search UI:

```bash
export DOCSEARCH_APP_ID="..."
export DOCSEARCH_API_KEY="..."
export DOCSEARCH_INDEX_NAME="proxywhirl"
```

Without these variables, Sphinx builds cleanly but omits DocSearch assets to avoid failing local contributors.

## Automating releases

1. Bump the library version in ``pyproject.toml`` and tag the release.
2. Regenerate exports with ``uv run proxywhirl export --output-dir export/release-$(date -u +%Y%m%d)``.
3. Update ``CHANGELOG.md`` with strategy, API, or storage changes.
4. Publish artifacts (PyPI, container, documentation host).
5. Deploy ``docs/build/html`` to your hosting target (GitHub Pages, S3, etc.).

## Suggested CI stages

| Stage | Commands | Purpose |
| --- | --- | --- |
| `lint` | `make format --check` / `make lint` | Style and static analysis |
| `typecheck` | `uv run mypy proxywhirl/` | Strict typing with Pydantic + SQLModel |
| `tests` | `make test-cov` | Enforce coverage gates and perf benchmarks |
| `docs` | `make docs && uv run sphinx-build -b linkcheck ...` | Doc health and link integrity |
| `publish` | `uv run proxywhirl export` (conditional) | Produce release artifacts |

Cache the ``uv`` environment per job to keep runtimes low, and pin to Python 3.11+ to match integration test expectations.
