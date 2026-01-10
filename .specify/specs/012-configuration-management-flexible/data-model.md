# Data Model: Configuration Management

**Feature**: 012-configuration-management-flexible  
**Date**: 2025-11-02  
**Purpose**: Define data structures for configuration management

## Entity Relationship Overview

```
ConfigurationSource (enum)
    ↓
ConfigurationManager
    ├── current_config: ProxyWhirlSettings
    ├── previous_config: ProxyWhirlSettings (for rollback)
    ├── sources: dict[str, ConfigurationSource]
    └── updates: list[ConfigUpdate]

ProxyWhirlSettings (Pydantic BaseSettings)
    ├── timeout: int
    ├── max_retries: int
    ├── log_level: str
    ├── proxy_url: SecretStr (optional)
    └── ... (other config fields)

ConfigUpdate (record)
    ├── user: User
    ├── timestamp: datetime
    ├── changes: dict[str, Any]
    ├── version: int
    └── source: ConfigurationSource

User (model)
    ├── id: str
    ├── username: str
    ├── is_admin: bool
    └── email: str (optional)

ValidationResult (model)
    ├── valid: bool
    ├── errors: list[ValidationError]
    └── warnings: list[str]

ConfigurationSnapshot (export model)
    ├── settings: dict[str, Any]
    ├── sources: dict[str, ConfigurationSource]
    ├── timestamp: datetime
    └── metadata: dict[str, str]
```

---

## 1. ProxyWhirlSettings

**Purpose**: Core configuration model with multi-source loading and validation

**Type**: Pydantic BaseSettings model

**Fields**:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr, field_validator
from typing import Literal

