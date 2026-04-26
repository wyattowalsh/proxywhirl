"""Performance profiling and optimization for proxywhirl.

Provides:
- Function-level performance profiling
- Bottleneck detection
- Memory profiling
- Performance metrics and reports
"""

from __future__ import annotations

import functools
import time
from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from loguru import logger

T = TypeVar("T")


@dataclass
class ProfileStats:
    """Performance statistics for a function."""

    function_name: str
    call_count: int = 0
    total_time_ms: float = 0.0
    min_time_ms: float = float("inf")
    max_time_ms: float = 0.0
    last_called: float = 0.0

    @property
    def avg_time_ms(self) -> float:
        """Average execution time."""
        if self.call_count == 0:
            return 0.0
        return self.total_time_ms / self.call_count

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "function_name": self.function_name,
            "call_count": self.call_count,
            "total_time_ms": round(self.total_time_ms, 2),
            "avg_time_ms": round(self.avg_time_ms, 2),
            "min_time_ms": round(self.min_time_ms, 2),
            "max_time_ms": round(self.max_time_ms, 2),
            "last_called": self.last_called,
        }


class PerformanceProfiler:
    """Performance profiler for functions and operations."""

    def __init__(self):
        """Initialize performance profiler."""
        self.stats: dict[str, ProfileStats] = {}
        self.enabled = True
        logger.info("Initialized PerformanceProfiler")

    def profile(
        self,
        func: Callable[..., T],
    ) -> Callable[..., T]:
        """Decorator to profile function performance.

        Args:
            func: Function to profile

        Returns:
            Wrapped function
        """

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            if not self.enabled:
                return func(*args, **kwargs)

            func_name = f"{func.__module__}.{func.__name__}"

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed_ms = (time.time() - start_time) * 1000
                self._record_call(func_name, elapsed_ms)

        return wrapper

    def _record_call(self, func_name: str, elapsed_ms: float) -> None:
        """Record function call timing.

        Args:
            func_name: Function name
            elapsed_ms: Elapsed time in milliseconds
        """
        if func_name not in self.stats:
            self.stats[func_name] = ProfileStats(function_name=func_name)

        stats = self.stats[func_name]
        stats.call_count += 1
        stats.total_time_ms += elapsed_ms
        stats.min_time_ms = min(stats.min_time_ms, elapsed_ms)
        stats.max_time_ms = max(stats.max_time_ms, elapsed_ms)
        stats.last_called = time.time()

        # Log slow calls
        if elapsed_ms > 1000:  # Warn on calls > 1 second
            logger.warning(f"Slow call: {func_name} took {elapsed_ms:.1f}ms")

    def get_stats(self, func_name: str | None = None) -> dict[str, Any] | list[dict[str, Any]]:
        """Get profiling statistics.

        Args:
            func_name: Specific function or None for all

        Returns:
            Statistics dictionary or list
        """
        if func_name:
            if func_name in self.stats:
                return self.stats[func_name].to_dict()
            return {}

        return [s.to_dict() for s in self.stats.values()]

    def get_slowest(self, count: int = 10) -> list[dict[str, Any]]:
        """Get slowest functions.

        Args:
            count: Number of functions to return

        Returns:
            List of slowest functions
        """
        sorted_stats = sorted(
            self.stats.values(),
            key=lambda s: s.avg_time_ms,
            reverse=True,
        )

        return [s.to_dict() for s in sorted_stats[:count]]

    def get_most_called(self, count: int = 10) -> list[dict[str, Any]]:
        """Get most called functions.

        Args:
            count: Number of functions to return

        Returns:
            List of most called functions
        """
        sorted_stats = sorted(
            self.stats.values(),
            key=lambda s: s.call_count,
            reverse=True,
        )

        return [s.to_dict() for s in sorted_stats[:count]]

    def reset(self) -> None:
        """Reset all statistics."""
        self.stats.clear()
        logger.info("Reset performance profiler statistics")

    def summary(self) -> dict[str, Any]:
        """Get profiler summary.

        Returns:
            Summary dictionary
        """
        if not self.stats:
            return {
                "functions_profiled": 0,
                "total_calls": 0,
                "total_time_ms": 0.0,
            }

        total_calls = sum(s.call_count for s in self.stats.values())
        total_time_ms = sum(s.total_time_ms for s in self.stats.values())

        return {
            "functions_profiled": len(self.stats),
            "total_calls": total_calls,
            "total_time_ms": round(total_time_ms, 2),
            "avg_call_time_ms": round(total_time_ms / total_calls, 2) if total_calls > 0 else 0,
            "slowest": self.get_slowest(5),
            "most_called": self.get_most_called(5),
        }


# Global profiler instance
_profiler: PerformanceProfiler | None = None


def get_profiler() -> PerformanceProfiler:
    """Get global profiler instance.

    Returns:
        Performance profiler
    """
    global _profiler
    if _profiler is None:
        _profiler = PerformanceProfiler()
    return _profiler


def profile_function(func: Callable[..., T]) -> Callable[..., T]:
    """Global profiling decorator.

    Args:
        func: Function to profile

    Returns:
        Wrapped function
    """
    profiler = get_profiler()
    return profiler.profile(func)


class TimerContext:
    """Context manager for timing code blocks."""

    def __init__(self, name: str = "operation"):
        """Initialize timer.

        Args:
            name: Operation name
        """
        self.name = name
        self.start_time = 0.0
        self.elapsed_ms = 0.0

    def __enter__(self) -> TimerContext:
        """Enter context."""
        self.start_time = time.time()
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context."""
        self.elapsed_ms = (time.time() - self.start_time) * 1000
        if self.elapsed_ms > 1000:  # Warn on slow operations
            logger.warning(f"Slow operation: {self.name} took {self.elapsed_ms:.1f}ms")
        else:
            logger.debug(f"Operation: {self.name} took {self.elapsed_ms:.1f}ms")
