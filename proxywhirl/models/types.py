"""proxywhirl/models/types.py -- Annotated types and validators for ProxyWhirl

This module contains advanced Pydantic v2 annotated types with validation,
serialization, and JSON schema generation for type safety and documentation.

Features:
- High-precision numeric types with validation
- Custom serializers for JSON output
- JSON schema generation for API documentation
- Performance-optimized validation patterns
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field, PlainSerializer, WithJsonSchema
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated


def _to_upper(v: Optional[str]) -> Optional[str]:
    """Convert country code to uppercase and validate format."""
    if v is None:
        return None
    upper = str(v).upper()  # Remove unnecessary isinstance check
    # Validate pattern after conversion
    if len(upper) != 2 or not upper.isalpha():
        raise ValueError(f"Country code must be 2 letters, got: {v}")
    return upper


CountryCode = Annotated[Optional[str], AfterValidator(_to_upper)]


# === Advanced Annotated Types with Pydantic v2 Patterns ===

PortNumber = Annotated[
    int,
    Field(ge=1, le=65535),
    WithJsonSchema(
        {
            "example": 8080,
            "description": "Valid TCP port number (1-65535)",
            "type": "integer",
            "minimum": 1,
            "maximum": 65535,
        }
    ),
]

ResponseTimeSeconds = Annotated[
    float,
    Field(ge=0.001, le=300.0),
    AfterValidator(lambda x: round(x, 3)),  # Precision control
    PlainSerializer(lambda x: f"{x:.3f}", when_used="json"),
    WithJsonSchema(
        {
            "example": 1.234,
            "description": "Response time in seconds (0.001-300.0)",
            "type": "number",
            "minimum": 0.001,
            "maximum": 300.0,
        }
    ),
]

QualityScore = Annotated[
    float,
    Field(ge=0.0, le=1.0),
    AfterValidator(lambda x: round(x, 4)),  # High precision for quality
    WithJsonSchema(
        {
            "example": 0.8750,
            "description": "Quality score from 0.0 (poor) to 1.0 (excellent)",
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
        }
    ),
]

SuccessRate = Annotated[
    float,
    Field(ge=0.0, le=1.0),
    AfterValidator(lambda x: round(x, 3)),
    PlainSerializer(lambda x: f"{x*100:.1f}%", when_used="json"),
    WithJsonSchema(
        {
            "example": 0.95,
            "description": "Success rate from 0.0 to 1.0 (serialized as percentage)",
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
        }
    ),
]

UptimePercentage = Annotated[
    float,
    Field(ge=0.0, le=100.0),
    AfterValidator(lambda x: round(x, 2)),
    WithJsonSchema(
        {
            "example": 99.95,
            "description": "Uptime percentage (0.0-100.0)",
            "type": "number",
            "minimum": 0.0,
            "maximum": 100.0,
        }
    ),
]