class ProxyWhirlSettings(BaseSettings):
    """ProxyWhirl runtime configuration with multi-source support."""
    
    model_config = SettingsConfigDict(
        env_prefix='PROXYWHIRL_',
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        validate_default=True,
    )
    
    # Request Configuration
    timeout: int = Field(
        default=5,
        ge=1,
        le=300,
        description="Request timeout in seconds",
        json_schema_extra={'hot_reloadable': True}
    )
    
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts",
        json_schema_extra={'hot_reloadable': True}
    )
    
    # Logging Configuration
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = Field(
        default='INFO',
        description="Logging level",
        json_schema_extra={'hot_reloadable': True}
    )
    
    # Proxy Configuration
    proxy_url: SecretStr | None = Field(
        default=None,
        description="HTTP proxy URL with credentials",
        json_schema_extra={'hot_reloadable': False}  # Requires restart
    )
    
    # Storage Configuration
    database_path: str = Field(
        default='proxywhirl.db',
        description="SQLite database file path",
        json_schema_extra={'hot_reloadable': False}  # Requires restart
    )
    
    # Server Configuration (if 003-rest-api active)
    server_host: str = Field(
        default='0.0.0.0',
        description="API server bind address",
        json_schema_extra={'hot_reloadable': False}  # Requires restart
    )
    
    server_port: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="API server port",
        json_schema_extra={'hot_reloadable': False}  # Requires restart
    )
    
    # Rate Limiting
    rate_limit_requests: int = Field(
        default=100,
        ge=1,
        description="Rate limit: requests per minute",
        json_schema_extra={'hot_reloadable': True}
    )
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is uppercase."""
        return v.upper()
    
    @field_validator('database_path')
    @classmethod
    def validate_database_path(cls, v: str) -> str:
        """Ensure database path has .db extension."""
        if not v.endswith('.db'):
            v += '.db'
        return v
    
    def is_hot_reloadable(self, field_name: str) -> bool:
        """Check if a field can be hot-reloaded."""
        field_info = self.model_fields.get(field_name)
        if field_info:
            return field_info.json_schema_extra.get('hot_reloadable', True)
        return False
    
    def get_restart_required_fields(self) -> set[str]:
        """Get fields that require restart when changed."""
        return {
            name for name, field_info in self.model_fields.items()
            if not field_info.json_schema_extra.get('hot_reloadable', True)
        }
```

**Constraints**:
- All fields have validation rules (ranges, enums)
- Credentials use `SecretStr` (automatically redacted)
- Hot-reloadable flag in `json_schema_extra`
- Restart-required fields marked explicitly

**Validation Rules**:
- `timeout`: 1-300 seconds
- `max_retries`: 0-10 attempts
- `log_level`: Must be valid logging level
- `server_port`: 1024-65535 (unprivileged ports)

---

## 2. ConfigurationSource

**Purpose**: Enumerate configuration value origins

**Type**: Enum

**Definition**:

```python
from enum import Enum

class ConfigurationSource(str, Enum):
    """Source of a configuration value."""
    
    DEFAULT = "default"
    YAML_FILE = "yaml_file"
    ENV_FILE = "env_file"
    ENVIRONMENT = "environment"
    CLI_ARGUMENT = "cli_argument"
    RUNTIME_UPDATE = "runtime_update"
```

**Usage**:

```python
# Track where each config value came from
sources = {
    'timeout': ConfigurationSource.CLI_ARGUMENT,
    'max_retries': ConfigurationSource.YAML_FILE,
    'log_level': ConfigurationSource.ENVIRONMENT,
}
```

**Precedence** (highest to lowest):
1. `CLI_ARGUMENT` - Command-line arguments
2. `RUNTIME_UPDATE` - API/programmatic updates
3. `ENVIRONMENT` - Environment variables
4. `ENV_FILE` - .env file
5. `YAML_FILE` - YAML configuration file
6. `DEFAULT` - Model defaults

---

## 3. ConfigUpdate

**Purpose**: Record of configuration change event

**Type**: Dataclass

**Definition**:

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass(frozen=True)
class ConfigUpdate:
    """Record of a configuration update."""
    
    user_id: str
    username: str
    timestamp: datetime
    changes: dict[str, Any]
    version: int
    source: ConfigurationSource = ConfigurationSource.RUNTIME_UPDATE
    
    def get_changed_keys(self) -> set[str]:
        """Get set of configuration keys changed."""
        return set(self.changes.keys())
    
    def conflicts_with(self, other: 'ConfigUpdate') -> set[str]:
        """Get keys that conflict with another update."""
        return self.get_changed_keys() & other.get_changed_keys()
```

**Usage**:

```python
update = ConfigUpdate(
    user_id="admin123",
    username="admin",
    timestamp=datetime.now(timezone.utc),
    changes={'timeout': 10, 'max_retries': 5},
    version=42,
)

# Check conflicts
if update.conflicts_with(previous_update):
    logger.warning("Concurrent configuration conflict detected")
```

**Constraints**:
- Immutable (frozen dataclass)
- Timestamp in UTC
- Version monotonically increasing

---

## 4. User

**Purpose**: Represent user for authorization and audit

**Type**: Pydantic model

**Definition**:

```python
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    """User model for authorization."""
    
    id: str
    username: str
    is_admin: bool = False
    email: EmailStr | None = None
    
    def require_admin(self):
        """Raise PermissionError if not admin."""
        if not self.is_admin:
            raise PermissionError(
                f"User {self.username} does not have admin privileges"
            )
```

**Usage**:

```python
user = User(id="u123", username="admin", is_admin=True)
user.require_admin()  # OK

regular_user = User(id="u456", username="user", is_admin=False)
regular_user.require_admin()  # Raises PermissionError
```

**Constraints**:
- `is_admin` defaults to False (least privilege)
- Email optional (may not be available)
- Username required for audit logs

---

## 5. ValidationResult

**Purpose**: Report configuration validation outcome

**Type**: Pydantic model

**Definition**:

```python
from pydantic import BaseModel

class ValidationError(BaseModel):
    """Single validation error."""
    field: str
    message: str
    value: Any | None = None

class ValidationResult(BaseModel):
    """Result of configuration validation."""
    
    valid: bool
    errors: list[ValidationError] = []
    warnings: list[str] = []
    
    @property
    def has_errors(self) -> bool:
        """Check if validation failed."""
        return not self.valid or len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if validation has warnings."""
        return len(self.warnings) > 0
    
    def raise_if_invalid(self):
        """Raise exception if validation failed."""
        if self.has_errors:
            error_messages = [f"{e.field}: {e.message}" for e in self.errors]
            raise ValueError(f"Configuration validation failed: {'; '.join(error_messages)}")
```

**Usage**:

```python
# Validate configuration
result = validate_config(new_settings)

if result.has_errors:
    for error in result.errors:
        logger.error(f"Validation error in {error.field}: {error.message}")
    raise ValueError("Invalid configuration")

if result.has_warnings:
    for warning in result.warnings:
        logger.warning(warning)
```

**Examples**:

```python
# Valid configuration
ValidationResult(valid=True, errors=[], warnings=[])

# Invalid configuration
ValidationResult(
    valid=False,
    errors=[
        ValidationError(field='timeout', message='Must be between 1 and 300', value=-5),
        ValidationError(field='log_level', message='Invalid level: TRACE', value='TRACE'),
    ]
)

# Valid with warnings
ValidationResult(
    valid=True,
    errors=[],
    warnings=['timeout value is very low (1s), may cause frequent timeouts']
)
```

---

## 6. ConfigurationSnapshot

**Purpose**: Export configuration state with metadata

**Type**: Pydantic model

**Definition**:

```python
from pydantic import BaseModel
from datetime import datetime

