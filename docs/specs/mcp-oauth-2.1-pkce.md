# ADR-007: MCP OAuth 2.1 + PKCE for Remote Transports

**Status:** Proposed (design only — no implementation in this change)
**Date:** 2026-07-17
**Deciders:** ProxyWhirl maintainers
**Related:** [MCP Authorization (2025-11-25)](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization), Wave 4 SOTA upgrade plan

## Context

ProxyWhirl ships an MCP server (`proxywhirl-mcp` / `proxywhirl.mcp.server`) used by AI assistants. Today:

- **stdio** is treated as a local-dev transport; credentials may come from the environment.
- **HTTP / SSE (and Streamable HTTP)** can run networked. Networked capability without strong auth is unsafe for public or multi-tenant exposure.
- Near-term hardening uses bearer / API key (`PROXYWHIRL_MCP_API_KEY`) for HTTP/SSE.
- The MCP specification’s authorization section for HTTP-based transports is based on **OAuth 2.1** with **PKCE**, Protected Resource Metadata (RFC 9728), and Authorization Server Metadata (RFC 8414).

We need a recorded decision for how ProxyWhirl will adopt OAuth 2.1+PKCE for **public remote** MCP without blocking the current API-key path for internal deployments.

## Decision (proposed)

1. **Transport split remains authoritative**
   - **stdio:** Do **not** implement OAuth; use env/config secrets (MCP spec guidance for STDIO).
   - **HTTP / SSE / Streamable HTTP:** Require authentication. Prefer API key for private/internal deployments; require OAuth 2.1+PKCE when the server is exposed as a **public remote** MCP resource.

2. **OAuth posture for public remote MCP**
   - Act as an OAuth 2.1 **resource server** accepting audience-bound bearer access tokens.
   - Advertise authorization servers via **OAuth 2.0 Protected Resource Metadata** (RFC 9728), including `authorization_servers`.
   - Challenge unauthenticated requests with `401` + `WWW-Authenticate` carrying `resource_metadata` (and optional `scope`).
   - Rely on an external or colocated **authorization server** that implements OAuth 2.1 with PKCE (`S256`). ProxyWhirl does not need to be the IdP in v1.
   - Clients MUST use authorization code + PKCE; implicit and password grants are forbidden.
   - Tokens MUST be bound to this MCP resource (RFC 8707 resource indicators where applicable); reject tokens with wrong audience.

3. **Discovery & registration (v1 scope)**
   - MUST: Protected Resource Metadata + AS metadata (RFC 8414 and/or OIDC Discovery with `code_challenge_methods_supported`).
   - SHOULD: Support Client ID Metadata Documents when clients present them.
   - MAY: Dynamic Client Registration (RFC 7591) — defer unless a concrete client ecosystem requires it.

4. **Coexistence with API keys**
   - Keep `PROXYWHIRL_MCP_API_KEY` as the supported auth for internal/single-tenant HTTP MCP until OAuth lands.
   - After OAuth ships: API keys remain allowed for loopback/private networks; public remote deployments document OAuth as required.
   - Do not silently accept anonymous `list` / `rotate` (or other capability tools) on networked transports.

5. **Out of scope for this ADR**
   - Implementing token validation, AS integration, DCR, or UI consent flows.
   - Changing stdio local-dev ergonomics beyond documenting the exception.
   - Replacing REST API auth (`PROXYWHIRL_API_KEY`) — separate surface.

## Consequences

### Positive

- Aligns public remote MCP with 2025–2026 MCP authorization guidance.
- Clear stdio vs HTTP split reduces accidental exposure.
- API-key path stays available for private ops without waiting on IdP work.

### Negative / risks

- OAuth adds operational dependency on an authorization server and client discovery.
- Dual auth modes (API key vs OAuth) increase docs and test matrix until a deprecation policy is chosen.
- Incorrect audience/resource binding is a common footgun — needs explicit tests when implemented.

## Alternatives considered

| Option | Why not (for public remote) |
| ------ | --------------------------- |
| API key only forever | Insufficient for public multi-client agent ecosystems; MCP AS discovery expects OAuth |
| mTLS only | Strong but poor fit for typical MCP assistant clients; complementary, not replacement |
| Implement full AS inside ProxyWhirl | Out of scope; prefer external AS + resource-server role |
| OAuth on stdio | Spec discourages; env credentials are correct for local pipes |

## Implementation sketch (future epic — not started)

1. Document public-remote requirement in MCP ops docs; keep ADR status **Proposed** until kickoff.
2. Add settings: e.g. `PROXYWHIRL_MCP_AUTH_MODE=api_key|oauth|api_key_or_oauth`, resource identifier, trusted AS metadata URLs / JWKS.
3. Serve `/.well-known/oauth-protected-resource` (and path-scoped variant if MCP endpoint is nested).
4. Validate bearer JWTs (or introspection) with audience = MCP resource URI; map scopes to tool classes (read vs write).
5. Contract tests: 401 + PRM challenge; PKCE S256 happy path against a test AS; reject missing/wrong audience; stdio unchanged.
6. Publish as Accepted when the epic lands; update [web ADR index](../../web/content/docs/project/adr/index.mdx) and MCP interface docs.

## References

- https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization
- OAuth 2.1 draft (draft-ietf-oauth-v2-1)
- RFC 9728 Protected Resource Metadata
- RFC 8414 Authorization Server Metadata
- RFC 7636 PKCE / OAuth 2.1 PKCE requirements (`S256`)
- RFC 8707 Resource Indicators
- Current code: `proxywhirl/mcp/server.py`, env `PROXYWHIRL_MCP_API_KEY`
