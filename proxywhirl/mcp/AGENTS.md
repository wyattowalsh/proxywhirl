# MCP Server Subsystem

> Extends: [../../AGENTS.md](../../AGENTS.md)

**Requires:** Python 3.10+, `uv pip install -e ".[mcp]"`

## Modules

| File | Key Classes |
|------|-------------|
| `server.py` | `MCPServer`, `main()`, `ProxyWhirlAuthMiddleware` |
| `auth.py` | API key validation |

## CLI

```bash
proxywhirl-mcp                                    # Default
proxywhirl-mcp --transport http --api-key $KEY   # With auth
uvx "proxywhirl[mcp]" proxywhirl-mcp             # No install
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `PROXYWHIRL_MCP_API_KEY` | Authentication key |
| `PROXYWHIRL_MCP_DB` | Database path (default: `proxywhirl.db`) |
| `PROXYWHIRL_MCP_LOG_LEVEL` | Log level (debug/info/warning/error) |

## Actions (11)

**Read:** `list`, `rotate`, `status`, `recommend`, `health`
**Write:** `add`, `remove`, `reset_cb`, `fetch`, `validate`, `set_strategy`

## Resources

`resource://proxywhirl/health`, `resource://proxywhirl/config`

## Boundaries

**Always:**
- Validate API keys when auth enabled
- Sanitize proxy data (strip credentials)
- Log all action invocations

**Never:**
- Expose credentials in responses
- Bypass auth checks
- Allow unauthenticated write actions

## Tests

Skip on Python < 3.10: `@pytest.mark.skipif(sys.version_info < (3, 10), ...)`
