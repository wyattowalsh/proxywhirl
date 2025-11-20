# Handler API Contract

**Feature**: 007-logging-system-structured  
**Purpose**: Define the contract for log handlers and custom serializers

## Handler Interface

### Loguru Handler Configuration

All handlers are configured via `logger.add()` with the following contract:

```python
from loguru import logger
from typing import Callable, Any

def configure_handler(
    sink: str | Callable,
    *,
    level: str = "INFO",
    format: str | Callable = "{message}",
    filter: Callable[[dict], bool] | None = None,
    colorize: bool = False,
    serialize: bool = False,
    backtrace: bool = True,
    diagnose: bool = True,
    enqueue: bool = False,
    catch: bool = True,
    rotation: str | int | None = None,
    retention: str | int | None = None,
    compression: str | None = None,
    **kwargs: Any
) -> int:
    """
    Configure a loguru handler.
    
    Args:
        sink: Destination (file path, sys.stdout, callable)
        level: Minimum log level for this handler
        format: Format string or formatter function
        filter: Optional filter function (return True to log)
        colorize: Enable ANSI color codes
        serialize: Enable JSON serialization
        backtrace: Include full traceback on errors
        diagnose: Include variable values in traceback
        enqueue: Enable async logging via background thread
        catch: Catch exceptions during logging
        rotation: When to rotate logs (size, time)
        retention: How long to keep logs
        compression: Compression format for rotated logs
        **kwargs: Additional handler-specific options
    
    Returns:
        Handler ID (for later removal)
    """
    return logger.add(
        sink=sink,
        level=level,
        format=format,
        filter=filter,
        colorize=colorize,
        serialize=serialize,
        backtrace=backtrace,
        diagnose=diagnose,
        enqueue=enqueue,
        catch=catch,
        rotation=rotation,
        retention=retention,
        compression=compression,
        **kwargs
    )
```

### Handler Types

#### 1. Console Handler

```python
# Basic console handler
handler_id = logger.add(
    sink=sys.stdout,
    level="INFO",
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# JSON console handler
handler_id = logger.add(
    sink=sys.stdout,
    level="INFO",
    serialize=True,  # JSON output
    enqueue=True     # Async logging
)
```

**Contract**:
- MUST write to stdout or stderr
- MUST support colorization (if terminal supports it)
- MUST support both text and JSON formats
- MUST NOT block on write (if enqueue=True)

#### 2. File Handler

```python
# Rotating file handler
handler_id = logger.add(
    sink="logs/proxywhirl.log",
    level="DEBUG",
    rotation="100 MB",      # Rotate when 100MB
    retention="30 days",    # Keep 30 days
    compression="gz",       # Compress rotated files
    serialize=True,         # JSON format
    enqueue=True,          # Async logging
    format="{message}"     # Raw message (already JSON)
)
```

**Contract**:
- MUST create parent directories if missing
- MUST rotate files atomically (no data loss)
- MUST respect retention policy (delete old files)
- MUST compress rotated files if configured
- MUST handle file system errors gracefully

#### 3. Syslog Handler

```python
import socket

# Unix socket syslog
handler_id = logger.add(
    sink=socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM),
    level="INFO",
    format="{message}",  # logfmt or JSON
    filter=lambda record: record["level"].no >= 20  # INFO+
)

# Network syslog (RFC 5424)
handler_id = logger.add(
    sink=("syslog.example.com", 514),
    level="INFO",
    format="<{level.no}>{time:MMM DD HH:mm:ss} {name}[{process.id}]: {message}"
)
```

**Contract**:
- MUST format messages per RFC 5424 (if network syslog)
- MUST include facility and severity codes
- MUST handle socket errors without crashing
- MUST support both Unix sockets and network sockets

#### 4. HTTP Handler

```python
import httpx

def http_sink(message: dict) -> None:
    """Send log entry to HTTP endpoint."""
    try:
        httpx.post(
            "https://logs.example.com/ingest",
            json=message.record,
            timeout=5.0,
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        # Fallback: log to stderr
        import sys
        print(f"HTTP logging failed: {e}", file=sys.stderr)

handler_id = logger.add(
    sink=http_sink,
    level="INFO",
    serialize=True,
    enqueue=True,  # MUST use async for network I/O
    catch=True     # Prevent exceptions from bubbling
)
```

