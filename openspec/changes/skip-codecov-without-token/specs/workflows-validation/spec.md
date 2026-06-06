## MODIFIED Requirements

### Requirement: Coverage Enforcement

Coverage threshold enforcement SHALL remain independent from optional third-party coverage upload services.

#### Scenario: Codecov token absent

- **WHEN** CI runs the Python 3.11 coverage job without a configured Codecov token
- **THEN** CI still enforces the local coverage threshold
- **AND** CI still uploads the local coverage artifact
- **AND** the Codecov upload step is skipped without warning or error log lines

#### Scenario: Codecov token present

- **WHEN** CI runs the Python 3.11 coverage job with a configured Codecov token
- **THEN** CI may upload the coverage report to Codecov using that token
