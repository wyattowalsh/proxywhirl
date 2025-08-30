"""ProxyWhirl API Package

Modern, modular FastAPI implementation with:
- Dependency injection patterns
- Advanced middleware stack
- Comprehensive authentication
- Real-time WebSocket support
- Production-ready patterns
"""

from .dependencies import get_current_active_user, get_current_user, get_proxywhirl
from .main import app

__all__ = ["app", "get_proxywhirl", "get_current_user", "get_current_active_user"]
