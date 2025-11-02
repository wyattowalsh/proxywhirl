# Configuration Management

ProxyWhirl provides comprehensive configuration management with multi-source loading, runtime updates, hot-reload capabilities, and configuration export.

## Features

- **Multi-Source Loading**: Load configuration from YAML files, environment variables, and command-line arguments with clear precedence rules
- **Runtime Updates**: Update configuration settings at runtime without restarting (admin-only, hot-reloadable fields)
- **Configuration Validation**: Validate configuration against schema before applying changes
- **Hot Reload**: Automatic reload when configuration files change
- **Configuration Export**: Export current configuration for backup and documentation
- **Concurrent Update Handling**: Last-write-wins with conflict detection and notification
- **Security**: 100% credential redaction in logs and exports

## Quick Start

### Basic Usage

```python
from proxywhirl import ProxyWhirlSettings, ConfigurationManager

# Load configuration from all sources
config = ProxyWhirlSettings()

# Or use configuration manager
manager = ConfigurationManager()
config = manager.get_config()

print(f"Timeout: {config.timeout}s")
print(f"Max retries: {config.max_retries}")
```

### Multi-Source Loading

Configuration sources are loaded with the following precedence (highest to lowest):

1. **Command-line arguments** (`--timeout 10`)
2. **Runtime API updates** (via `ConfigurationManager.update_runtime_config()`)
3. **Environment variables** (`PROXYWHIRL_TIMEOUT=10`)
4. **.env file**
5. **YAML configuration file** (`proxywhirl.yaml`)
6. **Default values**

#### YAML Configuration

Create a `proxywhirl.yaml` file:

```yaml
# Request Configuration
timeout: 10
max_retries: 5

# Logging
log_level: DEBUG

# Rate Limiting
rate_limit_requests: 200
```

Load with:

```python
from proxywhirl import ProxyWhirlSettings, load_yaml_config

yaml_config = load_yaml_config('proxywhirl.yaml')
config = ProxyWhirlSettings(**yaml_config)
```

#### Environment Variables

Set environment variables with `PROXYWHIRL_` prefix:

```bash
export PROXYWHIRL_TIMEOUT=15
export PROXYWHIRL_MAX_RETRIES=7
export PROXYWHIRL_LOG_LEVEL=DEBUG
```

Configuration is automatically loaded:

```python
from proxywhirl import ProxyWhirlSettings

config = ProxyWhirlSettings()  # Loads from environment
```

#### Command-Line Arguments

```python
from proxywhirl import ProxyWhirlSettings, parse_cli_args

cli_config = parse_cli_args(['--timeout', '20', '--log-level', 'INFO'])
config = ProxyWhirlSettings(**cli_config)
```

### Runtime Configuration Updates

Update configuration at runtime (requires admin privileges):

```python
from proxywhirl import ConfigurationManager, User

manager = ConfigurationManager()

# Admin user required for updates
admin = User(id="admin123", username="admin", is_admin=True)

# Update configuration
updates = {
    'timeout': 15,
    'max_retries': 7,
    'log_level': 'DEBUG'
}

manager.update_runtime_config(updates, admin)
```

#### Hot-Reloadable vs Restart-Required Fields

**Hot-Reloadable** (can be updated at runtime):
- `timeout`
- `max_retries`
- `log_level`
- `rate_limit_requests`

**Restart-Required** (require application restart):
- `proxy_url`
- `database_path`
- `server_host`
- `server_port`

Check if a field is hot-reloadable:

```python
config = ProxyWhirlSettings()
print(config.is_hot_reloadable('timeout'))      # True
print(config.is_hot_reloadable('server_port'))  # False
```

### Configuration Validation

Validate configuration before applying:

```python
from proxywhirl import validate_config

config_dict = {
    'timeout': 10,
    'max_retries': 5
}

result = validate_config(config_dict)

if result.valid:
    print("Configuration is valid")
else:
    for error in result.errors:
        print(f"Error in {error.field}: {error.message}")

if result.has_warnings:
    for warning in result.warnings:
        print(f"Warning: {warning}")
```

### Hot Reload

#### Manual Reload

```python
from proxywhirl import ConfigurationManager

manager = ConfigurationManager(config_path='proxywhirl.yaml')

# Later, when you want to reload
manager.reload()  # Validates and applies new configuration
```

#### Automatic Reload with File Watching

```python
from proxywhirl import ConfigurationManager
import time

manager = ConfigurationManager(config_path='proxywhirl.yaml')

# Enable file watching
observer = manager.enable_file_watching()

# Configuration automatically reloads when file changes
time.sleep(100)

# Stop watching when done
observer.stop()
observer.join()
```

### Configuration Export

Export current configuration for backup or documentation:

```python
from proxywhirl import ConfigurationManager

manager = ConfigurationManager()

# Export to string
yaml_export = manager.export_config()
print(yaml_export)

# Export to file
manager.export_config_to_file('backup_config.yaml')
```

Credentials are automatically redacted in exports:

```yaml
# ProxyWhirl Configuration Snapshot
# Generated: 2025-11-02T14:30:00Z

# Source: default
proxy_url: *** REDACTED ***

# Source: cli_argument
timeout: 10
```

### Rollback

Rollback to previous configuration:

```python
from proxywhirl import ConfigurationManager, User

manager = ConfigurationManager()
admin = User(id="admin123", username="admin", is_admin=True)

# Make an update
manager.update_runtime_config({'timeout': 50}, admin)

# Rollback if needed
if manager.rollback():
    print("Configuration rolled back successfully")
```

## Configuration Schema

### Available Settings

