# Configuration Reference

ProxyWhirl uses TOML configuration files for persistent settings. Configuration can be provided via project-local `pyproject.toml` or user-global config files.

## Configuration Discovery

ProxyWhirl discovers configuration files in the following priority order:

1. **Explicit path** - Path provided via CLI `--config` flag
2. **Project-local** - `./pyproject.toml` with `[tool.proxywhirl]` section
3. **User-global** - `~/.config/proxywhirl/config.toml`
4. **Defaults** - Built-in defaults if no config file found

### Example: Project-Local Configuration

Add a `[tool.proxywhirl]` section to your `pyproject.toml`:

```toml
[tool.proxywhirl]
timeout = 45
max_retries = 5
rotation_strategy = "weighted"
verbose = true
```

### Example: User-Global Configuration

Create `~/.config/proxywhirl/config.toml`:

```toml
# ~/.config/proxywhirl/config.toml
timeout = 30
max_retries = 3
default_format = "json"
color = false
cache_enabled = true
encrypt_credentials = true
```

## Configuration Sections

### CLI Configuration (`CLIConfig`)

The main configuration model with 23+ fields organized by category.

#### Proxy Pool

**`proxies`** (list of proxy configs)
- **Default:** `[]` (empty list)
- **Description:** List of static proxy configurations
- **Example:**
  ```toml
  [[proxies]]
  url = "http://proxy1.example.com:8080"
  username = "user1"
  password = "pass1"

  [[proxies]]
  url = "socks5://proxy2.example.com:1080"
  ```

**`proxy_file`** (path)
- **Default:** `None`
- **Description:** Path to external proxy list file (one proxy per line)
- **Example:** `proxy_file = "/path/to/proxies.txt"`

#### Rotation Settings

**`rotation_strategy`** (string)
- **Default:** `"round-robin"`
- **Valid Values:** `round-robin`, `random`, `weighted`, `least-used`
- **Description:** Strategy for selecting next proxy
- **Example:** `rotation_strategy = "weighted"`

**`health_check_interval`** (integer)
- **Default:** `300` (5 minutes)
- **Range:** `0` = disabled, `> 0` = seconds between checks
- **Description:** Interval for automatic proxy health checks
- **Example:** `health_check_interval = 600`

#### Request Settings

**`timeout`** (integer)
- **Default:** `30`
- **Description:** Request timeout in seconds
- **Example:** `timeout = 45`

**`max_retries`** (integer)
- **Default:** `3`
- **Description:** Maximum retry attempts per request
- **Example:** `max_retries = 5`

**`follow_redirects`** (boolean)
- **Default:** `true`
- **Description:** Whether to follow HTTP redirects automatically
- **Example:** `follow_redirects = false`

**`verify_ssl`** (boolean)
- **Default:** `true`
- **Description:** Whether to verify SSL certificates
- **Example:** `verify_ssl = false`

#### Output Settings

**`default_format`** (string)
- **Default:** `"text"`
- **Valid Values:** `text`, `json`, `csv` (deprecated aliases: `human` → `text`, `table` → `text`)
- **Description:** Default output format for CLI commands
- **Example:** `default_format = "json"`

**`color`** (boolean)
- **Default:** `true`
- **Description:** Enable colored terminal output
- **Example:** `color = false`

**`verbose`** (boolean)
- **Default:** `false`
- **Description:** Enable verbose logging output
- **Example:** `verbose = true`

#### Storage Settings

**`storage_backend`** (string)
- **Default:** `"file"`
- **Description:** Storage backend type
- **Example:** `storage_backend = "sqlite"`

**`storage_path`** (path)
- **Default:** `None`
- **Description:** Custom path for file/sqlite storage
- **Example:** `storage_path = "/var/lib/proxywhirl/data.db"`

#### Cache Settings

**`cache_enabled`** (boolean)
- **Default:** `true`
- **Description:** Enable three-tier caching system (L1=memory, L2=JSONL, L3=SQLite)
- **Example:** `cache_enabled = false`

