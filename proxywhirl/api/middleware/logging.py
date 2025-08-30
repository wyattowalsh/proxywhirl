"""Logging Middleware

Structured request/response logging middleware with correlation IDs,
performance metrics, and security event tracking.
"""

import time
from typing import Any, Dict

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from ...settings import get_api_settings

settings = get_api_settings()


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive logging middleware for FastAPI applications.
    
    Features:
    - Structured request/response logging
    - Performance metrics collection
    - Security event detection
    - Request correlation IDs
    - Sensitive data filtering
    """
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        
        # Sensitive headers and query params to filter from logs
        self.sensitive_headers = {
            "authorization", 
            "x-api-key", 
            "cookie", 
            "x-forwarded-for",
        }
        
        self.sensitive_params = {
            "password", 
            "token", 
            "key", 
            "secret",
            "auth",
        }
    
    async def dispatch(self, request: Request, call_next):
        """Log requests and responses with performance metrics."""
        start_time = time.time()
        
        # Extract request information
        request_info = await self._extract_request_info(request)
        
        # Log incoming request
        if settings.debug:
            logger.info(
                "Incoming request",
                extra={
                    "request_id": request_info["request_id"],
                    "method": request_info["method"],
                    "url": request_info["url"],
                    "client_ip": request_info["client_ip"],
                    "user_agent": request_info["user_agent"],
                    "headers": request_info["filtered_headers"],
                    "query_params": request_info["filtered_query_params"],
                }
            )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Extract response information
            response_info = self._extract_response_info(response, process_time)
            
            # Determine log level based on status code
            if response.status_code >= 500:
                log_level = "error"
            elif response.status_code >= 400:
                log_level = "warning"  
            else:
                log_level = "info"
            
            # Log response
            getattr(logger, log_level)(
                "Request completed",
                extra={
                    "request_id": request_info["request_id"],
                    "method": request_info["method"],
                    "url": request_info["url"],
                    "status_code": response_info["status_code"],
                    "process_time": response_info["process_time"],
                    "response_size": response_info["response_size"],
                    "client_ip": request_info["client_ip"],
                }
            )
            
            # Log security events
            await self._log_security_events(request_info, response_info)
            
            return response
            
        except Exception as e:
            # Log unhandled exceptions
            process_time = time.time() - start_time
            
            logger.error(
                "Request failed with exception",
                extra={
                    "request_id": request_info["request_id"],
                    "method": request_info["method"],
                    "url": request_info["url"],
                    "exception": str(e),
                    "exception_type": type(e).__name__,
                    "process_time": process_time,
                    "client_ip": request_info["client_ip"],
                }
            )
            
            raise  # Re-raise the exception
    
    async def _extract_request_info(self, request: Request) -> Dict[str, Any]:
        """Extract structured request information."""
        # Get or generate request ID
        request_id = getattr(request.state, "request_id", None)
        if not request_id:
            import uuid
            request_id = str(uuid.uuid4())
            request.state.request_id = request_id
        
        # Extract client IP (considering proxies)
        client_ip = self._get_client_ip(request)
        
        # Filter sensitive headers
        filtered_headers = {
            k: "[FILTERED]" if k.lower() in self.sensitive_headers else v
            for k, v in request.headers.items()
        }
        
        # Filter sensitive query parameters
        filtered_query_params = {
            k: "[FILTERED]" if any(sensitive in k.lower() for sensitive in self.sensitive_params) else v
            for k, v in request.query_params.items()
        }
        
        return {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "client_ip": client_ip,
            "user_agent": request.headers.get("user-agent", "Unknown"),
            "filtered_headers": filtered_headers,
            "filtered_query_params": filtered_query_params,
            "content_length": request.headers.get("content-length", 0),
        }
    
    def _extract_response_info(self, response: Response, process_time: float) -> Dict[str, Any]:
        """Extract structured response information."""
        # Get response size if available
        response_size = None
        if hasattr(response, "headers") and "content-length" in response.headers:
            try:
                response_size = int(response.headers["content-length"])
            except (ValueError, TypeError):
                pass
        
        return {
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
            "response_size": response_size,
        }
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address considering proxy headers.
        
        Checks common proxy headers in order of preference.
        """
        # Check for forwarded headers (common in production)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in case of multiple proxies
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    async def _log_security_events(self, request_info: Dict[str, Any], response_info: Dict[str, Any]):
        """Log potential security events."""
        # Authentication failures
        if response_info["status_code"] == 401:
            logger.warning(
                "Authentication failure",
                extra={
                    "request_id": request_info["request_id"],
                    "client_ip": request_info["client_ip"],
                    "path": request_info["path"],
                    "user_agent": request_info["user_agent"],
                    "security_event": "auth_failure",
                }
            )
        
        # Authorization failures
        elif response_info["status_code"] == 403:
            logger.warning(
                "Authorization failure",
                extra={
                    "request_id": request_info["request_id"],
                    "client_ip": request_info["client_ip"],
                    "path": request_info["path"],
                    "security_event": "authz_failure",
                }
            )
        
        # Rate limiting
        elif response_info["status_code"] == 429:
            logger.warning(
                "Rate limit exceeded",
                extra={
                    "request_id": request_info["request_id"],
                    "client_ip": request_info["client_ip"],
                    "path": request_info["path"],
                    "security_event": "rate_limit_exceeded",
                }
            )
        
        # Potential attacks (400 errors on sensitive endpoints)
        elif response_info["status_code"] == 400 and any(
            sensitive in request_info["path"].lower() 
            for sensitive in ["auth", "admin", "config"]
        ):
            logger.warning(
                "Potential attack on sensitive endpoint",
                extra={
                    "request_id": request_info["request_id"],
                    "client_ip": request_info["client_ip"],
                    "path": request_info["path"],
                    "security_event": "potential_attack",
                }
            )
