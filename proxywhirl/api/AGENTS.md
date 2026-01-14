# API Subsystem

> Extends: [../../AGENTS.md](../../AGENTS.md)

## Modules

| File | Key Classes/Functions |
|------|----------------------|
| `core.py` | `app`, `lifespan`, `get_rotator`, `get_storage`, `get_config` |
| `models.py` | Request/response Pydantic models |
| `routes/` | Endpoint route handlers |

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/proxies` | List all proxies |
| POST | `/api/v1/proxies` | Add proxy |
| GET | `/api/v1/rotate` | Get next proxy |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/stats` | Pool statistics |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PROXYWHIRL_STORAGE_PATH` | `proxywhirl.db` | SQLite database path |
| `PROXYWHIRL_STRATEGY` | `round-robin` | Rotation strategy |
| `PROXYWHIRL_TIMEOUT` | `30` | Request timeout (seconds) |
| `PROXYWHIRL_MAX_RETRIES` | `3` | Max retry attempts |
| `PROXYWHIRL_REQUIRE_AUTH` | `false` | Require API key auth |
| `PROXYWHIRL_CORS_ORIGINS` | `*` | CORS allowed origins |

## Boundaries

**Always:**
- Validate all request bodies with Pydantic
- Return consistent JSON response format
- Use proper HTTP status codes
- Log all requests for debugging

**Ask First:**
- New endpoints
- Response schema changes
- Authentication changes

**Never:**
- Expose internal errors to clients
- Return proxy credentials in responses
- Allow unauthenticated write operations