**`cache_l1_max_entries`** (integer)
- **Default:** `1000`
- **Description:** Maximum entries in L1 (in-memory) cache
- **Example:** `cache_l1_max_entries = 2000`

**`cache_l2_max_entries`** (integer)
- **Default:** `5000`
- **Description:** Maximum entries in L2 (JSONL file) cache
- **Example:** `cache_l2_max_entries = 10000`

**`cache_l3_max_entries`** (integer or null)
- **Default:** `None` (unlimited)
- **Description:** Maximum entries in L3 (SQLite) cache
- **Example:** `cache_l3_max_entries = 50000`

**`cache_default_ttl`** (integer)
- **Default:** `3600` (1 hour)
- **Range:** `>= 60` seconds
- **Description:** Default cache entry TTL in seconds
- **Example:** `cache_default_ttl = 7200`

**`cache_cleanup_interval`** (integer)
- **Default:** `60`
- **Range:** `>= 10` seconds
- **Description:** Interval for background cache cleanup
- **Example:** `cache_cleanup_interval = 120`

**`cache_l2_dir`** (string)
- **Default:** `".cache/proxies"`
- **Description:** Directory path for L2 cache files
- **Example:** `cache_l2_dir = "/tmp/proxywhirl/cache"`

**`cache_l3_db_path`** (string)
- **Default:** `".cache/db/proxywhirl.db"`
- **Description:** SQLite database path for L3 cache
- **Example:** `cache_l3_db_path = "/var/cache/proxywhirl.db"`

**`cache_encryption_key_env`** (string)
- **Default:** `"PROXYWHIRL_CACHE_ENCRYPTION_KEY"`
- **Description:** Environment variable name for cache encryption key
- **Example:** `cache_encryption_key_env = "MY_CACHE_KEY"`

**`cache_health_invalidation`** (boolean)
- **Default:** `true`
- **Description:** Automatically invalidate cache entries on health check failure
- **Example:** `cache_health_invalidation = false`

**`cache_failure_threshold`** (integer)
- **Default:** `3`
- **Range:** `>= 1`
- **Description:** Number of failures before cache health invalidation triggers
- **Example:** `cache_failure_threshold = 5`

#### Security Settings

**`encrypt_credentials`** (boolean)
- **Default:** `true`
- **Description:** Encrypt proxy credentials in config file using Fernet encryption
- **Example:** `encrypt_credentials = false`

**`encryption_key_env`** (string)
- **Default:** `"PROXYWHIRL_KEY"`
- **Description:** Environment variable name for credential encryption key
- **Example:** `encryption_key_env = "MY_ENCRYPTION_KEY"`

### Data Storage Configuration (`DataStorageConfig`)

Controls which fields are persisted to the database. Nested under `[data_storage]` section. All fields are boolean except ranges specified.

#### Request Timing Analytics

**`persist_latency_percentiles`** (boolean)
- **Default:** `true`
- **Description:** Store P50, P95, P99 response time percentiles

**`persist_response_time_stats`** (boolean)
- **Default:** `true`
- **Description:** Store min/max/stddev response times

#### Error Tracking

**`persist_error_types`** (boolean)
- **Default:** `true`
- **Description:** Store error type counts (timeout, ssl, connection, etc.)

**`persist_error_messages`** (boolean)
- **Default:** `true`
- **Description:** Store last error message for debugging

**`max_error_history`** (integer)
- **Default:** `20`
- **Range:** `0-100`
- **Description:** Maximum error history entries to keep per proxy

#### Geographic & IP Intelligence (Privacy-Sensitive)

**`persist_geo_data`** (boolean)
- **Default:** `false` (opt-in for privacy)
- **Description:** Store country/region/city information

**`persist_ip_intelligence`** (boolean)
- **Default:** `false` (opt-in for privacy)
- **Description:** Store is_residential/is_datacenter/is_vpn classification flags

