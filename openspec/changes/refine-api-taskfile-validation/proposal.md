# Refine API Surface, Task Runner, and Validation Gates

> **Superseded (Task Runner scope only):** The `Taskfile.yml`/`task <target>` workflow introduced below has been replaced by `justfile`/`just <recipe>` in [`migrate-taskfile-to-justfile`](../migrate-taskfile-to-justfile/proposal.md). The API surface, source validation, and coverage-enforcement scope of this proposal remain in effect.

## Summary

Standardize ProxyWhirl's public REST surface on unversioned `/api/*` paths, migrate local workflow examples to `go-task`, and make source validation and coverage gates explicit rather than implicit global pytest behavior.

## Motivation

The current tree still has first-class root metrics routes, Makefile-centric workflow text even though `Makefile` is ignored locally, and global pytest coverage options that make focused remediation commands slower and harder to interpret. This refinement keeps the public contract and validation workflow consistent with the approved repo direction.

## Scope

- Add `GET /api/rotate` using the existing API response envelope and sanitized proxy resource representation.
- Move first-class metrics endpoints under `/api/metrics/*`; remove root `/metrics/*` routes.
- Add a tracked `Taskfile.yml` with `uv run`-backed tasks for test, lint, typing, source validation, coverage, and docs.
- Update docs, AGENTS instructions, and source-validation workflow issue guidance from `make ...` to `task ...` plus direct `uv run ...` equivalents.
- Keep strict live source validation with `--timeout 5 --concurrency 5 --fail-on-unhealthy`.
- Preserve explicit empty model credentials while keeping malformed URL credentials rejected.
- Remove global pytest coverage addopts so coverage thresholds run only in explicit coverage tasks/jobs.

## Non-Goals

- No compatibility shims for removed root metrics paths.
- No generated documentation output checked into the repository.
- No broad source quarantine; unhealthy enabled sources are fixed, disabled with rationale, or removed from strict collections.
