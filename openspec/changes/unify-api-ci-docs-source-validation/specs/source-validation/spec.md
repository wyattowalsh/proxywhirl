## MODIFIED Requirements

### Requirement: Enabled sources are strict-gated

Every enabled source in `proxywhirl/sources.py` SHALL pass strict source
validation in the canonical source-validation gate.

#### Scenario: Running source validation in CI

- **WHEN** the source validation workflow runs
- **THEN** it invokes `uv run proxywhirl sources --validate --fail-on-unhealthy`
- **AND** the workflow fails when any enabled source is unhealthy.

#### Scenario: Source registry tests run

- **WHEN** source registry tests run
- **THEN** they verify enabled source shape and parseability metadata
- **AND** they verify disabled sources include rationale.

### Requirement: Source failures remain actionable

ProxyWhirl SHALL respond to repeated enabled-source failures by repairing,
removing, or disabling the specific source with rationale instead of weakening
the strict gate.

#### Scenario: External feed becomes unhealthy

- **WHEN** an enabled external feed repeatedly fails validation
- **THEN** maintainers update that source entry or disable it with documented
  rationale
- **AND** the `--fail-on-unhealthy` gate remains enabled.
