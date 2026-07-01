# Tasks

- [x] Create OpenSpec change superseding `refine-api-taskfile-validation`'s Task Runner requirement.
- [x] Add tracked `justfile` with `test`, `test-unit`, `test-integration`, `test-fast`, `test-parallel`, `test-slow`, `test-watch`, `test-rerun`, `test-benchmark`, `test-property`, `test-snapshot`, `test-snapshot-update`, `test-html`, `test-memory`, `coverage`, `test-coverage`, `lint`, `format`, `format-check`, `type-check`, `quality-gates`, `clean`, `commit`, `bump`, `bump-dry`, `bump-minor`, `bump-major`, `changelog`, `fetch`, `export`, `sources-list`, `validate-sources`, `validate-sources-ci`, `curate-sources`, `docs-generate`, `docs-html`, `docs-linkcheck`, and `docs-clean` recipes.
- [x] Remove root `Makefile` and `Taskfile.yml`.
- [x] Update `AGENTS.md` setup instructions to include `just --list`.
- [x] Update `CONTRIBUTING.md` prerequisites to include `just` installation.
- [x] Add a Developer commands block to `README.md`.
- [x] Fix phantom `make build` reference in `docs/devops-ci-cd-pipeline.md` (replaced with `uv build`, since `ci.yml` remains the source of truth for the real build job).
- [x] Update `docs/AGENTS.md`, Sphinx guides, and Fumadocs MDX guides from `task <target>` to `just <recipe>`.
- [x] Add `alias qg := quality-gates` and a `docs-generate` recipe to the `justfile`.
- [x] Add superseded note to `refine-api-taskfile-validation/proposal.md`.
- [x] Run focused validation (`openspec validate migrate-taskfile-to-justfile --strict`) and record results.
