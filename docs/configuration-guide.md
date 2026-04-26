# ProxyWhirl Configuration Guide

## Overview

ProxyWhirl uses a hierarchical configuration system that allows you to set options through multiple sources:

1. **Defaults** (hardcoded in library)
2. **TOML Configuration File** (`~/.proxywhirl/config.toml`)
3. **Environment Variables** (`PROXYWHIRL_*`)
4. **Runtime Arguments** (highest priority)

Each layer overrides the previous one, allowing flexibility from global defaults to per-call customization.

## Configuration Hierarchy Example

```python
# 1. Defaults (library)
max_retries = 3

# 2. TOML file
PROXYWHIRL_CONFIG=~/.proxywhirl/config.toml
max_retries = 5

# 3. Environment variable
PROXYWHIRL_MAX_RETRIES=7

# 4. Runtime argument (used)
ProxyWhirl(config=ProxyConfiguration(max_retries=10))
# Result: max_retries = 10
```

## Configuration File (TOML)

### Default Location

- **Linux/macOS**: `~/.proxywhirl/config.toml`
- **Windows**: `%APPDATA%\proxywhirl\config.toml`
- **Override**: Set `PROXYWHIRL_CONFIG=/custom/path/config.toml`

### Minimal Configuration

```toml
[pool]
rotation_strategy = "round_robin"
max_pool_size = 5000

[storage]
backend = "sqlite"
path = "~/.proxywhirl/proxies.db"

[api]
enabled = true
host = "0.0.0.0"
port = 8000
```

### Complete Configuration

```toml
# === POOL SETTINGS ===
[pool]
# Rotation strategy: round_robin, random, weighted, performance_based, least_used, location_based, latency_based
rotation_strategy = "round_robin"

# Maximum proxies to keep in memory
max_pool_size = 5000

# Health check interval in seconds
health_check_interval_seconds = 300

# Check only X% of pool per interval (0.1 = 10%)
health_check_sampling_rate = 0.1

# Enable/disable health checks
health_checks_enabled = true

# === RETRY SETTINGS ===
[retry]
# Maximum retry attempts
max_retries = 3

# Initial retry delay in milliseconds
initial_delay_ms = 100

# Maximum retry delay in milliseconds
max_delay_ms = 30000

# Exponential backoff multiplier
exponential_base = 2.0

# Add random jitter to delays
jitter_enabled = true

# Maximum jitter in milliseconds
max_jitter_ms = 1000

# Retryable exception types
retryable_exceptions = [
    "ProxyConnectionError",
    "ProxyTimeoutError",
    "ProxyValidationError"
]

# === CIRCUIT BREAKER ===
[circuit_breaker]
# Enable circuit breaker
enabled = true

# Failure threshold before opening circuit
failure_threshold = 10

# Recovery timeout in seconds
recovery_timeout_seconds = 60

# Sample size for failure tracking
sample_size = 100

# Success threshold in HALF_OPEN state
success_threshold_half_open = 3

# === RATE LIMITING ===
[rate_limiting]
# Requests per second
requests_per_second = 100.0

# Burst size (tokens in bucket)
burst_size = 50

# Enable token bucket rate limiter
enabled = true

# === CACHING ===
[cache]
# Enable caching
enabled = true

# Cache TTL in seconds
ttl_seconds = 300

# Maximum cache size
max_size = 10000

# Enable encryption for cached data
encryption_enabled = true

# Cache encryption key (use env var: PROXYWHIRL_CACHE_ENCRYPTION_KEY)
# encryption_key = "your-fernet-key-here"

# === STORAGE ===
[storage]
# Backend: sqlite, file
backend = "sqlite"

# SQLite database path
path = "~/.proxywhirl/proxies.db"

# Keep stats in database
track_stats = true

# Backup interval in days (0 = disabled)
backup_interval_days = 7

# === DATA STORAGE ===
[data_storage]
# Storage path for exports
path = "~/.proxywhirl/exports"

# Enable auto-backup
auto_backup_enabled = true

# Backup frequency in seconds
backup_interval_seconds = 3600

# === FETCHER SETTINGS ===
[fetcher]
# Timeout for fetching proxy lists in seconds
timeout_seconds = 30

# Verify SSL certificates
verify_ssl = true

# Retry failed fetches
retry_failed_fetches = true

# Maximum proxies to fetch per source
max_proxies_per_source = 1000

# === VALIDATOR SETTINGS ===
[validator]
# Timeout for proxy validation in seconds
timeout_seconds = 5

# Test URL for validation
test_url = "https://httpbin.org/ip"

# Verify SSL during validation
verify_ssl = false

# Validate on pool load
validate_on_load = false

# === BROWSER RENDERING ===
[browser]
# Enable Playwright browser support
enabled = false

# Browser type: chromium, firefox, webkit
browser_type = "chromium"

# Headless mode
headless = true

# Timeout in seconds
timeout_seconds = 30

# === PROXY SOURCES ===
[proxy_sources]
# Enabled sources
enabled = [
    "free-proxy-list",
    "proxy-list",
    "us-proxy"
]

# Fetch interval in hours
fetch_interval_hours = 6

# Validate fetched proxies
validate_on_fetch = true

# === LOGGING ===
[logging]
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
level = "INFO"

# Log file path (leave empty for stdout only)
file_path = "~/.proxywhirl/logs/proxywhirl.log"

# Log rotation size in bytes
rotation_size_bytes = 10485760  # 10MB

# Retention in days
retention_days = 7

# Include request body in logs
include_request_body = false

# Include response body in logs
include_response_body = false

# === API SERVER ===
[api]
# Enable API server
enabled = true

# Host to bind to
host = "0.0.0.0"

# Port to listen on
port = 8000

# API key for authentication (use env var: PROXYWHIRL_API_KEY)
# api_key = "sk_your_api_key_here"

# CORS origins (comma-separated)
cors_origins = ["http://localhost:3000", "http://localhost:8080"]

# Enable Swagger UI
swagger_ui_enabled = true

# Enable ReDoc
redoc_enabled = true

# Request timeout in seconds
request_timeout_seconds = 30

# === MCP SERVER ===
[mcp]
# Enable MCP server
enabled = false

# MCP server port
port = 5000

# MCP API key (use env var: PROXYWHIRL_MCP_API_KEY)
# api_key = "mcp_your_api_key_here"

# === METRICS ===
[metrics]
# Enable Prometheus metrics
enabled = true

# Metrics port
port = 9090

# Metrics collection interval in seconds
interval_seconds = 60

# === GEO ENRICHMENT ===
[geo]
# Enable IP geolocation
enabled = true

# Update interval in days
update_interval_days = 7

# === ADVANCED ===
[advanced]
# Master encryption key (use env var: PROXYWHIRL_KEY)
# encryption_key = "your-master-key-here"

# Enable proxy verification on startup
verify_on_startup = false

# Connection pool size for validators
validator_pool_size = 10

# Session persistence enabled
session_persistence = true

# Stats aggregation interval in seconds
stats_aggregation_interval = 60

# Enable debug mode
debug_mode = false
```

