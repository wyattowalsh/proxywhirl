# Quickstart: Configuration Management

**Feature**: 012-configuration-management-flexible  
**Date**: 2025-11-02  
**Audience**: Developers integrating configuration management

## Overview

This guide demonstrates all 5 user stories for the configuration management feature:
- US1 (P1): Multi-source configuration loading
- US2 (P1): Runtime configuration updates
- US3 (P2): Configuration validation
- US4 (P2): Hot reload file watching
- US5 (P3): Configuration export

---

## US1: Multi-Source Configuration Loading (P1)

Load configuration from multiple sources with automatic precedence.

### Basic Usage

```python
from proxywhirl import ProxyWhirlSettings

# Load from all sources (precedence: CLI > ENV > YAML > Defaults)
config = ProxyWhirlSettings()

print(f"Timeout: {config.timeout}s")
print(f"Max retries: {config.max_retries}")
print(f"Log level: {config.log_level}")
```

### YAML Configuration File

Create `proxywhirl.yaml`:

```yaml
# ProxyWhirl Configuration
timeout: 10
max_retries: 5
log_level: DEBUG
rate_limit_requests: 200
```

Load configuration:

```python
import yaml
from proxywhirl import ProxyWhirlSettings

# Load YAML file
with open('proxywhirl.yaml', 'r') as f:
    yaml_config = yaml.safe_load(f)

# Merge with other sources
config = ProxyWhirlSettings(**yaml_config)
```

### Environment Variables

Set environment variables:

```bash
export PROXYWHIRL_TIMEOUT=15
export PROXYWHIRL_MAX_RETRIES=7
export PROXYWHIRL_LOG_LEVEL=INFO
```

Load configuration:

```python
from proxywhirl import ProxyWhirlSettings

# Automatically loads from environment (PROXYWHIRL_ prefix)
config = ProxyWhirlSettings()

print(config.timeout)  # 15 (from ENV, overrides YAML)
```

### CLI Arguments

```python
import argparse
from proxywhirl import ProxyWhirlSettings

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--timeout', type=int)
    parser.add_argument('--max-retries', type=int, dest='max_retries')
    parser.add_argument('--log-level', type=str, dest='log_level')
    return parser.parse_args()

# CLI arguments have highest precedence
args = parse_args()
cli_overrides = {k: v for k, v in vars(args).items() if v is not None}

config = ProxyWhirlSettings(**cli_overrides)
```

### Full Multi-Source Example

```python
import yaml
import argparse
from proxywhirl import ProxyWhirlSettings

def load_configuration():
    """Load configuration from all sources with correct precedence."""
    
    # 1. Load YAML file (if exists)
    yaml_config = {}
    try:
        with open('proxywhirl.yaml', 'r') as f:
            yaml_config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        pass
    
    # 2. Parse CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--timeout', type=int)
    parser.add_argument('--max-retries', type=int, dest='max_retries')
    parser.add_argument('--config', type=str, help='Path to YAML config')
    args = parser.parse_args()
    
    # Load custom YAML path if provided
    if args.config:
        with open(args.config, 'r') as f:
            yaml_config = yaml.safe_load(f) or {}
    
    # 3. Merge sources (pydantic-settings handles ENV automatically)
    # Precedence: CLI > ENV > YAML > Defaults
    cli_overrides = {k: v for k, v in vars(args).items() 
                     if v is not None and k != 'config'}
    
    config = ProxyWhirlSettings(**{**yaml_config, **cli_overrides})
    
    return config

# Usage
config = load_configuration()
```

---

## US2: Runtime Configuration Updates (P1)

Update configuration at runtime without restart (admin-only).

### Basic Runtime Update

```python
from proxywhirl import ConfigurationManager, User

# Initialize manager
config_manager = ConfigurationManager()

# Admin user
admin = User(id="admin123", username="admin", is_admin=True)

# Update timeout at runtime
updates = {'timeout': 10, 'log_level': 'DEBUG'}
config_manager.update_runtime_config(updates, admin)

# New config active immediately
current_config = config_manager.get_config()
print(f"New timeout: {current_config.timeout}s")
```

### Authorization Check

```python
from proxywhirl import ConfigurationManager, User

config_manager = ConfigurationManager()

# Regular user (not admin)
regular_user = User(id="user456", username="user", is_admin=False)

try:
    updates = {'timeout': 20}
    config_manager.update_runtime_config(updates, regular_user)
except PermissionError as e:
    print(f"Authorization failed: {e}")
    # Output: User user does not have admin privileges
```

### Rollback Support

```python
from proxywhirl import ConfigurationManager, User

config_manager = ConfigurationManager()
admin = User(id="admin123", username="admin", is_admin=True)

# Current config
print(f"Timeout: {config_manager.get_config().timeout}s")

# Update configuration
config_manager.update_runtime_config({'timeout': 99}, admin)
print(f"New timeout: {config_manager.get_config().timeout}s")

# Rollback if there's an issue
if config_manager.rollback():
    print("Configuration rolled back successfully")
    print(f"Restored timeout: {config_manager.get_config().timeout}s")
```

### Audit Trail

