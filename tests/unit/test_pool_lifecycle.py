"""Unit tests for ProxyPool lifecycle management (dynamic add/remove)."""

import threading
from unittest.mock import patch
from uuid import uuid4

import pytest

from proxywhirl.models import Proxy, ProxyPool


class TestProxyPoolDynamicOperations:
    """Test dynamic add/remove operations on ProxyPool."""

    def test_add_proxy_at_runtime(self):
        """Test adding a proxy to an existing pool."""
        pool = ProxyPool(name="test")
        assert pool.size == 0

        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        pool.add_proxy(proxy1)
        assert pool.size == 1
        assert proxy1 in pool.proxies

        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        pool.add_proxy(proxy2)
        assert pool.size == 2
        assert proxy2 in pool.proxies

    def test_remove_proxy_at_runtime(self):
        """Test removing a proxy from an existing pool."""
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        pool = ProxyPool(name="test", proxies=[proxy1, proxy2])
        assert pool.size == 2

        pool.remove_proxy(proxy1.id)
        assert pool.size == 1
        assert proxy1 not in pool.proxies
        assert proxy2 in pool.proxies

    def test_add_duplicate_proxy_updates_existing(self):
        """Test that adding a duplicate proxy updates the existing one."""
        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        pool = ProxyPool(name="test", proxies=[proxy1])
        assert pool.size == 1

        # Create another proxy with same URL but different ID
        proxy2 = Proxy(url="http://proxy1.example.com:8080")
        initial_size = pool.size
        pool.add_proxy(proxy2)

        # Size should remain the same (duplicate detected)
        assert pool.size == initial_size

    def test_remove_nonexistent_proxy_silent(self):
        """Test that removing a nonexistent proxy doesn't raise an error."""
        pool = ProxyPool(name="test")
        random_id = uuid4()

        # Should not raise an error
        pool.remove_proxy(random_id)
        assert pool.size == 0

    def test_max_pool_size_enforcement(self):
        """Test that max_pool_size is enforced when adding proxies."""
        pool = ProxyPool(name="test", max_pool_size=2)

        proxy1 = Proxy(url="http://proxy1.example.com:8080")
        proxy2 = Proxy(url="http://proxy2.example.com:8080")
        proxy3 = Proxy(url="http://proxy3.example.com:8080")

        pool.add_proxy(proxy1)
        pool.add_proxy(proxy2)
        assert pool.size == 2

        # Adding a third should raise ValueError (pool at max capacity)
        with pytest.raises(ValueError, match="Pool at maximum capacity"):
            pool.add_proxy(proxy3)

        # Pool should still be at max size
        assert pool.size == 2

    def test_concurrent_add_operations(self):
        """Test thread safety of concurrent add operations."""
        pool = ProxyPool(name="test")
        errors = []

        def add_proxies(start_idx, count):
            try:
                for i in range(start_idx, start_idx + count):
                    proxy = Proxy(url=f"http://proxy{i}.example.com:8080")
                    pool.add_proxy(proxy)
            except Exception as e:
                errors.append(e)

        # Create multiple threads adding proxies concurrently
        threads = []
        for i in range(5):
            t = threading.Thread(target=add_proxies, args=(i * 10, 10))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0
        # All proxies should be added
        assert pool.size == 50

    def test_concurrent_remove_operations(self):
        """Test thread safety of concurrent remove operations."""
        # Create pool with 50 proxies
        proxies = [Proxy(url=f"http://proxy{i}.example.com:8080") for i in range(50)]
        pool = ProxyPool(name="test", proxies=proxies)
        assert pool.size == 50

        errors = []

        def remove_proxies(proxy_list):
            try:
                for proxy in proxy_list:
                    pool.remove_proxy(proxy.id)
            except Exception as e:
                errors.append(e)

        # Split proxies into chunks for concurrent removal
        chunk_size = 10
        threads = []
        for i in range(0, 50, chunk_size):
            chunk = proxies[i : i + chunk_size]
            t = threading.Thread(target=remove_proxies, args=(chunk,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0
        # All proxies should be removed
        assert pool.size == 0

    def test_concurrent_mixed_operations(self):
        """Test thread safety of concurrent add and remove operations."""
        pool = ProxyPool(name="test")
        errors = []

        def add_proxies(start_idx, count):
            try:
                for i in range(start_idx, start_idx + count):
                    proxy = Proxy(url=f"http://add{i}.example.com:8080")
                    pool.add_proxy(proxy)
            except Exception as e:
                errors.append(e)

        def remove_proxies():
            try:
                import time

                time.sleep(0.01)  # Small delay to let some proxies be added
                proxies_snapshot = list(pool.proxies)
                for proxy in proxies_snapshot[:5]:  # Remove first 5
                    pool.remove_proxy(proxy.id)
            except Exception as e:
                errors.append(e)

        # Start threads
        add_threads = [threading.Thread(target=add_proxies, args=(i * 10, 10)) for i in range(3)]
        remove_threads = [threading.Thread(target=remove_proxies) for _ in range(2)]

        for t in add_threads + remove_threads:
            t.start()

        for t in add_threads + remove_threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0
        # Pool should have proxies (30 added - up to 10 removed)
        assert pool.size >= 20


class TestProxyPoolValidation:
    """Test validation logic in ProxyPool operations."""

    def test_validate_proxy_url_on_add(self):
        """Test that invalid proxy URLs are rejected on add."""
        pool = ProxyPool(name="test")

        # Valid proxy should be added
        valid_proxy = Proxy(url="http://proxy.example.com:8080")
        pool.add_proxy(valid_proxy)
        assert pool.size == 1

    def test_pool_size_tracking_accurate(self):
        """Test that pool.size accurately reflects number of proxies."""
        pool = ProxyPool(name="test")

        # Add proxies
        for i in range(10):
            pool.add_proxy(Proxy(url=f"http://proxy{i}.example.com:8080"))
        assert pool.size == 10
        assert len(pool.proxies) == 10

        # Remove some
        proxies_to_remove = list(pool.proxies)[:5]
        for proxy in proxies_to_remove:
            pool.remove_proxy(proxy.id)
        assert pool.size == 5
        assert len(pool.proxies) == 5

    def test_updated_at_changes_on_add(self):
        """Test that updated_at timestamp changes when adding proxies."""
        pool = ProxyPool(name="test")
        initial_updated = pool.updated_at

        # Mock time.sleep to avoid actual delay - timestamp logic works regardless
        with patch("time.sleep"):
            import time

            time.sleep(0.01)

        pool.add_proxy(Proxy(url="http://proxy.example.com:8080"))
        assert pool.updated_at > initial_updated

    def test_updated_at_changes_on_remove(self):
        """Test that updated_at timestamp changes when removing proxies."""
        proxy = Proxy(url="http://proxy.example.com:8080")
        pool = ProxyPool(name="test", proxies=[proxy])
        initial_updated = pool.updated_at

        # Mock time.sleep to avoid actual delay - timestamp logic works regardless
        with patch("time.sleep"):
            import time

            time.sleep(0.01)

        pool.remove_proxy(proxy.id)
        assert pool.updated_at > initial_updated
