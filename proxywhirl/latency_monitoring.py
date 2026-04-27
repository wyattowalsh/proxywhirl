"""Latency monitoring and analysis."""

from typing import Dict, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import statistics


@dataclass
class LatencyStats:
    """Latency statistics."""

    min_ms: float
    max_ms: float
    mean_ms: float
    median_ms: float
    p95_ms: float
    p99_ms: float
    stddev_ms: float


class LatencyMonitor:
    """Monitors latency metrics."""

    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.latencies: deque = deque(maxlen=window_size)
        self.proxy_latencies: Dict[str, deque] = {}

    def record_latency(self, latency_ms: float, proxy_url: Optional[str] = None) -> None:
        """Record a latency measurement."""
        self.latencies.append(latency_ms)

        if proxy_url:
            if proxy_url not in self.proxy_latencies:
                self.proxy_latencies[proxy_url] = deque(maxlen=self.window_size)
            self.proxy_latencies[proxy_url].append(latency_ms)

    def get_stats(self) -> Optional[LatencyStats]:
        """Get latency statistics."""
        if not self.latencies:
            return None

        data = sorted(list(self.latencies))

        return LatencyStats(
            min_ms=min(data),
            max_ms=max(data),
            mean_ms=statistics.mean(data),
            median_ms=statistics.median(data),
            p95_ms=data[int(len(data) * 0.95)] if len(data) > 1 else data[0],
            p99_ms=data[int(len(data) * 0.99)] if len(data) > 1 else data[0],
            stddev_ms=statistics.stdev(data) if len(data) > 1 else 0.0,
        )

    def get_proxy_stats(self, proxy_url: str) -> Optional[LatencyStats]:
        """Get stats for specific proxy."""
        latencies = self.proxy_latencies.get(proxy_url)
        if not latencies or len(latencies) == 0:
            return None

        data = sorted(list(latencies))

        return LatencyStats(
            min_ms=min(data),
            max_ms=max(data),
            mean_ms=statistics.mean(data),
            median_ms=statistics.median(data),
            p95_ms=data[int(len(data) * 0.95)] if len(data) > 1 else data[0],
            p99_ms=data[int(len(data) * 0.99)] if len(data) > 1 else data[0],
            stddev_ms=statistics.stdev(data) if len(data) > 1 else 0.0,
        )
