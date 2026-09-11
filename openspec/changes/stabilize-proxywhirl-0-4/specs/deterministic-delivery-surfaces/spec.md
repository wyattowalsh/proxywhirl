## ADDED Requirements

### Requirement: Configuration has one source of truth
Python runtime settings, CLI defaults, REST settings, MCP settings, Docker,
Compose, Helm, and documentation SHALL derive shared defaults from one declared
configuration contract and MUST NOT encode contradictory production behavior.

#### Scenario: Configuration surfaces are compared
- **WHEN** equivalent settings are inspected across code, CLI help, environment examples, Compose, Helm, and docs
- **THEN** names, types, defaults, required secrets, and precedence rules agree

### Requirement: Package metadata and lock state are reproducible
`pyproject.toml`, `uv.lock`, entry points, optional extras, Python support, and
build metadata MUST resolve and build deterministically from a clean checkout;
the lockfile MUST have one writer and MUST NOT be hand-edited.

#### Scenario: Locked candidate is rebuilt
- **WHEN** dependencies are synchronized with `--locked` and distributions are built twice from the same candidate SHA
- **THEN** dependency resolution, included package set, entry points, and normalized artifact contents are equivalent

### Requirement: Deployment examples are internally complete and single-replica safe
Dockerfiles, Compose files, Kubernetes resources, and Helm templates SHALL use
the same application entry point, health/readiness semantics, storage path,
authentication requirements, and secret references; this program MUST NOT
claim multi-replica safety.

#### Scenario: Single-replica manifests are rendered
- **WHEN** Docker, Compose, and Helm/Kubernetes configurations are rendered for one replica
- **THEN** each starts the same authenticated application contract with valid probes, writable storage, and no embedded live secret

### Requirement: Workflows invoke canonical project gates
CI, security, source-validation, docs, and release workflows MUST call the
canonical `uv`, `just`, and `pnpm` commands with locked dependencies and MUST
retain coverage, artifacts, and actionable warning/error evidence.

#### Scenario: Workflow definitions are audited
- **WHEN** retained workflow definitions are parsed and compared with repository commands
- **THEN** every required gate maps to a live command and no duplicate workflow silently weakens or contradicts it

### Requirement: Generated documentation is script-owned and deterministic
OpenAPI pages, Python/CLI/strategy references, `llms.txt`, navigation metadata,
and generated JSON MUST be regenerated only by their declared scripts after
source contracts stabilize and MUST be clean on an immediate second generation.

#### Scenario: Documentation is generated twice
- **WHEN** the complete docs-generation sequence runs twice without source changes
- **THEN** the second run produces no tracked diff and all generated paths and links are stable

### Requirement: Generated public proxy assets preserve source/mirror parity
Proxy-list assets under `docs/proxy-lists/` and `web/public/proxy-lists/` SHALL
remain a generated source/mirror pair, with freshness and source-health claims
derived from the generation workflow rather than hand edits.

#### Scenario: Proxy assets are regenerated
- **WHEN** an authorized generation run updates canonical proxy-list assets
- **THEN** the public mirror matches the canonical files and reported counts and timestamps are internally consistent

### Requirement: Local and secret-adjacent artifacts are excluded
Build output, caches, reports, Terraform provider trees, local databases,
environment files, keys, credentials, and secret-bearing files MUST NOT enter a
release artifact or commit through broad staging or generation.

#### Scenario: Candidate file inventory is reviewed
- **WHEN** the distribution, container context, and Git change set are enumerated
- **THEN** local caches and secret-adjacent artifacts are absent and any excluded user-owned file remains untouched
