"""Tests for rollout system."""

import pytest

from proxywhirl.rollout_gradual import (
    RolloutConfig,
    RolloutManager,
    RolloutPhase,
    RolloutStrategy,
)


class TestRolloutPhase:
    """Test RolloutPhase class."""

    def test_phase_creation(self):
        """Test phase creation."""
        phase = RolloutPhase(name="canary", traffic_percentage=10.0)
        assert phase.name == "canary"
        assert phase.traffic_percentage == 10.0

    def test_phase_invalid_traffic(self):
        """Test invalid traffic percentage."""
        with pytest.raises(ValueError):
            RolloutPhase(name="canary", traffic_percentage=150.0)

    def test_phase_invalid_traffic_negative(self):
        """Test negative traffic percentage."""
        with pytest.raises(ValueError):
            RolloutPhase(name="canary", traffic_percentage=-10.0)


class TestRolloutConfig:
    """Test RolloutConfig class."""

    def test_config_creation(self):
        """Test configuration creation."""
        phases = [
            RolloutPhase(name="canary", traffic_percentage=10.0),
            RolloutPhase(name="stable", traffic_percentage=100.0),
        ]
        config = RolloutConfig(name="test", strategy=RolloutStrategy.CANARY, phases=phases)
        assert config.name == "test"
        assert len(config.phases) == 2

    def test_validate_valid_config(self):
        """Test validating valid config."""
        phases = [
            RolloutPhase(name="canary", traffic_percentage=10.0),
            RolloutPhase(name="stable", traffic_percentage=100.0),
        ]
        config = RolloutConfig(name="test", strategy=RolloutStrategy.CANARY, phases=phases)
        assert config.validate()

    def test_validate_no_phases(self):
        """Test validating config with no phases."""
        config = RolloutConfig(name="test", strategy=RolloutStrategy.CANARY, phases=[])
        assert not config.validate()

    def test_validate_incomplete_rollout(self):
        """Test validating incomplete rollout."""
        phases = [RolloutPhase(name="canary", traffic_percentage=10.0)]
        config = RolloutConfig(name="test", strategy=RolloutStrategy.CANARY, phases=phases)
        assert not config.validate()


class TestRolloutManager:
    """Test RolloutManager class."""

    def test_create_rollout(self):
        """Test creating rollout."""
        manager = RolloutManager()
        phases = [
            RolloutPhase(name="canary", traffic_percentage=10.0),
            RolloutPhase(name="stable", traffic_percentage=100.0),
        ]
        config = RolloutConfig(name="test", strategy=RolloutStrategy.CANARY, phases=phases)
        assert manager.create_rollout(config)

    def test_get_traffic_percentage(self):
        """Test getting traffic percentage."""
        manager = RolloutManager()
        phases = [
            RolloutPhase(name="canary", traffic_percentage=10.0),
            RolloutPhase(name="stable", traffic_percentage=100.0),
        ]
        config = RolloutConfig(name="test", strategy=RolloutStrategy.CANARY, phases=phases)
        manager.create_rollout(config)
        assert manager.get_traffic_percentage("test") == 10.0

    def test_record_request_success(self):
        """Test recording successful request."""
        manager = RolloutManager()
        phases = [
            RolloutPhase(name="canary", traffic_percentage=10.0),
            RolloutPhase(name="stable", traffic_percentage=100.0),
        ]
        config = RolloutConfig(name="test", strategy=RolloutStrategy.CANARY, phases=phases)
        manager.create_rollout(config)
        manager.record_request("test", success=True)
        status = manager.get_rollout_status("test")
        assert status["success_rate"] == 100.0

    def test_get_rollout_status(self):
        """Test getting rollout status."""
        manager = RolloutManager()
        phases = [
            RolloutPhase(name="canary", traffic_percentage=10.0),
            RolloutPhase(name="stable", traffic_percentage=100.0),
        ]
        config = RolloutConfig(name="test", strategy=RolloutStrategy.CANARY, phases=phases)
        manager.create_rollout(config)
        status = manager.get_rollout_status("test")
        assert status is not None
        assert status["name"] == "test"
