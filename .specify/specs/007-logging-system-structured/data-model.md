# Data Model: Structured Logging System

**Feature**: 007-logging-system-structured

This document outlines the key data models and entities for the structured logging system, based on the requirements in `spec.md`.

## 1. LogConfiguration (Pydantic Model)

**Description**: Defines the entire logging setup. Loaded from environment variables and/or a configuration file using `pydantic-settings`.

**Module**: `proxywhirl.logging_config`

```python
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

class LogHandlerConfig(BaseModel):
    """Configuration for a single log handler (sink)."""
    type: Literal["console", "file", "syslog", "http"]
    level: str = "INFO"
    format: str = "default"  # or "json", "logfmt"
    # File-specific settings
    path: Optional[str] = None
    rotation: Optional[str] = None
    retention: Optional[str] = None
    # Remote-specific settings
    url: Optional[str] = None

class LogConfiguration(BaseSettings):
    """Main logging configuration model."""
    level: str = "INFO"
    async_logging: bool = True
    queue_size: int = 1000
    drop_on_full: bool = True
    handlers: list[LogHandlerConfig] = Field(default_factory=list)

    class Config:
        env_prefix = "PROXYWHIRL_LOG_"
```

**Validation Rules**:
- `level` must be a valid log level (DEBUG, INFO, etc.).
- `queue_size` must be a positive integer.
- `handlers.type` must be one of the supported types.
- `path` is required if `type` is `file`.
- `url` is required if `type` is `http` or `syslog`.

## 2. LogEntry (Structured Log Schema)

**Description**: The JSON schema for a single log entry. This is not a Pydantic model in the application code, but a representation of the structured output.

**Format**: JSON

```json
{
  "timestamp": "2025-11-01T14:30:00.123Z",
  "level": "INFO",
  "message": "Proxy selected successfully",
  "context": {
    "request_id": "req-xyz-123",
    "operation": "proxy_selection",
    "proxy_url": "http://user:pass@proxy.example.com:8080",
    "source": "source_a"
  },
  "app_name": "proxywhirl",
  "process_id": 12345,
  "thread_name": "MainThread"
}
```

**Fields**:
- **timestamp**: ISO 8601 timestamp.
- **level**: Log level (e.g., `INFO`).
- **message**: The log message string.
- **context**: A dictionary of contextual metadata (from `loguru.bind()`).
- **app_name**: The application name (static).
- **process_id**: The process ID.
- **thread_name**: The thread name.

## 3. Log Statistics (Metrics)

**Description**: Metrics related to logging performance and reliability.

**Entities**:
- **Drop Counter**: An atomic counter (`int`) tracking the number of log entries dropped because the asynchronous queue was full.
- **Queue Size Gauge**: A gauge (`int`) reporting the current number of items in the logging queue.
- **Handler Errors Counter**: A counter for each handler tracking the number of times it failed to write a log entry.