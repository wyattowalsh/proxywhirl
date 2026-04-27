"""Tests for CLI batch operations."""

import pytest

from proxywhirl.cli_batch import BatchOperation, FileBatchProcessor


class TestBatchOperation:
    """Test batch operations."""

    def test_execute_batch(self):
        """Test batch execution."""
        operation = BatchOperation(lambda x: x * 2)
        results = operation.execute([1, 2, 3])
        assert results == [2, 4, 6]

    def test_batch_error_handling(self):
        """Test error handling."""

        def failing_op(x):
            if x == 2:
                raise ValueError("test error")
            return x

        operation = BatchOperation(failing_op)
        results = operation.execute([1, 2, 3], stop_on_error=False)
        assert 1 in results
        assert 3 in results
        assert len(operation.errors) == 1

    def test_batch_summary(self):
        """Test summary generation."""
        operation = BatchOperation(lambda x: x)
        operation.execute([1, 2, 3])
        summary = operation.get_summary()
        assert summary["successful"] == 3
        assert summary["failed"] == 0
