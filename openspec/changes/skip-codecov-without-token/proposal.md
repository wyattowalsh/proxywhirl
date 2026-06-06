# Skip Codecov Upload Without Token

## Summary

Prevent optional Codecov upload attempts from emitting warning or error log lines when the repository has no `CODECOV_TOKEN` secret configured.

## Motivation

The CI run succeeds, but the Codecov step currently runs with an empty token and emits non-gating `warning` and `error` log lines. That violates the production-readiness target of clean CI logs with no actionable warnings or errors.

## Scope

- Keep coverage threshold enforcement unchanged.
- Keep coverage artifact upload unchanged.
- Run the Codecov upload only when a Codecov token is configured.

## Non-Goals

- No coverage threshold changes.
- No Codecov configuration changes.
- No changes to test selection, matrix versions, or workflow triggers.