## Environment Variables

All configuration options can be set via environment variables with prefix `PROXYWHIRL_`:

```bash
# Pool settings
PROXYWHIRL_ROTATION_STRATEGY=round_robin
PROXYWHIRL_MAX_POOL_SIZE=5000
PROXYWHIRL_HEALTH_CHECK_INTERVAL=300

# Retry settings
PROXYWHIRL_MAX_RETRIES=3
PROXYWHIRL_RETRY_INITIAL_DELAY=100
PROXYWHIRL_RETRY_MAX_DELAY=30000

# Circuit breaker
PROXYWHIRL_CB_ENABLED=true
PROXYWHIRL_CB_FAILURE_THRESHOLD=10
PROXYWHIRL_CB_RECOVERY_TIMEOUT=60

# Rate limiting
PROXYWHIRL_RATE_LIMIT_RPS=100
PROXYWHIRL_RATE_LIMIT_BURST=50

# Caching
PROXYWHIRL_CACHE_ENABLED=true
PROXYWHIRL_CACHE_TTL=300
PROXYWHIRL_CACHE_ENCRYPTION_KEY=your_fernet_key

# Storage
PROXYWHIRL_STORAGE_BACKEND=sqlite
PROXYWHIRL_STORAGE_PATH=~/.proxywhirl/proxies.db

# API
PROXYWHIRL_API_ENABLED=true
PROXYWHIRL_API_HOST=0.0.0.0
PROXYWHIRL_API_PORT=8000
PROXYWHIRL_API_KEY=sk_your_api_key

# Logging
PROXYWHIRL_LOG_LEVEL=INFO
PROXYWHIRL_LOG_FILE=~/.proxywhirl/logs/proxywhirl.log

# Security
PROXYWHIRL_KEY=your_master_encryption_key
```

## Runtime Configuration

### Python API

```python
from proxywhirl import ProxyWhirl, ProxyConfiguration

# Create custom configuration
config = ProxyConfiguration(
    rotation_strategy="weighted",
    max_pool_size=5000,
    health_check_interval_seconds=600,
    max_retries=5,
    circuit_breaker_enabled=True,
    circuit_breaker_failure_threshold=15,
    cache_ttl_seconds=600,
    cache_max_size=20000,
    rate_limit_requests_per_second=50.0,
)

# Initialize ProxyWhirl
rotator = ProxyWhirl(config=config)

# Use rotator
proxy = rotator.get_proxy()
```

### Async Python API

```python
import asyncio
from proxywhirl import AsyncProxyWhirl, ProxyConfiguration

async def main():
    config = ProxyConfiguration(
        rotation_strategy="performance_based",
        max_retries=5,
    )
    
    rotator = AsyncProxyWhirl(config=config)
    proxy = await rotator.get_proxy()
    print(proxy)

asyncio.run(main())
```

### CLI Configuration

