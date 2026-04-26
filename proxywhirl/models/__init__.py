"""
Data models for ProxyWhirl using Pydantic v2.

This package provides all the core data models for proxy management,
including proxies, pools, sessions, and health monitoring.
"""

from proxywhirl.models.core import (
    BootstrapConfig,
    # Config models
    CircuitBreakerConfig,
    # Protocols and utilities
    HealthMonitor,
    # Enums
    HealthStatus,
    # Status/result models
    PoolSummary,
    # Core models
    Proxy,
    ProxyChain,
    ProxyConfiguration,
    ProxyCredentials,
    ProxyFormat,
    ProxyPool,
    ProxySource,
    ProxySourceConfig,
    ProxyStatus,
    RenderMode,
    RequestResult,
    SelectionContext,
    Session,
    SourceStats,
    StorageBackend,
    StrategyConfig,
    ValidationLevel,
)

__all__ = [
    # Enums
    "HealthStatus",
    "ProxyFormat",
    "ProxySource",
    "RenderMode",
    "ValidationLevel",
    # Config models
    "BootstrapConfig",
    "CircuitBreakerConfig",
    "ProxyConfiguration",
    "ProxySourceConfig",
    "SourceStats",
    "StrategyConfig",
    # Core models
    "Proxy",
    "ProxyChain",
    "ProxyCredentials",
    "ProxyPool",
    "SelectionContext",
    "Session",
    # Protocols and utilities
    "HealthMonitor",
    "StorageBackend",
    # Status/result models
    "PoolSummary",
    "ProxyStatus",
    "RequestResult",
]
