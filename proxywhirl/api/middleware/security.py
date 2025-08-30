"""Security Headers Middleware

Comprehensive security headers middleware for production FastAPI applications.
Implements modern security best practices including CSP, HSTS, and more.
"""

import time
from typing import Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from ...settings import get_api_settings

settings = get_api_settings()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Advanced security headers middleware with environment-specific configurations.
    
    Applies comprehensive security headers to protect against:
    - XSS attacks
    - Clickjacking
    - MIME type sniffing
    - Content injection
    - Protocol downgrade attacks
    """
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.is_production = settings.is_production
        
        # Production security headers
        self.production_headers = {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://fonts.gstatic.com; "
                "connect-src 'self' wss: ws:; "
                "frame-ancestors 'none'; "
                "base-uri 'self';"
            ),
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": (
                "accelerometer=(), "
                "camera=(), "
                "geolocation=(), "
                "gyroscope=(), "
                "magnetometer=(), "
                "microphone=(), "
                "payment=(), "
                "usb=()"
            ),
        }
        
        # Development headers (less restrictive for debugging)
        self.development_headers = {
            "Content-Security-Policy": (
                "default-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "connect-src 'self' ws: wss:; "
                "img-src 'self' data: https:;"
            ),
            "X-Frame-Options": "SAMEORIGIN",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer-when-downgrade",
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply security headers to all responses."""
        start_time = time.time()
        
        # Add request ID for correlation
        request_id = self._generate_request_id()
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Apply security headers based on environment
        headers_to_apply = (
            self.production_headers if self.is_production 
            else self.development_headers
        )
        
        # Apply security headers
        for header_name, header_value in headers_to_apply.items():
            response.headers[header_name] = header_value
        
        # Add common headers for all environments
        common_headers = {
            "X-Process-Time": f"{process_time:.4f}s",
            "X-API-Version": settings.version,
            "X-Request-ID": request_id,
            "Cache-Control": self._get_cache_control_header(request),
            "Pragma": "no-cache",
        }
        
        for header_name, header_value in common_headers.items():
            response.headers[header_name] = header_value
        
        # Remove server identification for security
        response.headers.pop("Server", None)
        
        # Log security header application in debug mode
        if settings.debug:
            logger.debug(
                f"Applied {len(headers_to_apply) + len(common_headers)} security headers "
                f"to {request.method} {request.url.path}"
            )
        
        return response
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID for correlation."""
        import uuid
        return str(uuid.uuid4())
    
    def _get_cache_control_header(self, request: Request) -> str:
        """
        Get appropriate cache control header based on request type.
        
        Static resources get longer cache times, API responses get no-cache.
        """
        path = request.url.path
        
        # Static resources can be cached
        if any(path.endswith(ext) for ext in ['.css', '.js', '.png', '.jpg', '.ico', '.woff', '.woff2']):
            return "public, max-age=3600"  # 1 hour cache
        
        # API responses should not be cached
        if path.startswith('/api') or path.startswith('/proxies'):
            return "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0"
        
        # Default no-cache for dynamic content
        return "no-cache, no-store, must-revalidate"
