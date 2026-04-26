"""Tests for deadletter module."""

from proxywhirl.deadletter import DeadLetterQueue, FailureReason


class TestDeadLetterQueue:
    """Test dead-letter queue."""

    def test_add_proxy(self):
        """Test adding proxy to queue."""
        queue = DeadLetterQueue()

        entry = queue.add(
            "http://proxy.com:8080",
            FailureReason.MAX_RETRIES_EXCEEDED,
            "Max retries exceeded",
        )

        assert entry.proxy_url == "http://proxy.com:8080"
        assert entry.reason == FailureReason.MAX_RETRIES_EXCEEDED
        assert entry.failure_count == 1

    def test_add_duplicate_proxy(self):
        """Test adding duplicate proxy increments failure count."""
        queue = DeadLetterQueue()
        proxy_url = "http://proxy.com:8080"

        entry1 = queue.add(proxy_url, FailureReason.MAX_RETRIES_EXCEEDED, "Error 1")
        entry2 = queue.add(proxy_url, FailureReason.CONNECTION_TIMEOUT, "Error 2")

        assert entry2.proxy_url == proxy_url
        assert entry2.failure_count == 2
        assert entry2.reason == FailureReason.CONNECTION_TIMEOUT
        assert len(queue) == 1

    def test_get_proxy(self):
        """Test getting proxy from queue."""
        queue = DeadLetterQueue()
        proxy_url = "http://proxy.com:8080"

        queue.add(proxy_url, FailureReason.MAX_RETRIES_EXCEEDED, "Error")
        entry = queue.get(proxy_url)

        assert entry is not None
        assert entry.proxy_url == proxy_url

    def test_get_nonexistent_proxy(self):
        """Test getting nonexistent proxy returns None."""
        queue = DeadLetterQueue()

        entry = queue.get("http://nonexistent.com:8080")
        assert entry is None

    def test_remove_proxy(self):
        """Test removing proxy from queue."""
        queue = DeadLetterQueue()
        proxy_url = "http://proxy.com:8080"

        queue.add(proxy_url, FailureReason.MAX_RETRIES_EXCEEDED, "Error")
        assert queue.remove(proxy_url) is True
        assert queue.get(proxy_url) is None

    def test_list_entries(self):
        """Test listing entries."""
        queue = DeadLetterQueue()

        queue.add(
            "http://proxy1.com:8080", FailureReason.MAX_RETRIES_EXCEEDED, "Error", pool_id="pool1"
        )
        queue.add(
            "http://proxy2.com:8080", FailureReason.CONNECTION_TIMEOUT, "Error", pool_id="pool1"
        )
        queue.add(
            "http://proxy3.com:8080", FailureReason.MAX_RETRIES_EXCEEDED, "Error", pool_id="pool2"
        )

        all_entries = queue.list_entries()
        assert len(all_entries) == 3

        pool1_entries = queue.list_entries(pool_id="pool1")
        assert len(pool1_entries) == 2

        retry_entries = queue.list_entries(reason=FailureReason.MAX_RETRIES_EXCEEDED)
        assert len(retry_entries) == 2

    def test_list_with_limit(self):
        """Test listing with limit."""
        queue = DeadLetterQueue()

        for i in range(5):
            queue.add(f"http://proxy{i}.com:8080", FailureReason.MAX_RETRIES_EXCEEDED, "Error")

        entries = queue.list_entries(limit=2)
        assert len(entries) == 2

    def test_clear_queue(self):
        """Test clearing queue."""
        queue = DeadLetterQueue()

        queue.add("http://proxy1.com:8080", FailureReason.MAX_RETRIES_EXCEEDED, "Error")
        queue.add("http://proxy2.com:8080", FailureReason.MAX_RETRIES_EXCEEDED, "Error")

        cleared_count = queue.clear()
        assert cleared_count == 2
        assert len(queue) == 0

    def test_max_queue_size(self):
        """Test max queue size enforcement."""
        queue = DeadLetterQueue(max_queue_size=3)

        queue.add("http://proxy1.com:8080", FailureReason.MAX_RETRIES_EXCEEDED, "Error")
        queue.add("http://proxy2.com:8080", FailureReason.MAX_RETRIES_EXCEEDED, "Error")
        queue.add("http://proxy3.com:8080", FailureReason.MAX_RETRIES_EXCEEDED, "Error")
        queue.add("http://proxy4.com:8080", FailureReason.MAX_RETRIES_EXCEEDED, "Error")

        assert len(queue) == 3
        assert queue.get("http://proxy1.com:8080") is None

    def test_iterate_queue(self):
        """Test iterating over queue."""
        queue = DeadLetterQueue()

        for i in range(3):
            queue.add(f"http://proxy{i}.com:8080", FailureReason.MAX_RETRIES_EXCEEDED, "Error")

        count = 0
        for entry in queue:
            count += 1
            assert entry.proxy_url.startswith("http://proxy")

        assert count == 3
