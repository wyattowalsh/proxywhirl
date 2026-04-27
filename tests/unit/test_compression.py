"""Tests for compression module."""

import pytest

from proxywhirl.compression import CompressionConfig, CompressionManager, CompressionType


class TestCompressionManager:
    """Test compression handler."""

    def test_should_compress_large_payload(self):
        """Test compression decision for large payload."""
        handler = CompressionManager()
        data = b"x" * 2000

        assert handler.should_compress(data) is True

    def test_should_not_compress_small_payload(self):
        """Test no compression for small payload."""
        handler = CompressionManager()
        data = b"x" * 100

        assert handler.should_compress(data) is False

    def test_should_not_compress_disabled(self):
        """Test no compression when disabled."""
        config = CompressionConfig(enabled=False)
        handler = CompressionManager(config)
        data = b"x" * 2000

        assert handler.should_compress(data) is False

    def test_compress_gzip(self):
        """Test gzip compression."""
        handler = CompressionManager()
        data = b"test data" * 100

        compressed, algo = handler.compress(data, CompressionType.GZIP)
        assert len(compressed) < len(data)
        assert algo == CompressionType.GZIP

    def test_decompress_gzip(self):
        """Test gzip decompression."""
        handler = CompressionManager()
        data = b"test data" * 100

        compressed, _ = handler.compress(data, CompressionType.GZIP)
        decompressed = handler.decompress(compressed, CompressionType.GZIP)

        assert decompressed == data

    def test_compress_deflate(self):
        """Test deflate compression."""
        handler = CompressionManager()
        data = b"test data" * 100

        compressed, algo = handler.compress(data, CompressionType.DEFLATE)
        assert len(compressed) < len(data)
        assert algo == CompressionType.DEFLATE

    def test_decompress_deflate(self):
        """Test deflate decompression."""
        handler = CompressionManager()
        data = b"test data" * 100

        compressed, _ = handler.compress(data, CompressionType.DEFLATE)
        decompressed = handler.decompress(compressed, CompressionType.DEFLATE)

        assert decompressed == data

    def test_compress_none(self):
        """Test no compression."""
        handler = CompressionManager()
        data = b"test data"

        compressed, algo = handler.compress(data, CompressionType.NONE)
        assert compressed == data
        assert algo == CompressionType.NONE

    def test_unsupported_algorithm(self):
        """Test unsupported algorithm raises error."""
        config = CompressionConfig(supported_algorithms=[CompressionType.GZIP])
        handler = CompressionManager(config)
        data = b"test data"

        with pytest.raises(ValueError, match="not supported"):
            handler.compress(data, CompressionType.DEFLATE)

    def test_get_accept_encoding(self):
        """Test Accept-Encoding header."""
        config = CompressionConfig(
            enabled=True,
            supported_algorithms=[CompressionType.GZIP, CompressionType.DEFLATE],
        )
        handler = CompressionManager(config)

        header = handler.get_accept_encoding()
        assert "gzip" in header
        assert "deflate" in header

    def test_get_accept_encoding_disabled(self):
        """Test Accept-Encoding when disabled."""
        config = CompressionConfig(enabled=False)
        handler = CompressionManager(config)

        header = handler.get_accept_encoding()
        assert header == "identity"
