# Dependency floor review (Wave 4)

**Status:** Extras and core floors applied in `pyproject.toml` (metadata synced in `uv.lock`). Resolved package versions unchanged.

## Applied (optional extras aligned to core)

| Extra | Previous | Applied |
| ----- | -------- | ------- |
| `storage` / `all` sqlmodel | `>=0.0.14` | `>=0.0.27` |
| `security` / `all` cryptography | `>=41.0.0` | `>=44.0.1` |
| `js` / `all` playwright | `>=1.40.0` | `>=1.55.0` |
| `mcp` / `all` fastmcp | `>=0.1.0` | `>=2.0.0` |

Lockfile change was **specifier metadata only** (resolved package versions unchanged). Python floor remains `>=3.10`.

## Applied core floors (final assurance)

| Package | Previous floor | Applied floor | Locked ≈ |
| ------- | -------------- | ------------- | -------- |
| httpx | `>=0.25.0` | `>=0.28.0` | 0.28.1 |
| pydantic | `>=2.0.0` | `>=2.10.0` | 2.13.x |
| pydantic-settings | `>=2.0.0` | `>=2.5.0` | 2.14.x |
| tenacity | `>=8.2.0` | `>=9.0.0` | 9.1.x |
| fastapi | `>=0.100.0` | `>=0.115.0` | 0.136.x |
| uvicorn | `>=0.24.0` | `>=0.30.0` | 0.46.x |
| typer | `>=0.9.0` | `>=0.12.0` | 0.25.x |
| rich | `>=13.0.0` | `>=14.0.0` | 15.x |
| prometheus-client | `>=0.19.0` | `>=0.21.0` | 0.25.x |
| portalocker | `>=2.8.0` | `>=3.0.0` | 3.2.x |
| platformdirs | `>=3.0.0` | `>=4.0.0` | 4.9.x |

## Not proposed (need separate review)

- Raising floors to **latest PyPI** majors that would force resolve upgrades (e.g. fastapi 0.139, cryptography 49, playwright 1.61, pandas 3).
- Dropping Python 3.10.
- Pinning exact `==` versions in library `pyproject` (prefer floors).
