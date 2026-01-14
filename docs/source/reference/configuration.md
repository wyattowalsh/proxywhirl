---
title: Configuration Reference
---

# Configuration Reference

Complete reference for all ProxyWhirl configuration options, environment variables, and TOML file formats.

## Configuration Discovery

ProxyWhirl automatically discovers configuration files in the following priority order:

1. **Explicit path** - Provided via CLI `--config` flag
2. **Project-local** - `./pyproject.toml` with `[tool.proxywhirl]` section
3. **User-global** - `~/.config/proxywhirl/config.toml`
4. **Defaults** - Built-in defaults if no config found

```python
from proxywhirl.config import discover_config, load_config

# Automatic discovery
config_path = discover_config()
config = load_config(config_path)

# Explicit path
from pathlib import Path
config = load_config(Path("./custom-config.toml"))
```

## TOML Configuration Format

:::{important}
ProxyWhirl uses **TOML format**, not YAML. Configuration files must be valid TOML.
:::

### File Locations

**Project-local** (`./pyproject.toml`):
```toml
[tool.proxywhirl]
rotation_strategy = "round-robin"
timeout = 30
# ... other options
```

**User-global** (`~/.config/proxywhirl/config.toml`):
```toml
# Root-level configuration (no [tool.proxywhirl] wrapper)
rotation_strategy = "round-robin"
timeout = 30
# ... other options
```

### Complete Configuration Example

```toml
[tool.proxywhirl]

# ============================================================================
# Proxy Pool Configuration
# ============================================================================

# List of proxies with optional authentication
[[tool.proxywhirl.proxies]]
url = "http://proxy1.example.com:8080"
username = "user1"  # Auto-encrypted when saved
password = "pass1"  # Auto-encrypted when saved

[[tool.proxywhirl.proxies]]
url = "socks5://proxy2.example.com:1080"

[[tool.proxywhirl.proxies]]
url = "http://10.0.1.100:3128"
# No authentication needed

# Path to proxy list file (one proxy per line, optional)
# proxy_file = "/path/to/proxies.txt"

# ============================================================================
# Rotation Settings
# ============================================================================

# Rotation strategy: "round-robin", "random", "weighted", "least-used"
rotation_strategy = "round-robin"

# Health check interval in seconds (0 = disabled)
health_check_interval = 300

# ============================================================================
# Request Settings
# ============================================================================

# Request timeout in seconds
timeout = 30

# Maximum retry attempts per request
max_retries = 3

# Follow HTTP redirects
follow_redirects = true

# Verify SSL certificates
verify_ssl = true

# ============================================================================
# Output Settings
# ============================================================================

# Default output format: "human", "json", "table", "csv"
default_format = "human"

# Enable colored terminal output
color = true

# Verbose logging
verbose = false

# ============================================================================
# Storage Settings
# ============================================================================

# Storage backend: "file", "sqlite", "memory"
storage_backend = "file"

# Path for file/sqlite storage
storage_path = "./proxywhirl.db"

# ============================================================================
# Cache Configuration (Three-Tier System)
# ============================================================================

# Enable caching system
cache_enabled = true

# L1 Cache (In-Memory LRU)
cache_l1_max_entries = 1000

# L2 Cache (JSONL Files)
cache_l2_max_entries = 5000
cache_l2_dir = ".cache/proxies"

# L3 Cache (SQLite)
# cache_l3_max_entries = 100000  # Uncomment to set limit (default: unlimited)
cache_l3_db_path = ".cache/db/proxywhirl.db"

# Cache TTL and cleanup
cache_default_ttl = 3600  # 1 hour (minimum 60 seconds)
cache_cleanup_interval = 60  # Background cleanup every 60 seconds (minimum 10)

# Cache encryption (requires PROXYWHIRL_CACHE_ENCRYPTION_KEY env var)
cache_encryption_key_env = "PROXYWHIRL_CACHE_ENCRYPTION_KEY"

# Auto-invalidate proxies on health check failure
cache_health_invalidation = true
cache_failure_threshold = 3  # Failures before invalidation (minimum 1)

# ============================================================================
# Security Configuration
# ============================================================================

# Encrypt credentials in config file
encrypt_credentials = true

# Environment variable name for encryption key
encryption_key_env = "PROXYWHIRL_KEY"

# ============================================================================
# Data Storage Configuration
# ============================================================================

[tool.proxywhirl.data_storage]

# --- Storage Backend Driver ---
async_driver = true  # Enable async SQLite driver (aiosqlite)

# --- Connection Pooling ---
pool_size = 5  # Max concurrent connections (1-100)
pool_max_overflow = 10  # Max overflow connections beyond pool_size (0-100)
pool_timeout = 30.0  # Timeout in seconds when getting connection (1.0-300.0)
pool_recycle = 3600  # Recycle connections after N seconds (-1 to disable)

# --- Request Timing Analytics ---
persist_latency_percentiles = true  # P50, P95, P99
persist_response_time_stats = true  # min/max/stddev

# --- Error Tracking ---
persist_error_types = true
persist_error_messages = true
max_error_history = 20  # 0-100 entries

# --- Geographic & IP Intelligence (Privacy-Sensitive) ---
persist_geo_data = false  # country/region/city
persist_ip_intelligence = false  # residential/datacenter/vpn flags
persist_coordinates = false  # latitude/longitude

# --- Protocol Details ---
persist_protocol_details = true  # HTTP/TLS versions
persist_capabilities = true  # https/http2/connect support

# --- Health Tracking ---
persist_health_transitions = true
persist_consecutive_streaks = true
max_health_transitions = 50  # 0-500 entries

# --- Source Metadata ---
persist_source_metadata = true
persist_fetch_duration = true

# --- Advanced Storage (Heavy) ---
persist_request_logs = false  # Individual request logs
persist_daily_aggregates = false  # Daily statistics
```

