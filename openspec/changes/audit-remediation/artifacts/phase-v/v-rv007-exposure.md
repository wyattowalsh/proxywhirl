# V-005: RV-007 — `/api/stats` and `/api/metrics` Public Path Exposure

## Trace

- `proxywhirl/api/middleware/auth.py` defines `PUBLIC_PATHS` (health/docs/metrics-style endpoints) that
  skip the `X-API-Key` check even when `PROXYWHIRL_REQUIRE_AUTH=true`.
- When auth is fully disabled (default, RV-001), **all** `/api/*` endpoints — including
  `/api/stats` and `/api/metrics` — are reachable without a key, since `APIKeyMiddleware` only enforces
  checks when `require_auth=true`.

## What leaks

- `/api/stats`: aggregate pool statistics (proxy counts by health state, rotation counts). No credentials,
  no raw proxy URLs with embedded auth (redacted via `redact_url()` / `public_proxy_url()` helpers).
- `/api/metrics`: Prometheus exposition format — request counters/latencies by endpoint, cache hit rates,
  circuit breaker state counts. No secrets; operationally sensitive (could inform an attacker about scale
  and load patterns) but not a credential-exposure vector.

## Risk classification

P2 / confidence 0.75 — informational disclosure of operational metrics, not a credential or PII leak.
Consistent with RV-001/RV-002: acceptable in local/dev deployments, should be gated behind auth or network
policy in production.

## Remediation (Track A)

- No code change required to redact stats/metrics payloads (they already exclude secrets).
- Document that `/api/stats` and `/api/metrics` are public whenever `PROXYWHIRL_REQUIRE_AUTH=false`, and
  recommend either enabling auth or restricting `/api/metrics` via a reverse-proxy allowlist for scraping
  infra (Prometheus) in production (see F-001 deployment docs).
- Add a contract test (`F-014`) documenting current behavior: stats/metrics remain reachable without a key
  even when `PROXYWHIRL_REQUIRE_AUTH=true`, while non-public routes reject unauthenticated requests.

**Status:** `documented` — see F-001, F-014.
