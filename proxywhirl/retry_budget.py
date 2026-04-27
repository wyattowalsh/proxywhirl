"""Retry budget management for request retries."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from loguru import logger


@dataclass
class RetryBudgetStats:
    """Statistics for retry budget usage."""

    total_requests: int = 0
    total_retries: int = 0
    successful_retries: int = 0
    failed_retries: int = 0
    budget_exhausted_count: int = 0
    last_reset_time: float = field(default_factory=time.time)


class RetryBudget:
    """
    Manage retry budget to prevent excessive retries.

    Implements budget patterns:
    - Global retry budget (e.g., 1000 retries/minute)
    - Per-request limit (e.g., max 3 retries per request)
    - Automatic budget reset
    """

    def __init__(
        self,
        total_budget_per_minute: int = 1000,
        max_retries_per_request: int = 3,
        reset_interval_seconds: int = 60,
    ):
        """
        Initialize retry budget.

        Args:
            total_budget_per_minute: Total retries allowed per minute
            max_retries_per_request: Maximum retries for a single request
            reset_interval_seconds: Time between budget resets
        """
        self.total_budget_per_minute = total_budget_per_minute
        self.max_retries_per_request = max_retries_per_request
        self.reset_interval_seconds = reset_interval_seconds
        self.stats = RetryBudgetStats()
        self.current_budget = total_budget_per_minute

    def check_retry_allowed(self, attempt_count: int = 1) -> tuple[bool, str]:
        """
        Check if a retry is allowed under budget.

        Args:
            attempt_count: Current attempt number (1-based)

        Returns:
            Tuple of (is_allowed, reason_message)
        """
        self._reset_if_needed()

        # Check per-request limit
        if attempt_count > self.max_retries_per_request:
            return False, f"Max retries per request exceeded: {attempt_count}/{self.max_retries_per_request}"

        # Check global budget
        if self.current_budget <= 0:
            self.stats.budget_exhausted_count += 1
            return False, f"Retry budget exhausted: {self.current_budget}/{self.total_budget_per_minute}"

        return True, "Retry allowed"

    def consume_retry(self, success: bool = False) -> None:
        """
        Consume one retry from the budget.

        Args:
            success: Whether the retry was successful
        """
        self._reset_if_needed()

        if self.current_budget > 0:
            self.current_budget -= 1

        self.stats.total_retries += 1
        if success:
            self.stats.successful_retries += 1
        else:
            self.stats.failed_retries += 1

    def consume_request(self, retries_used: int = 0) -> None:
        """
        Record a request and its retries.

        Args:
            retries_used: Number of retries used for this request
        """
        self._reset_if_needed()
        self.stats.total_requests += 1
        if retries_used > 0:
            self.current_budget = max(0, self.current_budget - retries_used)

    def reset_budget(self) -> None:
        """Reset the retry budget to full."""
        self.current_budget = self.total_budget_per_minute
        self.stats = RetryBudgetStats()

    def get_stats(self) -> dict[str, int | float]:
        """
        Get budget statistics.

        Returns:
            Dictionary with budget stats
        """
        return {
            "total_requests": self.stats.total_requests,
            "total_retries": self.stats.total_retries,
            "successful_retries": self.stats.successful_retries,
            "failed_retries": self.stats.failed_retries,
            "budget_exhausted_count": self.stats.budget_exhausted_count,
            "current_budget": self.current_budget,
            "budget_limit": self.total_budget_per_minute,
        }

    def get_retry_success_rate(self) -> float:
        """
        Get success rate of retries.

        Returns:
            Success rate as percentage (0-100)
        """
        if self.stats.total_retries == 0:
            return 100.0
        return (self.stats.successful_retries / self.stats.total_retries) * 100

    def _reset_if_needed(self) -> None:
        """Reset budget if interval has passed."""
        now = time.time()
        if now - self.stats.last_reset_time > self.reset_interval_seconds:
            self.reset_budget()
            self.stats.last_reset_time = now
