"""
Transparent request/response compression support for ProxyWhirl.

Provides automatic gzip and brotli compression/decompression.
"""

from __future__ import annotations

import gzip
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CompressionType(str, Enum):
    """Supported compression algorithms."""

    GZIP = "gzip"
    DEFLATE = "deflate"
    BROTLI = "brotli"
    NONE = "none"


class CompressionConfig(BaseModel):
    """Configuration for compression handling."""

    enabled: bool = Field(default=True, description="Enable compression")
    min_payload_size: int = Field(
        default=1024, ge=0, description="Minimum size to compress in bytes"
    )
    preferred_algorithm: CompressionType = Field(default=CompressionType.GZIP)
    supported_algorithms: list[CompressionType] = Field(
        default_factory=lambda: [CompressionType.GZIP, CompressionType.DEFLATE]
    )

    model_config = ConfigDict(frozen=True)


class CompressionHandler:
    """Handler for request/response compression."""

    def __init__(self, config: Optional[CompressionConfig] = None):
        """Initialize compression handler.

        Args:
            config: Compression configuration
        """
        self.config = config or CompressionConfig()

    def should_compress(self, data: bytes) -> bool:
        """Determine if data should be compressed.

        Args:
            data: Data to evaluate

        Returns:
            True if data meets compression criteria
        """
        if not self.config.enabled:
            return False

        return len(data) >= self.config.min_payload_size

    def compress(
        self,
        data: bytes,
        algorithm: Optional[CompressionType] = None,
    ) -> tuple[bytes, CompressionType]:
        """Compress data.

        Args:
            data: Data to compress
            algorithm: Compression algorithm (default: configured preferred)

        Returns:
            Tuple of (compressed_data, algorithm_used)

        Raises:
            ValueError: If algorithm not supported
        """
        algorithm = algorithm or self.config.preferred_algorithm

        if algorithm not in self.config.supported_algorithms:
            raise ValueError(f"Compression algorithm '{algorithm}' not supported")

        if algorithm == CompressionType.GZIP:
            return gzip.compress(data, compresslevel=6), CompressionType.GZIP

        elif algorithm == CompressionType.DEFLATE:
            import zlib

            return zlib.compress(data, level=6), CompressionType.DEFLATE

        elif algorithm == CompressionType.BROTLI:
            try:
                import brotli

                return brotli.compress(data), CompressionType.BROTLI
            except ImportError:
                raise ValueError("Brotli compression requires 'brotli' package")

        elif algorithm == CompressionType.NONE:
            return data, CompressionType.NONE

        raise ValueError(f"Unknown compression algorithm: {algorithm}")

    def decompress(
        self,
        data: bytes,
        algorithm: CompressionType,
    ) -> bytes:
        """Decompress data.

        Args:
            data: Compressed data
            algorithm: Compression algorithm used

        Returns:
            Decompressed data

        Raises:
            ValueError: If algorithm not recognized
        """
        if algorithm == CompressionType.GZIP:
            return gzip.decompress(data)

        elif algorithm == CompressionType.DEFLATE:
            import zlib

            return zlib.decompress(data)

        elif algorithm == CompressionType.BROTLI:
            try:
                import brotli

                return brotli.decompress(data)
            except ImportError:
                raise ValueError("Brotli decompression requires 'brotli' package")

        elif algorithm == CompressionType.NONE:
            return data

        raise ValueError(f"Unknown compression algorithm: {algorithm}")

    def get_accept_encoding(self) -> str:
        """Get Accept-Encoding header value.

        Returns:
            Accept-Encoding header string
        """
        if not self.config.enabled:
            return "identity"

        algorithms = [
            algo.value for algo in self.config.supported_algorithms if algo != CompressionType.NONE
        ]
        return ", ".join(algorithms) if algorithms else "identity"
