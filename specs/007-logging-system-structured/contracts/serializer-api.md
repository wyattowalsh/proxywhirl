# Serializer API Contract

**Feature**: 007-logging-system-structured  
**Purpose**: Define the contract for custom JSON serializers used in structured logging

## Overview

Custom serializers handle non-JSON-serializable Python objects (datetime, Enum, SecretStr, etc.) and apply redaction policies.

## Serializer Function Contract

### Function Signature

```python
from typing import Any

def serializer(obj: Any) -> Any:
    """
    Convert Python object to JSON-serializable representation.
    
    Args:
        obj: Any Python object
    
    Returns:
        JSON-serializable value (str, int, float, bool, list, dict, None)
    
    Raises:
        TypeError: If object cannot be serialized (caller handles fallback)
    """
    pass
```

### Required Behavior

1. **MUST return JSON-serializable types**:
   - `str`, `int`, `float`, `bool`, `None`
   - `list` of JSON-serializable values
   - `dict` with string keys and JSON-serializable values

2. **MUST handle common Python types**:
   - `datetime.datetime` → ISO 8601 string
   - `datetime.date` → ISO 8601 string
   - `enum.Enum` → enum value
   - `uuid.UUID` → string representation
   - `pathlib.Path` → string representation
   - `decimal.Decimal` → float or string

3. **MUST apply redaction**:
   - `pydantic.SecretStr` → `"***REDACTED***"`
   - Detect sensitive field names → redact values
   - Preserve URL structure (redact credentials only)

4. **MUST be deterministic**:
   - Same input → same output
   - No random values
   - No timestamps in serialization

5. **MUST NOT raise exceptions**:
   - Fallback to `str(obj)` for unknown types
   - Log warning for unhandled types
   - Never crash logging pipeline

## Standard Implementation

```python
from typing import Any
from datetime import datetime, date
from enum import Enum
from uuid import UUID
from pathlib import Path
from decimal import Decimal
from pydantic import SecretStr
import re

def standard_serializer(obj: Any) -> Any:
    """Standard serializer for proxywhirl logging."""
    
    # Datetime objects
    if isinstance(obj, datetime):
        return obj.isoformat()
    
    if isinstance(obj, date):
        return obj.isoformat()
    
    # Enums
    if isinstance(obj, Enum):
        return obj.value
    
    # UUID
    if isinstance(obj, UUID):
        return str(obj)
    
    # Path
    if isinstance(obj, Path):
        return str(obj)
    
    # Decimal (preserve precision)
    if isinstance(obj, Decimal):
        return str(obj)
    
    # SecretStr (REDACT)
    if isinstance(obj, SecretStr):
        return "***REDACTED***"
    
    # Pydantic models
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json")
    
    # Sets (convert to list)
    if isinstance(obj, set):
        return list(obj)
    
    # Bytes (base64 encode)
    if isinstance(obj, bytes):
        import base64
        return base64.b64encode(obj).decode("utf-8")
    
    # Fallback to str
    return str(obj)
```

## Redaction Policies

### Field Name Detection

```python
SENSITIVE_FIELD_PATTERNS = [
    re.compile(r'password', re.IGNORECASE),
    re.compile(r'token', re.IGNORECASE),
    re.compile(r'secret', re.IGNORECASE),
    re.compile(r'api[_-]?key', re.IGNORECASE),
    re.compile(r'auth', re.IGNORECASE),
    re.compile(r'credential', re.IGNORECASE),
]

def is_sensitive_field(field_name: str) -> bool:
    """Check if field name indicates sensitive data."""
    return any(pattern.search(field_name) for pattern in SENSITIVE_FIELD_PATTERNS)
```

### Value Redaction

```python
def redact_value(value: Any, field_name: str) -> Any:
    """
    Redact sensitive values based on field name or type.
    
    Args:
        value: Original value
        field_name: Field name for context
    
    Returns:
        Redacted value or original if not sensitive
    """
    # SecretStr always redacted
    if isinstance(value, SecretStr):
        return "***REDACTED***"
    
    # Check field name
    if is_sensitive_field(field_name):
        return "***REDACTED***"
    
    # URL with credentials
    if isinstance(value, str) and value.startswith(("http://", "https://")):
        return redact_url_credentials(value)
    
    # Return original if not sensitive
    return value

def redact_url_credentials(url: str) -> str:
    """
    Redact credentials from URL while preserving structure.
    
    Example:
        http://user:pass@proxy.com:8080 → http://user:***@proxy.com:8080
    """
    import re
    pattern = re.compile(r'(://[^:]+:)([^@]+)(@)')
    return pattern.sub(r'\1***\3', url)
```

### Dict Serialization with Redaction

```python
def serialize_dict(obj: dict, redact: bool = True) -> dict:
    """
    Serialize dict with optional redaction.
    
    Args:
        obj: Dictionary to serialize
        redact: Whether to apply redaction policies
    
    Returns:
        JSON-serializable dict
    """
    result = {}
    for key, value in obj.items():
        # Redact sensitive fields
        if redact:
            value = redact_value(value, field_name=key)
        
        # Recursively serialize
        if isinstance(value, dict):
            result[key] = serialize_dict(value, redact=redact)
        elif isinstance(value, list):
            result[key] = [
                serialize_dict(item, redact=redact) if isinstance(item, dict)
                else standard_serializer(item)
                for item in value
            ]
        else:
            result[key] = standard_serializer(value)
    
    return result
```

