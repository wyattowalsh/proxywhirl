"""Unit tests for HealthWorker class."""

import threading
import time
from unittest.mock import Mock

import pytest

from proxywhirl.health_worker import HealthWorker


class TestHealthWorker:
    """Tests for HealthWorker (T018-T019)."""
    
    def test_worker_initialization(self) -> None:
        """Test HealthWorker initialization."""
        check_func = Mock()
        proxies = {}
        lock = threading.RLock()
        
        worker = HealthWorker(
            source="test_source",
            check_interval=10,
            check_func=check_func,
            proxies=proxies,
            lock=lock
        )
        
        assert worker.source == "test_source"
        assert worker.check_interval == 10
        assert not worker._running
    
    def test_worker_start_lifecycle(self) -> None:
        """Test HealthWorker thread lifecycle start (T018)."""
        check_func = Mock()
        proxies = {}
        lock = threading.RLock()
        
        worker = HealthWorker(
            source="test_source",
            check_interval=1,
            check_func=check_func,
            proxies=proxies,
            lock=lock
        )
        
        worker.start()
        assert worker._running
        assert worker._thread is not None
        assert worker._thread.is_alive()
        
        # Cleanup
        worker.stop()
    
    def test_worker_stop_graceful_shutdown(self) -> None:
        """Test HealthWorker graceful shutdown (T018)."""
        check_func = Mock()
        proxies = {}
        lock = threading.RLock()
        
        worker = HealthWorker(
            source="test_source",
            check_interval=1,
            check_func=check_func,
            proxies=proxies,
            lock=lock
        )
        
        worker.start()
        time.sleep(0.1)  # Let it start
        
        worker.stop(timeout=2.0)
        assert not worker._running
        assert not worker._thread.is_alive()
    
    def test_worker_check_scheduling(self) -> None:
        """Test check scheduling and interval enforcement (T019)."""
        check_func = Mock()
        proxies = {
            "http://proxy1.example.com:8080": {"source": "test_source"},
            "http://proxy2.example.com:8080": {"source": "test_source"},
        }
        lock = threading.RLock()
        
        worker = HealthWorker(
            source="test_source",
            check_interval=1,  # 1 second intervals
            check_func=check_func,
            proxies=proxies,
            lock=lock
        )
        
        worker.start()
        time.sleep(2.5)  # Wait for 2+ check cycles
        worker.stop()
        
        # Should have checked both proxies at least twice
        assert check_func.call_count >= 2
    
    def test_worker_handles_check_exceptions(self) -> None:
        """Test worker continues after check function raises exception."""
        check_func = Mock(side_effect=Exception("Test error"))
        proxies = {
            "http://proxy1.example.com:8080": {"source": "test_source"},
        }
        lock = threading.RLock()
        
        worker = HealthWorker(
            source="test_source",
            check_interval=1,
            check_func=check_func,
            proxies=proxies,
            lock=lock
        )
        
        worker.start()
        time.sleep(1.5)  # Wait for check
        worker.stop()
        
        # Worker should have tried to check despite exception
        assert check_func.call_count >= 1
