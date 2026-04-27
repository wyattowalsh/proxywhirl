"""Statistics aggregation and reporting for ProxyWhirl."""

from __future__ import annotations

import statistics
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LatencyMetrics:
    """Latency statistics."""

    p50: float = 0.0  # 50th percentile
    p95: float = 0.0  # 95th percentile
    p99: float = 0.0  # 99th percentile
    min: float = float("inf")
    max: float = 0.0
    mean: float = 0.0
    stddev: float = 0.0


@dataclass
class ProxyStats:
    """Per-proxy statistics."""

    proxy_id: str
    requests: int = 0
    errors: int = 0
    success_rate: float = 0.0
    latency_ms: LatencyMetrics = field(default_factory=LatencyMetrics)
    bytes_transferred: int = 0
    last_used: float = field(default_factory=time.time)


class StatsAggregator:
    """
    Aggregate and report statistics for proxies and pools.

    Tracks:
    - Requests per minute
    - Error rates
    - Latency percentiles (p50, p95, p99)
    - Success rates
    """

    def __init__(self, window_seconds: int = 60):
        """
        Initialize stats aggregator.

        Args:
            window_seconds: Time window for aggregation
        """
        self.window_seconds = window_seconds
        self.proxy_stats: dict[str, ProxyStats] = {}
        self.latency_samples: dict[str, list[float]] = {}
        self.request_times: list[float] = []
        self.error_times: list[float] = []

    def record_request(
        self,
        proxy_id: str,
        latency_ms: float,
        success: bool = True,
        bytes_transferred: int = 0,
    ) -> None:
        """
        Record a proxy request.

        Args:
            proxy_id: Proxy identifier
            latency_ms: Request latency in milliseconds
            success: Whether request was successful
            bytes_transferred: Bytes transferred in request
        """
        current_time = time.time()

        # Initialize stats if needed
        if proxy_id not in self.proxy_stats:
            self.proxy_stats[proxy_id] = ProxyStats(proxy_id=proxy_id)
            self.latency_samples[proxy_id] = []

        stats = self.proxy_stats[proxy_id]

        # Update stats
        stats.requests += 1
        if not success:
            stats.errors += 1
        stats.latency_ms.max = max(stats.latency_ms.max, latency_ms)
        stats.latency_ms.min = min(stats.latency_ms.min, latency_ms)
        stats.bytes_transferred += bytes_transferred
        stats.last_used = current_time

        # Track latency samples
        self.latency_samples[proxy_id].append(latency_ms)

        # Track request times
        self.request_times.append(current_time)

        if not success:
            self.error_times.append(current_time)

        # Update success rate
        if stats.requests > 0:
            stats.success_rate = 1.0 - (stats.errors / stats.requests)

        # Update latency metrics
        self._update_latency_metrics(proxy_id)

    def _update_latency_metrics(self, proxy_id: str) -> None:
        """Update latency percentile metrics."""
        if proxy_id not in self.latency_samples:
            return

        samples = self.latency_samples[proxy_id]
        if not samples:
            return

        sorted_samples = sorted(samples)
        metrics = self.proxy_stats[proxy_id].latency_ms

        metrics.mean = statistics.mean(samples)
        if len(samples) > 1:
            metrics.stddev = statistics.stdev(samples)
        else:
            metrics.stddev = 0.0

        # Calculate percentiles
        def percentile(data: list[float], p: float) -> float:
            idx = int(len(data) * p / 100)
            return data[min(idx, len(data) - 1)]

        metrics.p50 = percentile(sorted_samples, 50)
        metrics.p95 = percentile(sorted_samples, 95)
        metrics.p99 = percentile(sorted_samples, 99)

    def get_proxy_stats(self, proxy_id: str) -> Optional[ProxyStats]:
        """
        Get statistics for a specific proxy.

        Args:
            proxy_id: Proxy identifier

        Returns:
            ProxyStats or None if not found
        """
        return self.proxy_stats.get(proxy_id)

    def get_all_stats(self) -> dict[str, ProxyStats]:
        """
        Get statistics for all proxies.

        Returns:
            Dictionary mapping proxy_id to ProxyStats
        """
        return self.proxy_stats.copy()

    def get_requests_per_minute(self) -> float:
        """
        Get current requests per minute.

        Returns:
            Requests per minute
        """
        current_time = time.time()
        one_minute_ago = current_time - 60

        # Count requests in last minute
        recent_requests = sum(1 for req_time in self.request_times if req_time > one_minute_ago)

        return recent_requests

    def get_errors_per_minute(self) -> float:
        """
        Get current errors per minute.

        Returns:
            Errors per minute
        """
        current_time = time.time()
        one_minute_ago = current_time - 60

        # Count errors in last minute
        recent_errors = sum(1 for err_time in self.error_times if err_time > one_minute_ago)

        return recent_errors

    def get_error_rate(self) -> float:
        """
        Get overall error rate.

        Returns:
            Error rate as percentage (0-100)
        """
        total_requests = sum(stats.requests for stats in self.proxy_stats.values())
        if total_requests == 0:
            return 0.0

        total_errors = sum(stats.errors for stats in self.proxy_stats.values())
        return (total_errors / total_requests) * 100

    def get_aggregate_latency(self) -> LatencyMetrics:
        """
        Get aggregate latency metrics across all proxies.

        Returns:
            LatencyMetrics with aggregated values
        """
        all_latencies = []
        for samples in self.latency_samples.values():
            all_latencies.extend(samples)

        if not all_latencies:
            return LatencyMetrics()

        metrics = LatencyMetrics()
        sorted_latencies = sorted(all_latencies)

        metrics.mean = statistics.mean(all_latencies)
        metrics.min = min(all_latencies)
        metrics.max = max(all_latencies)

        if len(all_latencies) > 1:
            metrics.stddev = statistics.stdev(all_latencies)

        def percentile(data: list[float], p: float) -> float:
            idx = int(len(data) * p / 100)
            return data[min(idx, len(data) - 1)]

        metrics.p50 = percentile(sorted_latencies, 50)
        metrics.p95 = percentile(sorted_latencies, 95)
        metrics.p99 = percentile(sorted_latencies, 99)

        return metrics

    def get_summary(self) -> dict[str, float | int]:
        """
        Get summary statistics.

        Returns:
            Dictionary with summary stats
        """
        total_requests = sum(stats.requests for stats in self.proxy_stats.values())
        total_errors = sum(stats.errors for stats in self.proxy_stats.values())
        total_bytes = sum(stats.bytes_transferred for stats in self.proxy_stats.values())

        return {
            "total_proxies": len(self.proxy_stats),
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate_percent": (total_errors / total_requests * 100) if total_requests else 0.0,
            "requests_per_minute": self.get_requests_per_minute(),
            "errors_per_minute": self.get_errors_per_minute(),
            "total_bytes_transferred": total_bytes,
            "avg_bytes_per_request": (total_bytes / total_requests) if total_requests else 0.0,
        }

    def get_top_performers(self, limit: int = 5) -> list[tuple[str, float]]:
        """
        Get top proxies by success rate.

        Args:
            limit: Number of top proxies to return

        Returns:
            List of (proxy_id, success_rate) tuples
        """
        sorted_proxies = sorted(
            self.proxy_stats.items(),
            key=lambda x: x[1].success_rate,
            reverse=True,
        )
        return [(pid, stats.success_rate) for pid, stats in sorted_proxies[:limit]]

    def get_worst_performers(self, limit: int = 5) -> list[tuple[str, float]]:
        """
        Get worst proxies by success rate.

        Args:
            limit: Number of worst proxies to return

        Returns:
            List of (proxy_id, success_rate) tuples
        """
        sorted_proxies = sorted(
            self.proxy_stats.items(),
            key=lambda x: x[1].success_rate,
        )
        return [(pid, stats.success_rate) for pid, stats in sorted_proxies[:limit]]

    def reset_stats(self, proxy_id: Optional[str] = None) -> None:
        """
        Reset statistics.

        Args:
            proxy_id: Specific proxy to reset, or None for all
        """
        if proxy_id:
            if proxy_id in self.proxy_stats:
                del self.proxy_stats[proxy_id]
            if proxy_id in self.latency_samples:
                del self.latency_samples[proxy_id]
        else:
            self.proxy_stats = {}
            self.latency_samples = {}
            self.request_times = []
            self.error_times = []
