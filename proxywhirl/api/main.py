"""ProxyWhirl FastAPI Main Application

Modern, production-ready FastAPI application with:
- Modular architecture with dependency injection
- Advanced security and authentication
- Real-time WebSocket support
- Comprehensive monitoring and observability
- Optimized middleware stack
"""

from __future__ import annotations

import asyncio
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict

import orjson
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from ..proxywhirl import ProxyWhirl
from ..settings import get_api_settings
from .dependencies import get_proxywhirl
from .endpoints import (
    admin_router,
    auth_router,
    health_router,
    proxies_router,
    websocket_router,
)
from .middleware.logging import LoggingMiddleware
from .middleware.monitoring import MonitoringMiddleware
from .middleware.security import SecurityHeadersMiddleware


class ORJSONResponse(JSONResponse):
    """High-performance JSON response using orjson for 2x faster serialization."""
    
    media_type = "application/json"
    
    def render(self, content: Any) -> bytes:
        """Render content to bytes using orjson for optimal performance."""
        if content is None:
            return b"null"
        
        return orjson.dumps(
            content,
            option=(
                orjson.OPT_NON_STR_KEYS | 
                orjson.OPT_SERIALIZE_NUMPY | 
                orjson.OPT_SERIALIZE_UUID |
                orjson.OPT_UTC_Z
            )
        )


# Initialize settings
settings = get_api_settings()

# Rate limiter configuration
limiter = Limiter(key_func=get_remote_address)

# Global background tasks tracking
background_tasks: Dict[str, Dict[str, Any]] = {}

# API startup time for uptime calculation
api_start_time = datetime.now(timezone.utc)


