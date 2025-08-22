"""Tests for proxywhirl.loaders.base module.

Unit tests for the BaseLoader abstract base class.
"""

import pytest
from pandas import DataFrame

from proxywhirl.loaders.base import BaseLoader


class TestBaseLoader:
    """Test BaseLoader abstract base class."""

    def test_base_loader_is_abstract(self):
        """Test that BaseLoader cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseLoader("test", "Test loader")  # type: ignore

    def test_concrete_implementation_works(self):
        """Test that concrete implementations work correctly."""

        class ConcreteLoader(BaseLoader):
            def load(self) -> DataFrame:
                return DataFrame({"host": ["1.2.3.4"], "port": [8080], "scheme": ["http"]})

        loader = ConcreteLoader("concrete", "Concrete test loader")
        assert loader.name == "concrete"
        assert loader.description == "Concrete test loader"

        # Test that load method is implemented and returns DataFrame
        result = loader.load()
        assert isinstance(result, DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["host"] == "1.2.3.4"
        assert result.iloc[0]["port"] == 8080
        assert result.iloc[0]["scheme"] == "http"

    def test_subclass_must_implement_load(self):
        """Test that subclasses must implement the load method."""

        class IncompleteLoader(BaseLoader):
            pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteLoader("incomplete", "Incomplete loader")  # type: ignore

    def test_multiple_inheritance_compatibility(self):
        """Test that BaseLoader works with multiple inheritance."""

        class Mixin:
            def extra_method(self):
                return "mixin"

        class MultiLoader(BaseLoader, Mixin):
            def load(self) -> DataFrame:
                return DataFrame()

        loader = MultiLoader("multi", "Multi inheritance loader")
        assert loader.name == "multi"
        assert loader.description == "Multi inheritance loader"
        assert loader.extra_method() == "mixin"
        assert isinstance(loader.load(), DataFrame)

    def test_initialization_with_empty_values(self):
        """Test initialization with empty strings."""

        class EmptyLoader(BaseLoader):
            def load(self) -> DataFrame:
                return DataFrame()

        loader = EmptyLoader("", "")
        assert loader.name == ""
        assert loader.description == ""

    def test_initialization_with_unicode(self):
        """Test initialization with unicode characters."""

        class UnicodeLoader(BaseLoader):
            def load(self) -> DataFrame:
                return DataFrame()

        loader = UnicodeLoader("测试", "Unicode test loader 🔥")
        assert loader.name == "测试"
        assert loader.description == "Unicode test loader 🔥"