```bash
# Use custom config file
proxywhirl --config /path/to/config.toml list

# Override via CLI flags
proxywhirl --max-retries 5 --rotation-strategy weighted fetch

# Set environment variables
export PROXYWHIRL_ROTATION_STRATEGY=random
export PROXYWHIRL_MAX_RETRIES=3
proxywhirl validate
```

## Configuration Examples

### Example 1: High-Performance Web Scraper

```toml
[pool]
rotation_strategy = "latency_based"
max_pool_size = 10000
health_check_interval_seconds = 60

[retry]
max_retries = 5
initial_delay_ms = 50
exponential_base = 1.5

[circuit_breaker]
enabled = true
failure_threshold = 20

[rate_limiting]
requests_per_second = 1000
burst_size = 500

[cache]
enabled = true
ttl_seconds = 60

[validator]
timeout_seconds = 3
```

### Example 2: Lightweight Single-Threaded Script

```toml
[pool]
rotation_strategy = "round_robin"
max_pool_size = 100
health_checks_enabled = false

[retry]
max_retries = 1

[circuit_breaker]
enabled = false

[rate_limiting]
enabled = false

[cache]
enabled = false

[storage]
backend = "file"
```

### Example 3: Enterprise Deployment

```toml
[pool]
rotation_strategy = "performance_based"
max_pool_size = 50000
health_check_interval_seconds = 30
health_check_sampling_rate = 0.1

[retry]
max_retries = 10
exponential_base = 2.0
jitter_enabled = true

[circuit_breaker]
enabled = true
failure_threshold = 5
recovery_timeout_seconds = 120

[rate_limiting]
requests_per_second = 10000
burst_size = 1000

[cache]
enabled = true
ttl_seconds = 300
max_size = 100000
encryption_enabled = true

[storage]
backend = "sqlite"
track_stats = true
backup_interval_days = 1

[api]
enabled = true
host = "0.0.0.0"
port = 8000
cors_origins = ["https://app.example.com"]

[logging]
level = "WARNING"
file_path = "/var/log/proxywhirl/main.log"
rotation_size_bytes = 104857600

[metrics]
enabled = true
port = 9090
```

### Example 4: Development with Debugging

```toml
[pool]
rotation_strategy = "round_robin"
health_checks_enabled = true

[logging]
level = "DEBUG"
file_path = "logs/proxywhirl.log"
include_request_body = true
include_response_body = true

[api]
enabled = true
swagger_ui_enabled = true
redoc_enabled = true

[advanced]
debug_mode = true
```

## Configuration Loading

The configuration loader follows this precedence:

```python
1. Library defaults
2. Global config (~/.proxywhirl/config.toml)
3. Project config (./proxywhirl.toml)
4. Environment variables (PROXYWHIRL_*)
5. Runtime arguments (highest priority)
```

## Validation

Configuration is automatically validated on load:

```python
try:
    config = ProxyConfiguration(
        rotation_strategy="invalid_strategy"  # Raises error
    )
except ValueError as e:
    print(f"Configuration error: {e}")
```

## Best Practices

### 1. Use Configuration Files for Production

```bash
# Don't
export PROXYWHIRL_API_KEY=sk_abc123
export PROXYWHIRL_ROTATION_STRATEGY=weighted
python app.py

# Do
proxywhirl --config /etc/proxywhirl/config.toml
```

### 2. Separate Configs by Environment

```
config/
├── development.toml
├── staging.toml
└── production.toml
```

### 3. Use Environment Variables for Secrets

```toml
# config.toml - no secrets
[api]
api_key = ""  # Will use PROXYWHIRL_API_KEY env var
```

```bash
export PROXYWHIRL_API_KEY=sk_your_key
proxywhirl --config config.toml
```

### 4. Version Your Configuration

```toml
# Version field helps track changes
[meta]
version = "1.0"
created_at = "2024-04-26"
```

### 5. Document Custom Settings

```toml
# Custom configuration for project XYZ
# See: https://internal-wiki.example.com/proxywhirl-config

[pool]
# Use latency-based selection for gaming proxies
rotation_strategy = "latency_based"
```

## Troubleshooting Configuration

### Configuration Not Loading

```python
import proxywhirl

# Check effective configuration
config = proxywhirl.config.load_config()
print(config)  # Print entire config

# Check specific value
print(config.rotation_strategy)
```

### Environment Variables Not Overriding

Ensure correct naming:

```bash
# Correct
PROXYWHIRL_ROTATION_STRATEGY=weighted

# Incorrect (won't work)
ROTATION_STRATEGY=weighted
PROXYWHIRL_rotation_strategy=weighted  # Case sensitive
```

### File Not Found

```python
import os
config_path = os.path.expanduser("~/.proxywhirl/config.toml")
print(f"Config path: {config_path}")
print(f"Exists: {os.path.exists(config_path)}")
```

## Configuration Reset

To reset to defaults:

```bash
# Remove configuration files
rm ~/.proxywhirl/config.toml
rm ./proxywhirl.toml

# Unset environment variables
unset PROXYWHIRL_*

# Use library defaults
proxywhirl list
```

