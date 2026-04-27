"""Tests for CLI command history."""

import pytest

from proxywhirl.cli_history import CommandHistory


class TestCommandHistory:
    """Test command history."""

    def test_add_command(self):
        """Test adding command to history."""
        history = CommandHistory()
        history.add("test command")
        assert len(history.entries) == 1

    def test_search(self):
        """Test searching history."""
        history = CommandHistory()
        history.add("validate proxy")
        history.add("rotate pool")
        
        results = history.search("validate")
        assert len(results) > 0
        assert "validate" in results[0].command

    def test_get_recent(self):
        """Test getting recent commands."""
        history = CommandHistory()
        history.add("cmd1")
        history.add("cmd2")
        history.add("cmd3")
        
        recent = history.get_recent(2)
        assert len(recent) == 2

    def test_stats(self):
        """Test statistics."""
        history = CommandHistory()
        history.add("cmd1", exit_code=0)
        history.add("cmd2", exit_code=1)
        
        stats = history.get_stats()
        assert stats["total_commands"] == 2
        assert stats["success_count"] == 1
        assert stats["failure_count"] == 1
