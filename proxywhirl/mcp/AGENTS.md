# MCP Server Subsystem

> Extends: [../../AGENTS.md](../../AGENTS.md)

**Requires:** Python 3.10+, `uv pip install -e ".[mcp]"`

## Modules

| File        | Key Classes                                       |
| ----------- | ------------------------------------------------- |
| `server.py` | `MCPServer`, `main()`, `ProxyWhirlAuthMiddleware` |
| `auth.py`   | API key validation                                |

## CLI

```bash
proxywhirl-mcp                                    # Default
proxywhirl-mcp --transport http --api-key $KEY   # With auth
uvx "proxywhirl[mcp]" proxywhirl-mcp             # No install
```

## Environment Variables

| Variable                                      | Purpose                                                   |
| --------------------------------------------- | --------------------------------------------------------- |
| `PROXYWHIRL_MCP_API_KEY`                      | Authentication key                                        |
| `PROXYWHIRL_MCP_ALLOW_UNAUTHENTICATED_WRITES` | Local-dev/test override for unauthenticated write actions |
| `PROXYWHIRL_MCP_DB`                           | Database path (default: `proxywhirl.db`)                  |
| `PROXYWHIRL_MCP_LOG_LEVEL`                    | Log level (debug/info/warning/error)                      |

`PROXYWHIRL_MCP_API_KEY` is unset by default (dev ergonomics). `main()` logs a `WARNING` at startup
whenever no key is configured, since read actions are then fully unauthenticated. Never rely on this
default outside local development.

## Actions (11)

**Read:** `list`, `rotate`, `status`, `recommend`, `health`
**Write:** `add`, `remove`, `reset_cb`, `fetch`, `validate`, `set_strategy`

## Resources

`resource://proxywhirl/health`, `resource://proxywhirl/config`

## Boundaries

**Always:**

- Validate API keys when auth enabled
- Read API keys from MCP metadata/headers; keep them out of tool schemas
- Sanitize proxy data (strip credentials)
- Sanitize model-visible exception strings before returning them
- Log all action invocations
- Keep unauthenticated write override local-only and explicit

**Never:**

- Expose credentials in responses
- Bypass auth checks
- Allow unauthenticated write actions in production

## Tests

Skip on Python < 3.10: `@pytest.mark.skipif(sys.version_info < (3, 10), ...)`
