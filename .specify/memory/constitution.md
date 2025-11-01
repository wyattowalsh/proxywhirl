# Proxywhirl Delivery Constitution

## Core Principles

### I. Library-First Architecture
- All new functionality ships as importable Python modules inside the existing `proxywhirl` package unless the plan explicitly approves a new project.
- Modules MUST remain self-contained, composable, and typed (`py.typed` marker required).
- Features MAY expose CLIs or APIs, but the library layer is the canonical contract.

### II. Test-First Development (Non-Negotiable)
- Red-Green-Refactor workflow is mandatory for every change.
- Tests MUST be authored or updated before implementation and must fail prior to code changes.
- Unit, integration, property, and benchmark suites are required when referenced by the spec or success criteria.

### III. Type Safety & Runtime Validation
- Production code MUST pass `mypy --strict`.
- Runtime configuration MUST be validated using pydantic (or approved equivalent).
- Public interfaces require precise type hints; no `Any` escapes except documented third-party integrations.

### IV. Independent User Stories
- Every user story must deliver value in isolation with clear acceptance criteria and tests.
- Plans and tasks MUST ensure stories can be implemented in parallel without hidden cross-story dependencies.
- Shared prerequisites belong in Setup/Foundational phases only.

### V. Performance & Observability Standards
- Success criteria for latency, throughput, and error budgets MUST be measured and enforced via automated tests or benchmarks.
- Structured logging and metrics collection are mandatory for production features.
- Performance regressions above documented thresholds are release blockers.

### VI. Security & Privacy by Default
- Sensitive data MUST be redacted in logs and persisted data.
- Secrets handling requires `SecretStr` (or equivalent) and audited storage.
- Error handling MUST avoid leaking credentials or internals.

### VII. Simplicity & Flat Architecture
- Favor flat module structures over deep package trees.
- New abstractions require justification in the plan’s complexity section.
- Default to built-in or existing dependencies; new third-party libraries require explicit approval in the plan.

## Delivery Workflow Requirements
- Specs define ALL functional and non-functional requirements; gaps must block implementation.
- Plans MUST describe architecture, data models, and technology decisions with no unresolved “TBD” items before tasks are generated.
- Tasks MUST trace directly to user stories or prerequisites. Each task includes file paths and checklist format.
- `uv run` is the required prefix for Python tooling commands.

## Quality Gates
- Code review MUST verify compliance with this constitution before merge.
- Any violation of a MUST statement is a release blocker.
- Benchmarks and long-running tests may gate release but can run asynchronously if recorded before deployment.

## Governance
- This constitution supersedes prior workflow documents.
- Amendments require explicit documentation, reviewer approval, and migration notes stored under `.specify/memory/`.
- Project leads are responsible for auditing adherence during planning and implementation phases.

**Version**: 1.0.0 | **Ratified**: 2025-10-01 | **Last Amended**: 2025-11-01
