## MODIFIED Requirements

### Requirement: Workflows are authoritative and non-duplicative

ProxyWhirl SHALL keep a smaller authoritative GitHub Actions set instead of
maintaining duplicate broken workflows.

#### Scenario: Pull request validation runs

- **WHEN** a pull request is opened or updated
- **THEN** the authoritative CI workflow runs lint, format check, type check,
  and tests
- **AND** duplicate workflows for the same lane are absent or disabled.

#### Scenario: Source validation runs

- **WHEN** scheduled or manual source validation runs
- **THEN** the retained source-validation workflow uses the strict source gate
- **AND** no duplicate source-validation workflow conflicts with the canonical
  lane.

### Requirement: Documentation reflects the canonical surface

ProxyWhirl docs SHALL describe unversioned API modules and REST routes as the
first-class public surface.

#### Scenario: API references are generated

- **WHEN** Sphinx API references are built
- **THEN** generated references point to canonical `proxywhirl.api` modules
- **AND** stale first-class `v1` or `v2` docs sections are removed or rewritten.

#### Scenario: README examples are reviewed

- **WHEN** README and guide examples mention REST routes
- **THEN** examples use `/api/proxies`, `/api/health`, `/api/stats`, and other
  unversioned paths
- **AND** examples do not present `/api/v1` or `/api/v2` as canonical routes.