class ConfigurationSnapshot(BaseModel):
    """Snapshot of configuration for export."""
    
    settings: dict[str, Any]
    sources: dict[str, ConfigurationSource]
    timestamp: datetime
    metadata: dict[str, str]
    
    @classmethod
    def from_config(
        cls,
        config: ProxyWhirlSettings,
        sources: dict[str, ConfigurationSource]
    ) -> 'ConfigurationSnapshot':
        """Create snapshot from current configuration."""
        # Convert config to dict, redacting SecretStr
        settings_dict = {}
        for field_name, field_info in config.model_fields.items():
            value = getattr(config, field_name)
            if isinstance(value, SecretStr):
                settings_dict[field_name] = "*** REDACTED ***"
            else:
                settings_dict[field_name] = value
        
        return cls(
            settings=settings_dict,
            sources=sources,
            timestamp=datetime.now(timezone.utc),
            metadata={
                'version': str(config.get_config_version()),
                'hot_reloadable_count': str(sum(
                    1 for f in config.model_fields.values()
                    if f.json_schema_extra.get('hot_reloadable', True)
                ))
            }
        )
    
    def to_yaml(self) -> str:
        """Export snapshot to YAML format."""
        lines = [
            "# ProxyWhirl Configuration Snapshot",
            f"# Generated: {self.timestamp.isoformat()}",
            f"# Merged from: {', '.join(set(self.sources.values()))}",
            "",
        ]
        
        for field_name, value in self.settings.items():
            source = self.sources.get(field_name, ConfigurationSource.DEFAULT)
            lines.append(f"# Source: {source.value}")
            lines.append(f"{field_name}: {value}")
            lines.append("")
        
        return "\n".join(lines)
```

**Usage**:

```python
# Create snapshot
snapshot = ConfigurationSnapshot.from_config(current_config, sources)

# Export to YAML
yaml_content = snapshot.to_yaml()
with open('config_snapshot.yaml', 'w') as f:
    f.write(yaml_content)

# Load snapshot
with open('config_snapshot.yaml', 'r') as f:
    snapshot = ConfigurationSnapshot.model_validate_json(f.read())
```

---

## Data Flow Diagram

```
┌─────────────────┐
│  CLI Arguments  │
└────────┬────────┘
         │
         ├──────────────────┐
         │                  │
         ▼                  ▼
┌─────────────┐    ┌────────────────┐
│ Environment │    │  YAML File     │
│  Variables  │    │  (.env, .yaml) │
└──────┬──────┘    └────────┬───────┘
       │                    │
       └─────────┬──────────┘
                 │
                 ▼
         ┌───────────────┐
         │ pydantic-     │
         │ settings      │
         │ merge         │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────────┐
         │ ProxyWhirlSettings│◄──── Validation
         │ (current config)  │
         └─────────┬─────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
         ▼                   ▼
   ┌─────────┐         ┌─────────────┐
   │ Runtime │         │   Export    │
   │ Update  │         │  (Snapshot) │
   │  (API)  │         └─────────────┘
   └─────────┘
         │
         ▼
   ┌──────────────┐
   │  ConfigUpdate│
   │   (audit)    │
   └──────────────┘
```

---

## Relationships

### 1. ConfigurationManager → ProxyWhirlSettings (1:1)
- Manager holds current configuration instance
- Atomic swaps on reload

### 2. ConfigurationManager → ConfigUpdate (1:N)
- Manager tracks update history
- Used for conflict detection and audit

### 3. ProxyWhirlSettings → ConfigurationSource (N:N)
- Each field has a source
- Tracked separately in manager

### 4. ConfigUpdate → User (N:1)
- Each update made by one user
- User ID logged for audit

### 5. ConfigurationSnapshot → ProxyWhirlSettings (N:1)
- Snapshot captures config at point in time
- Includes source attribution

---

## Type Safety

All models use Pydantic v2 for:
- Runtime validation
- Type hints (mypy --strict compatible)
- JSON serialization
- Documentation generation

**Credentials**:
- Always use `SecretStr` for passwords, tokens, URLs with auth
- Automatic redaction in logs (`***`)
- Explicit redaction in exports

**Validation**:
- Field validators for complex rules
- Model validators for cross-field checks
- Clear error messages

**Immutability**:
- ConfigUpdate frozen (audit integrity)
- ProxyWhirlSettings immutable after creation (create new instance for changes)

---

## Testing Considerations

### Unit Test Coverage
- All Pydantic models: 100% (validation paths)
- ConfigUpdate conflict detection: 100%
- SecretStr redaction: 100%

### Property-Based Testing (Hypothesis)
- Configuration merging precedence
- Concurrent update ordering
- Validation boundary conditions

### Integration Testing
- Multi-source loading
- Hot reload with validation
- Export → Import round-trip

---

## Summary

**Total Entities**: 6 (ProxyWhirlSettings, ConfigurationSource, ConfigUpdate, User, ValidationResult, ConfigurationSnapshot)

**Type Safety**: 100% Pydantic models, mypy --strict compatible

**Security**: SecretStr for credentials, admin-only authorization

**Performance**: Lightweight models, efficient validation

**Ready for implementation**: All data structures defined with complete type hints and validation rules.
