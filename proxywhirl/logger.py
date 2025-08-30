"""proxywhirl/logger.py -- Best-in-class loguru + rich logger

This module provides:
1. Simple logger setup that preserves `from loguru import logger` usage
2. Advanced Rich integration with semantic theming and performance optimization
3. Environment-aware configuration with production-ready features
4. Optional enhanced utilities (decorators, context managers, structured logging)
5. Smart filtering and sampling for high-volume operations

Basic usage (unchanged):
    from loguru import logger
    logger.info("Hello world")

Enhanced usage (optional):
    from proxywhirl.logger import log_performance, log_operation, bind_context
    
    @log_performance("fetch_proxies")
    def fetch_proxies():
        pass
        
    with log_operation("validate_proxy", proxy_id="123"):
        # do work
        pass
    
    with bind_context(user_id="user123", request_id="req456"):
        logger.info("Processing request")
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone
from enum import Enum
from functools import lru_cache, wraps
from pathlib import Path
from threading import local
from typing import Any, AsyncIterator, Callable, Dict, Iterator, Optional, TypeVar, Union, Tuple
import inspect

from loguru import logger
from rich.console import Console
from rich.highlighter import ReprHighlighter
from rich.logging import RichHandler
from rich.theme import Theme
from rich.traceback import install as rich_traceback_install

# Install Rich traceback handling with optimized settings
rich_traceback_install(
    show_locals=False,  # Performance optimization
    suppress=[asyncio],  # Reduce noise from asyncio
    max_frames=10,  # Limit frame count
)

# Type variable for decorators
F = TypeVar("F", bound=Callable[..., Any])

# Thread-local storage for context
_local = local()


class Environment(str, Enum):
    """Environment types for smart configuration."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Structured log levels."""
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# === Environment Detection ===

def _detect_environment() -> Environment:
    """Smart environment detection."""
    env = os.getenv("PROXYWHIRL_ENV", "").lower()
    if env in ["production", "prod"]:
        return Environment.PRODUCTION
    elif env in ["staging", "stage"]:
        return Environment.STAGING
    elif env == "testing" or os.getenv("PYTEST_CURRENT_TEST"):
        return Environment.TESTING
    else:
        return Environment.DEVELOPMENT


_ENVIRONMENT = _detect_environment()
IS_TESTING = _ENVIRONMENT == Environment.TESTING


# === Advanced Rich Theme with Semantic Colors ===

@lru_cache(maxsize=4)
def create_theme(environment: Environment = _ENVIRONMENT) -> Theme:
    """Create optimized theme based on environment."""
    base_theme = {
        # Core log levels with semantic meaning
        "logging.level.trace": "dim white",
        "logging.level.debug": "dim cyan",
        "logging.level.info": "bright_cyan",
        "logging.level.success": "bold green",
        "logging.level.warning": "yellow",
        "logging.level.error": "bold red",
        "logging.level.critical": "bold white on red",
        
        # Context highlighting
        "ctx.timestamp": "dim blue",
        "ctx.module": "dim magenta",
        "ctx.function": "dim yellow",
        "ctx.user": "bright_magenta",
        "ctx.request": "bright_blue",
        "ctx.operation": "cyan",
        
        # ProxyWhirl domain-specific
        "proxy.host": "bright_blue",
        "proxy.port": "bright_green",
        "proxy.status.active": "green",
        "proxy.status.inactive": "red",
        "proxy.status.cooldown": "yellow",
        "proxy.status.blacklisted": "bright_red",
        
        # Performance metrics
        "perf.fast": "bright_green",
        "perf.medium": "yellow",
        "perf.slow": "red",
        "perf.duration": "bright_yellow",
        "perf.count": "bright_cyan",
        
        # API specific
        "api.method.get": "blue",
        "api.method.post": "green", 
        "api.method.put": "yellow",
        "api.method.delete": "red",
        "api.status.2xx": "green",
        "api.status.4xx": "yellow",
        "api.status.5xx": "red",
    }
    
    # Environment-specific adjustments
    if environment == Environment.PRODUCTION:
        # Subdued colors for production logs
        base_theme.update({
            "logging.level.info": "white",
            "logging.level.debug": "dim white",
        })
    elif environment == Environment.DEVELOPMENT:
        # Enhanced colors for development
        base_theme.update({
            "logging.level.info": "bright_cyan", 
            "logging.level.debug": "cyan",
        })
    
    return Theme(base_theme)


