"""HTTP middleware pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from loguru import logger


@dataclass
class MiddlewareContext:
    """Middleware execution context."""

    request: dict[str, Any]
    response: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


MiddlewareFunc = Callable[[MiddlewareContext], MiddlewareContext | None]


class MiddlewarePipeline:
    """Pipeline for request/response middleware."""

    def __init__(self):
        """Initialize pipeline."""
        self._request_middleware: list[MiddlewareFunc] = []
        self._response_middleware: list[MiddlewareFunc] = []

    def add_request_middleware(self, middleware: MiddlewareFunc) -> None:
        """Add request middleware.

        Args:
            middleware: Middleware function
        """
        self._request_middleware.append(middleware)

    def add_response_middleware(self, middleware: MiddlewareFunc) -> None:
        """Add response middleware.

        Args:
            middleware: Middleware function
        """
        self._response_middleware.append(middleware)

    def execute_request_pipeline(self, request: dict[str, Any]) -> MiddlewareContext:
        """Execute request pipeline.

        Args:
            request: Request dict

        Returns:
            Context after middleware
        """
        context = MiddlewareContext(request=request, metadata={})

        for middleware in self._request_middleware:
            try:
                result = middleware(context)
                if result is None:
                    logger.warning("Middleware returned None, stopping pipeline")
                    break
                context = result
            except Exception as e:
                logger.error(f"Middleware error: {e}")
                raise

        return context

    def execute_response_pipeline(
        self,
        request: dict[str, Any],
        response: dict[str, Any],
    ) -> MiddlewareContext:
        """Execute response pipeline.

        Args:
            request: Request dict
            response: Response dict

        Returns:
            Context after middleware
        """
        context = MiddlewareContext(request=request, response=response, metadata={})

        for middleware in self._response_middleware:
            try:
                result = middleware(context)
                if result is None:
                    logger.warning("Middleware returned None, stopping pipeline")
                    break
                context = result
            except Exception as e:
                logger.error(f"Middleware error: {e}")
                raise

        return context


class HeaderMiddleware:
    """Middleware for header manipulation."""

    def __init__(self):
        """Initialize middleware."""
        self._headers_to_add: dict[str, str] = {}
        self._headers_to_remove: list[str] = []

    def add_header(self, name: str, value: str) -> None:
        """Add header to all requests.

        Args:
            name: Header name
            value: Header value
        """
        self._headers_to_add[name] = value

    def remove_header(self, name: str) -> None:
        """Remove header from all requests.

        Args:
            name: Header name
        """
        self._headers_to_remove.append(name)

    def __call__(self, context: MiddlewareContext) -> MiddlewareContext:
        """Apply header transformations.

        Args:
            context: Middleware context

        Returns:
            Updated context
        """
        headers = context.request.get("headers", {})

        for name, value in self._headers_to_add.items():
            headers[name] = value

        for name in self._headers_to_remove:
            headers.pop(name, None)

        context.request["headers"] = headers
        return context


class RateLimitMiddleware:
    """Middleware for rate limiting."""

    def __init__(self, max_requests: int, window_seconds: int):
        """Initialize middleware.

        Args:
            max_requests: Max requests per window
            window_seconds: Time window
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._request_counts: dict[str, list[float]] = {}

    def __call__(self, context: MiddlewareContext) -> MiddlewareContext:
        """Check rate limit.

        Args:
            context: Middleware context

        Returns:
            Updated context or raises
        """
        # Simplified rate limit check
        identifier = context.request.get("url", "unknown")
        if identifier not in self._request_counts:
            self._request_counts[identifier] = []

        self._request_counts[identifier].append(0)
        if len(self._request_counts[identifier]) > self.max_requests:
            raise RuntimeError(f"Rate limit exceeded for {identifier}")

        return context


class ValidationMiddleware:
    """Middleware for request/response validation."""

    def __init__(self):
        """Initialize middleware."""
        self._validators: list[Callable] = []

    def add_validator(self, validator: Callable) -> None:
        """Add validator.

        Args:
            validator: Validator function
        """
        self._validators.append(validator)

    def __call__(self, context: MiddlewareContext) -> MiddlewareContext:
        """Run validators.

        Args:
            context: Middleware context

        Returns:
            Updated context
        """
        for validator in self._validators:
            try:
                if not validator(context.request):
                    raise ValueError("Validation failed")
            except Exception as e:
                logger.error(f"Validation error: {e}")
                raise

        return context


class LoggingMiddleware:
    """Middleware for logging requests/responses."""

    def __call__(self, context: MiddlewareContext) -> MiddlewareContext:
        """Log request/response.

        Args:
            context: Middleware context

        Returns:
            Updated context
        """
        request = context.request
        response = context.response

        if response:
            logger.info(
                f"{request.get('method')} {request.get('url')} -> {response.get('status_code')}",
                request=request,
                response=response,
            )
        else:
            logger.info(
                f"{request.get('method')} {request.get('url')}",
                request=request,
            )

        return context
