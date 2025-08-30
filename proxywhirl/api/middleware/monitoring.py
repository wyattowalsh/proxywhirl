"""Monitoring Middleware

Performance monitoring and metrics collection middleware.
Integrates with Prometheus and custom metrics systems.
"""

import time
from typing import Any

from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from ...settings import get_api_settings

settings = get_api_settings()


class MonitoringMiddleware(BaseHTTPMiddleware):
    """
    Performance and business metrics collection middleware.
    
    Collects:
    - Request/response performance metrics
    - Business metrics (proxy operations)
    - Error rates and patterns
    - Resource utilization
    """
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        
        # Metrics storage (in production, this would be Prometheus/StatsD)
        self.metrics = {
            "requests_total": 0,
            "requests_by_status": {},
            "requests_by_path": {},
            "response_times": [],
            "active_requests": 0,
        }
        
        # Performance thresholds
        self.slow_request_threshold = 5.0  # seconds
        self.very_slow_request_threshold = 10.0  # seconds
    
    async def dispatch(self, request: Request, call_next):
        """Collect performance and business metrics."""
        start_time = time.time()
        path = request.url.path
        method = request.method
        
        # Increment active requests
        self.metrics["active_requests"] += 1
        
        # Record request start
        request_info = {
            "path": path,
            "method": method,
            "start_time": start_time,
        }
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate metrics
            end_time = time.time()
            response_time = end_time - start_time
            status_code = response.status_code
            
            # Update metrics
            await self._update_metrics(request_info, response_time, status_code)
            
            # Log slow requests
            if response_time > self.slow_request_threshold:
                severity = "error" if response_time > self.very_slow_request_threshold else "warning"
                getattr(logger, severity)(
                    f"Slow request detected: {response_time:.2f}s",
                    extra={
                        "path": path,
                        "method": method,
                        "response_time": response_time,
                        "status_code": status_code,
                        "performance_issue": True,
                    }
                )
            
            # Add metrics headers for debugging
            if settings.debug:
                response.headers["X-Response-Time"] = f"{response_time:.4f}"
                response.headers["X-Active-Requests"] = str(self.metrics["active_requests"])
            
            return response
            
        except Exception as e:
            # Record error metrics
            end_time = time.time()
            response_time = end_time - start_time
            
            await self._update_metrics(request_info, response_time, 500)
            
            logger.error(
                f"Request failed: {e}",
                extra={
                    "path": path,
                    "method": method,
                    "response_time": response_time,
                    "exception": str(e),
                    "performance_issue": response_time > self.slow_request_threshold,
                }
            )
            
            raise
        
        finally:
            # Decrement active requests
            self.metrics["active_requests"] = max(0, self.metrics["active_requests"] - 1)
    
    async def _update_metrics(self, request_info: dict, response_time: float, status_code: int):
        """Update internal metrics storage."""
        path = request_info["path"]
        method = request_info["method"]
        
        # Total requests
        self.metrics["requests_total"] += 1
        
        # Status code distribution
        status_key = f"{status_code // 100}xx"
        self.metrics["requests_by_status"][status_key] = (
            self.metrics["requests_by_status"].get(status_key, 0) + 1
        )
        
        # Path distribution (limit to avoid memory issues)
        path_key = f"{method} {path}"
        if len(self.metrics["requests_by_path"]) < 1000:
            self.metrics["requests_by_path"][path_key] = (
                self.metrics["requests_by_path"].get(path_key, 0) + 1
            )
        
        # Response times (keep last 1000)
        self.metrics["response_times"].append(response_time)
        if len(self.metrics["response_times"]) > 1000:
            self.metrics["response_times"] = self.metrics["response_times"][-1000:]
        
        # Log metrics periodically (every 100 requests in debug mode)
        if settings.debug and self.metrics["requests_total"] % 100 == 0:
            await self._log_metrics_summary()
    
    async def _log_metrics_summary(self):
        """Log performance metrics summary."""
        response_times = self.metrics["response_times"]
        
        if not response_times:
            return
        
        # Calculate statistics
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        # Calculate percentiles
        sorted_times = sorted(response_times)
        p95_index = int(len(sorted_times) * 0.95)
        p99_index = int(len(sorted_times) * 0.99)
        
        p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else max_response_time
        p99_response_time = sorted_times[p99_index] if p99_index < len(sorted_times) else max_response_time
        
        logger.info(
            "Performance metrics summary",
            extra={
                "total_requests": self.metrics["requests_total"],
                "active_requests": self.metrics["active_requests"],
                "avg_response_time": round(avg_response_time, 4),
                "min_response_time": round(min_response_time, 4),
                "max_response_time": round(max_response_time, 4),
                "p95_response_time": round(p95_response_time, 4),
                "p99_response_time": round(p99_response_time, 4),
                "status_distribution": self.metrics["requests_by_status"],
                "top_endpoints": dict(
                    sorted(self.metrics["requests_by_path"].items(), key=lambda x: x[1], reverse=True)[:10]
                ),
            }
        )
    
    def get_metrics(self) -> dict:
        """Get current metrics for API endpoints."""
        response_times = self.metrics["response_times"]
        
        if not response_times:
            return {
                "total_requests": self.metrics["requests_total"],
                "active_requests": self.metrics["active_requests"],
                "status_distribution": self.metrics["requests_by_status"],
                "top_endpoints": self.metrics["requests_by_path"],
            }
        
        # Calculate current statistics
        avg_response_time = sum(response_times) / len(response_times)
        sorted_times = sorted(response_times)
        p95_index = int(len(sorted_times) * 0.95)
        p99_index = int(len(sorted_times) * 0.99)
        
        return {
            "total_requests": self.metrics["requests_total"],
            "active_requests": self.metrics["active_requests"], 
            "avg_response_time": round(avg_response_time, 4),
            "min_response_time": round(min(response_times), 4),
            "max_response_time": round(max(response_times), 4),
            "p95_response_time": round(sorted_times[p95_index], 4),
            "p99_response_time": round(sorted_times[p99_index], 4),
            "status_distribution": self.metrics["requests_by_status"],
            "top_endpoints": dict(
                sorted(self.metrics["requests_by_path"].items(), key=lambda x: x[1], reverse=True)[:20]
            ),
        }