**Contract**:
- MUST use async logging (enqueue=True)
- MUST have timeout (<10 seconds)
- MUST NOT crash on network errors
- MUST fallback to stderr on failure
- MUST include authentication if required

## Custom Serializer Contract

### Serializer Function Signature

```python
from typing import Any
from datetime import datetime
from enum import Enum
from pydantic import SecretStr

def custom_serializer(obj: Any) -> Any:
    """
    Serialize objects for JSON logging.
    
    Args:
        obj: Python object to serialize
    
    Returns:
        JSON-serializable representation
    
    Raises:
        TypeError: If object cannot be serialized (fallback to str(obj))
    """
    # Handle datetime
    if isinstance(obj, datetime):
        return obj.isoformat()
    
    # Handle enums
    if isinstance(obj, Enum):
        return obj.value
    
    # Handle SecretStr (REDACT)
    if isinstance(obj, SecretStr):
        return "***REDACTED***"
    
    # Handle Pydantic models
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    
    # Fallback
    return str(obj)
```

### Serializer Registration

```python
import json
from loguru import logger

# Configure logger with custom serializer
logger.add(
    sink=sys.stdout,
    serialize=True,
    format=lambda record: json.dumps(
        record,
        default=custom_serializer,
        ensure_ascii=False
    )
)
```

## Redaction Filter Contract

### Filter Function Signature

```python
import re
from typing import Pattern

def redaction_filter(record: dict) -> bool:
    """
    Redact sensitive data from log records.
    
    Args:
        record: Loguru record dict
    
    Returns:
        True (always log, but modify record in-place)
    """
    # Patterns to redact
    patterns: list[tuple[Pattern, str]] = [
        (re.compile(r'password["\s:=]+([^"\s,}]+)', re.IGNORECASE), 'password="***"'),
        (re.compile(r'token["\s:=]+([^"\s,}]+)', re.IGNORECASE), 'token="***"'),
        (re.compile(r'api[_-]?key["\s:=]+([^"\s,}]+)', re.IGNORECASE), 'api_key="***"'),
        (re.compile(r'Bearer\s+[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), 'Bearer ***'),
    ]
    
    # Redact message
    message = record["message"]
    for pattern, replacement in patterns:
        message = pattern.sub(replacement, message)
    record["message"] = message
    
    # Redact extra fields
    if "extra" in record:
        for key, value in record["extra"].items():
            if isinstance(value, str):
                for pattern, replacement in patterns:
                    value = pattern.sub(replacement, value)
                record["extra"][key] = value
    
    return True  # Always log
```

### Filter Registration

```python
logger.add(
    sink=sys.stdout,
    filter=redaction_filter,
    serialize=True
)
```

## Context Binding Contract

### Context Manager Interface

```python
from contextvars import ContextVar
from contextlib import contextmanager
from typing import Iterator
import uuid

log_context: ContextVar[dict] = ContextVar("log_context", default={})

@contextmanager
def context_logger(**kwargs: Any) -> Iterator[None]:
    """
    Bind context to logger for duration of context manager.
    
    Args:
        **kwargs: Context fields to bind
    
    Yields:
        None
    
    Example:
        with context_logger(request_id=str(uuid.uuid4()), operation="proxy_selection"):
            logger.info("Selecting proxy")  # Includes context
    """
    # Set context
    token = log_context.set(kwargs)
    
    # Bind to logger
    with logger.contextualize(**kwargs):
        try:
            yield
        finally:
            # Reset context
            log_context.reset(token)
```

### Usage Contract

```python
# Basic usage
with context_logger(request_id="12345", operation="health_check"):
    logger.info("Starting health check")  # Includes request_id and operation

# Nested contexts (inner overrides outer)
with context_logger(request_id="12345"):
    logger.info("Outer context")
    
    with context_logger(operation="proxy_selection"):
        logger.info("Inner context")  # Has both request_id and operation

# Manual binding (no context manager)
logger.bind(request_id="12345", operation="health_check").info("Manual binding")
```

## Bounded Queue Contract

