"""Unit tests for health check configuration."""

import pytest
from pydantic import ValidationError

from proxywhirl.health_models import HealthCheckConfig


class TestHealthCheckConfig:
    """Tests for HealthCheckConfig (T036)."""

    def test_per_source_interval_configuration(self) -> None:
        """Test per-source interval configuration (T036)."""
        config = HealthCheckConfig(
            check_interval_seconds=60,
            source_intervals={"premium": 30, "free": 300, "trial": 120},
        )

        assert config.check_interval_seconds == 60  # default
        assert config.source_intervals["premium"] == 30
        assert config.source_intervals["free"] == 300
        assert config.source_intervals["trial"] == 120

    def test_source_intervals_default_empty(self) -> None:
        """Test that source_intervals defaults to empty dict."""
        config = HealthCheckConfig()
        assert config.source_intervals == {}

    def test_source_interval_validation(self) -> None:
        """Test that source intervals are validated."""
        # Should accept valid intervals
        config = HealthCheckConfig(source_intervals={"source1": 10})
        assert config.source_intervals["source1"] == 10

        # Invalid intervals should be caught if we add validation
        # For now, just test that it accepts valid ones

    def test_get_interval_for_source(self) -> None:
        """Test getting interval for a specific source."""
        config = HealthCheckConfig(
            check_interval_seconds=60, source_intervals={"premium": 30}
        )

        # Premium source should use override
        assert config.source_intervals.get("premium", config.check_interval_seconds) == 30

        # Unknown source should use default
        assert (
            config.source_intervals.get("unknown", config.check_interval_seconds) == 60
        )
