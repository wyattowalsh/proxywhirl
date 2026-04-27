"""Batch operations support for the CLI.

Provides utilities for executing batch commands on multiple files/resources.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from loguru import logger


class BatchOperation:
    """Represents a batch operation on multiple items.

    Example:
        >>> batch = BatchOperation(lambda proxy: validate(proxy))
        >>> results = batch.execute(proxies)
    """

    def __init__(self, operation: Callable[[Any], Any]) -> None:
        """Initialize batch operation.

        Args:
            operation: Function to apply to each item
        """
        self.operation = operation
        self.results: list[Any] = []
        self.errors: list[tuple[Any, Exception]] = []

    def execute(self, items: list[Any], stop_on_error: bool = False) -> list[Any]:
        """Execute operation on all items.

        Args:
            items: Items to process
            stop_on_error: Stop on first error if True

        Returns:
            List of results
        """
        self.results = []
        self.errors = []

        for item in items:
            try:
                result = self.operation(item)
                self.results.append(result)
            except Exception as e:
                logger.error(f"Batch operation failed for item {item}: {e}")
                self.errors.append((item, e))
                if stop_on_error:
                    raise

        return self.results

    def get_summary(self) -> dict[str, Any]:
        """Get execution summary.

        Returns:
            Dict with execution stats
        """
        return {
            "total_items": len(self.results) + len(self.errors),
            "successful": len(self.results),
            "failed": len(self.errors),
            "success_rate": (
                len(self.results) / (len(self.results) + len(self.errors)) * 100
                if self.results or self.errors
                else 0
            ),
        }


class FileBatchProcessor:
    """Process batch operations on files.

    Example:
        >>> processor = FileBatchProcessor()
        >>> results = processor.process_files("*.txt", lambda f: f.read_text())
    """

    @staticmethod
    def process_files(
        pattern: str,
        operation: Callable[[Path], Any],
        directory: str | Path = ".",
    ) -> list[Any]:
        """Process files matching pattern.

        Args:
            pattern: Glob pattern for files
            operation: Operation to apply to each file
            directory: Directory to search

        Returns:
            List of results
        """
        base_path = Path(directory)
        files = list(base_path.glob(pattern))

        batch = BatchOperation(operation)
        return batch.execute(files)


class QueryBatchProcessor:
    """Process batch queries on resources.

    Example:
        >>> processor = QueryBatchProcessor(proxy_pool)
        >>> results = processor.query_batch(["validate", "proxy-1", "proxy-2"])
    """

    def __init__(self, context: Any) -> None:
        """Initialize query processor.

        Args:
            context: Context object (pool, etc.)
        """
        self.context = context
        self.operations: dict[str, Callable[..., Any]] = {}

    def register_operation(
        self,
        name: str,
        operation: Callable[..., Any],
    ) -> None:
        """Register a batch operation.

        Args:
            name: Operation name
            operation: Callable
        """
        self.operations[name] = operation

    def execute_batch(
        self,
        operation_name: str,
        items: list[Any],
        **kwargs: Any,
    ) -> list[Any]:
        """Execute batch operation.

        Args:
            operation_name: Name of registered operation
            items: Items to process
            **kwargs: Additional arguments

        Returns:
            List of results
        """
        if operation_name not in self.operations:
            raise ValueError(f"Unknown operation: {operation_name}")

        operation = self.operations[operation_name]
        batch = BatchOperation(lambda item: operation(item, **kwargs))
        return batch.execute(items)
