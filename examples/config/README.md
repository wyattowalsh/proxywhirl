# ProxyWhirl YAML Configuration Schema Documentation

This document describes the complete YAML configuration schema for ProxyWhirl.

## Configuration File Structure

ProxyWhirl uses YAML configuration files to customize behavior. All settings are optional and have sensible defaults.

### Core Settings

```yaml
# Cache configuration
cache_type: memory | json | sqlite  # Default: memory
cache_path: /path/to/cache/file     # Default: null (memory only)

# Rotation strategy for proxy selection
rotation_strategy: round_robin | random | weighted | health_based | least_used  # Default: round_robin
```

### Health and Monitoring

```yaml
# Health check configuration
health_check_interval: 300          # Seconds between health checks (60-3600)
auto_validate: true                  # Auto-validate proxies on fetch

# Validation settings
validation_timeout: 10.0             # Timeout for proxy validation (1.0-60.0)
validation_test_url: "https://httpbin.org/ip"  # URL for testing proxies
validation_concurrent_limit: 10      # Max concurrent validations (1-100)
validation_min_success_rate: 0.7     # Minimum success rate (0.0-1.0)
validation_max_response_time: 30.0   # Max acceptable response time (0.1+)
```

### Loader Configuration

```yaml
# Default settings for proxy loaders
loader_timeout: 20.0                 # HTTP timeout in seconds (1.0-300.0)
loader_max_retries: 3                # Maximum retry attempts (0-10)
loader_rate_limit: null              # Requests per second limit (0.1+)
```

### Circuit Breaker

```yaml
# Circuit breaker for resilience
circuit_breaker_enabled: true        # Enable circuit breaker
circuit_breaker_failure_threshold: 5 # Failures before opening (1-20)
circuit_breaker_recovery_timeout: 300 # Recovery timeout in seconds (30-3600)
```

### Advanced Features

```yaml
# Feature toggles
enable_metrics: true                  # Enable performance metrics collection
enable_proxy_auth: false             # Enable authenticated proxy support
enable_rate_limiting: true           # Enable request rate limiting
enable_geolocation: false            # Enable geolocation enrichment
```

### Performance Tuning

```yaml
# Performance optimization
max_concurrent_validations: 50       # Maximum concurrent validations (1-200)
cache_refresh_interval: 3600         # Cache refresh interval in seconds (300-86400)
```

### Logging

```yaml
# Logging configuration
log_level: "INFO"                    # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
enable_debug_metrics: false         # Enable detailed debug metrics
```

### Quality Thresholds

```yaml
# Quality classification thresholds
premium_success_rate: 0.95          # Premium proxy threshold (0.0-1.0)
standard_success_rate: 0.8          # Standard proxy threshold (0.0-1.0)
basic_success_rate: 0.6             # Basic proxy threshold (0.0-1.0)
```

## Advanced YAML Features

### Using Anchors and References

ProxyWhirl supports YAML anchors (`&`) and references (`*`) for configuration reuse:

```yaml
# Define common settings
validation_defaults: &validation_defaults
  validation_timeout: 10.0
  validation_concurrent_limit: 15

# Use the reference
<<: *validation_defaults
```

### Environment Variable Substitution

Use environment variables with the `PROXYWHIRL_` prefix:

```bash
export PROXYWHIRL_CACHE_TYPE=sqlite
export PROXYWHIRL_LOG_LEVEL=DEBUG
export PROXYWHIRL_VALIDATION__TIMEOUT=5.0  # Note: double underscore for nested values
```

## Configuration Examples

See the `examples/config/` directory for complete configuration examples:

- `minimal.yaml` - Basic configuration with defaults
- `development.yaml` - Development-optimized settings
- `production.yaml` - Production-ready configuration
- `advanced.yaml` - Advanced features and YAML anchors

## Usage

Load a configuration file using the CLI:

```bash
proxywhirl --config /path/to/config.yaml fetch --loader proxyscrape
```

Or programmatically:

```python
from pathlib import Path
from proxywhirl.config import ProxyWhirlSettings

config = ProxyWhirlSettings.from_file(Path("config.yaml"))
```

## Validation

ProxyWhirl validates all configuration values and provides helpful error messages for invalid settings. All numeric values have appropriate ranges, and enum values are strictly validated.