**`persist_coordinates`** (boolean)
- **Default:** `false` (opt-in for privacy)
- **Description:** Store latitude/longitude coordinates

#### Protocol Details

**`persist_protocol_details`** (boolean)
- **Default:** `true`
- **Description:** Store HTTP version, TLS version info

**`persist_capabilities`** (boolean)
- **Default:** `true`
- **Description:** Store supports_https/http2/connect capability flags

#### Health Tracking

**`persist_health_transitions`** (boolean)
- **Default:** `true`
- **Description:** Store health status change history (healthy → unhealthy transitions)

**`persist_consecutive_streaks`** (boolean)
- **Default:** `true`
- **Description:** Store consecutive success/failure streak counts

**`max_health_transitions`** (integer)
- **Default:** `50`
- **Range:** `0-500`
- **Description:** Maximum health transition records to keep in history

#### Source Metadata

**`persist_source_metadata`** (boolean)
- **Default:** `true`
- **Description:** Store source name, fetch timestamp, validation info

**`persist_fetch_duration`** (boolean)
- **Default:** `true`
- **Description:** Store how long proxy fetch operation took

#### Advanced (Expensive Storage)

**`persist_request_logs`** (boolean)
- **Default:** `false`
- **Description:** Store individual request logs (warning: heavy storage usage)

**`persist_daily_aggregates`** (boolean)
- **Default:** `false`
- **Description:** Store daily aggregate statistics

## Environment Variables

ProxyWhirl recognizes the following environment variables:

### `PROXYWHIRL_KEY`

**Purpose:** Fernet encryption key for proxy credentials

**Usage:**
```bash
# Generate a new key
export PROXYWHIRL_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Or use an existing key
export PROXYWHIRL_KEY="your-base64-encoded-key"
```

**Key Management:**
- If not set, ProxyWhirl generates and persists a key to `~/.config/proxywhirl/key.enc`
- File permissions automatically set to `0600` (owner read/write only)
- For portability across machines, export the key:
  ```bash
  export PROXYWHIRL_KEY=$(cat ~/.config/proxywhirl/key.enc)
  ```

### `PROXYWHIRL_CACHE_ENCRYPTION_KEY`

**Purpose:** Fernet encryption key for cache data encryption

**Usage:**
```bash
export PROXYWHIRL_CACHE_ENCRYPTION_KEY="your-base64-encoded-key"
```

**Note:** Separate from credential encryption key to allow different security policies for cache vs. credentials.

### API Server Environment Variables

When running the REST API (`proxywhirl serve`), additional environment variables are available:

- **`PROXYWHIRL_REQUIRE_AUTH`** - Set to `"true"` to enable API authentication (default: `"false"`)
- **`PROXYWHIRL_API_KEY`** - API key for authentication (required if `REQUIRE_AUTH=true`)
- **`PROXYWHIRL_STORAGE_PATH`** - Override storage path for API server
- **`PROXYWHIRL_STRATEGY`** - Default rotation strategy (default: `"round-robin"`)
- **`PROXYWHIRL_TIMEOUT`** - Request timeout in seconds (default: `"30"`)
- **`PROXYWHIRL_MAX_RETRIES`** - Max retry attempts (default: `"3"`)
- **`PROXYWHIRL_CORS_ORIGINS`** - Comma-separated CORS origins (default: `"http://localhost:8000,http://127.0.0.1:8000"`)

## Complete Configuration Examples

### Minimal Configuration

```toml
# Use defaults for everything
timeout = 30
rotation_strategy = "round-robin"
```

### Development Configuration

```toml
# pyproject.toml
[tool.proxywhirl]
# Request settings
timeout = 45
max_retries = 5
verify_ssl = false
follow_redirects = true

# Output
verbose = true
default_format = "json"
color = true

# Storage
storage_backend = "sqlite"
storage_path = "./dev.db"

# Cache
cache_enabled = true
cache_default_ttl = 1800
cache_l1_max_entries = 500

# Security - disable for local dev
encrypt_credentials = false
```

