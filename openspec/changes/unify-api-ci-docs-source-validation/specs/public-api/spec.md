## MODIFIED Requirements

### Requirement: Canonical REST routes are unversioned

ProxyWhirl SHALL expose first-class REST routes under `/api/*` without `/api/v1`
or `/api/v2` version prefixes.

#### Scenario: Client lists proxies

- **WHEN** a client requests the proxy list
- **THEN** the canonical path is `GET /api/proxies`
- **AND** generated OpenAPI output includes `/api/proxies`
- **AND** generated OpenAPI output does not include `/api/v1/proxies` or
  `/api/v2/proxies` as first-class routes.

#### Scenario: Client checks service health

- **WHEN** a client checks service health
- **THEN** the canonical path is `GET /api/health`
- **AND** generated OpenAPI output includes `/api/health`
- **AND** generated OpenAPI output does not include `/api/v1/health` or
  `/api/v2/health` as first-class routes.

### Requirement: Canonical Python API modules are unversioned

ProxyWhirl SHALL expose API implementation from `proxywhirl.api` modules without
first-class `proxywhirl.api.v1` or `proxywhirl.api.v2` packages.

#### Scenario: Importing API application

- **WHEN** package users import the FastAPI application
- **THEN** they import from `proxywhirl.api`
- **AND** no documentation or tests require `proxywhirl.api.v1` or
  `proxywhirl.api.v2` as the canonical surface.

### Requirement: Tests encode current contracts

ProxyWhirl tests SHALL validate the current public contract rather than
reintroducing legacy aliases or compatibility adapters.

#### Scenario: Strategy selection tests

- **WHEN** tests invoke a rotation strategy
- **THEN** the first positional argument is a `ProxyPool`
- **AND** `SelectionContext` is supplied only as an optional context argument.

#### Scenario: API compatibility tests

- **WHEN** tests assert API behavior
- **THEN** they use unversioned route paths and canonical modules
- **AND** they do not assert redirects, aliases, or compatibility behavior for
  versioned paths unless a future approved change adds such compatibility.
