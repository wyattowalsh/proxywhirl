"""Tests for deprecation module."""

import warnings

from proxywhirl.deprecation import deprecated, deprecated_parameter, deprecated_property


class TestDeprecatedDecorator:
    """Test deprecated function decorator."""

    def test_deprecated_function_warning(self):
        """Test deprecation warning is raised."""

        @deprecated("Use new_func instead", "1.0", "2.0")
        def old_func():
            return "result"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_func()

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()
            assert result == "result"

    def test_deprecated_with_alternative(self):
        """Test deprecation message includes alternative."""

        @deprecated("Use new_func instead", "1.0", alternative="new_func")
        def old_func():
            return "result"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_func()

            assert "new_func" in str(w[0].message)

    def test_deprecated_with_removal_version(self):
        """Test deprecation message includes removal version."""

        @deprecated("Function is deprecated", "1.0", removal_version="2.0")
        def old_func():
            return "result"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_func()

            assert "2.0" in str(w[0].message)


class TestDeprecatedParameter:
    """Test deprecated parameter decorator."""

    def test_deprecated_parameter_warning(self):
        """Test deprecation warning for parameter."""

        @deprecated_parameter("old_param", "Use new_param instead", "1.0")
        def func(new_param=None, old_param=None):
            return f"{new_param}:{old_param}"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = func(old_param="value")

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "old_param" in str(w[0].message)

    def test_deprecated_parameter_no_warning(self):
        """Test no warning when deprecated parameter not used."""

        @deprecated_parameter("old_param", "Use new_param instead", "1.0")
        def func(new_param=None, old_param=None):
            return new_param

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = func(new_param="value")

            assert len(w) == 0


class TestDeprecatedProperty:
    """Test deprecated property decorator."""

    def test_deprecated_property_warning(self):
        """Test deprecation warning for property."""

        class MyClass:
            @deprecated_property("This property is deprecated", "1.0", alternative="new_prop")
            def old_prop(self):
                return "value"

        obj = MyClass()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            value = obj.old_prop

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "old_prop" in str(w[0].message)
            assert "new_prop" in str(w[0].message)
            assert value == "value"

    def test_deprecated_property_on_class(self):
        """Test accessing deprecated property on class."""

        class MyClass:
            @deprecated_property("This property is deprecated", "1.0")
            def old_prop(self):
                return "value"

        result = MyClass.old_prop
        assert isinstance(result, deprecated_property.__bases__[0])
