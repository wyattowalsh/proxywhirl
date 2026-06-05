"""Error handling and recovery strategies."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from loguru import logger


class RecoveryStrategy(str, Enum):
    """Recovery strategies for errors."""

    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAK = "circuit_break"
    SKIP = "skip"
    ABORT = "abort"


@dataclass
class ErrorContext:
    """Context for an error."""

    error: Exception
    attempt: int
    max_attempts: int
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryAction:
    """Action to take for recovery."""

    strategy: RecoveryStrategy
    delay_seconds: float = 0.0
    message: str = ""


class ErrorHandler:
    """Handles errors and selects recovery strategy."""

    def __init__(self):
        """Initialize handler."""
        self._handlers: dict[type, Callable] = {}
        self._recovery_strategies: dict[type, RecoveryStrategy] = {}

    def register_handler(
        self, error_type: type, handler: Callable[[ErrorContext], RecoveryAction]
    ) -> None:
        """Register error handler.

        Args:
            error_type: Exception type
            handler: Handler function
        """
        self._handlers[error_type] = handler

    def register_strategy(self, error_type: type, strategy: RecoveryStrategy) -> None:
        """Register recovery strategy for error type.

        Args:
            error_type: Exception type
            strategy: Recovery strategy
        """
        self._recovery_strategies[error_type] = strategy

    def handle_error(self, context: ErrorContext) -> RecoveryAction:
        """Handle an error.

        Args:
            context: Error context

        Returns:
            Recovery action
        """
        error_type = type(context.error)

        # Check for specific handler
        if error_type in self._handlers:
            try:
                return self._handlers[error_type](context)
            except Exception as e:
                logger.warning(f"Handler error: {e}")

        # Check for strategy
        if error_type in self._recovery_strategies:
            strategy = self._recovery_strategies[error_type]
            return RecoveryAction(strategy=strategy)

        # Default strategy
        if context.attempt < context.max_attempts:
            return RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                delay_seconds=min(2**context.attempt, 60),
            )
        else:
            return RecoveryAction(strategy=RecoveryStrategy.ABORT)


class ErrorRecovery:
    """Manages error recovery."""

    def __init__(self, max_attempts: int = 3):
        """Initialize recovery manager.

        Args:
            max_attempts: Maximum retry attempts
        """
        self.max_attempts = max_attempts
        self._handler = ErrorHandler()
        self._error_history: list[ErrorContext] = []

    def add_handler(
        self, error_type: type, handler: Callable[[ErrorContext], RecoveryAction]
    ) -> None:
        """Add error handler.

        Args:
            error_type: Exception type
            handler: Handler function
        """
        self._handler.register_handler(error_type, handler)

    def add_strategy(self, error_type: type, strategy: RecoveryStrategy) -> None:
        """Add recovery strategy.

        Args:
            error_type: Exception type
            strategy: Recovery strategy
        """
        self._handler.register_strategy(error_type, strategy)

    def recover_from(
        self,
        error: Exception,
        attempt: int = 1,
        metadata: dict[str, Any] | None = None,
    ) -> RecoveryAction:
        """Recover from error.

        Args:
            error: Exception
            attempt: Attempt number
            metadata: Additional context

        Returns:
            Recovery action
        """
        context = ErrorContext(
            error=error,
            attempt=attempt,
            max_attempts=self.max_attempts,
            metadata=metadata or {},
        )

        self._error_history.append(context)

        action = self._handler.handle_error(context)
        logger.info(f"Error recovery: {error.__class__.__name__} -> {action.strategy.value}")

        return action

    def get_error_history(self) -> list[ErrorContext]:
        """Get error history.

        Returns:
            List of error contexts
        """
        return self._error_history.copy()

    def get_frequent_errors(self, limit: int = 5) -> dict[type, int]:
        """Get most frequent errors.

        Args:
            limit: Top N errors to return

        Returns:
            Dict of error type -> count
        """
        error_counts: dict[type, int] = {}

        for context in self._error_history:
            error_type = type(context.error)
            error_counts[error_type] = error_counts.get(error_type, 0) + 1

        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_errors[:limit])

    def clear_history(self) -> None:
        """Clear error history."""
        self._error_history.clear()


class CircuitBreakerRecovery:
    """Recovery using circuit breaker pattern."""

    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        """Initialize circuit breaker recovery.

        Args:
            failure_threshold: Failures before opening
            timeout_seconds: Timeout before half-open
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self._failure_count = 0
        self._last_failure_time: datetime | None = None
        self._state = "closed"  # closed, open, half_open

    def record_failure(self) -> None:
        """Record a failure."""
        self._failure_count += 1
        self._last_failure_time = datetime.now()

        if self._failure_count >= self.failure_threshold:
            self._state = "open"
            logger.warning(f"Circuit breaker opened after {self._failure_count} failures")

    def record_success(self) -> None:
        """Record a success."""
        if self._state == "half_open":
            self._state = "closed"
            self._failure_count = 0
            logger.info("Circuit breaker closed after successful recovery")

    def is_open(self) -> bool:
        """Check if circuit breaker is open.

        Returns:
            True if open
        """
        if self._state == "open":
            # Check if timeout expired
            if self._last_failure_time:
                elapsed = (datetime.now() - self._last_failure_time).total_seconds()
                if elapsed > self.timeout_seconds:
                    self._state = "half_open"
                    logger.info("Circuit breaker half-open, trying recovery")
                    return False
            return True

        return False

    def is_half_open(self) -> bool:
        """Check if circuit breaker is half-open.

        Returns:
            True if half-open
        """
        return self._state == "half_open"

    def reset(self) -> None:
        """Reset circuit breaker."""
        self._failure_count = 0
        self._last_failure_time = None
        self._state = "closed"
        logger.info("Circuit breaker reset")
