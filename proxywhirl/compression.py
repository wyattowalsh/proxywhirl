"""Request/response compression support for proxy traffic.

Handles transparent compression (gzip, brotli, deflate) for reducing bandwidth
and improving performance on high-latency connections.
"""

from __future__ import annotations

import gzip
import io
from enum import Enum

try:
    import brotli
except ImportError:
    brotli = None  # type: ignore

from loguru import logger


class CompressionAlgorithm(str, Enum):
    """Supported compression algorithms."""

    GZIP = "gzip"
    BROTLI = "br"
    DEFLATE = "deflate"
    IDENTITY = "identity"  # No compression


class CompressionLevel(int, Enum):
    """Compression level (1-9, higher = smaller but slower)."""

    LOWEST = 1
    LOW = 3
    MEDIUM = 5
    HIGH = 7
    HIGHEST = 9


class CompressionConfig:
    """Configuration for request/response compression."""

    def __init__(
        self,
        enabled: bool = True,
        algorithms: list[CompressionAlgorithm] | None = None,
        min_size_bytes: int = 1024,  # Don't compress small responses
        level: CompressionLevel = CompressionLevel.MEDIUM,
    ):
        """Initialize compression config.

        Args:
            enabled: Enable compression
            algorithms: List of algorithms to use (in preference order)
            min_size_bytes: Minimum content size to compress
            level: Compression level
        """
        self.enabled = enabled
        self.algorithms = algorithms or [
            CompressionAlgorithm.BROTLI,
            CompressionAlgorithm.GZIP,
            CompressionAlgorithm.DEFLATE,
        ]
        # Filter out unsupported algorithms
        available = self._get_available_algorithms()
        self.algorithms = [
            algo for algo in self.algorithms if algo in available
        ]
        self.min_size_bytes = min_size_bytes
        self.level = level

    @staticmethod
    def _get_available_algorithms() -> set[CompressionAlgorithm]:
        """Get available compression algorithms."""
        available = {CompressionAlgorithm.GZIP, CompressionAlgorithm.DEFLATE}

        if brotli:
            available.add(CompressionAlgorithm.BROTLI)

        return available


class CompressionManager:
    """Manages compression of requests and responses."""

    def __init__(self, config: CompressionConfig | None = None):
        """Initialize compression manager.

        Args:
            config: Compression configuration
        """
        self.config = config or CompressionConfig()

    def get_request_headers(self) -> dict[str, str]:
        """Get headers to include in requests for compression.

        Returns:
            Headers dict with Accept-Encoding
        """
        if not self.config.enabled:
            return {}

        encodings = ", ".join(algo.value for algo in self.config.algorithms)
        return {"Accept-Encoding": encodings}

    def compress_response(
        self,
        data: bytes,
        algorithm: CompressionAlgorithm = CompressionAlgorithm.GZIP,
    ) -> bytes:
        """Compress response data.

        Args:
            data: Data to compress
            algorithm: Compression algorithm to use

        Returns:
            Compressed data

        Raises:
            ValueError: If algorithm is not supported
        """
        if not self.config.enabled or not data:
            return data

        if len(data) < self.config.min_size_bytes:
            return data

        try:
            if algorithm == CompressionAlgorithm.GZIP:
                return self._compress_gzip(data)
            elif algorithm == CompressionAlgorithm.BROTLI:
                return self._compress_brotli(data)
            elif algorithm == CompressionAlgorithm.DEFLATE:
                return self._compress_deflate(data)
            elif algorithm == CompressionAlgorithm.IDENTITY:
                return data
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")

        except Exception as e:
            logger.warning(
                f"Compression failed with {algorithm.value}: {e}. "
                "Returning uncompressed data."
            )
            return data

    def decompress_response(
        self,
        data: bytes,
        algorithm: CompressionAlgorithm,
    ) -> bytes:
        """Decompress response data.

        Args:
            data: Compressed data
            algorithm: Compression algorithm that was used

        Returns:
            Decompressed data

        Raises:
            ValueError: If algorithm is not supported
        """
        if not data or algorithm == CompressionAlgorithm.IDENTITY:
            return data

        try:
            if algorithm == CompressionAlgorithm.GZIP:
                return gzip.decompress(data)
            elif algorithm == CompressionAlgorithm.BROTLI:
                if not brotli:
                    raise ValueError("brotli module not available")
                return brotli.decompress(data)
            elif algorithm == CompressionAlgorithm.DEFLATE:
                return self._decompress_deflate(data)
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")

        except Exception as e:
            logger.error(
                f"Decompression failed with {algorithm.value}: {e}",
                exc_info=True,
            )
            raise

    def estimate_compression_ratio(
        self,
        data: bytes,
        algorithm: CompressionAlgorithm = CompressionAlgorithm.GZIP,
    ) -> float:
        """Estimate compression ratio for data.

        Args:
            data: Data to estimate compression for
            algorithm: Algorithm to use

        Returns:
            Compression ratio (0-1, where 1 = no compression)
        """
        if not data:
            return 0

        compressed = self.compress_response(data, algorithm)
        return len(compressed) / len(data) if data else 0

    @staticmethod
    def _compress_gzip(data: bytes) -> bytes:
        """Compress with gzip."""
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode='wb') as f:
            f.write(data)
        return buf.getvalue()

    @staticmethod
    def _compress_brotli(data: bytes) -> bytes:
        """Compress with brotli."""
        if not brotli:
            raise ValueError("brotli module not available")
        return brotli.compress(data)

    @staticmethod
    def _compress_deflate(data: bytes) -> bytes:
        """Compress with deflate."""
        import zlib
        return zlib.compress(data)

    @staticmethod
    def _decompress_deflate(data: bytes) -> bytes:
        """Decompress deflate."""
        import zlib
        return zlib.decompress(data)


def parse_content_encoding(encoding_header: str) -> CompressionAlgorithm:
    """Parse Content-Encoding header to get algorithm.

    Args:
        encoding_header: Value of Content-Encoding header

    Returns:
        CompressionAlgorithm
    """
    if not encoding_header:
        return CompressionAlgorithm.IDENTITY

    # Get the last encoding (proxies may add multiple)
    encodings = [e.strip() for e in encoding_header.split(",")]
    encoding = encodings[-1].lower()

    try:
        return CompressionAlgorithm(encoding)
    except ValueError:
        logger.warning(
            f"Unknown Content-Encoding: {encoding}, "
            "treating as identity"
        )
        return CompressionAlgorithm.IDENTITY
