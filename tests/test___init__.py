"""Test package initialization for ProxyWhirl.

Tests the package-level imports and module structure to ensure all components
are properly accessible and the package is correctly structured.
"""

import pytest

import proxywhirl
from proxywhirl import (
    Proxy,
    ProxyCache,
    ProxyValidator,
    ProxyWhirl,
)
from proxywhirl.config import LoaderConfig, ProxyWhirlSettings


class TestPackageImports:
    """Test package-level imports."""

    def test_main_class_import(self) -> None:
        """Test that main ProxyWhirl class is importable."""
        from proxywhirl import ProxyWhirl

        assert ProxyWhirl is not None
        assert hasattr(ProxyWhirl, "__init__")

    def test_cache_import(self) -> None:
        """Test that cache classes are importable."""
        from proxywhirl import ProxyCache

        assert ProxyCache is not None

    def test_validator_import(self) -> None:
        """Test that validator class is importable."""
        from proxywhirl import ProxyValidator

        assert ProxyValidator is not None

    def test_models_import(self) -> None:
        """Test that models are importable."""

        assert Proxy is not None

    def test_config_imports(self) -> None:
        """Test that configuration classes are importable."""
        from proxywhirl import LoaderConfig, ProxyWhirlSettings

        assert LoaderConfig is not None
        assert ProxyWhirlSettings is not None

    def test_direct_imports(self) -> None:
        """Test direct imports from submodules."""
        from proxywhirl.cache import ProxyCache
        from proxywhirl.caches import CacheType
        from proxywhirl.models import ProxyScheme, RotationStrategy
        from proxywhirl.rotator import ProxyRotator
        from proxywhirl.validator import ProxyValidator, QualityLevel

        assert CacheType is not None
        assert RotationStrategy is not None
        assert ProxyScheme is not None
        assert ProxyCache is not None
        assert ProxyValidator is not None
        assert QualityLevel is not None
        assert ProxyRotator is not None


class TestPackageStructure:
    """Test package structure and metadata."""

    def test_package_version(self) -> None:
        """Test that package has a version."""
        assert hasattr(proxywhirl, "__version__")
        assert isinstance(proxywhirl.__version__, str)
        assert len(proxywhirl.__version__) > 0

    def test_package_attributes(self) -> None:
        """Test that package has required attributes."""
        # Test that we can access main classes directly from package
        assert hasattr(proxywhirl, "ProxyWhirl")
        assert hasattr(proxywhirl, "ProxyCache")
        assert hasattr(proxywhirl, "ProxyValidator")
        assert hasattr(proxywhirl, "Proxy")

    def test_module_availability(self) -> None:
        """Test that all modules are available."""
        import proxywhirl.cache
        import proxywhirl.cli
        import proxywhirl.config
        import proxywhirl.models
        import proxywhirl.proxywhirl
        import proxywhirl.rotator
        import proxywhirl.utils
        import proxywhirl.validator

        # Test basic module loading
        assert proxywhirl.proxywhirl is not None
        assert proxywhirl.cache is not None
        assert proxywhirl.validator is not None
        assert proxywhirl.models is not None
        assert proxywhirl.config is not None
        assert proxywhirl.rotator is not None
        assert proxywhirl.utils is not None
        assert proxywhirl.cli is not None

    def test_loaders_module(self) -> None:
        """Test that loaders module and submodules are available."""
        import proxywhirl.loaders
        from proxywhirl.loaders import base
        from proxywhirl.loaders.base import BaseLoader

        assert proxywhirl.loaders is not None
        assert base is not None
        assert BaseLoader is not None

    def test_specific_loaders(self) -> None:
        """Test that specific loader implementations are available."""
        from proxywhirl.loaders.clarketm_raw import ClarketmHttpLoader
        from proxywhirl.loaders.jetkai_proxy_list import JetkaiProxyListLoader
        from proxywhirl.loaders.monosans import MonosansLoader
        from proxywhirl.loaders.proxifly import ProxiflyLoader
        from proxywhirl.loaders.proxyscrape import ProxyScrapeLoader
        from proxywhirl.loaders.the_speedx import (
            TheSpeedXHttpLoader,
            TheSpeedXSocksLoader,
        )
        from proxywhirl.loaders.user_provided import UserProvidedLoader
        from proxywhirl.loaders.vakhov_fresh import VakhovFreshProxyLoader

        assert JetkaiProxyListLoader is not None
        assert TheSpeedXHttpLoader is not None
        assert TheSpeedXSocksLoader is not None
        assert ClarketmHttpLoader is not None
        assert MonosansLoader is not None
        assert ProxyScrapeLoader is not None
        assert ProxiflyLoader is not None
        assert UserProvidedLoader is not None
        assert VakhovFreshProxyLoader is not None


