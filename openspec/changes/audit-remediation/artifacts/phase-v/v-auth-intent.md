# V-002: RV-001 / RV-002 Intent Validation

## RV-001 — `APISettings.require_auth: bool = False` (`proxywhirl/settings.py:83`)

- `tests/unit/test_api_auth.py::test_no_auth_required_by_default` explicitly asserts unauthenticated
  requests succeed by default — this is a **documented, tested product decision**, not an oversight.
- `APIKeyMiddleware` (`proxywhirl/api/middleware/auth.py`) fails closed with `503` when auth is required
  but no key is configured (`test_missing_config_returns_503`), and uses `secrets.compare_digest` for
  timing-safe comparison (`test_timing_attack_resistance`).
- `proxywhirl/api/AGENTS.md` already documents `PROXYWHIRL_REQUIRE_AUTH` / `PROXYWHIRL_API_KEY` as
  environment-configurable, defaulting to `false` for local/dev ergonomics (matches CLI-first, localhost
  dev-tool product positioning).

## RV-002 — MCP reads allowed without API key (`proxywhirl/mcp/auth.py:29-31`)

- `MCPAuth.authenticate()` returns `True` when `self.api_key` is `None` — by design, matching
  `tests/unit/test_mcp_server.py` fixtures that run the MCP server unauthenticated for local tool use.
- Write actions (`_WRITE_ACTIONS` in `proxywhirl/mcp/server.py`) are separately gated by
  `_allow_unauthenticated_writes()` (`PROXYWHIRL_MCP_ALLOW_UNAUTHENTICATED_WRITES`, default `False`),
  so unauthenticated MCP sessions can read but cannot mutate the pool unless explicitly opted in.
- `proxywhirl/mcp/AGENTS.md` already documents this boundary ("Never: Allow unauthenticated write
  actions in production").

## Conclusion

Both defaults are **intentional dev-ergonomics choices** for a CLI-first / local-first tool, already
covered by existing tests and existing boundary documentation. Per the remediation plan, these are
**Track A** findings: harden via documentation + startup warnings + deployment guidance only.
**No default flip** (`require_auth` stays `False`, MCP stays fail-open for reads) — a default flip would
be a breaking change requiring a major version bump and is out of scope for this remediation.

**Status:** `documented` (RV-001, RV-002) — see F-001..F-005 for the doc/warning implementation.