| Setting | Type | Default | Range | Hot-Reloadable |
|---------|------|---------|-------|----------------|
| `timeout` | int | 5 | 1-300 | ? |
| `max_retries` | int | 3 | 0-10 | ? |
| `log_level` | str | INFO | DEBUG, INFO, WARNING, ERROR, CRITICAL | ? |
| `proxy_url` | SecretStr | null | - | ? (restart required) |
| `database_path` | str | proxywhirl.db | - | ? (restart required) |
| `server_host` | str | 0.0.0.0 | - | ? (restart required) |
| `server_port` | int | 8000 | 1024-65535 | ? (restart required) |
| `rate_limit_requests` | int | 100 | ?1 | ? |

### Validation Rules

- **timeout**: Must be between 1 and 300 seconds
- **max_retries**: Must be between 0 and 10
- **log_level**: Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL (case-insensitive)
- **database_path**: Automatically appends `.db` extension if missing
- **server_port**: Must be unprivileged port (1024-65535)
- **rate_limit_requests**: Must be positive integer

## Advanced Usage

### Custom Reload Callback

```python
from proxywhirl import ConfigurationManager
from loguru import logger

def on_config_reload():
    config = manager.get_config()
    logger.info(f"Config reloaded: timeout={config.timeout}s")

manager = ConfigurationManager(
    config_path='proxywhirl.yaml',
    reload_callback=on_config_reload
)
```

### Configuration History

Track configuration changes for audit:

```python
from proxywhirl import ConfigurationManager

manager = ConfigurationManager()

# Get recent updates
history = manager.get_config_history(limit=10)

for update in history:
    print(f"Version {update.version}:")
    print(f"  User: {update.username}")
    print(f"  Time: {update.timestamp}")
    print(f"  Changes: {update.changes}")
```

### Concurrent Update Handling

ProxyWhirl handles concurrent configuration updates with last-write-wins semantics:

```python
from proxywhirl import ConfigurationManager, User

manager = ConfigurationManager()
admin1 = User(id="a1", username="alice", is_admin=True)
admin2 = User(id="a2", username="bob", is_admin=True)

# Concurrent updates
manager.update_runtime_config({'timeout': 10}, admin1)
manager.update_runtime_config({'timeout': 15}, admin2)

# Last write wins (timeout=15)
# Conflict is logged for operators
```

## Security Considerations

### Admin-Only Updates

Runtime configuration updates require admin privileges:

```python
from proxywhirl import ConfigurationManager, User

manager = ConfigurationManager()

# Regular user (no admin privileges)
user = User(id="u1", username="user", is_admin=False)

# This will raise PermissionError
manager.update_runtime_config({'timeout': 10}, user)
```

### Credential Redaction

All sensitive values (SecretStr fields) are automatically redacted in:
- Log messages
- Error messages
- Configuration exports
- Validation output

```python
from pydantic import SecretStr
from proxywhirl import ProxyWhirlSettings

config = ProxyWhirlSettings(
    proxy_url=SecretStr('http://user:pass@proxy.com:8080')
)

# Credential is hidden in exports and logs
snapshot = manager.export_config()
# Output: proxy_url: *** REDACTED ***
```

## Performance

Configuration management is designed for high performance:

- **Configuration Loading**: <500ms for 100+ settings
- **Runtime Updates**: <1 second to take effect
- **Hot Reload**: <2 seconds including validation
- **Validation**: <100ms for typical configurations

## Best Practices

1. **Use YAML files for base configuration** - Easy to read and version control
2. **Use environment variables for deployment-specific overrides** - Different values per environment
3. **Use CLI arguments for testing and debugging** - Quick temporary overrides
4. **Always validate before deploying** - Catch errors early
5. **Monitor configuration history** - Track who changed what and when
6. **Test configuration changes in staging first** - Validate before production
7. **Use hot-reloadable fields when possible** - Avoid service restarts
8. **Export configuration regularly** - Backup and documentation
9. **Keep credentials in environment variables** - Never commit to version control
10. **Enable file watching for development** - Faster iteration

## Troubleshooting

### Configuration Not Loading

**Problem**: Configuration changes not taking effect

**Solutions**:
- Check file precedence - CLI > ENV > YAML > Defaults
- Verify environment variable names have `PROXYWHIRL_` prefix
- Ensure YAML file syntax is correct
- Check file permissions

### Validation Errors

**Problem**: Configuration validation fails

**Solutions**:
- Check value ranges (e.g., timeout must be 1-300)
- Verify field names match schema exactly
- Check data types (integers, strings, etc.)
- Review validation error messages for details

### Hot Reload Not Working

**Problem**: File changes not triggering reload

**Solutions**:
- Verify file watching is enabled
- Check debounce interval (default 1 second)
- Ensure file path is correct
- Check filesystem permissions
- Some editors create temp files - may need to adjust watching

### Permission Errors

**Problem**: PermissionError when updating configuration

**Solutions**:
- Ensure user has `is_admin=True`
- Check authorization logic
- Verify admin credentials

## Examples

See `/workspace/examples/config_management_example.py` for comprehensive examples demonstrating:
- Multi-source configuration loading
- Runtime updates with authorization
- Configuration validation
- Hot reload with file watching
- Configuration export
- Rollback support
- Concurrent update handling

## API Reference

See the module documentation for detailed API reference:

```python
from proxywhirl import (
    ConfigurationManager,
    ProxyWhirlSettings,
    User,
    ValidationResult,
    ConfigurationSnapshot,
    ConfigurationSource,
    ConfigUpdate,
)
```

All classes and functions include comprehensive docstrings with type hints and examples.