## Environment Variables

### Security & Encryption

#### `PROXYWHIRL_KEY`
- **Purpose**: Master encryption key for proxy credentials
- **Format**: Base64-encoded Fernet key (44 bytes)
- **Default**: Auto-generated and stored in `~/.config/proxywhirl/key.enc`
- **Security**: File mode 600 (owner read/write only)

```bash
# Generate and export key
export PROXYWHIRL_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Or use the persisted key
export PROXYWHIRL_KEY=$(cat ~/.config/proxywhirl/key.enc)
```

#### `PROXYWHIRL_CACHE_ENCRYPTION_KEY`
- **Purpose**: Encryption key for cache tier encryption (optional)
- **Format**: Base64-encoded Fernet key
- **Default**: None (cache encryption disabled if not set)
- **Use case**: Encrypt cached proxy data at rest

```bash
export PROXYWHIRL_CACHE_ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
```

### REST API Configuration

#### `PROXYWHIRL_REQUIRE_AUTH`
- **Purpose**: Enable API key authentication for REST API
- **Values**: `"true"` or `"false"`
- **Default**: `"false"`

#### `PROXYWHIRL_API_KEY`
- **Purpose**: API key for REST endpoint authentication
- **Format**: Any string (recommend strong random key)
- **Required**: Only when `PROXYWHIRL_REQUIRE_AUTH=true`

```bash
export PROXYWHIRL_REQUIRE_AUTH=true
export PROXYWHIRL_API_KEY=$(openssl rand -hex 32)
```

#### `PROXYWHIRL_STORAGE_PATH`
- **Purpose**: Override SQLite database path for REST API
- **Format**: File path string
- **Default**: `./proxywhirl.db`

#### `PROXYWHIRL_STRATEGY`
- **Purpose**: Default rotation strategy for REST API
- **Values**: `"round-robin"`, `"random"`, `"weighted"`, `"least-used"`
- **Default**: `"round-robin"`

#### `PROXYWHIRL_TIMEOUT`
- **Purpose**: Request timeout in seconds
- **Format**: Integer string
- **Default**: `"30"`

#### `PROXYWHIRL_MAX_RETRIES`
- **Purpose**: Maximum retry attempts per request
- **Format**: Integer string
- **Default**: `"3"`

#### `PROXYWHIRL_CORS_ORIGINS`
- **Purpose**: Allowed CORS origins for REST API
- **Format**: Comma-separated URLs
- **Default**: `"http://localhost:8000,http://127.0.0.1:8000"`

```bash
export PROXYWHIRL_CORS_ORIGINS="https://app.example.com,https://www.example.com"
```

## Configuration Classes

### CLIConfig

Main configuration class for CLI and programmatic usage.

#### Proxy Pool

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `proxies` | `list[ProxyConfig]` | `[]` | List of proxy configurations |
| `proxy_file` | `Path \| None` | `None` | Path to proxy list file |

#### Rotation Settings