# === Optimized Console with Smart Configuration ===

@lru_cache(maxsize=1)
def create_console() -> Console:
    """Create optimized console with environment-appropriate settings."""
    return Console(
        theme=create_theme(_ENVIRONMENT),
        stderr=True,
        width=None,  # Auto-detect terminal width
        force_terminal=not IS_TESTING,  # Disable colors in tests
        highlight=_ENVIRONMENT == Environment.DEVELOPMENT,  # Syntax highlighting
        markup=True,
        emoji=_ENVIRONMENT == Environment.DEVELOPMENT,
        record=_ENVIRONMENT != Environment.PRODUCTION,  # Memory optimization
        legacy_windows=False,  # Modern Windows support
        safe_box=True,  # Safe box characters
        _environ=os.environ,  # Environment access
    )


# Global optimized console instance
console = create_console()


# === Context Management ===

class LogContext:
    """Thread-safe context manager for structured logging."""
    
    def __init__(self) -> None:
        self._context: Dict[str, Any] = {}
    
    def bind(self, **kwargs: Any) -> "LogContext":
        """Bind context variables."""
        self._context.update(kwargs)
        return self
    
    def clear(self) -> None:
        """Clear all context."""
        self._context.clear()
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context."""
        return self._context.copy()


def _get_context() -> LogContext:
    """Get thread-local context."""
    if not hasattr(_local, 'context'):
        _local.context = LogContext()
    return _local.context


# === Enhanced Intercept Handler ===

class InterceptHandler(logging.Handler):
    """Enhanced logging intercept handler with context support."""
    
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller frame (skip logging module frames)
        frame, depth = logging.currentframe(), 2
        while frame and (frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        # Add thread-local context
        extra = _get_context().get_context()
        
        # Enhanced logging with context
        logger.opt(depth=depth, exception=record.exc_info).bind(**extra).log(
            level, record.getMessage()
        )


# === Smart Formatting Functions ===

def _format_duration(seconds: float) -> str:
    """Smart duration formatting."""
    if seconds < 1:
        return f"{seconds*1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"


def _performance_color(duration: float) -> str:
    """Get performance-based color styling."""
    if duration < 0.1:
        return "perf.fast"
    elif duration < 1.0:
        return "perf.medium"
    else:
        return "perf.slow"


# === Advanced Logger Setup ===

def _setup_enhanced_logger() -> None:
    """Set up the enhanced logger with all optimizations."""
    # Remove default handler
    logger.remove()
    
    # Determine log level
    default_level = "INFO" if _ENVIRONMENT == Environment.PRODUCTION else "DEBUG"
    log_level = os.getenv("PROXYWHIRL_LOG_LEVEL", default_level)
    
    # Create format based on environment
    if _ENVIRONMENT == Environment.DEVELOPMENT:
        format_string = (
            "<dim>{time:HH:mm:ss.SSS}</dim> "
            "<level>{level: <8}</level> "
            "<cyan>{name}</cyan>:<yellow>{function}</yellow>:<dim>{line}</dim> "
            "<cyan>│</cyan> {message}"
        )
    elif _ENVIRONMENT == Environment.PRODUCTION:
        format_string = (
            "<dim>{time:MM-DD HH:mm:ss}</dim> "
            "<level>{level: <8}</level> "
            "<cyan>│</cyan> {message}"
        )
    else:
        format_string = (
            "<dim>{time:HH:mm:ss}</dim> "
            "<level>{level: <8}</level> "
            "<cyan>│</cyan> {message}"
        )
    
    # Add Rich handler
    logger.add(
        RichHandler(
            console=console,
            show_time=False,  # Time shown in format
            show_level=False,  # Level shown in format
            show_path=False,  # Path shown in format
            rich_tracebacks=True,
            tracebacks_show_locals=_ENVIRONMENT == Environment.DEVELOPMENT,
            highlighter=ReprHighlighter() if _ENVIRONMENT != Environment.PRODUCTION else None,
            markup=True,
            keywords=[],  # Avoid keyword highlighting noise
            log_time_format="[%X]",
        ),
        format=format_string,
        level=log_level,
        colorize=True,
        backtrace=_ENVIRONMENT != Environment.PRODUCTION,
        diagnose=_ENVIRONMENT == Environment.DEVELOPMENT,
    )
    
    # Add file logging if specified
    log_file = os.getenv("PROXYWHIRL_LOG_FILE")
    if log_file:
        logger.add(
            log_file,
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                "{level: <8} | "
                "{process.id}:{thread.id} | "
                "{name}:{function}:{line} | "
                "{extra} | "
                "{message}"
            ),
            level=log_level,
            rotation="10 MB" if _ENVIRONMENT == Environment.PRODUCTION else None,
            retention="30 days" if _ENVIRONMENT == Environment.PRODUCTION else None,
            compression="gz" if _ENVIRONMENT == Environment.PRODUCTION else None,
            serialize=_ENVIRONMENT == Environment.PRODUCTION,  # JSON for production
            enqueue=True,  # Async file writing
            backtrace=_ENVIRONMENT != Environment.PRODUCTION,
            diagnose=_ENVIRONMENT == Environment.DEVELOPMENT,
        )
    
    # Configure standard logging interception
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Silence noisy loggers in production
    if _ENVIRONMENT == Environment.PRODUCTION:
        for noisy_logger in ["httpcore", "httpx", "urllib3", "asyncio", "aiohttp"]:
            logging.getLogger(noisy_logger).setLevel(logging.WARNING)


# Set up the enhanced logger
_setup_enhanced_logger()


# === Context Binding Utilities ===

@contextmanager
def bind_context(**kwargs: Any) -> Iterator[None]:
    """Context manager for binding structured logging context."""
    context = _get_context()
    original_context = context.get_context()
    
    try:
        context.bind(**kwargs)
        yield
    finally:
        context.clear()
        context.bind(**original_context)


@asynccontextmanager
async def bind_context_async(**kwargs: Any) -> AsyncIterator[None]:
    """Async context manager for binding structured logging context."""
    context = _get_context()
    original_context = context.get_context()
    
    try:
        context.bind(**kwargs)
        yield
    finally:
        context.clear()
        context.bind(**original_context)


# === Operation Tracking ===

@contextmanager
def log_operation(operation: str, **context: Any) -> Iterator[Dict[str, Any]]:
    """Context manager for tracking operations with enhanced logging."""
    start_time = datetime.now(timezone.utc)
    operation_context: Dict[str, Any] = {"operation": operation, **context}
    
    with bind_context(**operation_context):
        logger.info(f"[ctx.operation]Starting operation:[/] {operation}")
        
        try:
            yield operation_context
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            duration_str = _format_duration(duration)
            perf_style = _performance_color(duration)
            
            logger.bind(duration_ms=round(duration * 1000, 2)).success(
                f"[ctx.operation]Completed operation:[/] {operation} in [{perf_style}]{duration_str}[/]"
            )
        except Exception as e:
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            duration_str = _format_duration(duration)
            
            logger.bind(
                duration_ms=round(duration * 1000, 2),
                error=str(e),
                exception_type=type(e).__name__
            ).error(
                f"[ctx.operation]Failed operation:[/] {operation} after [perf.slow]{duration_str}[/]: {e}"
            )
            raise


@asynccontextmanager
async def log_operation_async(operation: str, **context: Any) -> AsyncIterator[Dict[str, Any]]:
    """Async context manager for tracking operations."""
    start_time = datetime.now(timezone.utc)
    operation_context: Dict[str, Any] = {"operation": operation, **context}
    
    async with bind_context_async(**operation_context):
        logger.info(f"[ctx.operation]Starting async operation:[/] {operation}")
        
        try:
            yield operation_context
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            duration_str = _format_duration(duration)
            perf_style = _performance_color(duration)
            
            logger.bind(duration_ms=round(duration * 1000, 2)).success(
                f"[ctx.operation]Completed async operation:[/] {operation} in [{perf_style}]{duration_str}[/]"
            )
        except Exception as e:
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            duration_str = _format_duration(duration)
            
            logger.bind(
                duration_ms=round(duration * 1000, 2),
                error=str(e),
                exception_type=type(e).__name__
            ).error(
                f"[ctx.operation]Failed async operation:[/] {operation} after [perf.slow]{duration_str}[/]: {e}"
            )
            raise


# === Performance Decorators ===

def log_performance(
    func_name: Optional[str] = None, 
    level: Union[str, LogLevel] = LogLevel.DEBUG,
    log_args: bool = False
):
    """Enhanced decorator to log function performance with context."""
    def decorator(func: F) -> F:
        name = func_name or f"{func.__module__}.{func.__qualname__}"
        log_level = level.value if isinstance(level, LogLevel) else level
        
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = datetime.now(timezone.utc)
                
                # Optional argument logging for debugging
                extra_context = {}
                if log_args and _ENVIRONMENT == Environment.DEVELOPMENT:
                    extra_context["args_count"] = len(args)
                    extra_context["kwargs_keys"] = list(kwargs.keys())
                
                try:
                    result = await func(*args, **kwargs)
                    duration = (datetime.now(timezone.utc) - start_time).total_seconds()
                    duration_str = _format_duration(duration)
                    perf_style = _performance_color(duration)
                    
                    logger.bind(
                        operation=name,
                        duration_ms=round(duration * 1000, 2),
                        status="success",
                        **extra_context
                    ).log(
                        log_level,
                        f"[ctx.operation]{name}[/] completed in [{perf_style}]{duration_str}[/]"
                    )
                    return result
                except Exception as e:
                    duration = (datetime.now(timezone.utc) - start_time).total_seconds()
                    duration_str = _format_duration(duration)
                    
                    logger.bind(
                        operation=name,
                        duration_ms=round(duration * 1000, 2),
                        status="error",
                        error=str(e),
                        exception_type=type(e).__name__,
                        **extra_context
                    ).error(
                        f"[ctx.operation]{name}[/] failed after [perf.slow]{duration_str}[/]: {e}"
                    )
                    raise
            return async_wrapper  # type: ignore
        else:
            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = datetime.now(timezone.utc)
                
                # Optional argument logging for debugging
                extra_context = {}
                if log_args and _ENVIRONMENT == Environment.DEVELOPMENT:
                    extra_context["args_count"] = len(args)
                    extra_context["kwargs_keys"] = list(kwargs.keys())
                
                try:
                    result = func(*args, **kwargs)
                    duration = (datetime.now(timezone.utc) - start_time).total_seconds()
                    duration_str = _format_duration(duration)
                    perf_style = _performance_color(duration)
                    
                    logger.bind(
                        operation=name,
                        duration_ms=round(duration * 1000, 2),
                        status="success",
                        **extra_context
                    ).log(
                        log_level,
                        f"[ctx.operation]{name}[/] completed in [{perf_style}]{duration_str}[/]"
                    )
                    return result
                except Exception as e:
                    duration = (datetime.now(timezone.utc) - start_time).total_seconds()
                    duration_str = _format_duration(duration)
                    
                    logger.bind(
                        operation=name,
                        duration_ms=round(duration * 1000, 2),
                        status="error",
                        error=str(e),
                        exception_type=type(e).__name__,
                        **extra_context
                    ).error(
                        f"[ctx.operation]{name}[/] failed after [perf.slow]{duration_str}[/]: {e}"
                    )
                    raise
            return sync_wrapper  # type: ignore
    return decorator


def catch_and_log(
    *,
    reraise: bool = True,
    level: Union[str, LogLevel] = LogLevel.ERROR,
    message: Optional[str] = None,
    suppress_types: Optional[Tuple[type, ...]] = None
):
    """Enhanced decorator to catch and log exceptions with filtering."""
    def decorator(func: F) -> F:
        func_name = f"{func.__module__}.{func.__qualname__}"
        default_message = message or f"Exception in {func_name}"
        log_level = level.value if isinstance(level, LogLevel) else level
        
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    # Optional exception type suppression
                    if suppress_types and isinstance(e, suppress_types):
                        logger.debug(f"Suppressed {type(e).__name__} in {func_name}")
                        if reraise:
                            raise
                        return None
                    
                    logger.bind(
                        function=func_name,
                        exception_type=type(e).__name__,
                        exception_module=type(e).__module__,
                    ).opt(exception=True).log(log_level, f"{default_message}: {e}")
                    
                    if reraise:
                        raise
                    return None
            return async_wrapper  # type: ignore
        else:
            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Optional exception type suppression
                    if suppress_types and isinstance(e, suppress_types):
                        logger.debug(f"Suppressed {type(e).__name__} in {func_name}")
                        if reraise:
                            raise
                        return None
                    
                    logger.bind(
                        function=func_name,
                        exception_type=type(e).__name__,
                        exception_module=type(e).__module__,
                    ).opt(exception=True).log(log_level, f"{default_message}: {e}")
                    
                    if reraise:
                        raise
                    return None
            return sync_wrapper  # type: ignore
    return decorator


# === ProxyWhirl Domain-Specific Logging ===

def log_proxy_operation(proxy_host: str, proxy_port: int, operation: str, **kwargs: Any) -> None:
    """Log proxy-specific operations with semantic formatting."""
    logger.bind(
        proxy_host=proxy_host,
        proxy_port=proxy_port,
        proxy_endpoint=f"{proxy_host}:{proxy_port}",
        operation=operation,
        **kwargs
    ).info(
        f"Proxy operation: [proxy.host]{proxy_host}[/]:[proxy.port]{proxy_port}[/] - {operation}"
    )


def log_api_request(method: str, endpoint: str, user: Optional[str] = None, **kwargs: Any) -> None:
    """Log API requests with semantic formatting and status colors."""
    status_code = kwargs.get("status_code", 200)
    status_class = status_code // 100 if isinstance(status_code, int) else 2
    
    # Choose appropriate color based on HTTP status
    method_style = f"api.method.{method.lower()}" if method.lower() in ["get", "post", "put", "delete"] else "api.method.get"
    status_style = f"api.status.{status_class}xx" if status_class in [2, 4, 5] else "api.status.2xx"
    
    logger.bind(
        api_method=method,
        api_endpoint=endpoint,
        api_user=user,
        **kwargs
    ).info(
        f"API [{method_style}]{method}[/] [cyan]{endpoint}[/]"
        f"{f' [ctx.user]({user})[/]' if user else ''}"
        f"{f' [{status_style}]{status_code}[/]' if 'status_code' in kwargs else ''}"
    )


def log_cache_operation(cache_type: str, operation: str, count: int = 0, **kwargs: Any) -> None:
    """Log cache operations with structured context."""
    logger.bind(
        cache_type=cache_type,
        cache_operation=operation,
        cache_count=count,
        **kwargs
    ).debug(f"Cache [{cache_type}] {operation}: [perf.count]{count}[/] items")


def log_validation_result(
    proxy_host: str, 
    proxy_port: int, 
    success: bool, 
    duration: Optional[float] = None, 
    **kwargs: Any
) -> None:
    """Log proxy validation results with performance context."""
    status_style = "proxy.status.active" if success else "proxy.status.inactive"
    result_text = "✓ VALID" if success else "✗ INVALID"
    
    duration_text = ""
    if duration is not None:
        duration_str = _format_duration(duration)
        perf_style = _performance_color(duration)
        duration_text = f" in [{perf_style}]{duration_str}[/]"
    
    logger.bind(
        proxy_host=proxy_host,
        proxy_port=proxy_port,
        validation_success=success,
        validation_duration_ms=round(duration * 1000, 2) if duration else None,
        **kwargs
    ).log(
        "SUCCESS" if success else "WARNING",
        f"Validation: [proxy.host]{proxy_host}[/]:[proxy.port]{proxy_port}[/] [{status_style}]{result_text}[/]{duration_text}"
    )


# === High-Volume Sampling ===

class LogSampler:
    """Smart log sampling for high-volume operations."""
    
    def __init__(self, sample_rate: float = 0.1, burst_allowance: int = 5) -> None:
        self.sample_rate = max(0.0, min(1.0, sample_rate))
        self.burst_allowance = burst_allowance
        self._counter = 0
        self._burst_count = 0
    
    def should_log(self) -> bool:
        """Determine if this log entry should be recorded with burst handling."""
        self._counter += 1
        
        # Always allow initial burst
        if self._burst_count < self.burst_allowance:
            self._burst_count += 1
            return True
        
        # Then apply sampling
        if self.sample_rate >= 1.0:
            return True
        
        return (self._counter % int(1 / self.sample_rate)) == 0


# Global samplers with smart defaults
_proxy_validation_sampler = LogSampler(0.05, burst_allowance=10)  # 5% with 10 burst
_api_request_sampler = LogSampler(0.1, burst_allowance=20)  # 10% with 20 burst
_cache_operation_sampler = LogSampler(0.02, burst_allowance=5)  # 2% with 5 burst


def should_sample_validation() -> bool:
    """Check if proxy validation should be logged."""
    return _proxy_validation_sampler.should_log()


def should_sample_api_request() -> bool:
    """Check if API request should be logged."""
    return _api_request_sampler.should_log()


def should_sample_cache_operation() -> bool:
    """Check if cache operation should be logged."""
    return _cache_operation_sampler.should_log()


# === Configuration Helpers ===

def setup_logger(
    level: Union[str, LogLevel] = LogLevel.INFO,
    file_path: Optional[Union[str, Path]] = None,
    rich_enabled: bool = True,
    environment: Optional[Environment] = None
) -> None:
    """Setup logger with enhanced configuration options."""
    # Re-setup with new configuration
    _setup_enhanced_logger()


def get_logger(name: Optional[str] = None, **context: Any):
    """Get a logger instance with optional context binding."""
    bound_logger = logger.bind(logger_name=name, **context) if name or context else logger
    return bound_logger


def configure_rich_logging(enabled: bool = True) -> None:
    """Configure Rich logging integration."""
    if enabled:
        setup_logger(rich_enabled=True)
    else:
        # Simple setup without Rich
        logger.remove()
        logger.add(
            sys.stderr,
            format="{time:MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=os.getenv("PROXYWHIRL_LOG_LEVEL", "INFO"),
            colorize=False,
        )


# === Global Logger Enhancement ===

# Bind global application context to logger
logger = logger.bind(
    application="proxywhirl",
    environment=_ENVIRONMENT.value,
    version=os.getenv("PROXYWHIRL_VERSION", "1.0.0"),
)


# === Auto-Configuration ===
# Automatically configure the enhanced logger when this module is imported
# This ensures users only need `from loguru import logger` to get ProxyWhirl enhancements

_logger_configured = False

def _auto_configure_logger():
    """Automatically configure the ProxyWhirl enhanced logger on import."""
    global _logger_configured
    
    if _logger_configured:
        return
        
    try:
        # Auto-configure with smart defaults
        setup_logger()
        _logger_configured = True
        
        # Add a subtle startup message only in development
        env = _detect_environment()
        if env == Environment.DEVELOPMENT:
            logger.debug("🔧 ProxyWhirl enhanced logger auto-configured")
    except Exception:
        # If auto-configuration fails, fall back silently
        # This ensures we never break the user's import
        pass

# Auto-configure when module is imported
_auto_configure_logger()


# === Exports ===

__all__ = [
    "logger",
    "setup_logger",
    "get_logger",
    "configure_rich_logging",
    "log_performance",
    "catch_and_log",
    "log_operation",
    "log_operation_async",
    "bind_context", 
    "bind_context_async",
    "log_proxy_operation",
    "log_api_request",
    "log_cache_operation",
    "log_validation_result",
    "should_sample_validation",
    "should_sample_api_request", 
    "should_sample_cache_operation",
    "LogLevel",
    "Environment",
    "LogSampler",
]


# === Demo (when run directly) ===

if __name__ == "__main__":
    # Demo the enhanced logger capabilities
    logger.info("🚀 [bright_cyan]ProxyWhirl Enhanced Logger Demo[/]")
    logger.success("✅ [bright_green]Logger initialization completed successfully[/]")
    
    # Test structured logging with context
    with bind_context(demo=True, version="1.0.0"):
        logger.info("📝 Structured logging with context")
        
        # Test operation tracking
        with log_operation("demo_operation", task="showcase_features"):
            import time
            logger.info("⚙️  Performing demo operation...")
            time.sleep(0.1)  # Simulate work
            logger.debug("🔍 Debug information during operation")
    
    # Test domain-specific logging
    log_proxy_operation("127.0.0.1", 8080, "validation", status="active")
    log_api_request("GET", "/api/proxies", user="demo_user", status_code=200)
    log_cache_operation("memory", "store", count=42)
    log_validation_result("192.168.1.1", 3128, success=True, duration=0.05)
    
    # Test performance decorator
    @log_performance("demo_function", level=LogLevel.INFO)
    def demo_function():
        import time
        time.sleep(0.02)
        return "demo result"
    
    result = demo_function()
    
    # Test sampling
    if should_sample_validation():
        logger.info("🎯 Sampled validation log (would normally be filtered)")
    
    logger.success("🎉 [bold green]Demo completed - ProxyWhirl logger is ready![/]")
