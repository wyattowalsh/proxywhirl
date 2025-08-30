"""Response Models

Pydantic models for API responses with comprehensive coverage from api.py integration.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ...caches.config import CacheType
from ...models import (
    Proxy,
    ProxyStatus,
    RotationStrategy,
    ValidationErrorType,
)


class ErrorResponse(BaseModel):
    """Standardized error response model."""
    
    error_code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Additional error context and debugging information"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Error occurrence timestamp"
    )
    request_id: Optional[str] = Field(None, description="Request correlation ID")


class ProxyResponse(BaseModel):
    """Enhanced proxy response with comprehensive health and quality metrics."""
    
    model_config = ConfigDict(from_attributes=True)
    
    proxy: Proxy
    quality_score: float = Field(
        ge=0.0, 
        le=1.0, 
        description="Overall proxy quality score (0.0-1.0)"
    )
    last_used: Optional[datetime] = Field(
        default=None, 
        description="Timestamp when proxy was last used"
    )
    consecutive_failures: int = Field(
        ge=0, 
        description="Count of consecutive validation failures"
    )
    is_available: bool = Field(
        description="Whether proxy is currently available for use"
    )
    response_time_avg: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Average response time in seconds"
    )
    success_rate: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Success rate over recent attempts"
    )


class ProxyListResponse(BaseModel):
    """Paginated proxy list response with metadata."""
    
    proxies: List[ProxyResponse]
    total: int = Field(ge=0, description="Total number of proxies matching filters")
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, le=1000, description="Number of items per page")
    has_next: bool = Field(description="Whether there are more pages available")
    has_previous: bool = Field(description="Whether there are previous pages available")
    total_pages: int = Field(ge=0, description="Total number of pages")
    filters_applied: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Summary of applied filters"
    )


class FetchProxiesResponse(BaseModel):
    """Response model for fetch proxies background operation."""
    
    task_id: str = Field(..., description="Background task ID for progress tracking")
    message: str = Field(..., description="Operation status message")
    estimated_duration: int = Field(
        ge=0, 
        description="Estimated completion time in seconds"
    )
    sources_queued: int = Field(
        ge=0,
        description="Number of proxy sources queued for processing"
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Operation start timestamp"
    )


class ValidationResponse(BaseModel):
    """Response model for proxy validation operations."""
    
    valid_proxies: int = Field(ge=0, description="Number of valid proxies found")
    invalid_proxies: int = Field(ge=0, description="Number of invalid proxies found")
    success_rate: float = Field(
        ge=0.0, 
        le=1.0, 
        description="Overall validation success rate"
    )
    avg_response_time: Optional[float] = Field(
        default=None, 
        ge=0.0,
        description="Average response time for valid proxies in seconds"
    )
    errors: Dict[ValidationErrorType, int] = Field(
        default_factory=dict, 
        description="Error counts categorized by error type"
    )
    duration: float = Field(
        ge=0.0,
        description="Total validation operation duration in seconds"
    )
    concurrent_validations: int = Field(
        ge=1,
        description="Number of concurrent validation operations used"
    )


class HealthResponse(BaseModel):
    """Comprehensive API health status response."""
    
    status: str = Field(..., description="Overall health status (healthy/degraded/unhealthy)")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Health check execution timestamp"
    )
    version: str = Field(..., description="ProxyWhirl version")
    uptime: float = Field(ge=0.0, description="API uptime in seconds")
    proxy_count: int = Field(ge=0, description="Total cached proxies")
    healthy_proxies: int = Field(ge=0, description="Number of healthy/active proxies")
    degraded_proxies: int = Field(ge=0, description="Number of degraded proxies")
    failed_proxies: int = Field(ge=0, description="Number of failed proxies")
    system_metrics: Optional[Dict[str, Any]] = Field(
        default=None,
        description="System resource metrics (CPU, memory, disk)"
    )
    component_status: Optional[Dict[str, str]] = Field(
        default=None,
        description="Status of individual system components"
    )


class CacheStatsResponse(BaseModel):
    """Cache system statistics and performance metrics."""
    
    cache_type: CacheType = Field(..., description="Active cache backend type")
    total_proxies: int = Field(ge=0, description="Total proxies stored in cache")
    healthy_proxies: int = Field(ge=0, description="Number of healthy cached proxies")
    cache_hits: Optional[int] = Field(
        default=None, 
        ge=0,
        description="Cache hit count (if supported by backend)"
    )
    cache_misses: Optional[int] = Field(
        default=None, 
        ge=0,
        description="Cache miss count (if supported by backend)"
    )
    hit_ratio: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Cache hit ratio (hits / (hits + misses))"
    )
    cache_size: Optional[int] = Field(
        default=None, 
        ge=0,
        description="Current cache size in items"
    )
    memory_usage: Optional[int] = Field(
        default=None,
        ge=0,
        description="Cache memory usage in bytes"
    )
    last_cleanup: Optional[datetime] = Field(
        default=None,
        description="Timestamp of last cache cleanup operation"
    )


class ConfigResponse(BaseModel):
    """Current system configuration response."""
    
    rotation_strategy: RotationStrategy = Field(..., description="Active rotation strategy")
    cache_type: CacheType = Field(..., description="Active cache backend")
    auto_validate: bool = Field(..., description="Automatic validation enabled status")
    max_fetch_proxies: Optional[int] = Field(
        None, 
        description="Maximum proxies fetched per operation"
    )
    validation_timeout: float = Field(
        gt=0.0,
        description="Default proxy validation timeout in seconds"
    )
    health_check_interval: int = Field(
        gt=0,
        description="Health check interval in seconds"
    )
    background_tasks_enabled: bool = Field(
        default=True,
        description="Whether background tasks are enabled"
    )
    websocket_enabled: bool = Field(
        default=True,
        description="Whether WebSocket endpoints are enabled"
    )


class TaskStatusResponse(BaseModel):
    """Background task status and progress information."""
    
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Task status (pending/running/completed/failed)")
    progress: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Task completion progress (0.0-1.0)"
    )
    message: Optional[str] = Field(None, description="Current task status message")
    created_at: datetime = Field(..., description="Task creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Task start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Task completion timestamp")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result data")
    error: Optional[str] = Field(None, description="Error message if task failed")
    estimated_remaining: Optional[float] = Field(
        None,
        ge=0.0,
        description="Estimated remaining time in seconds"
    )


class ErrorDetail(BaseModel):
    """Detailed error information for enhanced error handling."""
    
    error_code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Additional error context"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class TaskListResponse(BaseModel):
    """Response model for listing background tasks."""
    
    tasks: List[TaskStatusResponse]
    total: int = Field(ge=0, description="Total number of tasks")
    active_tasks: int = Field(ge=0, description="Number of currently running tasks")
    completed_tasks: int = Field(ge=0, description="Number of completed tasks")
    failed_tasks: int = Field(ge=0, description="Number of failed tasks")
