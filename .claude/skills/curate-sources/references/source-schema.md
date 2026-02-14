# ProxySourceConfig Schema Reference

## Model Definition

From `proxywhirl/models/core.py`:

```python
class ProxySourceConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    url: HttpUrl                          # Source URL (required)
    format: ProxyFormat = ProxyFormat.JSON # Data format
    render_mode: RenderMode = RenderMode.AUTO
    parser: str | None = None             # Named parser
    custom_parser: Any | None = None      # Custom parser function
    protocol: str | None = None           # Default protocol (http if None)
    wait_selector: str | None = None      # CSS selector for browser rendering
    wait_timeout: int = 30000             # Browser wait timeout (ms)
    refresh_interval: int = 3600          # Refresh interval (seconds)
    enabled: bool = True                  # Whether source is active
    priority: int = 0                     # Fetch priority
    trusted: bool = False                 # Source pre-validates proxies
    headers: dict[str, str] = {}          # Custom HTTP headers
    auth: tuple[str, str] | None = None   # Basic auth credentials
    metadata: dict[str, Any] = {}         # Arbitrary metadata
```

## ProxyFormat Enum

| Value | Description |
|-------|-------------|
| `json` | JSON format (default) |
| `csv` | CSV format |
| `plain_text` | Plain text (IP:PORT per line) |
| `html_table` | HTML table format |

## RenderMode Enum

| Value | Description |
|-------|-------------|
| `auto` | Auto-detect (default) |
| `static` | Static HTTP fetch |
| `browser` | Browser rendering (Playwright) |

## Variable Naming Conventions

### GitHub Sources
Pattern: `GITHUB_{OWNER}_{PROTOCOL}`
- Owner is UPPER_SNAKE_CASE version of GitHub username
- Protocol: `HTTP`, `HTTPS`, `SOCKS4`, `SOCKS5`, `ALL`
- Examples:
  - `GITHUB_MONOSANS_HTTP` (monosans/proxy-list)
  - `GITHUB_THESPEEDX_SOCKS5` (TheSpeedX/PROXY-List)
  - `GITHUB_PROXIFLY_HTTP` (proxifly/free-proxy-list)

### API Sources
Pattern: `{SERVICE}_{PROTOCOL}`
- Examples:
  - `PROXY_SCRAPE_HTTP`
  - `GEONODE_SOCKS4`
  - `PUBPROXY_HTTP`

### Web Sources
Pattern: `{DOMAIN}_{PROTOCOL}`
- Examples:
  - `PROXYSPACE_HTTP`
  - `OPENPROXYLIST_HTTP`
  - `JSDELIVR_PROXIFLY_ALL`

## Collection Lists

| List | Variable | Contents |
|------|----------|----------|
| HTTP sources | `ALL_HTTP_SOURCES` | All HTTP/HTTPS proxy sources |
| SOCKS4 sources | `ALL_SOCKS4_SOURCES` | All SOCKS4 proxy sources |
| SOCKS5 sources | `ALL_SOCKS5_SOURCES` | All SOCKS5 proxy sources |
| All sources | `ALL_SOURCES` | `ALL_HTTP_SOURCES + ALL_SOCKS4_SOURCES + ALL_SOCKS5_SOURCES` |
| Recommended | `RECOMMENDED_SOURCES` | Hand-picked reliable sources (5 currently) |
| API only | `API_SOURCES` | API-based sources only (GeoNode) |

## `_get_source_name()` Patterns

The helper at `proxywhirl/sources.py:1040` extracts readable names:
- GitHub raw URLs → `{owner}/{repo} ({FILENAME})`
- GeoNode API → `GeoNode ({PROTOCOL})`
- ProxyScrape API → `ProxyScrape ({PROTOCOL})`
- ProxySpace → `ProxySpace ({FILENAME})`
- OpenProxyList → `OpenProxyList (HTTP)`
- Fallback → truncated URL

When adding sources with new URL patterns, update `_get_source_name()`.

## Downstream Files to Sync

When sources are added, removed, or disabled, these files must also be updated:

| File | What changes |
|------|-------------|
| `known-sources.md` (this directory) | Add/remove rows, update repo list |
| `tests/unit/test_sources.py` | Add `_get_source_name()` tests for new URL patterns |
| `tests/contract/test_proxy_sources.py` | Update imports if top/recommended sources change |
| `docs/source/reference/python-api.md` | Update collection docs if changed |
| `README.md` | Update feature card source count (`<strong>N Sources</strong>`) |

## `trusted=True` Criteria

A source should be marked `trusted=True` ONLY if it:
- Pre-validates/checks proxies before listing them (not just scraping)
- Updates frequently (at least hourly)
- Has a track record of providing working proxies
- Examples: monosans (5-min checks), proxifly (5-min), GeoNode (lastChecked sort)
