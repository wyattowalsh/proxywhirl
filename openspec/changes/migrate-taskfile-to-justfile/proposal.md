# Migrate Task Runner from go-task to just

## Summary

Replace the tracked `Taskfile.yml` (go-task) and root `Makefile` with a single tracked `justfile` (Casey Rodarmor's `just`), and update every developer-facing workflow example from `task <name>` to `just <name>`.

## Motivation

The repo previously carried two parallel task runners — a root `Makefile` and a tracked `Taskfile.yml` (added by `refine-api-taskfile-validation`) — which duplicated recipes and confused contributors about which entry point was authoritative. `just` consolidates both into one dependency-light, cross-platform command runner already adopted across the tree (CI docs, MDX guides, Sphinx guides, `AGENTS.md`). This change formalizes that migration as the single source of truth and retires the superseded `Taskfile.yml`/`Makefile` workflow spec.

## Scope

- Remove root `Makefile` and `Taskfile.yml`; keep the tracked `justfile` as the sole local task runner (Sphinx's `docs/Makefile` is unrelated and out of scope).
- Update `AGENTS.md`, `CONTRIBUTING.md`, `README.md`, `docs/AGENTS.md`, `docs/devops-ci-cd-pipeline.md`, Sphinx guides (`docs/source/**`), and Fumadocs MDX guides (`web/content/docs/**`) to reference `just <recipe>` instead of `task <target>` or `make <target>`.
- Add `just --list` to onboarding/setup instructions so contributors can discover recipes.
- Add convenience surface: `alias qg := quality-gates` and a `docs-generate` recipe wrapping `pnpm --dir web run docs:generate`.
- Supersede the `Task Runner` requirement previously introduced by `refine-api-taskfile-validation`.

## Non-Goals

- No change to the underlying commands each recipe runs (lint/type-check/test/coverage/docs semantics are unchanged).
- No changes to CI workflow YAML beyond the `task` → `just` command-string rewrites already required for consistency.
- No re-introduction of `make` as a project-level task runner (the Sphinx-only `docs/Makefile` alias is preserved as legacy Sphinx tooling, not the active project task runner).
