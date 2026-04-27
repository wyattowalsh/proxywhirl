"""Sampling telemetry to reduce tracing overhead."""

from __future__ import annotations

import random
from enum import Enum

from loguru import logger


class SamplingLevel(str, Enum):
    """Sampling strategy levels."""

    NONE = "none"  # No sampling
    LOW = "low"  # 1% sampling
    MEDIUM = "medium"  # 5% sampling
    HIGH = "high"  # 10% sampling
    VERY_HIGH = "very_high"  # 50% sampling
    ALL = "all"  # 100% sampling


class SamplingConfig:
    """Configuration for trace sampling."""

    SAMPLING_RATES = {
        SamplingLevel.NONE: 0.0,
        SamplingLevel.LOW: 0.01,
        SamplingLevel.MEDIUM: 0.05,
        SamplingLevel.HIGH: 0.1,
        SamplingLevel.VERY_HIGH: 0.5,
        SamplingLevel.ALL: 1.0,
    }

    def __init__(
        self,
        sample_rate: float | SamplingLevel = SamplingLevel.MEDIUM,
    ):
        """
        Initialize sampling configuration.

        Args:
            sample_rate: Sampling rate (0.0-1.0) or SamplingLevel
        """
        if isinstance(sample_rate, SamplingLevel):
            self.sample_rate = self.SAMPLING_RATES[sample_rate]
            self.level = sample_rate
        elif isinstance(sample_rate, float):
            if not 0.0 <= sample_rate <= 1.0:
                raise ValueError(f"Sample rate must be 0.0-1.0, got {sample_rate}")
            self.sample_rate = sample_rate
            # Find closest level
            closest_level = min(
                self.SAMPLING_RATES.items(),
                key=lambda x: abs(x[1] - sample_rate),
            )
            self.level = closest_level[0]
        else:
            raise TypeError(f"Invalid sample_rate type: {type(sample_rate)}")

    def should_sample(self) -> bool:
        """
        Determine if this trace should be sampled.

        Returns:
            True if trace should be included
        """
        return random.random() < self.sample_rate


class TraceSampler:
    """
    Trace sampler for reducing telemetry overhead.

    Implements probabilistic sampling to reduce load while maintaining
    representative data.
    """

    def __init__(
        self,
        default_sample_rate: float | SamplingLevel = SamplingLevel.MEDIUM,
    ):
        """
        Initialize trace sampler.

        Args:
            default_sample_rate: Default sampling rate
        """
        self.config = SamplingConfig(default_sample_rate)
        self.traces_sampled = 0
        self.traces_dropped = 0

    def sample_trace(
        self,
        trace_id: str,
        sample_rate: float | SamplingLevel | None = None,
    ) -> bool:
        """
        Sample a trace.

        Args:
            trace_id: Trace identifier
            sample_rate: Optional override sample rate

        Returns:
            True if trace should be sampled
        """
        config = SamplingConfig(sample_rate) if sample_rate is not None else self.config

        if config.should_sample():
            self.traces_sampled += 1
            logger.debug(f"Sampling trace {trace_id} (rate: {config.sample_rate:.1%})")
            return True
        else:
            self.traces_dropped += 1
            logger.debug(f"Dropped trace {trace_id} (rate: {config.sample_rate:.1%})")
            return False

    def set_sample_rate(self, sample_rate: float | SamplingLevel) -> None:
        """
        Update sampling rate.

        Args:
            sample_rate: New sampling rate
        """
        self.config = SamplingConfig(sample_rate)
        logger.info(f"Updated sampling rate to {self.config.level} ({self.config.sample_rate:.1%})")

    def get_stats(self) -> dict[str, int | float]:
        """
        Get sampling statistics.

        Returns:
            Dictionary with stats
        """
        total = self.traces_sampled + self.traces_dropped
        effective_rate = self.traces_sampled / total if total > 0 else 0.0

        return {
            "traces_sampled": self.traces_sampled,
            "traces_dropped": self.traces_dropped,
            "total_traces": total,
            "configured_rate_percent": self.config.sample_rate * 100,
            "effective_rate_percent": effective_rate * 100,
        }

    def reset_stats(self) -> None:
        """Reset sampling statistics."""
        self.traces_sampled = 0
        self.traces_dropped = 0


class AdaptiveSampler:
    """
    Adaptive sampler that adjusts rate based on system load.

    Increases sampling when system is healthy, decreases under load.
    """

    def __init__(
        self,
        min_rate: float = 0.01,
        max_rate: float = 1.0,
        target_sample_rate: float = 0.1,
    ):
        """
        Initialize adaptive sampler.

        Args:
            min_rate: Minimum sampling rate
            max_rate: Maximum sampling rate
            target_sample_rate: Target sampling rate under normal load
        """
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.target_rate = target_sample_rate
        self.current_rate = target_sample_rate
        self.sampler = TraceSampler(target_sample_rate)

    def adjust_rate(self, cpu_percent: float, memory_percent: float) -> float:
        """
        Adjust sampling rate based on system load.

        Args:
            cpu_percent: CPU utilization percentage (0-100)
            memory_percent: Memory utilization percentage (0-100)

        Returns:
            New sampling rate
        """
        load_percent = max(cpu_percent, memory_percent)

        if load_percent > 80:
            # Reduce sampling under high load
            new_rate = self.target_rate * 0.1
        elif load_percent > 60:
            # Moderate reduction
            new_rate = self.target_rate * 0.5
        elif load_percent < 30:
            # Increase sampling when idle
            new_rate = self.target_rate * 2.0
        else:
            # Normal load, use target
            new_rate = self.target_rate

        # Clamp to min/max
        new_rate = max(self.min_rate, min(self.max_rate, new_rate))

        if new_rate != self.current_rate:
            self.current_rate = new_rate
            self.sampler.set_sample_rate(new_rate)
            logger.info(
                f"Adaptive sampling rate adjusted to {new_rate:.1%} "
                f"(CPU: {cpu_percent:.1f}%, Memory: {memory_percent:.1f}%)"
            )

        return self.current_rate

    def sample_trace(self, trace_id: str) -> bool:
        """
        Sample a trace using current adaptive rate.

        Args:
            trace_id: Trace identifier

        Returns:
            True if trace should be sampled
        """
        return self.sampler.sample_trace(trace_id)
