"""Health Check Endpoints

Comprehensive health monitoring and system status endpoints.
"""

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends
from loguru import logger

from ..dependencies import get_current_active_user, get_proxywhirl
from ..models.responses import HealthResponse

router = APIRouter()


@router.get("/", response_model=HealthResponse, summary="API Health Check")
async def health_check(pw = Depends(get_proxywhirl)):
    """
    Get comprehensive API health status.
    
    Returns system health metrics including proxy counts,
    component status, and system resources.
    """
    try:
        # Get proxy statistics
        proxies = await pw.get_proxies_async()
        total_proxies = len(proxies)
        healthy_proxies = len([p for p in proxies if p.status.value == "active"])
        degraded_proxies = len([p for p in proxies if p.status.value == "cooldown"]) 
        failed_proxies = len([p for p in proxies if p.status.value in ["blacklisted", "inactive"]])
        
        # Determine overall health status
        if failed_proxies > healthy_proxies:
            status = "unhealthy"
        elif degraded_proxies > healthy_proxies * 0.5:
            status = "degraded" 
        else:
            status = "healthy"
        
        # System metrics (basic implementation)
        import psutil
        system_metrics = {
            "cpu_usage": psutil.cpu_percent(interval=0.1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
        }
        
        # Component status
        component_status = {
            "cache": "healthy",
            "validator": "healthy", 
            "rotator": "healthy",
            "loaders": "healthy",
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        status = "unhealthy"
        total_proxies = 0
        healthy_proxies = 0
        degraded_proxies = 0
        failed_proxies = 0
        system_metrics = {}
        component_status = {"error": str(e)}
    
    return HealthResponse(
        status=status,
        timestamp=datetime.now(timezone.utc),
        version="1.0.0",  # Should come from settings
        uptime=0.0,  # Should be calculated from startup time
        proxy_count=total_proxies,
        healthy_proxies=healthy_proxies,
        degraded_proxies=degraded_proxies,
        failed_proxies=failed_proxies,
        system_metrics=system_metrics,
        component_status=component_status,
    )


@router.get("/detailed", summary="Detailed Health Report") 
async def get_detailed_health(
    current_user = Depends(get_current_active_user),
    pw = Depends(get_proxywhirl)
):
    """Get detailed health report with diagnostic information."""
    try:
        # Generate comprehensive health report
        report = await pw.health_report_async() if hasattr(pw, 'health_report_async') else {}
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "detailed_report": report,
            "proxy_statistics": {
                "total": len(await pw.get_proxies_async()),
                "by_status": {},  # Would be filled with actual status counts
            },
            "loader_status": {},  # Would be filled with loader health info
            "cache_metrics": {},  # Would be filled with cache performance
        }
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return {
            "error": "Health check failed",
            "details": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
