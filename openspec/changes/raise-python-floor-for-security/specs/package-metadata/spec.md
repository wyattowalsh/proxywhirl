## MODIFIED Requirements

### Requirement: Supported Python Runtime Floor

ProxyWhirl SHALL publish and validate support for Python 3.10 and newer.

#### Scenario: Package metadata advertises supported runtimes

- **WHEN** package metadata is built
- **THEN** `requires-python` is `>=3.10`
- **AND** classifiers include Python 3.10, 3.11, 3.12, and 3.13
- **AND** classifiers do not include Python 3.9

#### Scenario: Package metadata avoids deprecated license fields

- **WHEN** package metadata is built
- **THEN** `license` is published as the SPDX expression `MIT`
- **AND** `license-files` includes `LICENSE`
- **AND** classifiers do not include deprecated license classifier entries

#### Scenario: Dependency security export

- **WHEN** maintainers export production dependencies from `uv.lock`
- **THEN** the export does not include Python 3.9-only vulnerable dependency
  branches
- **AND** authenticated or unauthenticated dependency scanners report no known
  vulnerabilities for the supported runtime set
