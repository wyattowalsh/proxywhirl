"""API Models Package

Pydantic models for API request/response validation and documentation.
"""

from .auth import Token, TokenData, UserResponse
from .requests import (
    ConfigUpdateRequest,
    FetchProxiesRequest,
    ValidationRequest,
)
from .responses import (
    CacheStatsResponse,
    ConfigResponse,
    ErrorResponse,
    FetchProxiesResponse,
    HealthResponse,
    ProxyListResponse,
    ProxyResponse,
    ValidationResponse,
)

__all__ = [
    # Authentication models
    "Token",
    "TokenData", 
    "UserResponse",
    # Request models
    "FetchProxiesRequest",
    "ValidationRequest",
    "ConfigUpdateRequest",
    # Response models
    "ProxyResponse",
    "ProxyListResponse",
    "FetchProxiesResponse", 
    "ValidationResponse",
    "HealthResponse",
    "CacheStatsResponse",
    "ConfigResponse",
    "ErrorResponse",
]
