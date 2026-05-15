# Tasks

## Change Control

- [x] Create OpenSpec change artifacts before implementation.
- [x] Snapshot branch and dirty worktree state before mutation.
- [x] Validate OpenSpec artifacts.

## API And Contracts

- [x] Promote canonical API modules and remove first-class versioned API package
      naming.
- [x] Convert REST routes and OpenAPI assertions to unversioned `/api/*` paths.
- [x] Update API, contract, integration, and docs references away from `/api/v1`
      and `/api/v2`.

## Core Correctness

- [x] Fix `ProxyPool` defaults and tests that rely on current model behavior.
- [x] Fix `SQLiteStorage` construction and nullable SQLModel comparisons.
- [x] Fix auth key expiration behavior.
- [x] Fix CLI import, command dispatch, and return typing issues.
- [x] Fix strategy tests to use `ProxyPool` plus optional `SelectionContext`.
- [x] Fix Python 3.9-incompatible annotations.

## Sources

- [x] Preserve strict enabled-source validation in the CLI and workflows.
- [x] Add or refresh source-registry tests for enabled shape, parser metadata,
      disabled rationale, and `--fail-on-unhealthy` workflow coverage.

## CI And Docs

- [x] Consolidate workflows into authoritative lanes and remove duplicates.
- [x] Fix retained workflow syntax and action/input drift.
- [x] Update `.gitignore` for observed generated artifacts only.
- [x] Verify no tracked generated/test artifacts require removal.
- [x] Update README, Sphinx pages, generated references, and AGENTS docs for the
      canonical surface.

## Verification

- [x] Run `uv run ruff check .`.
- [x] Run `uv run ruff format --check .`.
- [x] Run `uv run ty check proxywhirl/`.
- [x] Run focused API, strategy, storage, auth, CLI, source-registry, and docs
      generation tests.
- [ ] Run full non-slow pytest with coverage reports.
- [x] Run `uv run proxywhirl sources --validate --fail-on-unhealthy --timeout 5
      --concurrency 5`.
- [x] Run Sphinx HTML build with warnings as errors.
- [x] Run packaging build.
- [x] Run workflow linting for retained GitHub Actions.