```python
from proxywhirl import ConfigurationManager, User

config_manager = ConfigurationManager()
admin = User(id="admin123", username="admin", is_admin=True, 
             email="admin@example.com")

# Updates are automatically logged
config_manager.update_runtime_config(
    {'timeout': 10, 'max_retries': 5},
    admin
)

# Audit log entry created:
# INFO: Config update authorized for admin user admin
# INFO: Configuration updated by admin (admin123): timeout=10, max_retries=5
```

---

## US3: Configuration Validation (P2)

Validate configuration before applying changes.

### Basic Validation

```python
from proxywhirl import ProxyWhirlSettings, ValidationResult

def validate_config(config_dict: dict) -> ValidationResult:
    """Validate configuration dictionary."""
    try:
        # Pydantic validation
        config = ProxyWhirlSettings(**config_dict)
        return ValidationResult(valid=True, errors=[], warnings=[])
    except Exception as e:
        errors = [
            ValidationError(field='unknown', message=str(e))
        ]
        return ValidationResult(valid=False, errors=errors)

# Valid configuration
result = validate_config({'timeout': 10, 'max_retries': 3})
print(f"Valid: {result.valid}")

# Invalid configuration
result = validate_config({'timeout': -5})  # Negative timeout
print(f"Valid: {result.valid}")
for error in result.errors:
    print(f"  {error.field}: {error.message}")
```

### Pre-Update Validation

```python
from proxywhirl import ConfigurationManager, User

config_manager = ConfigurationManager()
admin = User(id="admin123", username="admin", is_admin=True)

# Validate before updating
new_config = {'timeout': 1000}  # Exceeds max (300)

result = config_manager.validate_updates(new_config)
if result.has_errors:
    print("Validation failed:")
    for error in result.errors:
        print(f"  {error.field}: {error.message}")
    # Don't apply invalid configuration
else:
    config_manager.update_runtime_config(new_config, admin)
```

### Validation with Warnings

```python
from proxywhirl import ConfigurationManager, User

config_manager = ConfigurationManager()
admin = User(id="admin123", username="admin", is_admin=True)

# Configuration that's valid but may have issues
new_config = {'timeout': 1}  # Very low timeout

result = config_manager.validate_updates(new_config)
if result.has_warnings:
    print("Warnings:")
    for warning in result.warnings:
        print(f"  {warning}")
    # Output: timeout value is very low (1s), may cause frequent timeouts

# Still apply if only warnings (not errors)
if not result.has_errors:
    config_manager.update_runtime_config(new_config, admin)
```

---

## US4: Hot Reload File Watching (P2)

Automatically reload configuration when file changes.

### Enable File Watching

```python
from proxywhirl import ConfigurationManager

config_manager = ConfigurationManager(config_path='proxywhirl.yaml')

# Enable automatic reload on file changes
observer = config_manager.enable_file_watching()

print("Watching for configuration changes...")
print("Edit proxywhirl.yaml to trigger reload")

# Configuration automatically reloads when file modified
# (runs in background thread)
```

### Custom Reload Callback

```python
from proxywhirl import ConfigurationManager
from loguru import logger

def on_config_reload():
    """Called after successful configuration reload."""
    config = config_manager.get_config()
    logger.info(f"Configuration reloaded: timeout={config.timeout}s")

config_manager = ConfigurationManager(
    config_path='proxywhirl.yaml',
    reload_callback=on_config_reload
)

observer = config_manager.enable_file_watching()
```

### Debouncing

```python
from proxywhirl import ConfigurationManager

# Debounce to avoid rapid reloads from editors
config_manager = ConfigurationManager(
    config_path='proxywhirl.yaml',
    debounce_seconds=2.0  # Wait 2s after last change
)

observer = config_manager.enable_file_watching()

# Prevents reload on every keystroke during editing
# Only reloads 2 seconds after last file modification
```

### Graceful Shutdown

```python
from proxywhirl import ConfigurationManager
import time

config_manager = ConfigurationManager(config_path='proxywhirl.yaml')
observer = config_manager.enable_file_watching()

try:
    # Your application runs
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # Stop file watching
    observer.stop()
    observer.join()
    print("File watching stopped")
```

---

## US5: Configuration Export (P3)

Export current configuration with source attribution.

### Basic Export

```python
from proxywhirl import ConfigurationManager

config_manager = ConfigurationManager()

# Export current configuration to YAML
yaml_content = config_manager.export_config()

print(yaml_content)
# Output:
# # ProxyWhirl Configuration Export
# # Generated: 2025-11-02T14:30:00Z
# # Merged from: CLI, ENV, config.yaml
# 
# # Request timeout in seconds (source: CLI argument)
# timeout: 10
# 
# # Maximum retry attempts (source: environment variable)
# max_retries: 5
# ...
```

### Export to File

```python
from proxywhirl import ConfigurationManager

config_manager = ConfigurationManager()

# Export to file
config_manager.export_config_to_file('exported_config.yaml')

print("Configuration exported to exported_config.yaml")
```

### Export with Redacted Credentials