## Integration with Loguru

### Method 1: Custom Format Function

```python
import json
from loguru import logger

def json_formatter(record: dict) -> str:
    """Format log record as JSON with custom serialization."""
    serialized = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
        **record["extra"],  # Include context fields
    }
    
    # Serialize with redaction
    return json.dumps(
        serialize_dict(serialized, redact=True),
        default=standard_serializer,
        ensure_ascii=False
    ) + "\n"

# Register formatter
logger.add(
    sink=sys.stdout,
    format=json_formatter,
    serialize=False  # Use custom formatter instead
)
```

### Method 2: Serialize with Default Parameter

```python
import json
from loguru import logger

logger.add(
    sink=sys.stdout,
    serialize=True,
    format=lambda record: json.dumps(
        record,
        default=standard_serializer,
        ensure_ascii=False
    )
)
```

## Testing Contract

### Serializer Tests

```python
import pytest
from datetime import datetime
from enum import Enum
from pydantic import SecretStr
from proxywhirl.serializers import standard_serializer

def test_datetime_serialization():
    """Datetime serializes to ISO 8601."""
    dt = datetime(2025, 11, 1, 12, 34, 56, 789000)
    result = standard_serializer(dt)
    assert isinstance(result, str)
    assert result == "2025-11-01T12:34:56.789000"

def test_enum_serialization():
    """Enum serializes to value."""
    class Color(Enum):
        RED = "red"
        BLUE = "blue"
    
    result = standard_serializer(Color.RED)
    assert result == "red"

def test_secret_str_redaction():
    """SecretStr always redacted."""
    secret = SecretStr("my-password-123")
    result = standard_serializer(secret)
    assert result == "***REDACTED***"
    assert "password" not in result

def test_url_credential_redaction():
    """URL credentials redacted."""
    url = "http://user:pass@proxy.com:8080"
    result = redact_url_credentials(url)
    assert result == "http://user:***@proxy.com:8080"
    assert "pass" not in result

def test_fallback_to_str():
    """Unknown types fallback to str()."""
    class CustomClass:
        def __str__(self):
            return "custom"
    
    result = standard_serializer(CustomClass())
    assert result == "custom"
```

### Redaction Tests

```python
def test_sensitive_field_detection():
    """Sensitive field names detected."""
    assert is_sensitive_field("password")
    assert is_sensitive_field("api_key")
    assert is_sensitive_field("secret_token")
    assert not is_sensitive_field("username")

def test_dict_redaction():
    """Dicts with sensitive fields redacted."""
    data = {
        "username": "alice",
        "password": "secret123",
        "api_key": "xyz789",
        "email": "alice@example.com"
    }
    
    result = serialize_dict(data, redact=True)
    
    assert result["username"] == "alice"
    assert result["password"] == "***REDACTED***"
    assert result["api_key"] == "***REDACTED***"
    assert result["email"] == "alice@example.com"
```

## Performance Contract

- **Serialization**: <5ms per log entry (P95)
- **Redaction Check**: <1ms per field
- **Memory**: <1KB per serialized entry
- **CPU**: <1% overhead for logging at 1000 entries/sec

## Error Handling

### Serialization Failure

```python
def safe_serializer(obj: Any) -> Any:
    """Serializer with error handling."""
    try:
        return standard_serializer(obj)
    except Exception as e:
        # Log warning (to stderr to avoid recursion)
        import sys
        print(f"Serialization failed for {type(obj)}: {e}", file=sys.stderr)
        
        # Fallback to str()
        try:
            return str(obj)
        except Exception:
            return f"<unserializable: {type(obj).__name__}>"
```

### Circular Reference Detection

```python
def serialize_with_cycle_detection(obj: Any, seen: set | None = None) -> Any:
    """Serialize with circular reference detection."""
    if seen is None:
        seen = set()
    
    obj_id = id(obj)
    
    # Detect cycles
    if obj_id in seen:
        return f"<circular: {type(obj).__name__}>"
    
    # For dicts and lists, track visited objects
    if isinstance(obj, dict):
        seen.add(obj_id)
        result = {k: serialize_with_cycle_detection(v, seen) for k, v in obj.items()}
        seen.remove(obj_id)
        return result
    
    if isinstance(obj, list):
        seen.add(obj_id)
        result = [serialize_with_cycle_detection(item, seen) for item in obj]
        seen.remove(obj_id)
        return result
    
    # Use standard serializer for other types
    return standard_serializer(obj)
```

## Custom Serializer Extension

### Adding Custom Types

```python
def custom_serializer(obj: Any) -> Any:
    """Extended serializer with custom types."""
    
    # Custom type: Proxy
    if isinstance(obj, Proxy):
        return {
            "url": redact_url_credentials(obj.url),
            "source": obj.source,
            "weight": obj.weight
        }
    
    # Custom type: Strategy
    if isinstance(obj, RotationStrategy):
        return obj.name
    
    # Fallback to standard serializer
    return standard_serializer(obj)
```

### Registration

```python
# Use custom serializer for all handlers
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

## Best Practices

1. **Always use redaction** for production logs
2. **Test serializers** with property-based testing (Hypothesis)
3. **Handle cycles** to prevent infinite recursion
4. **Log serialization failures** to stderr (avoid recursion)
5. **Benchmark serializers** to ensure <5ms target
6. **Use standard_serializer** as base, extend for custom types
7. **Validate JSON output** with schema validation tests
