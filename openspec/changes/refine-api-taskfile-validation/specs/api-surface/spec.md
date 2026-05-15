## ADDED Requirements

### Requirement: Rotate Endpoint

The API SHALL expose `GET /api/rotate` as a read endpoint that selects the next proxy from the configured rotation strategy without making an outbound target request.

#### Scenario: Select next proxy

- **WHEN** a client calls `GET /api/rotate` and a proxy is available
- **THEN** the response uses the existing `APIResponse` success envelope
- **AND** the `data` payload uses the public `ProxyResource` representation
- **AND** the proxy URL in the payload does not include credentials

#### Scenario: No proxy available

- **WHEN** a client calls `GET /api/rotate` and no proxy is available
- **THEN** the endpoint returns HTTP 503

### Requirement: API Metrics Endpoint

The API SHALL expose Prometheus metrics at `GET /api/metrics`.

#### Scenario: Fetch Prometheus metrics

- **WHEN** a client calls `GET /api/metrics`
- **THEN** the response is Prometheus text format
- **AND** the root `/metrics` route is not exposed

## MODIFIED Requirements

### Requirement: Metrics Routes

First-class metrics endpoints SHALL be exposed only under `/api/metrics/*`.

#### Scenario: Canonical metrics routes

- **WHEN** the OpenAPI schema is generated
- **THEN** retry summary is available at `/api/metrics/retries`
- **AND** retry time series is available at `/api/metrics/retries/timeseries`
- **AND** retry by proxy is available at `/api/metrics/retries/by-proxy`
- **AND** circuit breaker metrics are available at `/api/metrics/circuit-breakers`

#### Scenario: Removed stale routes

- **WHEN** the OpenAPI schema is generated
- **THEN** no path starts with `/api/v1`
- **AND** no path starts with `/api/v2`
- **AND** no path starts with `/metrics`

### Requirement: Proxied Request Response

Proxied request responses SHALL never expose proxy credentials.

#### Scenario: Sanitized proxy_used

- **WHEN** a proxied request succeeds through a credentialed proxy
- **THEN** the `data.proxy_used` value does not include userinfo credentials
