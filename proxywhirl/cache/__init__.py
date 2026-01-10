"""
Multi-tier caching functionality for ProxyWhirl.

This subpackage provides L1 (memory), L2 (disk), and L3 (SQLite) caching tiers
with credential encryption and comprehensive cache management.

Modules:
    manager: Main CacheManager class for multi-tier caching
    crypto: Credential encryption for secure caching
    models: Pydantic models for cache entries and configuration
    tiers: Cache tier implementations (Memory, Disk, SQLite)
"""

from __future__ import annotations

from .crypto import CredentialEncryptor
from .manager import CacheManager
from .models import (
    CacheConfig,
    CacheEntry,
    CacheStatistics,
    CacheTierConfig,
    CacheTierType,
    HealthStatus,
)
from .tiers import DiskCacheTier, MemoryCacheTier, SQLiteCacheTier

__all__ = [
    # Main manager
    "CacheManager",
    # Models
    "CacheConfig",
    "CacheEntry",
    "CacheStatistics",
    "CacheTierConfig",
    "CacheTierType",
    "HealthStatus",
    # Tier implementations
    "MemoryCacheTier",
    "DiskCacheTier",
    "SQLiteCacheTier",
    # Utilities
    "CredentialEncryptor",
]
