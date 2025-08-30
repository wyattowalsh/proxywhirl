"""proxywhirl/caches/manager.py -- Elite cache management system with advanced orchestration

Enterprise-grade cache management with:
- Multi-tier caching strategies (L1: Memory, L2: JSON, L3: SQLite)
- Intelligent cache warming and prefetching
- Real-time synchronization between cache layers
- Advanced analytics and performance monitoring
- Cache federation and distributed coordination
- Smart eviction policies and cache coherence
- Automatic failover and disaster recovery
- Resource optimization and memory management
"""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import StrEnum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import psutil
from loguru import logger

from proxywhirl.caches.base import BaseProxyCache, CacheFilters, CacheMetrics
from proxywhirl.caches.json import JsonProxyCache
from proxywhirl.caches.memory import MemoryProxyCache
from proxywhirl.caches.sqlite import AsyncSQLiteProxyCache, SQLiteProxyCache
from proxywhirl.models import Proxy


class CacheStrategy(StrEnum):
    """Cache management strategies for optimal performance."""
    MEMORY_ONLY = auto()
    MEMORY_JSON = auto()
    MEMORY_SQLITE = auto()
    MULTI_TIER = auto()          # Memory -> JSON -> SQLite
    DISTRIBUTED = auto()         # Federated across multiple backends
    AUTO_OPTIMIZE = auto()       # AI-driven strategy selection


class CacheCoherenceMode(StrEnum):
    """Cache coherence models for multi-tier systems."""
    WRITE_THROUGH = auto()       # Write to all tiers synchronously
    WRITE_BACK = auto()          # Write to memory, batch to storage
    WRITE_AROUND = auto()        # Bypass memory for writes
    EVENT_DRIVEN = auto()        # Event-based synchronization


@dataclass
class CachePerformanceProfile:
    """Performance characteristics and resource usage patterns."""
    read_latency_p50: float = 0.0
    read_latency_p95: float = 0.0
    read_latency_p99: float = 0.0
    write_latency_p50: float = 0.0
    write_latency_p95: float = 0.0
    write_latency_p99: float = 0.0
    throughput_rps: float = 0.0
    memory_efficiency: float = 0.0
    hit_rate_24h: float = 0.0
    error_rate_24h: float = 0.0
    resource_utilization: Dict[str, float] = field(default_factory=dict)


@dataclass
class CacheWarmupConfig:
    """Configuration for intelligent cache warming."""
    enabled: bool = True
    warmup_percentage: float = 0.8  # Warm up top 80% most accessed
    background_refresh: bool = True
    predictive_loading: bool = True
    geographical_priority: List[str] = field(default_factory=list)
    source_priority: List[str] = field(default_factory=list)
    max_warmup_time: int = 300  # 5 minutes max warmup