| Field | Type | Default | Validation | Description |
|-------|------|---------|------------|-------------|
| `rotation_strategy` | `str` | `"round-robin"` | `{"round-robin", "random", "weighted", "least-used"}` | Proxy rotation algorithm |
| `health_check_interval` | `int` | `300` | `>= 0` | Seconds between health checks (0=disabled) |

#### Request Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `timeout` | `int` | `30` | Request timeout in seconds |
| `max_retries` | `int` | `3` | Maximum retry attempts |
| `follow_redirects` | `bool` | `true` | Follow HTTP redirects |
| `verify_ssl` | `bool` | `true` | Verify SSL certificates |

#### Output Settings

| Field | Type | Default | Validation | Description |
|-------|------|---------|------------|-------------|
| `default_format` | `str` | `"human"` | `{"human", "json", "table", "csv"}` | Default output format |
| `color` | `bool` | `true` | - | Enable colored output |
| `verbose` | `bool` | `false` | - | Verbose logging |

#### Storage Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `storage_backend` | `str` | `"file"` | Storage backend type |
| `storage_path` | `Path \| None` | `None` | Storage file path |

#### Cache Settings

| Field | Type | Default | Validation | Description |
|-------|------|---------|------------|-------------|
| `cache_enabled` | `bool` | `true` | - | Enable three-tier caching |
| `cache_l1_max_entries` | `int` | `1000` | - | L1 (memory) max entries |
| `cache_l2_max_entries` | `int` | `5000` | - | L2 (JSONL) max entries |
| `cache_l3_max_entries` | `int \| None` | `None` | - | L3 (SQLite) max entries (None=unlimited) |
| `cache_default_ttl` | `int` | `3600` | `>= 60` | Default cache TTL in seconds |
| `cache_cleanup_interval` | `int` | `60` | `>= 10` | Background cleanup interval (seconds) |
| `cache_l2_dir` | `str` | `".cache/proxies"` | - | L2 cache directory |
| `cache_l3_db_path` | `str` | `".cache/db/proxywhirl.db"` | - | L3 SQLite database path |
| `cache_encryption_key_env` | `str` | `"PROXYWHIRL_CACHE_ENCRYPTION_KEY"` | - | Env var for cache encryption key |
| `cache_health_invalidation` | `bool` | `true` | - | Auto-invalidate on health failure |
| `cache_failure_threshold` | `int` | `3` | `>= 1` | Failures before invalidation |

#### Security Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `encrypt_credentials` | `bool` | `true` | Encrypt credentials in config file |
| `encryption_key_env` | `str` | `"PROXYWHIRL_KEY"` | Environment variable for encryption key |

#### Data Storage Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `data_storage` | `DataStorageConfig` | See below | Configure database persistence |

### DataStorageConfig

Fine-grained control over what data gets persisted to the database.

#### Storage Backend Driver

| Field | Type | Default | Validation | Description |
|-------|------|---------|------------|-------------|
| `async_driver` | `bool` | `true` | - | Enable async SQLite driver (aiosqlite) |

#### Connection Pooling

| Field | Type | Default | Validation | Description |
|-------|------|---------|------------|-------------|
| `pool_size` | `int` | `5` | `1-100` | SQLite connection pool size (max concurrent connections) |
| `pool_max_overflow` | `int` | `10` | `0-100` | Max overflow connections beyond pool_size |
| `pool_timeout` | `float` | `30.0` | `1.0-300.0` | Timeout in seconds when getting connection from pool |
| `pool_recycle` | `int` | `3600` | `>= -1` | Recycle connections after N seconds (-1 to disable) |

#### Request Timing Analytics

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `persist_latency_percentiles` | `bool` | `true` | Store P50, P95, P99 percentiles |
| `persist_response_time_stats` | `bool` | `true` | Store min/max/stddev times |

#### Error Tracking

| Field | Type | Default | Validation | Description |
|-------|------|---------|------------|-------------|
| `persist_error_types` | `bool` | `true` | - | Store error type counts |
| `persist_error_messages` | `bool` | `true` | - | Store last error message |
| `max_error_history` | `int` | `20` | `0-100` | Max error history entries |

#### Geographic & IP Intelligence (Privacy-Sensitive)

:::{warning}
Geographic and IP intelligence data is **disabled by default** for privacy. Only enable if you have proper consent and data protection measures.
:::

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `persist_geo_data` | `bool` | `false` | Store country/region/city (opt-in) |
| `persist_ip_intelligence` | `bool` | `false` | Store residential/datacenter/VPN flags |
| `persist_coordinates` | `bool` | `false` | Store latitude/longitude |

