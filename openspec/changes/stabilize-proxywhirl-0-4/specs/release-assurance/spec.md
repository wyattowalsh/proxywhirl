## ADDED Requirements

### Requirement: Evidence is bound to an exact baseline
Every assurance result SHALL record the commit SHA, dirty-path count and scope,
command, exit code, relevant counts, and artifact or run identifier; evidence
from a different tree or SHA MUST be treated as historical only.

#### Scenario: Prior green result is considered
- **WHEN** a green result was produced before the current 310-record/327-path dirty baseline was integrated
- **THEN** it is retained as historical context but cannot satisfy a `0.4` release gate

### Requirement: The release candidate passes the complete local matrix
`0.4.0rc1` MUST pass OpenSpec validation, compatibility tests, lint, format,
types, focused security and behavior tests, full quality gates, packaging and
isolated-install smoke, migration tests, docs generation/build, and applicable
deployment/workflow validation on the candidate tree.

#### Scenario: Any candidate gate fails
- **WHEN** a required local command exits nonzero or emits an actionable unwaived warning/error marker
- **THEN** candidate promotion stops and the failure is assigned to the owning leaf before the failed gate and dependent gates are rerun

### Requirement: The known remote security blocker is cleared
The program MUST resolve or explicitly, time-boundedly waive the findings from
Security Scan run `31285534474`, Safety job `93173499813`, step
`Run Safety check`, before release promotion.

#### Scenario: Candidate dependency scan completes
- **WHEN** the exact `0.4.0rc1` SHA runs the Security Scan
- **THEN** cryptography, joserfc, pydantic-settings, pyjwt, and soupsieve no longer produce the 11 known findings and all program-blocking security jobs are green

### Requirement: Remote assurance runs on the exact candidate SHA
CI, Security Scan, and Validate Proxy Sources MUST complete successfully on the
exact candidate SHA, and required jobs MUST NOT be inferred from Vercel-only or
different-SHA status.

#### Scenario: Live main has only Vercel status
- **WHEN** `cba6e74875fba8181d70c33c843c4a55232a732a` or a successor has no GitHub Actions runs
- **THEN** remote assurance remains unproven until the required workflows execute on the actual candidate SHA

### Requirement: Stable promotion repeats drift-prone gates
`0.4.0` promotion SHALL occur only after the release candidate acceptance
period and SHALL rerun dependency security, source health, build/install,
generated-output drift, and exact-SHA remote gates against the final release
tree.

#### Scenario: Release tree changes after rc1
- **WHEN** any source, dependency, manifest, workflow, release, or generated file changes after the accepted `0.4.0rc1`
- **THEN** every affected gate and all final drift-prone gates rerun before `0.4.0` promotion

### Requirement: Assurance logs preserve actionable markers
Remote and local assurance review SHALL inspect `##[warning]`, `##[error]`,
`::warning::`, `::error::`, Python warning classes, tracebacks, and upload
errors, and SHALL record why any surviving marker is non-actionable.

#### Scenario: Workflow concludes green with warning markers
- **WHEN** a required workflow has a successful conclusion but its logs contain an actionable marker
- **THEN** release remains blocked until the marker is fixed or documented with evidence and approval

### Requirement: Change control does not grant release authority
Completing these OpenSpec tasks MUST NOT itself authorize commits, pushes,
workflow dispatch, tags, package publication, GitHub release creation, or
deployment; each externally mutating step requires separate trusted authority.

#### Scenario: Local assurance is complete
- **WHEN** all local tasks are green but no explicit publication authority exists
- **THEN** the program reports the ready state and stops before any external mutation
