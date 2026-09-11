## ADDED Requirements

### Requirement: The 0.3.3 contract is the compatibility baseline
ProxyWhirl SHALL inventory and preserve the public Python exports and import
paths, CLI command and option surface, REST paths and schemas, MCP tool/resource
contracts, configuration keys/defaults, and supported persisted-data shapes
shipped by version `0.3.3`.

#### Scenario: Existing consumer upgrades to 0.4
- **WHEN** a supported `0.3.3` consumer installs `0.4.0rc1` or `0.4.0`
- **THEN** its documented import, invocation, request, tool, configuration, and data-loading paths continue to work unless an approved security exception is recorded

### Requirement: Compatibility facades have one implementation
Compatibility modules and top-level exports MUST delegate to one canonical
implementation and MUST NOT create parallel state, duplicated registries, or
behavioral divergence between legacy and current import paths.

#### Scenario: Legacy and current imports are compared
- **WHEN** a contract test imports the same public symbol through a `0.3.3` path and its canonical `0.4` path
- **THEN** both paths resolve to behaviorally equivalent objects backed by the same implementation and registries

### Requirement: Deprecations are explicit and testable
An intentional public-contract evolution that is not an approved immediate
security break SHALL retain a compatibility path through the `0.4.x` line and
emit a targeted deprecation signal with replacement and migration guidance.

#### Scenario: Deprecated interface is used
- **WHEN** a consumer uses a public interface scheduled for later removal
- **THEN** the interface still functions in `0.4.x` and emits a documented deprecation warning that names the supported replacement

### Requirement: Installed distributions match source-tree behavior
The wheel and source distribution MUST contain all runtime packages, migration
resources, entry points, and typed/public metadata needed to reproduce the
validated source-tree contract in an isolated installation.

#### Scenario: Candidate wheel is installed in isolation
- **WHEN** the built `0.4.0rc1` wheel is installed outside the repository checkout
- **THEN** import smoke tests, CLI help, migration discovery, and representative public-contract tests pass without relying on untracked source files

### Requirement: Persisted 0.3.3 data remains readable
Every supported storage backend SHALL read supported `0.3.3` data and SHALL
either preserve it unchanged or migrate it through a deterministic, tested,
data-preserving path.

#### Scenario: Existing database is upgraded
- **WHEN** an application opens a representative `0.3.3` database with `0.4.0rc1`
- **THEN** the migration reaches the single declared Alembic head without losing proxy records, health state, or non-secret configuration data

### Requirement: Breaking exceptions require a recorded gate
An immediate compatibility break MUST be limited to a demonstrated P0 defect or
security exposure and MUST include impact evidence, migration instructions,
release-note prominence, and an explicit approval record before implementation.

#### Scenario: Security fix conflicts with compatibility
- **WHEN** preserving a `0.3.3` behavior would retain a demonstrated security vulnerability
- **THEN** implementation stops until the exception record identifies the affected contract, threat, replacement path, tests, and approval
