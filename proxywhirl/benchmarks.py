"""Comprehensive benchmark suite for ProxyWhirl.

Benchmarks rotation speed, proxy validation, and memory usage.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from loguru import logger


class RotationBenchmark:
    """Benchmark proxy rotation performance.

    Measures rotation speed, throughput, and memory impact
    of different rotation strategies.

    Example:
        >>> bench = RotationBenchmark()
        >>> results = await bench.benchmark_rotation_speed(pool, iterations=1000)
    """

    @staticmethod
    async def benchmark_rotation_speed(
        pool: Any,
        iterations: int = 1000,
    ) -> dict[str, float]:
        """Benchmark rotation operation speed.

        Args:
            pool: ProxyPool instance
            iterations: Number of rotations to perform

        Returns:
            Dict with benchmark results (ops/sec, avg latency, etc.)
        """
        start_time = time.perf_counter()

        for _ in range(iterations):
            await pool.get_next()

        elapsed = time.perf_counter() - start_time
        ops_per_sec = iterations / elapsed

        return {
            "total_iterations": iterations,
            "elapsed_seconds": elapsed,
            "operations_per_second": ops_per_sec,
            "average_latency_ms": (elapsed / iterations) * 1000,
        }

    @staticmethod
    async def benchmark_concurrent_rotation(
        pool: Any,
        concurrent_requests: int = 100,
        requests_per_client: int = 10,
    ) -> dict[str, Any]:
        """Benchmark concurrent rotation performance.

        Args:
            pool: ProxyPool instance
            concurrent_requests: Number of concurrent tasks
            requests_per_client: Requests per concurrent client

        Returns:
            Benchmark results
        """

        async def client_task() -> int:
            """Single client making multiple rotation requests."""
            count = 0
            for _ in range(requests_per_client):
                await pool.get_next()
                count += 1
            return count

        start_time = time.perf_counter()
        tasks = [client_task() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start_time

        total_requests = sum(results)

        return {
            "concurrent_clients": concurrent_requests,
            "requests_per_client": requests_per_client,
            "total_requests": total_requests,
            "elapsed_seconds": elapsed,
            "requests_per_second": total_requests / elapsed,
            "average_latency_ms": (elapsed / total_requests) * 1000,
        }


class ValidationBenchmark:
    """Benchmark proxy validation performance.

    Measures validation speed, success rates, and throughput
    of proxy validation operations.
    """

    @staticmethod
    async def benchmark_validation_speed(
        validator: Any,
        proxies: list[Any],
        batch_size: int = 100,
    ) -> dict[str, Any]:
        """Benchmark validation throughput.

        Args:
            validator: ProxyValidator instance
            proxies: List of proxies to validate
            batch_size: Validation batch size

        Returns:
            Benchmark results
        """
        start_time = time.perf_counter()
        valid_count = 0

        for i in range(0, len(proxies), batch_size):
            batch = proxies[i : i + batch_size]
            try:
                results = await validator.validate_batch(batch)
                valid_count += sum(1 for r in results if r.get("valid"))
            except Exception as e:
                logger.warning(f"Validation batch failed: {e}")

        elapsed = time.perf_counter() - start_time

        return {
            "total_proxies": len(proxies),
            "valid_proxies": valid_count,
            "success_rate": (valid_count / len(proxies)) * 100 if proxies else 0,
            "elapsed_seconds": elapsed,
            "validations_per_second": len(proxies) / elapsed if elapsed > 0 else 0,
            "average_validation_ms": (elapsed / len(proxies)) * 1000 if proxies else 0,
        }


class MemoryBenchmark:
    """Benchmark memory usage of proxy operations.

    Measures memory footprint of pools, caches, and validation.
    """

    @staticmethod
    def benchmark_pool_memory(pool: Any) -> dict[str, Any]:
        """Benchmark proxy pool memory usage.

        Args:
            pool: ProxyPool instance

        Returns:
            Memory metrics
        """
        import sys

        proxy_count = len(pool.proxies) if hasattr(pool, "proxies") else 0
        pool_size = sys.getsizeof(pool)

        return {
            "proxy_count": proxy_count,
            "pool_object_bytes": pool_size,
            "bytes_per_proxy": pool_size / proxy_count if proxy_count > 0 else 0,
        }

    @staticmethod
    def benchmark_cache_memory(cache: Any) -> dict[str, Any]:
        """Benchmark cache memory usage.

        Args:
            cache: Cache instance

        Returns:
            Memory metrics
        """
        import sys

        cache_size = sys.getsizeof(cache)

        return {
            "cache_object_bytes": cache_size,
        }


class BenchmarkSuite:
    """Complete benchmark suite for ProxyWhirl.

    Orchestrates all benchmarks and generates reports.

    Example:
        >>> suite = BenchmarkSuite()
        >>> report = await suite.run_all_benchmarks(pool, validator)
    """

    async def run_all_benchmarks(
        self,
        pool: Any,
        validator: Any | None = None,
    ) -> dict[str, Any]:
        """Run complete benchmark suite.

        Args:
            pool: ProxyPool instance
            validator: Optional ProxyValidator instance

        Returns:
            Comprehensive benchmark report
        """
        report = {}

        # Rotation benchmarks
        logger.info("Running rotation speed benchmark...")
        report["rotation_speed"] = await RotationBenchmark.benchmark_rotation_speed(pool)

        logger.info("Running concurrent rotation benchmark...")
        report["concurrent_rotation"] = await RotationBenchmark.benchmark_concurrent_rotation(pool)

        # Validation benchmarks
        if validator:
            proxies = list(pool.proxies.values()) if hasattr(pool, "proxies") else []
            if proxies:
                logger.info("Running validation benchmark...")
                report["validation"] = await ValidationBenchmark.benchmark_validation_speed(
                    validator, proxies
                )

        # Memory benchmarks
        logger.info("Running memory benchmarks...")
        report["pool_memory"] = MemoryBenchmark.benchmark_pool_memory(pool)

        return report

    def generate_report(self, results: dict[str, Any]) -> str:
        """Generate human-readable benchmark report.

        Args:
            results: Benchmark results

        Returns:
            Formatted report string
        """
        lines = ["=== ProxyWhirl Benchmark Report ===", ""]

        if "rotation_speed" in results:
            rot = results["rotation_speed"]
            lines.append("Rotation Speed:")
            lines.append(f"  Operations/sec: {rot['operations_per_second']:.1f}")
            lines.append(f"  Avg latency: {rot['average_latency_ms']:.3f}ms")
            lines.append("")

        if "concurrent_rotation" in results:
            conc = results["concurrent_rotation"]
            lines.append("Concurrent Rotation:")
            lines.append(f"  Requests/sec: {conc['requests_per_second']:.1f}")
            lines.append(f"  Avg latency: {conc['average_latency_ms']:.3f}ms")
            lines.append("")

        if "validation" in results:
            val = results["validation"]
            lines.append("Validation:")
            lines.append(f"  Validations/sec: {val['validations_per_second']:.1f}")
            lines.append(f"  Success rate: {val['success_rate']:.1f}%")
            lines.append("")

        if "pool_memory" in results:
            mem = results["pool_memory"]
            lines.append("Memory:")
            lines.append(f"  Pool size: {mem['pool_object_bytes']} bytes")
            lines.append(f"  Proxies: {mem['proxy_count']}")
            lines.append("")

        return "\n".join(lines)