#### Protocol Details

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `persist_protocol_details` | `bool` | `true` | Store HTTP/TLS version info |
| `persist_capabilities` | `bool` | `true` | Store https/http2/connect flags |

#### Health Tracking

| Field | Type | Default | Validation | Description |
|-------|------|---------|------------|-------------|
| `persist_health_transitions` | `bool` | `true` | - | Store health status changes |
| `persist_consecutive_streaks` | `bool` | `true` | - | Store success/failure streaks |
| `max_health_transitions` | `int` | `50` | `0-500` | Max transitions in history |

#### Source Metadata

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `persist_source_metadata` | `bool` | `true` | Store source name, fetch time, validation |
| `persist_fetch_duration` | `bool` | `true` | Store fetch duration |

#### Advanced Storage (Heavy)

:::{warning}
These options can generate significant storage overhead. Only enable for detailed analytics needs.
:::

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `persist_request_logs` | `bool` | `false` | Store individual request logs |
| `persist_daily_aggregates` | `bool` | `false` | Store daily aggregate statistics |

### ProxyConfig

Configuration for individual proxy entries.

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `url` | `str` | Yes | Must start with `http://`, `https://`, `socks4://`, or `socks5://` | Proxy URL |
| `username` | `SecretStr \| None` | No | - | Authentication username (auto-encrypted) |
| `password` | `SecretStr \| None` | No | - | Authentication password (auto-encrypted) |

## Programmatic Configuration

### Loading Configuration

```python
from pathlib import Path
from proxywhirl.config import load_config, discover_config

# Auto-discover
config_path = discover_config()
config = load_config(config_path)

# Explicit path
config = load_config(Path("./config.toml"))

# Use defaults (no config file)
config = load_config(None)
```

### Creating Configuration

```python
from proxywhirl.config import CLIConfig, ProxyConfig, DataStorageConfig
from pydantic import SecretStr

config = CLIConfig(
    proxies=[
        ProxyConfig(
            url="http://proxy1.example.com:8080",
            username=SecretStr("user"),
            password=SecretStr("pass")
        )
    ],
    rotation_strategy="weighted",
    timeout=45,
    cache_enabled=True,
    cache_default_ttl=7200,
    data_storage=DataStorageConfig(
        persist_geo_data=True,  # Opt-in to geo tracking
        persist_request_logs=False,
        max_error_history=50,
        pool_size=10,  # Increase connection pool
        pool_timeout=60.0
    )
)
```

### Saving Configuration

```python
from pathlib import Path
from proxywhirl.config import save_config

# Save to user config
user_config = Path.home() / ".config" / "proxywhirl" / "config.toml"
save_config(config, user_config)

# Save to project (wraps in [tool.proxywhirl])
project_config = Path("./pyproject.toml")
save_config(config, project_config)
```

## Validation Rules

### Rotation Strategy

Must be one of:
- `"round-robin"` - Sequential rotation
- `"random"` - Random selection
- `"weighted"` - Weight-based (by success rate)
- `"least-used"` - Select least recently used

### Output Format

Must be one of:
- `"human"` - Human-readable text
- `"json"` - JSON output
- `"table"` - Formatted table
- `"csv"` - Comma-separated values

### Proxy URL Schemes

Must start with one of:
- `http://` - HTTP proxy
- `https://` - HTTPS proxy
- `socks4://` - SOCKS4 proxy
- `socks5://` - SOCKS5 proxy

### Numeric Constraints

| Field | Minimum | Maximum | Notes |
|-------|---------|---------|-------|
| `cache_default_ttl` | 60 | - | Minimum 1 minute TTL |
| `cache_cleanup_interval` | 10 | - | Minimum 10 seconds |
| `cache_failure_threshold` | 1 | - | At least 1 failure |
| `max_error_history` | 0 | 100 | 0-100 entries |
| `max_health_transitions` | 0 | 500 | 0-500 entries |
| `health_check_interval` | 0 | - | 0 = disabled |
| `pool_size` | 1 | 100 | Connection pool size |
| `pool_max_overflow` | 0 | 100 | Overflow connections |
| `pool_timeout` | 1.0 | 300.0 | Seconds |
| `pool_recycle` | -1 | - | -1 = disabled |