### Production Configuration

```toml
# ~/.config/proxywhirl/config.toml

# Rotation
rotation_strategy = "weighted"
health_check_interval = 300

# Request settings
timeout = 30
max_retries = 3
verify_ssl = true
follow_redirects = true

# Output
default_format = "json"
color = false
verbose = false

# Storage
storage_backend = "sqlite"
storage_path = "/var/lib/proxywhirl/production.db"

# Cache - high performance
cache_enabled = true
cache_l1_max_entries = 5000
cache_l2_max_entries = 20000
cache_l3_max_entries = 100000
cache_default_ttl = 3600
cache_cleanup_interval = 120
cache_l2_dir = "/var/cache/proxywhirl/l2"
cache_l3_db_path = "/var/cache/proxywhirl/l3.db"

# Security - enabled
encrypt_credentials = true
encryption_key_env = "PROXYWHIRL_KEY"

# Data storage - analytics enabled
[data_storage]
persist_latency_percentiles = true
persist_response_time_stats = true
persist_error_types = true
persist_error_messages = true
max_error_history = 50

# Privacy - geo data enabled for production analytics
persist_geo_data = true
persist_ip_intelligence = true
persist_coordinates = false

persist_protocol_details = true
persist_capabilities = true
persist_health_transitions = true
persist_consecutive_streaks = true
max_health_transitions = 100
persist_source_metadata = true
persist_fetch_duration = true

# Advanced analytics
persist_request_logs = false
persist_daily_aggregates = true
```

### Privacy-Focused Configuration

```toml
# Minimal data persistence for privacy
timeout = 30
rotation_strategy = "round-robin"
cache_enabled = true
encrypt_credentials = true

[data_storage]
# Core functionality only
persist_latency_percentiles = true
persist_response_time_stats = true
persist_error_types = true
persist_error_messages = false  # Don't store error details
max_error_history = 5

# NO geographic or IP intelligence
persist_geo_data = false
persist_ip_intelligence = false
persist_coordinates = false

persist_protocol_details = true
persist_capabilities = true
persist_health_transitions = true
persist_consecutive_streaks = true
max_health_transitions = 20
persist_source_metadata = false  # Don't track sources
persist_fetch_duration = false

# NO advanced logging
persist_request_logs = false
persist_daily_aggregates = false
```

### Configuration with Static Proxies

```toml
timeout = 30
rotation_strategy = "round-robin"
encrypt_credentials = true

# Define proxies inline
[[proxies]]
url = "http://proxy1.example.com:8080"
username = "user1"
password = "secret1"

[[proxies]]
url = "https://proxy2.example.com:8443"
username = "user2"
password = "secret2"

[[proxies]]
url = "socks5://proxy3.example.com:1080"
# No auth required

[data_storage]
persist_latency_percentiles = true
persist_response_time_stats = true
```

### Configuration with External Proxy File

```toml
timeout = 30
rotation_strategy = "random"
proxy_file = "/etc/proxywhirl/proxies.txt"

[data_storage]
persist_latency_percentiles = true
persist_health_transitions = true
```

## Proxy Configuration (`ProxyConfig`)

Individual proxy entries support the following fields:

**`url`** (string, required)
- **Format:** `<protocol>://<host>:<port>`
- **Valid Protocols:** `http://`, `https://`, `socks4://`, `socks5://`
- **Example:** `"http://proxy.example.com:8080"`

**`username`** (string, optional)
- **Description:** Proxy authentication username
- **Encrypted:** Yes (if `encrypt_credentials = true`)

**`password`** (string, optional)
- **Description:** Proxy authentication password
- **Encrypted:** Yes (if `encrypt_credentials = true`)

### Proxy URL Validation

