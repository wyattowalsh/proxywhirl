"""Unit tests for multi-level proxy validation."""

from proxywhirl.fetchers import ProxyValidator
from proxywhirl.models import ValidationLevel


class TestValidationLevels:
    """Test validation level configuration."""

    def test_validation_level_basic(self) -> None:
        """T003: Test BASIC validation level initialization."""
        validator = ProxyValidator(level=ValidationLevel.BASIC)
        
        assert validator.level == ValidationLevel.BASIC
        assert validator.timeout == 5.0  # default
        assert validator.concurrency == 50  # default

    def test_validation_level_standard(self) -> None:
        """T004: Test STANDARD validation level initialization."""
        validator = ProxyValidator(level=ValidationLevel.STANDARD)
        
        assert validator.level == ValidationLevel.STANDARD
        assert validator.timeout == 5.0
        assert validator.concurrency == 50

    def test_validation_level_full(self) -> None:
        """T005: Test FULL validation level initialization."""
        validator = ProxyValidator(level=ValidationLevel.FULL)
        
        assert validator.level == ValidationLevel.FULL
        assert validator.timeout == 5.0
        assert validator.concurrency == 50

    def test_validation_level_defaults_to_standard(self) -> None:
        """Test that validation level defaults to STANDARD when not specified."""
        validator = ProxyValidator()
        
        assert validator.level == ValidationLevel.STANDARD

    def test_validation_level_with_custom_settings(self) -> None:
        """Test validation level with custom timeout and concurrency."""
        validator = ProxyValidator(
            level=ValidationLevel.FULL,
            timeout=10.0,
            concurrency=100
        )
        
        assert validator.level == ValidationLevel.FULL
        assert validator.timeout == 10.0
        assert validator.concurrency == 100
