# R-001: Production Deployment Checklist for FastAPI API-Key Middleware

## Findings

- `proxywhirl/api/middleware/auth.py` implements a standard header-based API-key middleware
  (`X-API-Key`) with a public-path allowlist and `secrets.compare_digest` timing-safe comparison —
  aligned with OWASP API Security Top 10 (API2:2023 Broken Authentication) guidance for lightweight
  service-to-service auth.
- Current defaults (`PROXYWHIRL_REQUIRE_AUTH=false`) are appropriate for local dev but must be flipped
  explicitly per-deployment; there is no runtime signal (log warning) today telling an operator that
  auth is off.

## Recommended production checklist (added to deployment docs, F-001)

1. Set `PROXYWHIRL_REQUIRE_AUTH=true` and `PROXYWHIRL_API_KEY=$(openssl rand -base64 32)`.
2. Terminate TLS in front of the API (Nginx/Caddy/ALB) — the API itself does not do TLS.
3. Restrict `PROXYWHIRL_CORS_ORIGINS` to known origins; never combine `*` with credentials
   (already enforced at import time in `proxywhirl/api/core.py`).
4. Put `/api/metrics` behind network policy or a separate internal listener for Prometheus scraping
   instead of relying on the public-path allowlist in production.
5. Monitor the new "auth disabled" startup warning (F-002) in log aggregation/alerting.
6. Rotate `PROXYWHIRL_API_KEY` on a schedule; store it in a secrets manager, not in compose/env files
   committed to git.

## Sources

- OWASP API Security Top 10 2023 — API2 Broken Authentication.
- Existing repo precedent: `docs/source/deployment.md` `## Security` section already documents step 1-3;
  this task extends it with a "Production Hardening" subsection and startup-warning guidance.
