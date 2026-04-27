"""Task scheduling and execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable

from loguru import logger


class TaskStatus(str, Enum):
    """Task status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Task:
    """Scheduled task."""

    name: str
    callback: Callable
    scheduled_time: datetime
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    retry_count: int = 0
    max_retries: int = 3
    result: Any = None
    error: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_ready(self) -> bool:
        """Check if task is ready to run.

        Returns:
            True if ready
        """
        return (
            self.status == TaskStatus.PENDING
            and datetime.now() >= self.scheduled_time
        )

    def can_retry(self) -> bool:
        """Check if can retry.

        Returns:
            True if can retry
        """
        return self.retry_count < self.max_retries


class TaskScheduler:
    """Schedules and executes tasks."""

    def __init__(self, max_workers: int = 5):
        """Initialize scheduler.

        Args:
            max_workers: Maximum concurrent workers
        """
        self.max_workers = max_workers
        self._tasks: list[Task] = []
        self._running_count = 0
        self._stats = {
            "total_scheduled": 0,
            "total_completed": 0,
            "total_failed": 0,
            "total_cancelled": 0,
        }

    def schedule(
        self,
        name: str,
        callback: Callable,
        delay_seconds: float = 0,
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
    ) -> Task:
        """Schedule a task.

        Args:
            name: Task name
            callback: Callback function
            delay_seconds: Delay before execution
            priority: Task priority
            max_retries: Maximum retries

        Returns:
            Task object
        """
        scheduled_time = datetime.now() + timedelta(seconds=delay_seconds)

        task = Task(
            name=name,
            callback=callback,
            scheduled_time=scheduled_time,
            priority=priority,
            max_retries=max_retries,
        )

        self._tasks.append(task)
        self._stats["total_scheduled"] += 1

        logger.info(f"Scheduled task: {name}")

        return task

    def get_ready_tasks(self) -> list[Task]:
        """Get all ready tasks.

        Returns:
            List of ready tasks
        """
        ready = [task for task in self._tasks if task.is_ready()]
        ready.sort(key=lambda t: t.priority.value, reverse=True)

        return ready

    def execute_task(self, task: Task) -> bool:
        """Execute a task.

        Args:
            task: Task to execute

        Returns:
            True if succeeded
        """
        if self._running_count >= self.max_workers:
            logger.warning("Max workers reached, queuing task")
            return False

        task.status = TaskStatus.RUNNING
        self._running_count += 1

        try:
            result = task.callback()
            task.result = result
            task.status = TaskStatus.COMPLETED
            self._stats["total_completed"] += 1

            logger.info(f"Task completed: {task.name}")

            return True
        except Exception as e:
            logger.error(f"Task failed: {task.name} - {e}")

            if task.can_retry():
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                logger.info(f"Task queued for retry: {task.name} (attempt {task.retry_count})")
            else:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                self._stats["total_failed"] += 1

            return False
        finally:
            self._running_count -= 1

    def cancel_task(self, task: Task) -> bool:
        """Cancel a task.

        Args:
            task: Task to cancel

        Returns:
            True if cancelled
        """
        if task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            self._stats["total_cancelled"] += 1

            logger.info(f"Task cancelled: {task.name}")

            return True

        return False

    def get_task_by_name(self, name: str) -> Task | None:
        """Get task by name.

        Args:
            name: Task name

        Returns:
            Task or None
        """
        for task in self._tasks:
            if task.name == name:
                return task

        return None

    def get_stats(self) -> dict[str, int]:
        """Get scheduler stats.

        Returns:
            Stats dict
        """
        return {
            **self._stats,
            "pending_tasks": len([t for t in self._tasks if t.status == TaskStatus.PENDING]),
            "running_tasks": self._running_count,
        }

    def clear_completed(self) -> int:
        """Clear completed and failed tasks.

        Returns:
            Number of tasks cleared
        """
        before = len(self._tasks)

        self._tasks = [
            t for t in self._tasks
            if t.status not in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)
        ]

        cleared = before - len(self._tasks)
        logger.info(f"Cleared {cleared} completed/failed tasks")

        return cleared


class CronScheduler:
    """Cron-like task scheduler."""

    def __init__(self):
        """Initialize cron scheduler."""
        self._cron_tasks: dict[str, Task] = {}

    def add_cron(
        self,
        name: str,
        callback: Callable,
        hour: int | None = None,
        minute: int | None = None,
    ) -> None:
        """Add cron task.

        Args:
            name: Task name
            callback: Callback function
            hour: Hour (0-23)
            minute: Minute (0-59)
        """
        task = Task(
            name=name,
            callback=callback,
            scheduled_time=datetime.now(),
            metadata={
                "hour": hour,
                "minute": minute,
            },
        )

        self._cron_tasks[name] = task
        logger.info(f"Added cron task: {name} at {hour}:{minute}")

    def should_run(self, task: Task) -> bool:
        """Check if cron task should run.

        Args:
            task: Cron task

        Returns:
            True if should run
        """
        hour = task.metadata.get("hour")
        minute = task.metadata.get("minute")

        now = datetime.now()

        if hour is not None and now.hour != hour:
            return False

        return not (minute is not None and now.minute != minute)
