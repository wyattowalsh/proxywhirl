# Design

## Canonical API Surface

`proxywhirl.api` owns the FastAPI app, auth helpers, models, and route
registration. Route modules expose unversioned paths only:

- `GET /api/health`
- `GET /api/stats`
- `GET /api/proxies`
- `POST /api/proxies`
- `GET /api/rotate`

Any useful validation, auth, and response-shaping behavior from the experimental
`proxywhirl/api/v2` tree is moved into canonical modules. The `v2` package and
`/api/v1` references are removed rather than aliased.

## Contract Alignment

Tests should encode the current contract instead of restoring legacy aliases.
Strategy tests call strategies with `ProxyPool` plus an optional
`SelectionContext`; they do not pass `SelectionContext` as the first positional
argument. API contract tests use unversioned routes and assert that generated
OpenAPI paths match the canonical route set.

## Core Correctness

Fixes are made at the module boundary:

- `ProxyPool` defaults are provided by the model, not by tests compensating for
  missing fields.
- `SQLiteStorage` accepts the construction shape used by current callers and
  tests.
- Auth expiration comparisons are timezone-safe and deterministic.
- CLI helper return types and imports remain compatible with Typer/Click and
  Python 3.9.
- SQLModel nullable comparisons use explicit `is_(None)` or equivalent
  expression APIs instead of Python boolean comparisons.
- Public annotations avoid Python 3.10-only syntax when runtime support includes
  Python 3.9.

## Source Validation

Enabled sources in `proxywhirl/sources.py` remain strict. Source-registry tests
verify source shape, parser metadata, disabled-source rationale, and that the
source validation workflow invokes `--fail-on-unhealthy`.

## CI Consolidation

Retain only authoritative workflows:

- `ci.yml` for lint, format check, type check, focused tests, and broad tests.
- `security.yml` for dependency and code security checks.
- `release.yml` for build and publish/release checks.
- `validate-sources.yml` for strict source health.
- `docs.yml` for Sphinx docs build.
- `generate-proxies.yml` for scheduled proxy data generation.
- Optional scheduled benchmark/flaky workflow if it is valid and non-blocking.

Other duplicate or broken workflows are removed rather than patched indefinitely.

## Documentation Stewardship

Sphinx docs, README examples, generated API references, and agent instructions are
updated to remove stale `v1`/`v2` terminology for first-class public surfaces.
Docs validation includes warnings-as-errors Sphinx builds and targeted checks for
Mermaid, code snippets, tables, tabs/admonitions, and accessibility notes when
those assets are touched.

## Rollback

Rollback is version-control based. No compatibility adapters are introduced as a
temporary rollback layer.