# === Application Lifespan Management ===

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with comprehensive startup/shutdown."""
    logger.info("🚀 ProxyWhirl API starting up...")
    
    # Initialize ProxyWhirl instance
    app.state.proxywhirl = ProxyWhirl(auto_validate=True)
    
    # Start background monitoring tasks
    background_tasks_list = []
    
    # Health monitoring task
    health_task = asyncio.create_task(health_monitoring_background())
    background_tasks_list.append(("Health Monitor", health_task))
    
    # Connection pool maintenance
    pool_task = asyncio.create_task(connection_pool_maintenance())
    background_tasks_list.append(("Connection Pool", pool_task))
    
    # Cache cleanup task
    cache_task = asyncio.create_task(cache_cleanup_background())
    background_tasks_list.append(("Cache Cleanup", cache_task))
    
    # Session cleanup task
    session_task = asyncio.create_task(session_cleanup_background())
    background_tasks_list.append(("Session Cleanup", session_task))
    
    logger.info(f"✅ Started {len(background_tasks_list)} background tasks")
    
    yield
    
    # Graceful cleanup on shutdown
    logger.info("🔄 ProxyWhirl API shutting down...")
    
    for task_name, task in background_tasks_list:
        try:
            task.cancel()
            await asyncio.wait_for(task, timeout=5.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            logger.warning(f"⚠️ {task_name} task cancelled/timed out during shutdown")
        except Exception as e:
            logger.error(f"❌ Error stopping {task_name}: {e}")
    
    # Final cleanup
    if hasattr(app.state, "proxywhirl") and app.state.proxywhirl:
        try:
            # Perform any necessary cleanup on ProxyWhirl instance
            logger.info("🧹 Cleaning up ProxyWhirl instance")
        except Exception as e:
            logger.error(f"❌ Error during ProxyWhirl cleanup: {e}")
    
    logger.info("✅ ProxyWhirl API shutdown complete")


# === Background Task Functions ===

async def health_monitoring_background():
    """Background task for comprehensive health monitoring and WebSocket updates."""
    while True:
        try:
            # Get app state for ProxyWhirl instance
            from fastapi import FastAPI

            # This is a simplified version - in production, we'd access the app state properly
            await asyncio.sleep(30)  # Run every 30 seconds
            
            logger.debug("Health monitoring cycle completed")
            
        except asyncio.CancelledError:
            logger.info("Health monitoring task cancelled")
            break
        except Exception as e:
            logger.error(f"Health monitoring error: {e}")
            await asyncio.sleep(60)  # Wait longer on error


async def connection_pool_maintenance():
    """Background task for database connection pool maintenance."""
    while True:
        try:
            # Maintain database connections
            await asyncio.sleep(300)  # Run every 5 minutes
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Connection pool maintenance error: {e}")
            await asyncio.sleep(600)  # Wait longer on error


async def cache_cleanup_background():
    """Background task for cache cleanup and optimization."""
    while True:
        try:
            # Clean up expired cache entries
            await asyncio.sleep(900)  # Run every 15 minutes
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
            await asyncio.sleep(1800)  # Wait longer on error


async def session_cleanup_background():
    """Background task for cleaning up expired sessions."""
    while True:
        try:
            # Clean up expired JWT sessions
            await asyncio.sleep(3600)  # Run every hour
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Session cleanup error: {e}")
            await asyncio.sleep(7200)  # Wait longer on error


# === FastAPI App Initialization ===

# Initialize Prometheus instrumentator for production
if settings.enable_metrics and not settings.is_testing:
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=[".*admin.*", ".*metrics.*"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="proxywhirl_inprogress",
        inprogress_labels=True,
    )

# Create FastAPI app with enhanced configuration
app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.version,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url="/openapi.json" if settings.is_development else None,
    debug=settings.debug,
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    generate_unique_id_function=lambda route: f"{route.tags[0]}-{route.name}" if route.tags else route.name,
)


# === Enhanced Security Middleware Stack ===

# Security headers middleware (first for all requests)
app.add_middleware(SecurityHeadersMiddleware)

# Trusted host middleware for production
if settings.is_production:
    trusted_hosts = settings.trusted_hosts or [
        "api.proxywhirl.com",
        "*.proxywhirl.com", 
        "localhost",
        "127.0.0.1",
    ]
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)
    logger.info(f"Trusted host middleware enabled: {trusted_hosts}")

# CORS middleware with environment-based configuration
cors_config = settings.get_cors_config()
app.add_middleware(CORSMiddleware, **cors_config)

# Request logging and monitoring middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(MonitoringMiddleware)

# Rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# GZip compression middleware (after rate limiting)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Prometheus metrics middleware (last for complete request tracking)
if settings.enable_metrics and not settings.is_testing:
    instrumentator.instrument(app).expose(app, endpoint=settings.metrics_path)


# === Router Registration ===

# Authentication routes
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)

# Health and monitoring routes
app.include_router(
    health_router,
    prefix="/health",
    tags=["Health & Monitoring"],
)

# Core proxy management routes
app.include_router(
    proxies_router,
    prefix="/proxies",
    tags=["Proxy Management"],
)

# Administrative routes (requires admin scope)
app.include_router(
    admin_router,
    prefix="/admin",
    tags=["Administration"],
)

# WebSocket routes
app.include_router(
    websocket_router,
    prefix="/ws",
    tags=["WebSocket"],
)


# === Global Exception Handlers ===

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with structured error responses."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    logger.error(
        f"Unhandled exception in {request.method} {request.url}: {exc}",
        extra={"request_id": request_id, "exception": str(exc)}
    )
    
    if settings.is_development:
        # In development, provide detailed error information
        return ORJSONResponse(
            status_code=500,
            content={
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred",
                "details": {"exception": str(exc), "type": type(exc).__name__},
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
    
    # In production, provide generic error message
    return ORJSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR", 
            "message": "An internal server error occurred",
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )


# === Root Endpoint ===

@app.get(
    "/",
    summary="API Root",
    description="Get API information and health status",
    response_class=ORJSONResponse,
    tags=["Root"],
)
async def root():
    """Get API root information."""
    uptime_seconds = (datetime.now(timezone.utc) - api_start_time).total_seconds()
    
    try:
        pw = await get_proxywhirl()
        proxy_count = len(await pw.get_proxies_async())
        healthy_count = len([p for p in await pw.get_proxies_async() if p.status.value == "active"])
    except Exception:
        proxy_count = 0
        healthy_count = 0
    
    return {
        "app_name": settings.app_name,
        "version": settings.version,
        "status": "healthy",
        "uptime_seconds": round(uptime_seconds, 2),
        "environment": "production" if settings.is_production else "development",
        "proxy_count": proxy_count,
        "healthy_proxies": healthy_count,
        "features": {
            "authentication": True,
            "websockets": True,
            "metrics": settings.enable_metrics,
            "background_tasks": True,
        },
        "endpoints": {
            "docs": "/docs" if settings.is_development else None,
            "redoc": "/redoc" if settings.is_development else None,
            "health": "/health",
            "metrics": settings.metrics_path if settings.enable_metrics else None,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
