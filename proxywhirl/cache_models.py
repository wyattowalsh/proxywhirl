"""
Re-exports from cache.models for backward compatibility.

DEPRECATED: This module exists only for backward compatibility.
New code should import directly from proxywhirl.cache.models instead.

All cache model definitions have been consolidated into proxywhirl/cache/models.py.
This file now serves as a compatibility shim to avoid breaking existing imports.
"""

from __future__ import annotations

from proxywhirl.cache.models import (
    CacheConfig,
    CacheEntry,
    CacheStatistics,
    CacheTierConfig,
    CacheTierType,
    HealthStatus,
    L2BackendType,
    TierStatistics,
)

__all__ = [
    "HealthStatus",
    "L2BackendType",
    "CacheTierType",
    "CacheEntry",
    "CacheTierConfig",
    "CacheConfig",
    "TierStatistics",
    "CacheStatistics",
]
