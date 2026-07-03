## ADDED Requirements

### Requirement: Audit Remediation Evidence

Audit remediation evidence SHALL be stored in a valid OpenSpec change when it is placed under `openspec/changes/`.

#### Scenario: Evidence change is listed

- **WHEN** maintainers run `openspec list --json`
- **THEN** the audit remediation change appears with a task count greater than zero
- **AND** the change is not reported as `no-tasks`

#### Scenario: Evidence change validates

- **WHEN** maintainers run `openspec validate audit-remediation --strict`
- **THEN** the change validates successfully
- **AND** its task log and artifacts remain linked from the change directory

#### Scenario: Bandit evidence is recorded

- **WHEN** Bandit findings are suppressed as false positives
- **THEN** each suppression includes a rule code
- **AND** each suppression has an adjacent concise rationale
- **AND** the evidence log matches the current suppressed call sites
