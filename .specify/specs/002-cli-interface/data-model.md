# Data Model: CLI Interface

**Phase 1 Output** | **Date**: 2025-10-25 | **Feature**: 002-cli-interface

## Overview

This document defines the data models for CLI configuration, command state, and output formatting. All models leverage existing Pydantic models from the core library where possible.

---

## 1. CLI Configuration Model

**Purpose**: Persistent user settings stored in TOML configuration files

**File Locations**:

- Project-local: `./pyproject.toml` under `[tool.proxywhirl]`
- User-global: `~/.config/proxywhirl/config.toml` (XDG/AppData)

**Schema**:

```python
from pydantic import BaseModel, Field, SecretStr, field_validator
from typing import Optional, List
from pathlib import Path

class ProxyConfig(BaseModel):
    """Configuration for a single proxy (stored in config file)."""
    url: str  # http://host:port or socks5://host:port
    username: Optional[SecretStr] = None
    password: Optional[SecretStr] = None
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        # Reuse validation from proxywhirl.models.Proxy
        if not v.startswith(('http://', 'https://', 'socks4://', 'socks5://')):
            raise ValueError("Invalid proxy URL scheme")
        return v

class CLIConfig(BaseModel):
    """Complete CLI configuration (maps to [tool.proxywhirl] in TOML)."""
    
    # Proxy pool
    proxies: List[ProxyConfig] = Field(default_factory=list, description="List of proxies to use")
    proxy_file: Optional[Path] = Field(None, description="Path to proxy list file")
    
    # Rotation settings
    rotation_strategy: str = Field("round-robin", description="round-robin, random, weighted, least-used")
    health_check_interval: int = Field(300, description="Seconds between health checks (0=disabled)")
    
    # Request settings
    timeout: int = Field(30, description="Request timeout in seconds")
    max_retries: int = Field(3, description="Max retry attempts per request")
    follow_redirects: bool = Field(True, description="Follow HTTP redirects")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")
    
    # Output settings
    default_format: str = Field("human", description="human, json, table, csv")
    color: bool = Field(True, description="Enable colored output")
    verbose: bool = Field(False, description="Verbose output mode")
    
    # Storage settings (Phase 2 integration)
    storage_backend: str = Field("file", description="file, sqlite, memory")
    storage_path: Optional[Path] = Field(None, description="Path for file/sqlite storage")
    
    # Security
    encrypt_credentials: bool = Field(True, description="Encrypt credentials in config file")
    encryption_key_env: str = Field("PROXYWHIRL_KEY", description="Env var for encryption key")
    
    @field_validator('rotation_strategy')
    @classmethod
    def validate_strategy(cls, v: str) -> str:
        valid = {"round-robin", "random", "weighted", "least-used"}
        if v not in valid:
            raise ValueError(f"Invalid rotation strategy. Must be one of: {valid}")
        return v
    
    @field_validator('default_format')
    @classmethod
    def validate_format(cls, v: str) -> str:
        valid = {"human", "json", "table", "csv"}
        if v not in valid:
            raise ValueError(f"Invalid output format. Must be one of: {valid}")
        return v

    class Config:
        # Enable writing to TOML
        use_enum_values = True
        json_encoders = {
            SecretStr: lambda v: v.get_secret_value(),  # For encryption, never logged
            Path: str
        }
```

**TOML Example**:

```toml
[tool.proxywhirl]
rotation_strategy = "round-robin"
timeout = 30
default_format = "json"
encrypt_credentials = true

[[tool.proxywhirl.proxies]]
url = "http://proxy1.example.com:8080"
username = "user1"
password = "***ENCRYPTED***"

[[tool.proxywhirl.proxies]]
url = "socks5://proxy2.example.com:1080"
```

**Validation Rules**:

- URLs MUST match `Proxy.url` validation from core library
- Credentials encrypted with Fernet before writing (if `encrypt_credentials=true`)
- File paths resolved relative to config file location
- Invalid strategies/formats raise clear error messages

---

## 2. Command Context Model

**Purpose**: Shared state passed between Typer commands via `typer.Context`

**Schema**:

```python
from proxywhirl import ProxyRotator
from proxywhirl.storage import StorageBackend
from dataclasses import dataclass
from typing import Optional

@dataclass
class CommandContext:
    """Shared state for CLI commands (stored in typer.Context.obj)."""
    
    config: CLIConfig
    rotator: Optional[ProxyRotator] = None  # Lazy-initialized
    storage: Optional[StorageBackend] = None  # Lazy-initialized
    output_format: str = "human"  # Overridden by --format flag
    verbose: bool = False  # Overridden by --verbose flag
    config_path: Optional[Path] = None  # Which config file was loaded
    
    def get_rotator(self) -> ProxyRotator:
        """Lazy-initialize rotator from config."""
        if self.rotator is None:
            # Convert CLIConfig.proxies to Proxy objects
            proxies = [
                Proxy(
                    url=p.url,
                    username=p.username.get_secret_value() if p.username else None,
                    password=p.password.get_secret_value() if p.password else None
                )
                for p in self.config.proxies
            ]
            self.rotator = ProxyRotator(
                proxies=proxies,
                strategy=self.config.rotation_strategy
            )
        return self.rotator
```

**Usage in Typer Commands**:

```python
import typer

app = typer.Typer()

@app.callback()
def main(ctx: typer.Context) -> None:
    """ProxyWhirl CLI - Proxy rotation made simple."""
    config = load_config()  # From config.py
    ctx.obj = CommandContext(config=config)

@app.command()
def pool_list(ctx: typer.Context) -> None:
    rotator = ctx.obj.get_rotator()
    # ... use rotator
```