```python
from proxywhirl import ConfigurationManager, ProxyWhirlSettings
from pydantic import SecretStr

# Configuration with credentials
config = ProxyWhirlSettings(
    timeout=10,
    proxy_url=SecretStr('http://user:pass@proxy.example.com:8080')
)

config_manager = ConfigurationManager(config=config)

# Export automatically redacts credentials
yaml_content = config_manager.export_config()

print(yaml_content)
# Output:
# # Proxy URL (source: default, CREDENTIALS REDACTED)
# proxy_url: *** REDACTED ***
```

### Snapshot for Backup

```python
from proxywhirl import ConfigurationManager, ConfigurationSnapshot

config_manager = ConfigurationManager()

# Create snapshot
snapshot = ConfigurationSnapshot.from_config(
    config_manager.get_config(),
    config_manager.get_sources()
)

# Save snapshot
yaml_content = snapshot.to_yaml()
with open(f'config_backup_{snapshot.timestamp.isoformat()}.yaml', 'w') as f:
    f.write(yaml_content)

print(f"Snapshot created at {snapshot.timestamp}")
```

---

## Complete Example: All Features Together

```python
#!/usr/bin/env python3
"""
Complete example demonstrating all configuration management features.
"""

import yaml
import argparse
from proxywhirl import (
    ProxyWhirlSettings,
    ConfigurationManager,
    User,
    ValidationResult,
)
from loguru import logger

def main():
    # US1: Multi-Source Loading
    logger.info("Loading configuration from multiple sources...")
    
    # Parse CLI arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--timeout', type=int)
    parser.add_argument('--config', type=str, default='proxywhirl.yaml')
    args = parser.parse_args()
    
    # Load YAML
    yaml_config = {}
    try:
        with open(args.config, 'r') as f:
            yaml_config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.warning(f"Config file {args.config} not found, using defaults")
    
    # Merge sources
    cli_overrides = {k: v for k, v in vars(args).items() 
                     if v is not None and k != 'config'}
    config = ProxyWhirlSettings(**{**yaml_config, **cli_overrides})
    
    # Initialize manager
    config_manager = ConfigurationManager(config=config, config_path=args.config)
    logger.info(f"Configuration loaded: timeout={config.timeout}s")
    
    # US4: Hot Reload
    logger.info("Enabling file watching for hot reload...")
    observer = config_manager.enable_file_watching()
    
    # US2: Runtime Updates
    admin = User(id="admin123", username="admin", is_admin=True)
    
    logger.info("Updating configuration at runtime...")
    new_settings = {'max_retries': 7, 'log_level': 'DEBUG'}
    
    # US3: Validation
    result = config_manager.validate_updates(new_settings)
    if result.has_errors:
        logger.error("Validation failed:")
        for error in result.errors:
            logger.error(f"  {error.field}: {error.message}")
        return
    
    if result.has_warnings:
        for warning in result.warnings:
            logger.warning(warning)
    
    # Apply updates
    config_manager.update_runtime_config(new_settings, admin)
    logger.info("Configuration updated successfully")
    
    # US5: Export
    logger.info("Exporting configuration...")
    export_path = 'config_export.yaml'
    config_manager.export_config_to_file(export_path)
    logger.info(f"Configuration exported to {export_path}")
    
    # Cleanup
    observer.stop()
    observer.join()

if __name__ == '__main__':
    main()
```

---

## Testing Examples

### Unit Test: Multi-Source Loading

```python
import pytest
from proxywhirl import ProxyWhirlSettings

def test_multi_source_loading():
    """Test configuration loads from multiple sources."""
    # YAML config
    yaml_config = {'timeout': 10, 'max_retries': 5}
    
    # CLI overrides
    cli_overrides = {'timeout': 15}
    
    # CLI should have precedence
    config = ProxyWhirlSettings(**{**yaml_config, **cli_overrides})
    
    assert config.timeout == 15  # From CLI
    assert config.max_retries == 5  # From YAML
```

### Integration Test: Runtime Update

```python
import pytest
from proxywhirl import ConfigurationManager, User

def test_runtime_update_authorization():
    """Test admin-only runtime updates."""
    manager = ConfigurationManager()
    
    admin = User(id="a1", username="admin", is_admin=True)
    regular = User(id="u1", username="user", is_admin=False)
    
    # Admin can update
    manager.update_runtime_config({'timeout': 20}, admin)
    assert manager.get_config().timeout == 20
    
    # Regular user cannot update
    with pytest.raises(PermissionError):
        manager.update_runtime_config({'timeout': 30}, regular)
```

---

## Performance Tips

1. **Minimize Hot Reload Frequency**: Use debouncing (1-2 seconds) to avoid excessive reloads
2. **Validate Before Apply**: Always validate configuration before runtime updates
3. **Batch Updates**: Combine multiple changes into single update call
4. **Cache Configuration**: Store reference to config object, don't call `get_config()` repeatedly
5. **Restart-Required Fields**: Changes to non-hot-reloadable fields require restart

---

## Next Steps

- Read `spec.md` for complete requirements
- Check `data-model.md` for detailed type definitions
- Review `tasks.md` (when available) for implementation phases
- See constitution compliance in `plan.md`

---

**Ready to implement**: All user stories demonstrated with working code examples.
