"""ProxyWhirl API route modules.

Registers all API routers on the core FastAPI application.
"""

from __future__ import annotations

from proxywhirl.api.routes.health import router as health_router
from proxywhirl.api.routes.pools import router as pools_router
from proxywhirl.api.routes.proxies import router as proxies_router

__all__ = [
    "health_router",
    "pools_router",
    "proxies_router",
]
