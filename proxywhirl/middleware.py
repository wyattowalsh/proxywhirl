"""Middleware chain pattern for request/proxy/response processing.

Allows composing request handlers with hooks before/after proxy selection.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from loguru import logger


@dataclass
class RequestContext:
    """Context for a proxy request."""

    request_data: dict[str, Any]
    metadata: dict[str, Any]
    selected_proxy: Optional[Any] = None
    response_data: Optional[dict[str, Any]] = None
    error: Optional[Exception] = None


class Middleware(ABC):
    """Base class for middleware in the chain."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for this middleware."""
        pass

    @abstractmethod
    async def before_proxy_selection(self, context: RequestContext) -> None:
        """Hook called before proxy selection."""
        pass

    @abstractmethod
    async def after_proxy_selection(self, context: RequestContext) -> None:
        """Hook called after proxy selection."""
        pass

    @abstractmethod
    async def on_success(self, context: RequestContext) -> None:
        """Hook called when request succeeds."""
        pass

    @abstractmethod
    async def on_error(self, context: RequestContext) -> None:
        """Hook called when request fails."""
        pass


class MiddlewareChain:
    """Chain of responsibility for request middleware."""

    def __init__(self) -> None:
        """Initialize middleware chain."""
        self._middlewares: list[Middleware] = []

    def add_middleware(self, middleware: Middleware) -> None:
        """Add middleware to chain."""
        if any(m.name == middleware.name for m in self._middlewares):
            logger.warning(f"Middleware {middleware.name} already exists, skipping")
            return

        self._middlewares.append(middleware)
        logger.debug(f"Added middleware: {middleware.name}")

    def remove_middleware(self, name: str) -> bool:
        """Remove middleware from chain by name."""
        for i, middleware in enumerate(self._middlewares):
            if middleware.name == name:
                self._middlewares.pop(i)
                logger.debug(f"Removed middleware: {name}")
                return True

        return False

    def get_middleware(self, name: str) -> Optional[Middleware]:
        """Get middleware by name."""
        for middleware in self._middlewares:
            if middleware.name == name:
                return middleware

        return None

    async def execute_before_selection(self, context: RequestContext) -> None:
        """Execute all before_proxy_selection hooks."""
        for middleware in self._middlewares:
            try:
                await middleware.before_proxy_selection(context)
            except Exception as e:
                logger.error(f"Error in {middleware.name}.before_proxy_selection: {e}")

    async def execute_after_selection(self, context: RequestContext) -> None:
        """Execute all after_proxy_selection hooks."""
        for middleware in self._middlewares:
            try:
                await middleware.after_proxy_selection(context)
            except Exception as e:
                logger.error(f"Error in {middleware.name}.after_proxy_selection: {e}")

    async def execute_on_success(self, context: RequestContext) -> None:
        """Execute all on_success hooks."""
        for middleware in self._middlewares:
            try:
                await middleware.on_success(context)
            except Exception as e:
                logger.error(f"Error in {middleware.name}.on_success: {e}")

    async def execute_on_error(self, context: RequestContext) -> None:
        """Execute all on_error hooks."""
        for middleware in self._middlewares:
            try:
                await middleware.on_error(context)
            except Exception as e:
                logger.error(f"Error in {middleware.name}.on_error: {e}")


# Example middleware implementations


class LoggingMiddleware(Middleware):
    """Middleware for logging requests and responses."""

    @property
    def name(self) -> str:
        """Name of this middleware."""
        return "logging"

    async def before_proxy_selection(self, context: RequestContext) -> None:
        """Log before proxy selection."""
        logger.debug(f"Request: {context.request_data}")

    async def after_proxy_selection(self, context: RequestContext) -> None:
        """Log after proxy selection."""
        if context.selected_proxy:
            logger.debug(f"Selected proxy: {context.selected_proxy}")

    async def on_success(self, context: RequestContext) -> None:
        """Log successful request."""
        logger.debug(f"Request succeeded with {context.selected_proxy}")

    async def on_error(self, context: RequestContext) -> None:
        """Log failed request."""
        logger.warning(f"Request failed: {context.error}")


class MetricsMiddleware(Middleware):
    """Middleware for collecting request metrics."""

    def __init__(self) -> None:
        """Initialize metrics."""
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0

    @property
    def name(self) -> str:
        """Name of this middleware."""
        return "metrics"

    async def before_proxy_selection(self, context: RequestContext) -> None:
        """Count requests."""
        self.request_count += 1

    async def after_proxy_selection(self, context: RequestContext) -> None:
        """No-op."""
        pass

    async def on_success(self, context: RequestContext) -> None:
        """Count successes."""
        self.success_count += 1

    async def on_error(self, context: RequestContext) -> None:
        """Count errors."""
        self.error_count += 1

    def get_stats(self) -> dict[str, int]:
        """Get metrics statistics."""
        return {
            "total_requests": self.request_count,
            "successful": self.success_count,
            "failed": self.error_count,
        }


class RetryMiddleware(Middleware):
    """Middleware for automatic retry on failure."""

    def __init__(self, max_retries: int = 3) -> None:
        """Initialize retry middleware."""
        self.max_retries = max_retries
        self.retry_count: dict[str, int] = {}

    @property
    def name(self) -> str:
        """Name of this middleware."""
        return "retry"

    async def before_proxy_selection(self, context: RequestContext) -> None:
        """Reset retry count for new request."""
        request_id = id(context)
        self.retry_count[request_id] = 0

    async def after_proxy_selection(self, context: RequestContext) -> None:
        """No-op."""
        pass

    async def on_success(self, context: RequestContext) -> None:
        """Clear retry count on success."""
        request_id = id(context)
        self.retry_count.pop(request_id, None)

    async def on_error(self, context: RequestContext) -> None:
        """Track retries on error."""
        request_id = id(context)
        current_retries = self.retry_count.get(request_id, 0)

        if current_retries < self.max_retries:
            self.retry_count[request_id] = current_retries + 1
            logger.info(f"Will retry request (attempt {current_retries + 1})")


class RateLimitMiddleware(Middleware):
    """Middleware for rate limiting."""

    def __init__(self, max_requests_per_second: float = 10.0) -> None:
        """Initialize rate limit middleware."""
        self.max_requests_per_second = max_requests_per_second
        self.last_request_time: float = 0.0

    @property
    def name(self) -> str:
        """Name of this middleware."""
        return "rate_limit"

    async def before_proxy_selection(self, context: RequestContext) -> None:
        """Check rate limit before request."""
        import asyncio
        import time

        current_time = time.time()
        min_interval = 1.0 / self.max_requests_per_second

        if current_time - self.last_request_time < min_interval:
            wait_time = min_interval - (current_time - self.last_request_time)
            logger.debug(f"Rate limit: waiting {wait_time:.3f}s")
            await asyncio.sleep(wait_time)

        self.last_request_time = time.time()

    async def after_proxy_selection(self, context: RequestContext) -> None:
        """No-op."""
        pass

    async def on_success(self, context: RequestContext) -> None:
        """No-op."""
        pass

    async def on_error(self, context: RequestContext) -> None:
        """No-op."""
        pass
