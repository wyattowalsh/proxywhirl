## MODIFIED Requirements

### Requirement: Task Runner

Developer workflow examples SHALL use the tracked `Taskfile.yml` and `task <name>` commands, with direct `uv run ...` equivalents where useful.

#### Scenario: Developer task commands

- **WHEN** a developer lists project tasks
- **THEN** `Taskfile.yml` defines `test`, `test-unit`, `test-integration`, `test-fast`, `test-parallel`, `lint`, `format`, `type-check`, `quality-gates`, `coverage`, `validate-sources`, `validate-sources-ci`, `sources-list`, `docs-html`, `docs-linkcheck`, and `docs-clean`
- **AND** Python commands inside tasks use `uv run`

### Requirement: Source Validation

Strict source validation SHALL treat `ALL_*` collections as the enabled built-in source set. Disabled sources SHALL NOT appear in those collections and SHALL include an inline rationale.

#### Scenario: Strict source validation

- **WHEN** CI validates sources
- **THEN** it runs `uv run proxywhirl sources --validate --fail-on-unhealthy --timeout 5 --concurrency 5`
- **AND** any unhealthy enabled source fails the job

#### Scenario: Upstream flakiness

- **WHEN** an upstream source is unhealthy or flaky
- **THEN** the source is fixed, disabled with rationale, or removed
- **AND** CI is not softened to pass despite unhealthy enabled sources

### Requirement: Coverage Enforcement

Focused pytest commands SHALL NOT inherit coverage collection or pytest-xdist parallelism from global pytest addopts. Coverage thresholds SHALL be enforced only by explicit coverage tasks and CI coverage jobs.

#### Scenario: Focused pytest

- **WHEN** a developer runs a focused pytest command
- **THEN** global pytest addopts do not add `--cov` arguments
- **AND** global pytest addopts do not add `-n auto`

#### Scenario: Explicit coverage

- **WHEN** a developer runs `task coverage` or CI runs a coverage job
- **THEN** coverage threshold enforcement is explicit in that command
- **AND** slow and stress-oriented suites are not part of the coverage threshold gate