The following proxy URLs are **valid**:
```toml
url = "http://proxy.example.com:8080"
url = "https://secure.proxy.com:443"
url = "socks4://socks.proxy.net:1080"
url = "socks5://socks5.proxy.org:1080"
```

The following are **invalid** and will raise `ValueError`:
```toml
url = "ftp://proxy.example.com:21"        # Invalid protocol
url = "proxy.example.com:8080"             # Missing protocol
url = "tcp://proxy.example.com:8080"       # Unsupported protocol
```

## Configuration File Permissions

ProxyWhirl automatically sets restrictive permissions on configuration files containing sensitive data:

- **Config files:** `0600` (owner read/write only)
- **Encryption key files:** `0600` (owner read/write only)

This prevents unauthorized access to proxy credentials and encryption keys.

## Configuration Validation

All configuration values are validated on load using Pydantic:

- **Type validation:** Ensures correct data types (int, bool, string, etc.)
- **Range validation:** Enforces min/max constraints (e.g., `cache_default_ttl >= 60`)
- **Enum validation:** Checks against valid values (e.g., rotation strategies)
- **URL validation:** Verifies proxy URL format and protocol

Invalid configurations raise descriptive `ValueError` exceptions.

## Programmatic Configuration

While TOML files are recommended, you can also configure ProxyWhirl programmatically:

```python
from proxywhirl.config import CLIConfig, DataStorageConfig, ProxyConfig
from pydantic import SecretStr

# Create configuration
config = CLIConfig(
    rotation_strategy="weighted",
    timeout=45,
    max_retries=5,
    cache_enabled=True,
    cache_default_ttl=7200,
    proxies=[
        ProxyConfig(
            url="http://proxy1.example.com:8080",
            username=SecretStr("user1"),
            password=SecretStr("pass1")
        )
    ],
    data_storage=DataStorageConfig(
        persist_geo_data=True,
        persist_ip_intelligence=True,
        max_error_history=50
    )
)

# Save to file
from proxywhirl.config import save_config
from pathlib import Path

save_config(config, Path("~/.config/proxywhirl/config.toml").expanduser())
```

## Configuration Loading Priority

When multiple configuration sources exist, ProxyWhirl merges them with the following priority (highest to lowest):

1. **CLI arguments** (e.g., `--timeout 60`)
2. **Environment variables** (e.g., `PROXYWHIRL_TIMEOUT=60`)
3. **Explicit config file** (via `--config` flag)
4. **Project-local** (`./pyproject.toml`)
5. **User-global** (`~/.config/proxywhirl/config.toml`)
6. **Built-in defaults**

## Troubleshooting

### Encryption Key Issues

**Problem:** "Failed to decrypt credentials"

**Solution:**
1. Check that `PROXYWHIRL_KEY` environment variable is set correctly
2. Verify the key matches the one used during encryption
3. Check `~/.config/proxywhirl/key.enc` exists and has correct permissions
4. Regenerate key if needed (will require re-encrypting credentials)

### Configuration Not Found

**Problem:** ProxyWhirl ignores your config file

**Solutions:**
1. Verify file exists at expected path
2. Check `[tool.proxywhirl]` section exists in `pyproject.toml`
3. Use `--config` flag to specify explicit path
4. Enable verbose mode: `proxywhirl --verbose <command>`

### Invalid Configuration Values

**Problem:** `ValueError: Invalid rotation strategy`

**Solution:** Check allowed values in this documentation and ensure your config uses valid options.

### Permission Errors

**Problem:** "Permission denied" when saving config

**Solution:** Ensure you have write permissions to the config directory:
```bash
mkdir -p ~/.config/proxywhirl
chmod 700 ~/.config/proxywhirl
```

## See Also

- [Getting Started Guide](getting_started.md) - Quick start with configuration examples
- [Database Migrations Guide](migrations.md) - Managing database schema changes
- [CLI Reference](cli.md) - Command-line interface documentation (if available)
