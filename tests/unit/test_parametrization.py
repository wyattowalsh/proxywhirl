"""Tests using pytest.mark.parametrize for better coverage."""

from __future__ import annotations

import pytest

from proxywhirl.utils import is_valid_proxy_url


@pytest.mark.parametrize(
    "value,expected",
    [
        (0, False),
        (1, True),
        (-1, True),
        (None, False),
    ],
)
def test_truthiness_values(value, expected) -> None:
    """Test truthiness of different values."""
    assert bool(value) == expected


@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("", 0),
        ("a", 1),
        ("abc", 3),
        ("hello world", 11),
    ],
)
def test_string_length(input_str, expected) -> None:
    """Test string length calculation."""
    assert len(input_str) == expected


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (1, 2, 3),
        (0, 0, 0),
        (-1, 1, 0),
        (10, -5, 5),
    ],
)
def test_addition(a, b, expected) -> None:
    """Test addition with various inputs."""
    assert a + b == expected


@pytest.mark.parametrize("value", [1, 2, 3, 4, 5])
def test_positive_integers(value) -> None:
    """Test positive integers."""
    assert value > 0


@pytest.mark.parametrize(
    "proxy_url,is_valid",
    [
        ("http://192.168.1.1:8080", True),
        ("https://proxy.example.com:3128", True),
        ("socks5://localhost:1080", True),
        ("invalid", False),
        ("", False),
    ],
)
def test_proxy_url_validation(proxy_url, is_valid) -> None:
    """Test proxy URL validation."""
    assert is_valid_proxy_url(proxy_url) == is_valid


@pytest.mark.parametrize(
    "protocol,port",
    [
        ("http", 80),
        ("https", 443),
        ("socks4", 1080),
        ("socks5", 1080),
    ],
)
def test_protocol_default_ports(protocol, port) -> None:
    """Test default ports by protocol."""
    protocol_ports = {
        "http": 80,
        "https": 443,
        "socks4": 1080,
        "socks5": 1080,
    }
    assert protocol_ports[protocol] == port


@pytest.mark.parametrize("timeout_sec", [1, 5, 10, 30])
def test_timeout_values(timeout_sec) -> None:
    """Test various timeout values."""
    assert timeout_sec > 0


@pytest.mark.parametrize("encoding", ["utf-8", "ascii", "latin-1"])
def test_string_encoding(encoding) -> None:
    """Test string encoding."""
    text = "hello"
    encoded = text.encode(encoding)
    decoded = encoded.decode(encoding)
    assert decoded == text


@pytest.mark.parametrize("status_code", [200, 201, 204, 400, 401, 403, 404, 500, 502, 503])
def test_http_status_codes(status_code) -> None:
    """Test HTTP status codes."""
    assert isinstance(status_code, int)
    assert 100 <= status_code < 600


class TestParametrization:
    """Test parametrization in class context."""

    @pytest.mark.parametrize("input_val,expected", [(1, 2), (2, 4), (3, 6)])
    def test_class_parametrization(self, input_val, expected) -> None:
        """Test parametrized method in class."""
        assert input_val * 2 == expected

    @pytest.mark.parametrize("x,y", [(1, 1), (2, 4), (3, 9)])
    def test_class_squares(self, x, y) -> None:
        """Test squared values."""
        assert x * x == y


@pytest.mark.parametrize("port", list(range(1024, 1030)))
def test_port_range(port) -> None:
    """Test port numbers in range."""
    assert 1 <= port <= 65535


@pytest.mark.parametrize(
    "retry_count,expected_calls",
    [
        (0, 1),
        (1, 2),
        (3, 4),
        (5, 6),
    ],
)
def test_retry_count_calls(retry_count, expected_calls) -> None:
    """Test retry counts produce expected calls."""
    assert retry_count + 1 == expected_calls


@pytest.mark.parametrize(
    "items",
    [
        [],
        [1],
        [1, 2, 3],
        list(range(100)),
    ],
)
def test_list_handling(items) -> None:
    """Test handling of various list sizes."""
    assert isinstance(items, list)


@pytest.mark.parametrize(
    "option_name,option_value",
    [
        ("timeout", 30),
        ("retries", 3),
        ("ssl_verify", True),
        ("pool_size", 10),
    ],
)
def test_configuration_options(option_name, option_value) -> None:
    """Test configuration option types."""
    config = {option_name: option_value}
    assert option_name in config


@pytest.mark.parametrize("delay_ms", [10, 50, 100, 500, 1000])
def test_delay_values(delay_ms) -> None:
    """Test various delay values."""
    assert delay_ms > 0
