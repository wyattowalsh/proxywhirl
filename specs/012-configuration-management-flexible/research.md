# Research: Configuration Management

**Feature**: 012-configuration-management-flexible  
**Date**: 2025-11-02  
**Purpose**: Resolve technical unknowns identified in plan.md Phase 0

## 1. pydantic-settings Multi-Source Configuration

### Decision: **Custom SettingsConfigDict with priority-based sources**

### Rationale:
- **pydantic-settings V2**: Built-in support for multiple sources with `SettingsConfigDict`
- **Source Priority**: Can define custom source ordering via `settings_customise_sources`
- **Type Safety**: Full Pydantic validation on all sources
- **Python 3.9+ Compatible**: Fully supports target Python versions

### Implementation Pattern:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Union
import yaml

class ProxyWhirlSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='PROXYWHIRL_',
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
    )
    
    # Configuration fields
    timeout: int = Field(default=5, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    log_level: str = Field(default="INFO", description="Logging level")
    
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        # Precedence: CLI (init) > ENV > File > Defaults
        return (
            init_settings,  # CLI arguments (highest priority)
            env_settings,   # Environment variables
            dotenv_settings,  # YAML/env file
            file_secret_settings,
        )
```

### YAML File Loading:
```python
def load_yaml_config(path: str) -> dict:
    """Load configuration from YAML file."""
    with open(path, 'r') as f:
        return yaml.safe_load(f) or {}

# Integration with pydantic-settings
config = ProxyWhirlSettings(**load_yaml_config('config.yaml'))
```

### Alternatives Considered:
- **configparser**: Limited to INI format, no type validation
- **dynaconf**: Feature-rich but adds complexity, not type-safe by default
- **python-decouple**: Simpler but lacks Pydantic integration

---

## 2. YAML File Parsing Strategy

### Decision: **PyYAML with safe_load**

### Rationale:
- **Mature & Stable**: Industry-standard YAML parser for Python
- **Python 3.9+ Compatible**: Full support for all target versions
- **Safe Loading**: `safe_load()` prevents code execution attacks
- **Lightweight**: Minimal dependencies, fast parsing
- **Wide Adoption**: Well-documented, extensive community support

### Implementation Notes:
```python
import yaml

def load_yaml(path: str) -> dict:
    """Load YAML configuration safely."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in {path}: {e}")
    except FileNotFoundError:
        # Optional file, return empty dict
        return {}

def save_yaml(path: str, data: dict, comments: dict[str, str] = None):
    """Save configuration to YAML with optional comments."""
    with open(path, 'w', encoding='utf-8') as f:
        if comments:
            for key, comment in comments.items():
                f.write(f"# {comment}\n")
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
```

### Alternatives Considered:
- **ruamel.yaml**: Preserves comments and formatting, but heavier and more complex for our needs
- **strictyaml**: Type-safe but requires schema definition, redundant with Pydantic
- **oyaml**: Ordered YAML, but standard dict ordering in Python 3.7+ makes it unnecessary

---

## 3. Filesystem Watching Implementation

### Decision: **watchdog with file modification events**

### Rationale:
- **Cross-Platform**: Works on Linux (inotify), macOS (FSEvents), Windows (ReadDirectoryChangesW)
- **Reliable Events**: Handles file modifications, creates, deletes
- **Low Overhead**: Efficient native filesystem API usage
- **Active Maintenance**: Well-maintained with Python 3.9+ support
- **Simple API**: Easy to integrate with configuration reload logic

### Implementation Pattern:
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time

class ConfigFileHandler(FileSystemEventHandler):
    def __init__(self, config_path: str, reload_callback):
        self.config_path = Path(config_path).resolve()
        self.reload_callback = reload_callback
        self.last_reload = 0
        self.debounce_seconds = 1  # Avoid rapid reloads
    
    def on_modified(self, event):
        if event.src_path == str(self.config_path):
            now = time.time()
            if now - self.last_reload > self.debounce_seconds:
                self.last_reload = now
                self.reload_callback()

class ConfigurationManager:
    def enable_file_watching(self, config_path: str):
        """Enable automatic reload on config file changes."""
        handler = ConfigFileHandler(config_path, self.reload)
        observer = Observer()
        observer.schedule(handler, str(Path(config_path).parent), recursive=False)
        observer.start()
        return observer
```

### Debouncing Strategy:
- 1-second debounce to avoid rapid reloads from editors that write multiple times
- Track last reload timestamp to skip redundant events

### Alternatives Considered:
- **polling (os.stat)**: Simple but inefficient, high CPU usage for low-latency
- **inotify (Linux-only)**: Native but not cross-platform
- **asyncio file watching**: More complex, doesn't justify async overhead for this use case

---

## 4. CLI Argument Parsing

### Decision: **argparse with custom action for pydantic-settings integration**

### Rationale:
- **Standard Library**: No additional dependencies
- **Python 3.9+ Compatible**: Part of stdlib
- **Type Coercion**: Built-in type conversion
- **Help Generation**: Automatic --help text
- **Integration**: Easy to convert argparse namespace to dict for pydantic-settings

### Implementation Pattern:
```python
import argparse
from typing import Any

def parse_cli_args() -> dict[str, Any]:
    """Parse CLI arguments for configuration override."""
    parser = argparse.ArgumentParser(description='ProxyWhirl Configuration')
    
    # Add arguments matching configuration fields
    parser.add_argument('--timeout', type=int, help='Request timeout in seconds')
    parser.add_argument('--max-retries', type=int, dest='max_retries', help='Maximum retry attempts')
    parser.add_argument('--log-level', type=str, dest='log_level', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    parser.add_argument('--config', type=str, help='Path to YAML config file')
    
    args = parser.parse_args()
    
    # Convert to dict, filtering None values (not provided)
    return {k: v for k, v in vars(args).items() if v is not None}

# Usage with pydantic-settings
cli_overrides = parse_cli_args()
config = ProxyWhirlSettings(**cli_overrides)
```

### Alternatives Considered:
- **click**: More features but adds dependency, overkill for configuration
- **typer**: Modern but adds dependency, type hints nice but redundant with Pydantic
- **docopt**: Declarative but less type-safe, harder to integrate

---

## 5. Hot Reload Implementation

### Decision: **Threading Lock with atomic configuration swap**

### Rationale:
- **Thread Safety**: `threading.Lock` ensures atomic configuration updates
- **No Downtime**: New config loaded and validated before swapping
- **Rollback Support**: Keep old config until new one validated successfully
- **In-Flight Preservation**: Lock only during swap, not during request handling
- **Simple**: No complex async coordination needed

### Implementation Pattern:
```python
import threading
from typing import Optional
from copy import deepcopy

class ConfigurationManager:
    def __init__(self):
        self._config: Optional[ProxyWhirlSettings] = None
        self._config_lock = threading.Lock()
        self._previous_config: Optional[ProxyWhirlSettings] = None
    
    def reload(self) -> bool:
        """Reload configuration from all sources."""
        try:
            # Load new configuration (outside lock)
            new_config = self._load_config_from_sources()
            
            # Validate new configuration
            self._validate_config(new_config)
            
            # Atomic swap (inside lock)
            with self._config_lock:
                self._previous_config = deepcopy(self._config)
                self._config = new_config
            
            logger.info("Configuration reloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Configuration reload failed: {e}")
            # Keep existing configuration (no swap occurred)
            return False
    
    def get_config(self) -> ProxyWhirlSettings:
        """Get current configuration (thread-safe read)."""
        with self._config_lock:
            return self._config
    
    def rollback(self) -> bool:
        """Rollback to previous configuration."""
        with self._config_lock:
            if self._previous_config:
                self._config = self._previous_config
                self._previous_config = None
                return True
            return False
```

### Hot-Reloadable vs Restart-Required:
```python
class ConfigField:
    def __init__(self, hot_reloadable: bool = True):
        self.hot_reloadable = hot_reloadable

class ProxyWhirlSettings(BaseSettings):
    # Hot-reloadable (can change at runtime)
    timeout: int = Field(default=5, json_schema_extra={'hot_reloadable': True})
    max_retries: int = Field(default=3, json_schema_extra={'hot_reloadable': True})
    log_level: str = Field(default='INFO', json_schema_extra={'hot_reloadable': True})
    
    # Restart-required (structural settings)
    server_port: int = Field(default=8000, json_schema_extra={'hot_reloadable': False})
    database_path: str = Field(default='db.sqlite', json_schema_extra={'hot_reloadable': False})
```

### Alternatives Considered:
- **asyncio locks**: More complex, not needed for configuration (infrequent updates)
- **multiprocessing shared memory**: Overkill, adds significant complexity
- **Read-copy-update (RCU)**: Advanced but unnecessary for configuration frequency

---

## 6. Configuration Export Format

### Decision: **YAML with inline comments for source attribution**

### Rationale:
- **Human-Readable**: YAML is easy to read and edit
- **Source Attribution**: Inline comments indicate where each value came from
- **Credential Redaction**: SecretStr values automatically hidden
- **Re-importable**: Exported files can be used directly as config files

### Export Format Example:
```yaml
# ProxyWhirl Configuration Export
# Generated: 2025-11-02T14:30:00Z
# Merged from: CLI, ENV, config.yaml

# Request timeout in seconds (source: CLI argument)
timeout: 10

# Maximum retry attempts (source: environment variable PROXYWHIRL_MAX_RETRIES)
max_retries: 5

# Logging level (source: config.yaml)
log_level: DEBUG

# Proxy URL (source: config.yaml, CREDENTIALS REDACTED)
proxy_url: http://***:***@proxy.example.com:8080

# === Defaults (not explicitly set) ===

# Connection pool size (source: default)
pool_size: 10
```

### Implementation Pattern:
```python
def export_config(config: ProxyWhirlSettings, sources: dict[str, str]) -> str:
    """Export configuration with source attribution."""
    output = ["# ProxyWhirl Configuration Export"]
    output.append(f"# Generated: {datetime.now(timezone.utc).isoformat()}")
    output.append(f"# Merged from: {', '.join(set(sources.values()))}")
    output.append("")
    
    for field_name, field_info in config.model_fields.items():
        value = getattr(config, field_name)
        source = sources.get(field_name, 'default')
        
        # Redact SecretStr values
        if isinstance(value, SecretStr):
            value = "*** REDACTED ***"
        
        # Add comment with source
        output.append(f"# {field_info.description} (source: {source})")
        output.append(f"{field_name}: {value}")
        output.append("")
    
    return "\n".join(output)
```

### Alternatives Considered:
- **JSON**: Less human-readable, no comment support
- **TOML**: Good format but less widely used than YAML for config
- **Separate metadata file**: More complex, harder to maintain consistency

---

## 7. Authorization Integration

### Decision: **Simple User model with is_admin flag**

### Rationale:
- **Minimal Complexity**: Simple boolean flag for admin check
- **Reusable**: Can be extended if more roles needed later
- **Fast**: O(1) authorization check
- **Compatible**: Works with or without existing auth system
- **Audit Trail**: User ID logged in all config changes

### User Model:
```python
from pydantic import BaseModel

class User(BaseModel):
    id: str
    username: str
    is_admin: bool = False
    email: str | None = None

def require_admin(user: User):
    """Decorator/function to check admin authorization."""
    if not user.is_admin:
        raise PermissionError(f"User {user.username} does not have admin privileges")

class ConfigurationManager:
    def update_runtime_config(self, updates: dict, user: User):
        """Update configuration at runtime (admin-only)."""
        require_admin(user)
        
        # Log the authorization check
        logger.info(f"Config update authorized for admin user {user.username}")
        
        # Apply updates...
        self._apply_updates(updates)
        
        # Audit log
        self._log_config_change(user.id, user.username, updates)
```

### REST API Integration (if 003-rest-api active):
```python
from fastapi import Depends, HTTPException, status

async def get_current_user() -> User:
    """Get current authenticated user from request context."""
    # Integration with existing auth system
    # Or simple API key mapping for now
    pass

async def require_admin_user(user: User = Depends(get_current_user)) -> User:
    """Dependency that ensures user is admin."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user

@app.post("/api/v1/config")
async def update_config(
    updates: dict,
    user: User = Depends(require_admin_user)
):
    config_manager.update_runtime_config(updates, user)
    return {"status": "updated"}
```

### Alternatives Considered:
- **Fine-grained ACLs**: Too complex for initial release, can add later if needed
- **External auth system**: Adds dependency, simple model sufficient
- **No authorization**: Security risk, doesn't meet clarification requirement

---

## 8. Concurrent Update Handling

### Decision: **Last-write-wins with conflict logging and notification**

### Rationale:
- **Simple**: No distributed locking or complex coordination
- **Non-Blocking**: No requests blocked waiting for locks
- **Audit Trail**: All conflicts logged with timestamps and users
- **Notification**: Operators informed when their changes overwritten
- **Deterministic**: Clear outcome (last write wins) vs ambiguous merge

### Implementation Pattern:
```python
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class ConfigUpdate:
    user_id: str
    username: str
    timestamp: datetime
    changes: dict[str, Any]
    version: int

class ConfigurationManager:
    def __init__(self):
        self._config_version = 0
        self._recent_updates: list[ConfigUpdate] = []
        self._update_lock = threading.Lock()
    
    def update_runtime_config(self, updates: dict, user: User) -> ConfigUpdate:
        """Update configuration with conflict detection."""
        with self._update_lock:
            # Create update record
            update = ConfigUpdate(
                user_id=user.id,
                username=user.username,
                timestamp=datetime.now(timezone.utc),
                changes=updates,
                version=self._config_version + 1
            )
            
            # Check for conflicts (updates within last 5 seconds)
            recent_cutoff = datetime.now(timezone.utc) - timedelta(seconds=5)
            conflicts = [
                u for u in self._recent_updates
                if u.timestamp > recent_cutoff and 
                set(u.changes.keys()) & set(updates.keys())
            ]
            
            if conflicts:
                # Log conflict
                conflicting_users = [u.username for u in conflicts]
                logger.warning(
                    f"Config update conflict detected: {user.username} "
                    f"overwrote changes by {', '.join(conflicting_users)}"
                )
                
                # Notify conflicted users
                for conflicted_update in conflicts:
                    self._notify_config_conflict(
                        conflicted_update,
                        update,
                        overlapping_keys=set(conflicted_update.changes.keys()) & set(updates.keys())
                    )
            
            # Apply update (last-write-wins)
            self._apply_updates(updates)
            self._config_version += 1
            
            # Track recent updates
            self._recent_updates.append(update)
            self._cleanup_old_updates()
            
            return update
    
    def _notify_config_conflict(
        self,
        original: ConfigUpdate,
        overwriting: ConfigUpdate,
        overlapping_keys: set[str]
    ):
        """Notify operator of configuration conflict."""
        message = (
            f"Your configuration changes to {', '.join(overlapping_keys)} "
            f"at {original.timestamp.isoformat()} were overwritten by "
            f"{overwriting.username} at {overwriting.timestamp.isoformat()}"
        )
        
        logger.warning(f"Conflict notification for {original.username}: {message}")
        
        # Could also send email, webhook, or in-app notification
        # self._send_notification(original.user_id, message)
    
    def _cleanup_old_updates(self):
        """Remove updates older than 1 hour from tracking."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
        self._recent_updates = [
            u for u in self._recent_updates
            if u.timestamp > cutoff
        ]
```

### Conflict Detection Window:
- Track updates in last 5 seconds for conflict detection
- Keep 1 hour of history for audit purposes
- Configurable thresholds

### Alternatives Considered:
- **Optimistic locking**: Requires version tokens, adds client complexity
- **Pessimistic locking**: Blocking, reduces availability
- **CRDT merge**: Overkill for configuration, complex resolution rules
- **Queue all updates**: Adds latency, doesn't prevent conflicts

---

## Summary of Decisions

| Area | Decision | Key Dependencies |
|------|----------|------------------|
| Multi-Source Config | pydantic-settings with custom sources | `pydantic-settings>=2.0.0` |
| YAML Parsing | PyYAML with safe_load | `pyyaml>=6.0` |
| File Watching | watchdog | `watchdog>=3.0.0` |
| CLI Parsing | argparse (stdlib) | None (standard library) |
| Hot Reload | Threading lock with atomic swap | `threading` (stdlib) |
| Export Format | YAML with source comments | `pyyaml>=6.0` |
| Authorization | User model with is_admin flag | Simple model |
| Concurrency | Last-write-wins with conflict detection | `threading` (stdlib) |

**All unknowns resolved**. Ready for Phase 1 (data-model.md, contracts, quickstart.md).
