"""API Endpoints Package

Modular FastAPI router implementations organized by functionality.
"""

from .admin import router as admin_router
from .auth import router as auth_router
from .health import router as health_router
from .proxies import router as proxies_router
from .websocket import router as websocket_router

__all__ = [
    "auth_router",
    "health_router", 
    "proxies_router",
    "admin_router",
    "websocket_router",
]