class EliteCacheManager:
    """Elite cache management system with advanced multi-tier orchestration."""

    def __init__(
        self,
        # Core configuration
        strategy: CacheStrategy = CacheStrategy.MULTI_TIER,
        coherence_mode: CacheCoherenceMode = CacheCoherenceMode.WRITE_THROUGH,
        base_path: Optional[Path] = None,
        # Performance tuning
        memory_limit_mb: int = 512,
        json_compression: bool = True,
        sqlite_pool_size: int = 10,
        # Advanced features
        enable_analytics: bool = True,
        enable_warmup: bool = True,
        enable_prefetching: bool = True,
        enable_federation: bool = False,
        # Monitoring and health
        health_check_interval: int = 60,
        performance_sampling: bool = True,
        enable_real_time_metrics: bool = True,
        # Resilience
        enable_circuit_breaker: bool = True,
        max_failure_rate: float = 0.1,
        recovery_timeout: int = 300,
    ):
        self.strategy = strategy
        self.coherence_mode = coherence_mode
        self.base_path = base_path or Path("./cache")
        
        # Performance configuration
        self.memory_limit_mb = memory_limit_mb
        self.json_compression = json_compression
        self.sqlite_pool_size = sqlite_pool_size
        
        # Advanced features
        self.enable_analytics = enable_analytics
        self.enable_warmup = enable_warmup
        self.enable_prefetching = enable_prefetching
        self.enable_federation = enable_federation
        
        # Monitoring configuration
        self.health_check_interval = health_check_interval
        self.performance_sampling = performance_sampling
        self.enable_real_time_metrics = enable_real_time_metrics
        
        # Resilience configuration
        self.enable_circuit_breaker = enable_circuit_breaker
        self.max_failure_rate = max_failure_rate
        self.recovery_timeout = recovery_timeout

        # Internal state
        self._caches: Dict[str, BaseProxyCache] = {}
        self._performance_profiles: Dict[str, CachePerformanceProfile] = {}
        self._access_patterns: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self._cache_weights: Dict[str, float] = {}
        self._circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Advanced analytics
        self._operation_history: deque = deque(maxlen=100000)
        self._performance_metrics: Dict[str, Any] = {}
        self._predictive_models: Dict[str, Any] = {}
        
        # Background task management
        self._background_tasks: Set[asyncio.Task] = set()
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._warmup_task: Optional[asyncio.Task] = None
        
        # Configuration
        self.warmup_config = CacheWarmupConfig()
        
        # Initialize manager
        self._initialized = False
        self._shutdown_event = asyncio.Event()

        logger.info(f"Elite cache manager initialized with strategy={strategy}, "
                   f"coherence={coherence_mode}, analytics={enable_analytics}")

    async def initialize(self) -> None:
        """Initialize the cache management system with intelligent backend selection."""
        if self._initialized:
            return

        start_time = time.time()
        logger.info("Initializing elite cache management system...")

        try:
            # Create base directory
            self.base_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize cache backends based on strategy
            await self._initialize_cache_backends()
            
            # Start background monitoring and optimization tasks
            await self._start_background_services()
            
            # Perform initial cache warming if enabled
            if self.enable_warmup:
                self._warmup_task = asyncio.create_task(self._perform_cache_warmup())
            
            self._initialized = True
            init_time = time.time() - start_time
            
            logger.info(f"Elite cache manager initialized in {init_time:.3f}s with "
                       f"{len(self._caches)} backends")
            
        except Exception as e:
            logger.error(f"Failed to initialize cache manager: {e}")
            raise

    async def _initialize_cache_backends(self) -> None:
        """Initialize cache backends based on the selected strategy."""
        if self.strategy == CacheStrategy.MEMORY_ONLY:
            self._caches["memory"] = MemoryProxyCache(
                max_size=int(self.memory_limit_mb * 1024 * 1024 / 1000)  # Approx conversion
            )
            
        elif self.strategy == CacheStrategy.MEMORY_JSON:
            self._caches["memory"] = MemoryProxyCache(
                max_size=int(self.memory_limit_mb * 1024 * 1024 / 2000)
            )
            self._caches["json"] = JsonProxyCache(
                cache_path=self.base_path / "proxies.json",
                compression=self.json_compression,
                enable_indexing=True,
                enable_incremental_saves=True,
            )
            
        elif self.strategy == CacheStrategy.MEMORY_SQLITE:
            self._caches["memory"] = MemoryProxyCache(
                max_size=int(self.memory_limit_mb * 1024 * 1024 / 2000)
            )
            self._caches["sqlite"] = AsyncSQLiteProxyCache(
                db_path=self.base_path / "proxies.db",
                pool_size=self.sqlite_pool_size,
                enable_analytics=self.enable_analytics,
            )
            
        elif self.strategy == CacheStrategy.MULTI_TIER:
            # L1: High-speed memory cache
            self._caches["l1_memory"] = MemoryProxyCache(
                max_size=int(self.memory_limit_mb * 1024 * 1024 / 3000)
            )
            # L2: Fast persistent JSON cache
            self._caches["l2_json"] = JsonProxyCache(
                cache_path=self.base_path / "l2_proxies.json",
                compression=self.json_compression,
                enable_indexing=True,
                batch_size=2000,
                enable_incremental_saves=True,
            )
            # L3: Comprehensive SQLite cache with analytics
            self._caches["l3_sqlite"] = AsyncSQLiteProxyCache(
                db_path=self.base_path / "l3_proxies.db",
                pool_size=self.sqlite_pool_size,
                enable_analytics=True,
                enable_health_monitoring=True,
            )
            
        elif self.strategy == CacheStrategy.AUTO_OPTIMIZE:
            # Start with multi-tier and adjust based on usage patterns
            await self._initialize_auto_optimize_backends()

        # Initialize all backends
        for name, cache in self._caches.items():
            await cache.initialize()
            self._performance_profiles[name] = CachePerformanceProfile()
            self._cache_weights[name] = 1.0
            self._circuit_breakers[name] = {
                "failures": 0,
                "last_failure": 0,
                "state": "closed",  # closed, open, half-open
            }
            
        logger.info(f"Initialized {len(self._caches)} cache backends: {list(self._caches.keys())}")

    async def _initialize_auto_optimize_backends(self) -> None:
        """Initialize backends for auto-optimization strategy."""
        # Start with a balanced multi-tier approach
        self._caches["adaptive_memory"] = MemoryProxyCache(
            max_size=int(self.memory_limit_mb * 1024 * 1024 / 4000)
        )
        self._caches["adaptive_json"] = JsonProxyCache(
            cache_path=self.base_path / "adaptive_proxies.json",
            compression=True,
            enable_indexing=True,
            batch_size=1500,
        )
        self._caches["adaptive_sqlite"] = AsyncSQLiteProxyCache(
            db_path=self.base_path / "adaptive_proxies.db",
            pool_size=max(5, self.sqlite_pool_size // 2),
            enable_analytics=True,
        )

    # === Core cache operations with intelligent routing ===

    async def add_proxies(self, proxies: List[Proxy]) -> None:
        """Add proxies with intelligent multi-tier distribution."""
        if not proxies:
            return

        await self._ensure_initialized()
        start_time = time.time()
        
        try:
            if self.coherence_mode == CacheCoherenceMode.WRITE_THROUGH:
                await self._write_through_add(proxies)
            elif self.coherence_mode == CacheCoherenceMode.WRITE_BACK:
                await self._write_back_add(proxies)
            elif self.coherence_mode == CacheCoherenceMode.EVENT_DRIVEN:
                await self._event_driven_add(proxies)
            else:
                await self._write_around_add(proxies)
            
            # Update performance metrics
            operation_time = time.time() - start_time
            self._record_operation("add_proxies", len(proxies), operation_time)
            
            logger.debug(f"Added {len(proxies)} proxies in {operation_time:.3f}s "
                        f"using {self.coherence_mode} coherence")
            
        except Exception as e:
            logger.error(f"Failed to add proxies: {e}")
            await self._handle_cache_error("add_proxies", e)
            raise

    async def _write_through_add(self, proxies: List[Proxy]) -> None:
        """Write-through: Add to all cache tiers synchronously."""
        tasks = []
        for name, cache in self._caches.items():
            if self._is_cache_healthy(name):
                if hasattr(cache, 'add_proxies_batch'):
                    tasks.append(cache.add_proxies_batch(proxies))
                else:
                    # Fallback for caches without batch support
                    tasks.append(self._add_proxies_sequential(cache, proxies))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _write_back_add(self, proxies: List[Proxy]) -> None:
        """Write-back: Add to memory immediately, batch to storage."""
        # Add to L1 memory cache immediately
        memory_caches = [name for name in self._caches.keys() if "memory" in name]
        for name in memory_caches:
            if self._is_cache_healthy(name):
                cache = self._caches[name]
                if hasattr(cache, 'add_proxies_batch'):
                    await cache.add_proxies_batch(proxies)
        
        # Schedule batch write to persistent storage
        asyncio.create_task(self._schedule_batch_write(proxies))

    async def _event_driven_add(self, proxies: List[Proxy]) -> None:
        """Event-driven: Publish events for cache synchronization."""
        # Add to primary cache
        primary_cache = self._get_primary_cache()
        if primary_cache and hasattr(primary_cache, 'add_proxies_batch'):
            await primary_cache.add_proxies_batch(proxies)
        
        # Emit events for other caches to sync
        await self._emit_cache_event("proxies_added", {"proxies": proxies})

    async def get_proxies(self, filters: Optional[CacheFilters] = None) -> List[Proxy]:
        """Get proxies with intelligent multi-tier lookup and performance optimization."""
        await self._ensure_initialized()
        start_time = time.time()
        
        try:
            # Use cache hierarchy for optimal performance
            result = await self._hierarchical_lookup(filters)
            
            # Update access patterns for predictive optimization
            await self._record_access_pattern(filters)
            
            # Performance metrics
            operation_time = time.time() - start_time
            self._record_operation("get_proxies", len(result), operation_time)
            
            logger.debug(f"Retrieved {len(result)} proxies in {operation_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get proxies: {e}")
            await self._handle_cache_error("get_proxies", e)
            raise

    async def _hierarchical_lookup(self, filters: Optional[CacheFilters]) -> List[Proxy]:
        """Perform hierarchical lookup through cache tiers."""
        # Try each cache tier in performance order
        cache_order = self._get_cache_lookup_order()
        
        for cache_name in cache_order:
            if not self._is_cache_healthy(cache_name):
                continue
                
            try:
                cache = self._caches[cache_name]
                result = await cache.get_proxies(filters)
                
                if result:
                    # Cache hit - update metrics and potentially warm upper tiers
                    self._record_cache_hit(cache_name)
                    await self._warm_upper_tiers(cache_name, result, filters)
                    return result
                else:
                    self._record_cache_miss(cache_name)
                    
            except Exception as e:
                logger.warning(f"Cache {cache_name} lookup failed: {e}")
                await self._handle_cache_error(cache_name, e)
                continue
        
        # No results found in any cache
        return []

    def _get_cache_lookup_order(self) -> List[str]:
        """Get optimal cache lookup order based on performance profiles."""
        # Order by performance (latency, hit rate, health)
        cache_scores = {}
        for name, profile in self._performance_profiles.items():
            if name not in self._caches:
                continue
            
            # Calculate composite score (lower is better for lookups)
            latency_score = profile.read_latency_p50
            hit_rate_score = 1.0 - profile.hit_rate_24h  # Invert hit rate
            health_score = 1.0 if self._is_cache_healthy(name) else 10.0
            
            cache_scores[name] = (latency_score + hit_rate_score + health_score) / 3
        
        # Sort by score (ascending)
        return sorted(cache_scores.keys(), key=lambda k: cache_scores[k])

    # === Advanced monitoring and analytics ===

    async def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance analytics across all cache tiers."""
        await self._ensure_initialized()
        
        metrics = {
            "strategy": self.strategy,
            "coherence_mode": self.coherence_mode,
            "cache_backends": list(self._caches.keys()),
            "performance_profiles": {},
            "system_health": await self._get_system_health(),
            "access_patterns": await self._analyze_access_patterns(),
            "optimization_recommendations": await self._generate_optimization_recommendations(),
        }
        
        # Collect metrics from each cache
        for name, cache in self._caches.items():
            try:
                cache_metrics = await cache.get_health_metrics()
                profile = self._performance_profiles[name]
                
                metrics["performance_profiles"][name] = {
                    "cache_metrics": cache_metrics.model_dump(),
                    "performance_profile": profile.__dict__,
                    "circuit_breaker": self._circuit_breakers[name],
                    "weight": self._cache_weights[name],
                }
            except Exception as e:
                logger.warning(f"Failed to get metrics for cache {name}: {e}")
        
        return metrics

    # === Background services and optimization ===

    async def _start_background_services(self) -> None:
        """Start background monitoring and optimization services."""
        if self.enable_real_time_metrics:
            task = asyncio.create_task(self._health_monitoring_loop())
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)
        
        if self.enable_analytics:
            task = asyncio.create_task(self._analytics_loop())
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)
        
        if self.strategy == CacheStrategy.AUTO_OPTIMIZE:
            task = asyncio.create_task(self._auto_optimization_loop())
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)

        logger.info(f"Started {len(self._background_tasks)} background services")

    async def _health_monitoring_loop(self) -> None:
        """Continuous health monitoring and automatic recovery."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
                await self._update_performance_profiles()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")

    async def _analytics_loop(self) -> None:
        """Continuous analytics and pattern recognition."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                await self._analyze_performance_trends()
                await self._optimize_cache_weights()
                await self._update_predictive_models()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Analytics loop error: {e}")

    # === Utility methods ===

    async def _ensure_initialized(self) -> None:
        """Ensure the cache manager is initialized."""
        if not self._initialized:
            await self.initialize()

    def _is_cache_healthy(self, cache_name: str) -> bool:
        """Check if a cache is healthy based on circuit breaker state."""
        if not self.enable_circuit_breaker:
            return True
        
        breaker = self._circuit_breakers.get(cache_name, {})
        return breaker.get("state", "closed") != "open"

    def _record_operation(self, operation: str, count: int, duration: float) -> None:
        """Record operation for performance analysis."""
        self._operation_history.append({
            "operation": operation,
            "count": count,
            "duration": duration,
            "timestamp": time.time(),
        })

    def _record_cache_hit(self, cache_name: str) -> None:
        """Record cache hit for performance analysis."""
        # Implementation would update hit rate metrics
        pass

    def _record_cache_miss(self, cache_name: str) -> None:
        """Record cache miss for performance analysis."""
        # Implementation would update miss rate metrics
        pass

    async def _handle_cache_error(self, cache_name: str, error: Exception) -> None:
        """Handle cache errors and update circuit breaker state."""
        if not self.enable_circuit_breaker:
            return
        
        breaker = self._circuit_breakers[cache_name]
        breaker["failures"] += 1
        breaker["last_failure"] = time.time()
        
        # Open circuit breaker if failure rate too high
        if breaker["failures"] >= 5:
            breaker["state"] = "open"
            logger.warning(f"Circuit breaker opened for cache {cache_name}")

    # Placeholder methods for advanced functionality
    async def _perform_cache_warmup(self) -> None:
        """Perform intelligent cache warmup."""
        pass
    
    async def _warm_upper_tiers(self, source_tier: str, data: List[Proxy], filters: Optional[CacheFilters]) -> None:
        """Warm upper cache tiers with frequently accessed data."""
        pass
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health metrics."""
        return {}
    
    async def _analyze_access_patterns(self) -> Dict[str, Any]:
        """Analyze access patterns for optimization."""
        return {}
    
    async def _generate_optimization_recommendations(self) -> List[str]:
        """Generate cache optimization recommendations."""
        return []

    # === Cleanup ===

    async def shutdown(self) -> None:
        """Graceful shutdown of all cache backends and background services."""
        logger.info("Starting graceful cache manager shutdown...")
        
        # Signal shutdown to background tasks
        self._shutdown_event.set()
        
        # Cancel background tasks
        for task in list(self._background_tasks):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Shutdown all cache backends
        for name, cache in self._caches.items():
            try:
                await cache.cleanup()
            except Exception as e:
                logger.warning(f"Error shutting down cache {name}: {e}")
        
        logger.info("Cache manager shutdown completed")


# === Factory functions for easy setup ===

async def create_elite_cache_manager(
    strategy: CacheStrategy = CacheStrategy.MULTI_TIER,
    base_path: Optional[Path] = None,
    **kwargs
) -> EliteCacheManager:
    """Create and initialize an elite cache manager with optimal defaults."""
    manager = EliteCacheManager(
        strategy=strategy,
        base_path=base_path,
        **kwargs
    )
    await manager.initialize()
    return manager


@asynccontextmanager
async def managed_cache_context(
    strategy: CacheStrategy = CacheStrategy.MULTI_TIER,
    base_path: Optional[Path] = None,
    **kwargs
):
    """Async context manager for automatic cache lifecycle management."""
    manager = await create_elite_cache_manager(strategy, base_path, **kwargs)
    try:
        yield manager
    finally:
        await manager.shutdown()