### Queue Wrapper Interface

```python
from queue import Queue, Full
from threading import Lock
from proxywhirl.models import DropCounter

class BoundedQueueWithCounter:
    """Bounded queue that tracks dropped entries."""
    
    def __init__(self, maxsize: int, handler_id: str) -> None:
        self.queue: Queue = Queue(maxsize=maxsize)
        self.handler_id = handler_id
        self.drop_counter = DropCounter.get_instance()
        self.lock = Lock()
    
    def put(self, item: Any, block: bool = False) -> None:
        """
        Put item in queue, drop oldest if full.
        
        Args:
            item: Log record to enqueue
            block: Whether to block (always False for drop-oldest policy)
        """
        try:
            self.queue.put_nowait(item)
        except Full:
            # Drop oldest entry
            with self.lock:
                try:
                    self.queue.get_nowait()  # Remove oldest
                    self.queue.put_nowait(item)  # Add new
                except Exception:
                    # Failed to drop, count it
                    self.drop_counter.record_drop(self.handler_id)
    
    def get(self, block: bool = True, timeout: float | None = None) -> Any:
        """Get item from queue."""
        return self.queue.get(block=block, timeout=timeout)
```

### Integration with Loguru

```python
# Custom enqueue function
def custom_enqueue(message: dict, queue: BoundedQueueWithCounter) -> None:
    """Enqueue with drop tracking."""
    queue.put(message)

# Configure handler with custom queue
custom_queue = BoundedQueueWithCounter(maxsize=1000, handler_id="file_handler")
logger.add(
    sink="logs/app.log",
    enqueue=True,
    # Note: Loguru doesn't directly support custom queues,
    # so we use a wrapper sink function
)
```

## Handler Lifecycle Contract

### Adding Handlers

```python
# Add handler
handler_id = logger.add(sink=sys.stdout, level="INFO")

# Returns integer ID for later reference
assert isinstance(handler_id, int)
```

### Removing Handlers

```python
# Remove specific handler
logger.remove(handler_id)

# Remove all handlers
logger.remove()

# Remove handlers matching predicate
logger.remove(lambda h: h["sink"] == sys.stdout)
```

### Runtime Reconfiguration

```python
# Atomic handler replacement
old_handler_id = logger.add(sink="logs/old.log")

# Add new handler
new_handler_id = logger.add(sink="logs/new.log")

# Remove old handler (no dropped logs)
logger.remove(old_handler_id)
```

## Error Handling Contract

### Handler Failure Behavior

1. **Console Handler Fails**:
   - Fallback to stderr
   - Log warning about failure
   - Continue logging to other handlers

2. **File Handler Fails** (disk full, permissions):
   - Fallback to stderr
   - Log warning about failure
   - Retry after 60 seconds

3. **Network Handler Fails** (HTTP, syslog):
   - Fallback to stderr
   - Log warning about failure
   - Continue logging to other handlers
   - DO NOT retry (avoid blocking)

4. **All Handlers Fail**:
   - Fallback to stderr
   - Log CRITICAL warning
   - Application continues (logging never crashes app)

### Exception Handling

```python
# Handlers MUST use catch=True
logger.add(
    sink=my_sink,
    catch=True,  # Catch exceptions in sink
    enqueue=True  # Async (prevents blocking)
)

# Custom sinks MUST handle exceptions
def safe_http_sink(message: dict) -> None:
    try:
        send_to_http(message)
    except Exception as e:
        # Log to stderr, don't crash
        import sys
        print(f"HTTP sink failed: {e}", file=sys.stderr)
```

## Performance Contract

- **Handler Addition**: <10ms per handler
- **Log Entry Processing**: <1ms average (async mode)
- **Queue Operations**: <0.1ms per put/get
- **Serialization**: <5ms per entry (JSON)
- **File Rotation**: <100ms (atomic, no lost logs)
- **Configuration Reload**: <1 second (SC-002)

## Thread Safety Contract

- All handler operations MUST be thread-safe
- Queue operations MUST be thread-safe
- DropCounter MUST use locks for concurrent access
- Logger.bind() is thread-local (safe for concurrent use)
- Context variables are thread-safe (contextvars)