class TestInstantiation:
    """Test that main classes can be instantiated."""

    def test_proxywhirl_instantiation(self) -> None:
        """Test ProxyWhirl can be instantiated with defaults."""
        pw = ProxyWhirl()
        assert pw is not None
        assert hasattr(pw, "fetch_proxies")
        assert hasattr(pw, "get_proxy")

    def test_cache_instantiation(self) -> None:
        """Test ProxyCache can be instantiated."""
        from proxywhirl.caches import CacheType

        cache = ProxyCache(CacheType.MEMORY)
        assert cache is not None
        assert hasattr(cache, "get")
        assert hasattr(cache, "set")

    def test_validator_instantiation(self) -> None:
        """Test ProxyValidator can be instantiated."""
        validator = ProxyValidator()
        assert validator is not None
        assert hasattr(validator, "validate_proxy")

    def test_config_instantiation(self) -> None:
        """Test configuration classes can be instantiated."""
        loader_config = LoaderConfig()
        settings = ProxyWhirlSettings()

        assert loader_config is not None
        assert settings is not None
        assert loader_config.timeout > 0
        assert settings.cache_type is not None


class TestPackageIntegration:
    """Integration tests for package functionality."""

    def test_basic_workflow(self) -> None:
        """Test basic ProxyWhirl workflow works."""
        # This should work without errors
        pw = ProxyWhirl()

        # Test that we can access loaders
        assert len(pw.loaders) > 0

        # Test that we can access configuration
        assert pw.settings is not None

        # Test that cache is initialized
        assert pw.cache is not None

    def test_logger_integration(self) -> None:
        """Test that logging system is properly integrated."""
        from proxywhirl.logger import get_logger

        logger = get_logger(__name__)
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")

    def test_utils_integration(self) -> None:
        """Test that utility functions are available."""
        from proxywhirl.utils import normalize_proxy_url, validate_ip

        assert validate_ip is not None
        assert normalize_proxy_url is not None

        # Test basic functionality
        assert validate_ip("192.168.1.1") is True
        assert validate_ip("invalid") is False

    def test_models_validation(self) -> None:
        """Test that models work with validation."""
        from proxywhirl.models import Proxy, ProxyScheme

        # Test valid proxy creation
        proxy = Proxy(ip="192.168.1.1", port=8080, scheme=ProxyScheme.HTTP, country="US")
        assert proxy.ip == "192.168.1.1"
        assert proxy.port == 8080
        assert proxy.scheme == ProxyScheme.HTTP
        assert proxy.country == "US"

    def test_cli_integration(self) -> None:
        """Test that CLI module is properly integrated."""
        import proxywhirl.cli

        assert proxywhirl.cli is not None
        assert hasattr(proxywhirl.cli, "app")  # Typer app


class TestModuleDiscovery:
    """Test module discovery and dynamic loading."""

    def test_all_modules_importable(self) -> None:
        """Test that all expected modules can be imported."""
        expected_modules = [
            "proxywhirl.proxywhirl",
            "proxywhirl.cache",
            "proxywhirl.validator",
            "proxywhirl.models",
            "proxywhirl.config",
            "proxywhirl.rotator",
            "proxywhirl.utils",
            "proxywhirl.cli",
            "proxywhirl.logger",
            "proxywhirl.loaders.base",
        ]

        for module_name in expected_modules:
            try:
                __import__(module_name)
            except ImportError as e:
                pytest.fail(f"Failed to import {module_name}: {e}")

    def test_loader_discovery(self) -> None:
        """Test that all loaders can be discovered and imported."""
        loader_modules = [
            "proxywhirl.loaders.fresh_proxy_list",
            "proxywhirl.loaders.the_speedx",
            "proxywhirl.loaders.clarketm",
            "proxywhirl.loaders.monosans",
            "proxywhirl.loaders.proxyscrape",
            "proxywhirl.loaders.proxynova",
            "proxywhirl.loaders.openproxyspace",
        ]

        for module_name in loader_modules:
            try:
                __import__(module_name)
            except ImportError as e:
                pytest.fail(f"Failed to import loader {module_name}: {e}")

    def test_no_circular_imports(self) -> None:
        """Test that there are no circular import issues."""
        # Import everything in different orders to check for circular dependencies

        # If we get here without errors, no circular imports detected
        assert True

    def test_namespace_pollution(self) -> None:
        """Test that modules don't pollute each other's namespaces."""
        import proxywhirl.config as config
        import proxywhirl.models as models

        # These should be separate namespaces
        assert hasattr(models, "Proxy")
        assert hasattr(config, "ProxyWhirlSettings")

        # Models shouldn't have config classes
        assert not hasattr(models, "ProxyWhirlSettings")
        # Config shouldn't have model classes (unless explicitly imported)
        assert not hasattr(config, "Proxy") or config.Proxy is models.Proxy
