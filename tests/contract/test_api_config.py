"""Contract tests for configuration endpoints (US4).

Tests API contracts for:
- GET /api/config - Get current configuration
- PUT /api/config - Update configuration
"""

import pytest
from pydantic import ValidationError

from proxywhirl.api.models import ConfigurationSettings, UpdateConfigRequest


def test_configuration_settings_schema() -> None:
    """T059: Configuration responses expose the complete stable field set."""
    settings = ConfigurationSettings()
    schema = ConfigurationSettings.model_json_schema()

    assert set(settings.model_dump()) == {
        "rotation_strategy",
        "timeout",
        "max_retries",
        "rate_limits",
        "auth_enabled",
        "cors_origins",
    }
    assert set(schema["properties"]) == set(settings.model_dump())
    with pytest.raises(ValidationError):
        ConfigurationSettings(timeout=0)


def test_update_config_request_schema() -> None:
    """T060: Configuration updates are partial, bounded, and closed to extras."""
    assert UpdateConfigRequest().model_dump(exclude_none=True) == {}
    update = UpdateConfigRequest(rotation_strategy="random", timeout=60)
    assert update.model_dump(exclude_none=True) == {
        "rotation_strategy": "random",
        "timeout": 60,
    }

    with pytest.raises(ValidationError):
        UpdateConfigRequest.model_validate({"unknown": True})
    with pytest.raises(ValidationError):
        UpdateConfigRequest(timeout=301)
    with pytest.raises(ValidationError):
        UpdateConfigRequest(rotation_strategy="not-a-strategy")