## Security Best Practices

### Credential Encryption

1. **Enable encryption** (default: enabled)
   ```toml
   encrypt_credentials = true
   ```

2. **Set encryption key** (one-time setup)
   ```bash
   # Option 1: Use auto-generated key file (recommended)
   # Key is auto-created at ~/.config/proxywhirl/key.enc

   # Option 2: Set environment variable
   export PROXYWHIRL_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
   ```

3. **Credentials are encrypted when saved**
   - Plaintext credentials in config are encrypted on `save_config()`
   - Encrypted credentials are decrypted on `load_config()`
   - Encryption is transparent to the application

### Config File Permissions

Config files are automatically created with mode `600` (owner read/write only):

```bash
$ ls -la ~/.config/proxywhirl/
-rw------- 1 user user  1234 Dec 27 10:00 config.toml
-rw------- 1 user user    44 Dec 27 10:00 key.enc
```

### API Key Security

For REST API authentication:

```bash
# Generate strong API key
export PROXYWHIRL_API_KEY=$(openssl rand -hex 32)

# Enable authentication
export PROXYWHIRL_REQUIRE_AUTH=true

# Start API server
uvicorn proxywhirl.api:app --host 0.0.0.0 --port 8000
```

Clients must include the API key:

```bash
curl -H "X-API-Key: $PROXYWHIRL_API_KEY" http://localhost:8000/api/v1/rotate
```

## Configuration Examples

### Minimal Configuration

```toml
[tool.proxywhirl]
rotation_strategy = "round-robin"

[[tool.proxywhirl.proxies]]
url = "http://proxy.example.com:8080"
```

### High-Performance Configuration

```toml
[tool.proxywhirl]
rotation_strategy = "weighted"
timeout = 10
max_retries = 5
cache_enabled = true
cache_default_ttl = 7200

[tool.proxywhirl.data_storage]
pool_size = 20
pool_max_overflow = 30
pool_timeout = 60.0
persist_request_logs = false
persist_daily_aggregates = false
```

### Privacy-Focused Configuration

```toml
[tool.proxywhirl]
encrypt_credentials = true
cache_enabled = false

[tool.proxywhirl.data_storage]
persist_geo_data = false
persist_ip_intelligence = false
persist_coordinates = false
persist_error_messages = false
persist_request_logs = false
```

### Analytics-Enabled Configuration

```toml
[tool.proxywhirl]
rotation_strategy = "weighted"
health_check_interval = 300

[tool.proxywhirl.data_storage]
persist_latency_percentiles = true
persist_response_time_stats = true
persist_error_types = true
persist_error_messages = true
persist_health_transitions = true
persist_consecutive_streaks = true
persist_source_metadata = true
persist_daily_aggregates = true
max_error_history = 100
max_health_transitions = 500
```

## Migration from Legacy Config

If you have an older configuration format, migrate to the new structure:

```python
from proxywhirl.config import load_config, save_config
from pathlib import Path

# Load legacy config
old_config = load_config(Path("./old-config.toml"))

# Update to new defaults (example)
old_config.cache_enabled = True
old_config.cache_default_ttl = 3600
old_config.data_storage.persist_geo_data = False
old_config.data_storage.pool_size = 10

# Save in new format
save_config(old_config, Path("./pyproject.toml"))
```

## Troubleshooting

### Config File Not Found

```python
from proxywhirl.config import discover_config

# Check discovery
config_path = discover_config()
if config_path is None:
    print("No config file found, using defaults")
else:
    print(f"Using config: {config_path}")
```

### Invalid TOML Syntax

TOML is strict about syntax. Common mistakes:

```toml
# WRONG: Using = for nested tables
[tool.proxywhirl.data_storage] = {...}

# CORRECT: Use table syntax
[tool.proxywhirl.data_storage]
persist_geo_data = false
```

### Encryption Key Issues

If credentials fail to decrypt:

```bash
# Regenerate encryption key
rm ~/.config/proxywhirl/key.enc

# Next run will auto-generate new key
# WARNING: Old encrypted credentials will be unrecoverable
```

## Related Documentation

- [Getting Started](../getting-started/index.md) - Initial setup and configuration
- [CLI Reference](../guides/cli-reference.md) - Command-line interface documentation
- [REST API Reference](./rest-api.md) - REST API configuration and deployment
- [Caching Guide](../guides/caching.md) - Cache configuration and optimization
