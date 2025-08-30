"""Request Models

Pydantic models for API request validation.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class FetchProxiesRequest(BaseModel):
    """Request model for fetching proxies with validation options."""
    
    validate_proxies: bool = Field(
        default=True, 
        description="Whether to validate proxies after fetching"
    )
    max_proxies: Optional[int] = Field(
        default=None, 
        ge=1, 
        le=10000, 
        description="Maximum number of proxies to fetch"
    )
    sources: Optional[List[str]] = Field(
        default=None, 
        description="Specific proxy sources to use (empty = all)"
    )
    timeout: Optional[float] = Field(
        default=30.0,
        ge=5.0,
        le=300.0,
        description="Timeout for fetch operation in seconds"
    )


class ValidationRequest(BaseModel):
    """Request model for proxy validation operations."""
    
    proxy_ids: Optional[List[str]] = Field(
        default=None, 
        description="Specific proxy IDs to validate (empty = all)"
    )
    max_proxies: Optional[int] = Field(
        default=None, 
        ge=1, 
        le=1000, 
        description="Maximum number of proxies to validate"
    )
    target_urls: Optional[List[str]] = Field(
        default=None, 
        description="Custom target URLs for validation testing"
    )
    timeout: Optional[float] = Field(
        default=10.0,
        ge=1.0,
        le=60.0,
        description="Timeout per proxy validation in seconds"
    )
    concurrent_limit: Optional[int] = Field(
        default=50,
        ge=1,
        le=200,
        description="Maximum concurrent validations"
    )


class ConfigUpdateRequest(BaseModel):
    """Request model for configuration updates."""
    
    rotation_strategy: Optional[str] = Field(
        None, 
        description="Proxy rotation strategy"
    )
    cache_type: Optional[str] = Field(
        None,
        description="Cache backend type"
    )
    auto_validate: Optional[bool] = Field(
        None,
        description="Enable automatic proxy validation"
    )
    max_fetch_proxies: Optional[int] = Field(
        None,
        ge=1,
        le=50000,
        description="Maximum proxies to fetch per operation"
    )
    validation_timeout: Optional[float] = Field(
        None,
        ge=1.0,
        le=120.0,
        description="Default validation timeout"
    )
    health_check_interval: Optional[int] = Field(
        None,
        ge=60,
        le=3600,
        description="Health check interval in seconds"
    )