---

## 3. Output Models

**Purpose**: Structured data for rendering in different formats (JSON, table, CSV)

### RequestResult

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class RequestResult(BaseModel):
    """Result of HTTP request made through proxy."""
    
    url: str
    method: str  # GET, POST, PUT, DELETE, etc.
    status_code: int
    elapsed_ms: float
    proxy_used: str  # URL of proxy that succeeded
    attempts: int  # Number of retries before success
    headers: Dict[str, str]  # Response headers
    body: Optional[str] = None  # Response body (truncated if large)
    error: Optional[str] = None  # Error message if failed
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300
```

### ProxyStatus

```python
class ProxyStatus(BaseModel):
    """Status of a single proxy in the pool."""
    
    url: str
    health: str  # "healthy", "degraded", "failed", "unknown"
    last_check: Optional[datetime] = None
    response_time_ms: Optional[float] = None
    success_rate: float = 0.0  # 0.0-1.0
    total_requests: int = 0
    failed_requests: int = 0
    is_active: bool = True
```

### PoolSummary

```python
class PoolSummary(BaseModel):
    """Summary of entire proxy pool."""
    
    total_proxies: int
    healthy: int
    degraded: int
    failed: int
    rotation_strategy: str
    current_index: int  # For round-robin
    proxies: List[ProxyStatus]
```

---

## 4. Lock File Model

**Purpose**: Track concurrent CLI execution to prevent corruption

**File Location**: `{config_dir}/.proxywhirl.lock`

**Schema**:

```python
import os
import time

@dataclass
class LockFileData:
    """Data stored in lock file."""
    
    pid: int = Field(default_factory=os.getpid)
    hostname: str = Field(default_factory=lambda: os.uname().nodename)
    command: str = ""  # e.g., "proxywhirl pool add"
    timestamp: float = Field(default_factory=time.time)
    
    def is_stale(self, timeout_seconds: int = 300) -> bool:
        """Check if lock is stale (process died or timeout exceeded)."""
        # Check if process still running
        try:
            os.kill(self.pid, 0)  # Doesn't kill, just checks existence
            return False
        except OSError:
            return True  # Process doesn't exist
    
    def to_json(self) -> str:
        """Serialize to JSON for lock file."""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, data: str) -> "LockFileData":
        """Deserialize from JSON."""
        return cls(**json.loads(data))
```

---

## 5. Relationships

```text
┌─────────────────┐
│   CLIConfig     │──┬──> ProxyConfig (1..N)
│  (TOML file)    │  │
└─────────────────┘  │
         │           │
         v           v
┌─────────────────────────────┐
│   CommandContext            │
│  (Typer context object)     │──> ProxyRotator (lazy init)
│                             │──> StorageBackend (lazy init)
└─────────────────────────────┘
         │
         v
┌─────────────────┐
│  RequestResult  │──> OutputRenderer ──> human/json/table/csv
│  PoolSummary    │
│  ProxyStatus    │
└─────────────────┘

Lock File (independent, file-based coordination)
```

**Key Relationships**:

- `CLIConfig` → `ProxyConfig[]`: One config contains many proxy definitions
- `CommandContext` → `ProxyRotator`: Lazy-initialized from config proxies
- `CommandContext` → `StorageBackend`: Lazy-initialized from config storage settings
- `RequestResult`, `PoolSummary` → `OutputRenderer`: Models rendered in multiple formats
- `LockFileData`: Independent file-based coordination (no in-memory relationships)

---

## 6. State Transitions

### Configuration Lifecycle

```text
1. Discovery:  Find config file (project → user → defaults)
2. Load:       Parse TOML → CLIConfig model
3. Validate:   Pydantic validation (URLs, strategies, formats)
4. Decrypt:    Decrypt credentials using Fernet (if encrypted)
5. Use:        Pass to CommandContext
6. Modify:     Update via `config set` command
7. Encrypt:    Encrypt credentials before writing
8. Save:       Write back to TOML (atomic rename)
```

### Lock Lifecycle

```text
1. Acquire:    Create lock file with PID, timestamp
2. Validate:   Check if stale (process dead or timeout)
3. Hold:       Execute command
4. Release:    Delete lock file (automatic via context manager)
5. Cleanup:    Remove stale locks on startup
```

### Request Lifecycle

```text
1. Parse:      CLI args → RequestConfig
2. Select:     Get proxy from rotator
3. Execute:    Make HTTP request through proxy
4. Retry:      On failure, select next proxy
5. Record:     Create RequestResult
6. Render:     Format output (human/json/table/csv)
7. Exit:       Return exit code (0=success, 1=error)
```

---

## Summary

**New Models** (not in core library):

- `CLIConfig`: Persistent TOML configuration
- `ProxyConfig`: Single proxy definition (with credentials)
- `CommandContext`: Shared CLI state (Typer context object)
- `RequestResult`: HTTP request result for output
- `ProxyStatus`: Proxy health for pool listings
- `PoolSummary`: Aggregate pool statistics
- `LockFileData`: Concurrency lock metadata

**Reused Models** (from core library):

- `Proxy`: Core proxy model (from `proxywhirl.models`)
- `ProxyRotator`: Rotation logic (from `proxywhirl.rotator`)
- `StorageBackend`: Storage interface (from `proxywhirl.storage`)

**Validation**:

- All URLs validated by core `Proxy` model
- TOML parsing errors handled with clear messages
- Invalid strategies/formats rejected at config load time
- Credentials encrypted/decrypted transparently
