# API Subsystem

> Extends: [../../AGENTS.md](../../AGENTS.md)

## Modules

`core.py` (`app`, `lifespan`, `get_rotator`), `models.py` (Pydantic), `routes/`

## Endpoints

`GET /api/proxies` (list), `POST /api/proxies` (add), `GET /api/rotate`, `GET /api/health`, `GET /api/stats`

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `PROXYWHIRL_STORAGE_PATH` | `proxywhirl.db` | Database |
| `PROXYWHIRL_STRATEGY` | `round-robin` | Strategy |
| `PROXYWHIRL_TIMEOUT` | `30` | Timeout (s) |
| `PROXYWHIRL_MAX_RETRIES` | `3` | Max retries |
| `PROXYWHIRL_REQUIRE_AUTH` | `false` | Auth required |
| `PROXYWHIRL_API_KEY` | — | Auth key |
| `PROXYWHIRL_CORS_ORIGINS` | localhost | CORS origins (comma-sep) |
| `PROXYWHIRL_RATE_LIMIT` | `100/minute` | Default rate limit |

## Boundaries

**Always:** Pydantic validation, consistent JSON, proper HTTP codes

**Never:** Expose internal errors, return credentials, unauthenticated writes
