# Proposal

## Problem

ProxyWhirl currently has competing API concepts, stale versioned documentation,
duplicative GitHub Actions, and validation behavior that is not consistently
anchored to one canonical public surface. This makes tests and generated
references drift between `/api/v1`, experimental `api/v2`, and current module
expectations while CI spends effort maintaining broken duplicate lanes.

## Intent

Unify the project around one current public surface: unversioned Python API
modules and unversioned REST routes under `/api/*`. Keep source health strict,
make CI authoritative rather than exhaustive, and update docs/tests to validate
the same contract.

## Scope

- Promote useful untracked `proxywhirl/api/v2` behavior into canonical
  `proxywhirl.api` modules without retaining first-class `v1` or `v2` package
  names.
- Replace versioned REST paths with unversioned routes such as `/api/proxies`,
  `/api/health`, and `/api/stats`.
- Update API, contract, CLI-example, strategy, storage, source-registry, and docs
  tests to target the canonical surface.
- Fix core correctness issues discovered while aligning tests, including
  `ProxyPool` defaults, `SQLiteStorage` construction, auth key expiration, CLI
  typing/imports, SQLModel nullable comparisons, and Python 3.9-compatible
  annotations.
- Consolidate GitHub Actions into a smaller authoritative workflow set: PR CI,
  security scan, release, source validation, docs build, proxy generation, and
  optional scheduled benchmark/flaky reporting.
- Keep enabled sources strict-gated with
  `uv run proxywhirl sources --validate --fail-on-unhealthy`.
- Remove tracked generated/test artifacts that are demonstrably local outputs,
  and update `.gitignore` only for concrete generated paths observed in the repo.

## Out Of Scope

- Compatibility aliases, redirects, or dual-path adapters for `/api/v1` or
  `/api/v2` unless a deployed consumer is later identified.
- Weakening source validation because external feeds are volatile.
- Adding new third-party dependencies.
- Creating branches or committing changes.

## Affected Users And Tools

- Python users importing `proxywhirl.api`.
- REST clients targeting the FastAPI application.
- Maintainers relying on GitHub Actions status checks.
- Docs consumers reading Sphinx-generated API references and README examples.
- Source curation workflows that validate enabled proxy feeds.

## Risks

- Removing versioned routes can break undeclared consumers; this is intentional
  for the current unshipped cleanup unless evidence of deployed usage appears.
- Strict source validation may fail in future if an upstream feed breaks; failures
  should disable or repair the specific source with rationale, not bypass the
  gate.
- CI consolidation can hide coverage if authoritative lanes omit important
  checks, so retained workflows must directly cover lint, format, type, tests,
  docs, sources, security, packaging, and release semantics.
