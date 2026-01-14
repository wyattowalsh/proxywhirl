# MCP Server Subsystem

> Extends: [../../AGENTS.md](../../AGENTS.md)

**Requires:** Python 3.10+, `uv pip install -e ".[mcp]"`

## Modules

| File | Key Classes |
|------|-------------|
| `server.py` | `MCPServer`, `main()` CLI entry point, `ProxyWhirlAuthMiddleware` |
| `auth.py` | API key validation |

## FastMCP v2 Features

| Feature | Implementation |
|---------|----------------|
| **Lifespan** | `_mcp_lifespan` context manager for startup/shutdown |
| **Middleware** | `ProxyWhirlAuthMiddleware` for API key validation |
| **Progress** | `ctx.report_progress()` in fetch/validate operations |
| **Context Logging** | `_async_log()` helper for context-based logging |
| **Resource URIs** | Standard `resource://proxywhirl/` scheme |

## CLI Usage

```bash
# Run MCP server (after pip install)
proxywhirl-mcp

# With uvx (no install)
uvx "proxywhirl[mcp]" proxywhirl-mcp

# With options
proxywhirl-mcp --transport http --api-key $KEY --db /path/to.db --log-level debug
```

## Environment Variables

- `PROXYWHIRL_MCP_API_KEY` - API key for authentication
- `PROXYWHIRL_MCP_DB` - Path to proxy database
- `PROXYWHIRL_MCP_LOG_LEVEL` - Log level (debug/info/warning/error)

## Actions (11 total)

| Action | Description |
|--------|-------------|
| `list` | List all proxies |
| `rotate` | Get next proxy |
| `status` | Get proxy status |
| `recommend` | Get best proxy for criteria |
| `health` | Pool health overview |
| `reset_cb` | Reset circuit breaker |
| `add` | Add proxy to pool |
| `remove` | Remove proxy from pool |
| `fetch` | Fetch from public sources |
| `validate` | Test proxy connectivity |
| `set_strategy` | Change rotation strategy |

## Resources

| URI | Description |
|-----|-------------|
| `resource://proxywhirl/health` | Real-time pool health |
| `resource://proxywhirl/config` | Server configuration |

## Boundaries

**Always:**
- Validate API keys when auth is enabled (via middleware)
- Return structured JSON responses for all actions
- Handle errors gracefully with informative messages
- Log all action invocations for audit
- Sanitize proxy data before returning (strip credentials)
- Use context for logging when available (`_async_log`)

**Ask First:**
- Adding new MCP actions
- Authentication mechanism changes
- Response schema modifications
- Environment variable changes

**Never:**
- Expose proxy credentials/passwords in responses
- Bypass authentication checks
- Return raw internal errors to clients
- Allow unauthenticated access to write actions (`add`, `remove`, `reset_cb`)

## Tests

Skip on Python < 3.10: `@pytest.mark.skipif(sys.version_info < (3, 10), reason="MCP requires 3.10+")`

Coverage target: ≥90% (currently at 90.23%)
