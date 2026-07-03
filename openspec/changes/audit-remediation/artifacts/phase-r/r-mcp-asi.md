# R-002: OWASP Agentic Security Initiative (ASI) Mapping for MCP Tool Surface

## Scope

`proxywhirl/mcp/server.py` exposes 11 tool actions (5 read, 6 write) to AI assistants via FastMCP.

## ASI control mapping

| ASI concern | Current control | Gap |
| ----------- | ---------------- | --- |
| Excessive agency (unrestricted tool actions) | Write actions gated by `_WRITE_ACTIONS` + `_allow_unauthenticated_writes()` | None — write actions require explicit opt-in or API key |
| Credential leakage to model context | `api_key` kept out of tool JSON schemas; extracted from context metadata/headers only | None |
| Tool output injection / unsafe strings | `_sanitize_error_text()` redacts proxy URLs in error messages before returning to the model | None |
| Silent unauthenticated operation | No startup signal when the server boots with no `PROXYWHIRL_MCP_API_KEY` | **Gap — addressed by F-003** |
| Audit trail | `logger.info` on all major actions (rotator init, auth changes) | Adequate for read actions; no dedicated audit log stream (out of scope for this remediation) |

## Recommendation

Add a startup warning (F-003) when `main()` launches without `--api-key`/`PROXYWHIRL_MCP_API_KEY`, and
document the read-vs-write auth posture explicitly in the MCP docs/AGENTS.md (F-004) so operators
integrating this MCP server into agent fleets understand the fail-open-for-reads / fail-closed-for-writes
model before granting an agent unattended access.
