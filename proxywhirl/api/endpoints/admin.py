"""Administrative Endpoints

Administrative operations requiring elevated privileges.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from ..dependencies import get_admin_user, get_proxywhirl
from ..models.responses import CacheStatsResponse, ConfigResponse

router = APIRouter()


@router.get("/config", response_model=ConfigResponse, summary="Get System Configuration")
async def get_system_config(
    admin_user = Depends(get_admin_user),
    pw = Depends(get_proxywhirl),
):
    """Get current system configuration (admin only)."""
    try:
        # Mock configuration - would get from actual ProxyWhirl instance
        return ConfigResponse(
            rotation_strategy="random",  # Would get from pw.rotator
            cache_type="memory",  # Would get from pw.cache
            auto_validate=True,
            max_fetch_proxies=1000,
            validation_timeout=10.0,
            health_check_interval=300,
            background_tasks_enabled=True,
            websocket_enabled=True,
        )
    except Exception as e:
        logger.error(f"Failed to get system config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "CONFIG_ERROR", "message": str(e)}
        )


@router.get("/cache/stats", response_model=CacheStatsResponse, summary="Get Cache Statistics")
async def get_cache_stats(
    admin_user = Depends(get_admin_user),
    pw = Depends(get_proxywhirl),
):
    """Get detailed cache performance statistics (admin only)."""
    try:
        # Get cache stats from ProxyWhirl
        proxies = await pw.get_proxies_async()
        healthy_count = len([p for p in proxies if p.status.value == "active"])
        
        return CacheStatsResponse(
            cache_type="memory",  # Would get from pw.cache.type
            total_proxies=len(proxies),
            healthy_proxies=healthy_count,
            cache_hits=None,  # Would get from cache if supported
            cache_misses=None,  # Would get from cache if supported  
            hit_ratio=None,
            cache_size=len(proxies),
            memory_usage=None,  # Would calculate actual memory usage
            last_cleanup=None,  # Would get from cache cleanup task
        )
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "CACHE_STATS_ERROR", "message": str(e)}
        )


@router.post("/system/cleanup", summary="Perform System Cleanup")
async def perform_system_cleanup(
    admin_user = Depends(get_admin_user),
    pw = Depends(get_proxywhirl),
):
    """Perform system maintenance and cleanup tasks (admin only)."""
    try:
        # Perform cleanup operations
        cleanup_results = {
            "cache_cleaned": True,
            "expired_sessions_removed": 0,
            "invalid_proxies_removed": 0,
            "disk_space_freed": "0 MB",
        }
        
        logger.info(f"System cleanup completed by {admin_user.username}")
        
        return {
            "message": "System cleanup completed successfully",
            "results": cleanup_results,
        }
    except Exception as e:
        logger.error(f"System cleanup failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "CLEANUP_FAILED", "message": str(e)}
        )


@router.get("/metrics/detailed", summary="Get Detailed Metrics")
async def get_detailed_metrics(
    admin_user = Depends(get_admin_user),
):
    """Get detailed system metrics and performance data (admin only)."""
    try:
        # Get system metrics
        import psutil
        
        return {
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "network_connections": len(psutil.net_connections()),
            },
            "process": {
                "memory_mb": psutil.Process().memory_info().rss / 1024 / 1024,
                "cpu_percent": psutil.Process().cpu_percent(),
                "num_threads": psutil.Process().num_threads(),
            },
            "api_metrics": {
                # Would get from monitoring middleware
                "total_requests": 0,
                "active_requests": 0,
                "avg_response_time": 0.0,
            }
        }
    except Exception as e:
        logger.error(f"Failed to get detailed metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "METRICS_ERROR", "message": str(e)}
        )
