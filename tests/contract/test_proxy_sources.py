"""Contract tests for external proxy sources.

This module validates that external proxy source APIs still return data
in the expected format. These tests require network access and can be
skipped in CI environments.

The tests verify:
1. Source is accessible (HTTP 200)
2. Response format matches expected format
3. Response contains valid proxy data
4. Parsing succeeds without errors

Contract tests are marked with @pytest.mark.network to allow selective
execution via: pytest -m network
"""

import asyncio

import httpx
import pytest

from proxywhirl.fetchers import (
    JSONParser,
    ProxySourceConfig,
)
from proxywhirl.sources import (
    GEONODE_HTTP,
    GITHUB_KOMUTAN_HTTP,
    GITHUB_MONOSANS_HTTP,
    GITHUB_PROXIFLY_HTTP,
    PROXY_SCRAPE_HTTP,
)

# =============================================================================
# Proxy Source Contract Documentation
# =============================================================================

"""
PROXY SOURCE API CONTRACTS
===========================

This document describes the expected contracts for external proxy sources
tested in this module. These contracts are based on observations as of
December 2025 and may change if providers update their APIs.

1. ProxyScrape API (https://api.proxyscrape.com)
   ----------------------------------------------
   Format: Plain text (one proxy per line)
   Rate Limit: None observed (as of Dec 2025)
   Schema:
       - Each line: IP:PORT (e.g., "1.2.3.4:8080")
       - Empty lines allowed
       - No comments or headers
   Example:
       1.2.3.4:8080
       5.6.7.8:3128
       9.10.11.12:80

2. GeoNode API (https://proxylist.geonode.com)
   -------------------------------------------
   Format: JSON
   Rate Limit: Unknown, but pagination supported
   Schema:
       {
           "data": [
               {
                   "ip": "1.2.3.4",
                   "port": "8080",
                   "protocols": ["http", "https"],
                   "country": "US",
                   "anonymityLevel": "elite",
                   "speed": 1234,
                   "upTime": 95,
                   "lastChecked": 1234567890
               },
               ...
           ],
           "total": 1000,
           "page": 1,
           "limit": 500
       }

3. GitHub Raw Text Files (monosans, proxifly, komutan)
   ---------------------------------------------------
   Format: Plain text (one proxy per line)
   Rate Limit: GitHub API rate limits apply
   Update Frequency:
       - monosans: Every 5 minutes
       - proxifly: Varies (verified working proxies)
       - komutan: Every 2 minutes (fastest update)
   Schema:
       - Each line: IP:PORT (e.g., "1.2.3.4:8080")
       - No protocol prefix
       - Empty lines allowed
       - Comments starting with # may appear
   Example:
       1.2.3.4:8080
       5.6.7.8:3128
       # This is a comment
       9.10.11.12:80

4. General Contract Expectations
   -----------------------------
   All sources must:
   - Return HTTP 200 on success
   - Provide non-empty response body
   - Contain parseable proxy data (IP:PORT format)
   - Support basic HTTP GET requests
   - Not require authentication (free sources)

5. Failure Modes
   -------------
   Expected failure scenarios:
   - Temporary network issues (timeout, connection reset)
   - Rate limiting (HTTP 429)
   - Service downtime (HTTP 5xx)
   - Changed API format (parsing errors)

   Tests should be tolerant of temporary failures but alert
   on persistent contract violations.
"""


# =============================================================================
# Test Configuration
# =============================================================================

# Network timeout for contract tests (longer than normal to handle slow APIs)
NETWORK_TIMEOUT = 30.0

# Minimum expected content length (bytes) to consider response valid
MIN_CONTENT_LENGTH = 100


# =============================================================================
# Helper Functions
# =============================================================================


def validate_plain_text_format(content: str) -> tuple[bool, str]:
    """Validate plain text proxy format.

    Args:
        content: Response content to validate

    Returns:
        Tuple of (is_valid, error_message)
        is_valid is True if format is valid, False otherwise
    """
    if not content or len(content) < MIN_CONTENT_LENGTH:
        return (
            False,
            f"Content too short (got {len(content)} bytes, expected >{MIN_CONTENT_LENGTH})",
        )

    lines = [
        line.strip() for line in content.split("\n") if line.strip() and not line.startswith("#")
    ]

    if not lines:
        return False, "No valid proxy lines found"

    # Validate at least some lines have IP:PORT format (with or without scheme)
    valid_lines = 0
    for line in lines[:10]:  # Check first 10 lines
        if ":" in line:
            # Handle both "IP:PORT" and "scheme://IP:PORT" formats
            if line.startswith(("http://", "https://", "socks4://", "socks5://")):
                # Full URL format
                parts = line.split("//", 1)[1].split(":")
            else:
                # Just IP:PORT format
                parts = line.split(":")

            if len(parts) >= 2:
                port = parts[-1]  # Last part should be port
                if port.isdigit() and 1 <= int(port) <= 65535:
                    valid_lines += 1

    if valid_lines == 0:
        return False, "No valid IP:PORT format found in first 10 lines"

    return True, ""


def validate_json_format(content: str) -> tuple[bool, str]:
    """Validate JSON proxy format.

    Args:
        content: Response content to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    import json

    if not content or len(content) < MIN_CONTENT_LENGTH:
        return (
            False,
            f"Content too short (got {len(content)} bytes, expected >{MIN_CONTENT_LENGTH})",
        )

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    # GeoNode specific validation
    if not isinstance(data, dict):
        return False, "JSON root must be an object"

    if "data" not in data:
        return False, "Missing 'data' field in JSON"

    if not isinstance(data["data"], list):
        return False, "'data' field must be an array"

    if not data["data"]:
        return False, "'data' array is empty"

    # Validate first proxy entry has expected fields
    first_proxy = data["data"][0]
    required_fields = ["ip", "port", "protocols"]
    for field in required_fields:
        if field not in first_proxy:
            return False, f"Missing required field '{field}' in proxy data"

    return True, ""


async def fetch_source_content(
    source: ProxySourceConfig, timeout: float = NETWORK_TIMEOUT
) -> tuple[int, str, str]:
    """Fetch content from a proxy source.

    Args:
        source: Proxy source configuration
        timeout: Request timeout in seconds

    Returns:
        Tuple of (status_code, content, error_message)
        error_message is empty string if no error
    """
    try:
        # Convert HttpUrl to string for httpx compatibility
        url = str(source.url)
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
            response = await client.get(url)
            return response.status_code, response.text, ""
    except httpx.TimeoutException:
        return 0, "", f"Request timeout after {timeout}s"
    except httpx.ConnectError as e:
        return 0, "", f"Connection error: {e}"
    except Exception as e:
        return 0, "", f"Unexpected error: {e}"


# =============================================================================
# Contract Tests - ProxyScrape API
# =============================================================================


@pytest.mark.network
async def test_proxyscrape_http_contract():
    """Test ProxyScrape HTTP API contract.

    Validates:
    - API returns HTTP 200
    - Response is plain text format
    - Contains valid IP:PORT entries

    Note: ProxyScrape may return "Invalid API request" if rate limited.
    The test will be skipped if this occurs.
    """
    source = PROXY_SCRAPE_HTTP

    # Fetch content
    status_code, content, error = await fetch_source_content(source)

    # Validate response
    assert error == "", f"Failed to fetch ProxyScrape: {error}"
    assert status_code == 200, f"ProxyScrape returned status {status_code}"

    # Skip if rate limited
    if "Invalid API request" in content or len(content) < MIN_CONTENT_LENGTH:
        pytest.skip(f"ProxyScrape appears rate limited or down (content: {content[:100]})")

    # Validate format
    is_valid, format_error = validate_plain_text_format(content)
    assert is_valid, f"ProxyScrape format validation failed: {format_error}"


# =============================================================================
# Contract Tests - GeoNode API
# =============================================================================


@pytest.mark.network
async def test_geonode_http_contract():
    """Test GeoNode HTTP API contract.

    Validates:
    - API returns HTTP 200
    - Response is valid JSON
    - Contains 'data' array with proxy objects
    - Each proxy has required fields (ip, port, protocols)
    - Parser can process the response
    """
    source = GEONODE_HTTP

    # Fetch content
    status_code, content, error = await fetch_source_content(source)

    # Validate response
    assert error == "", f"Failed to fetch GeoNode: {error}"
    assert status_code == 200, f"GeoNode returned status {status_code}"

    # Validate format
    is_valid, format_error = validate_json_format(content)
    assert is_valid, f"GeoNode format validation failed: {format_error}"

    # Validate parser can process
    parser = JSONParser(key="data")
    proxies = parser.parse(content)
    assert len(proxies) > 0, "GeoNode parser returned no proxies"

    # Validate required fields in parsed proxies
    first_proxy = proxies[0]
    assert "ip" in first_proxy, "Parsed proxy missing 'ip' field"
    assert "port" in first_proxy, "Parsed proxy missing 'port' field"
    assert "protocols" in first_proxy, "Parsed proxy missing 'protocols' field"


# =============================================================================
# Contract Tests - GitHub monosans
# =============================================================================


@pytest.mark.network
async def test_github_monosans_http_contract():
    """Test GitHub monosans HTTP proxy list contract.

    Validates:
    - GitHub raw URL is accessible
    - Response is plain text format
    - Contains valid IP:PORT entries

    Note: GitHub sources return IP:PORT format without scheme prefix.
    """
    source = GITHUB_MONOSANS_HTTP

    # Verify source configuration
    assert source.format.value == "plain_text", "monosans should use plain_text format"

    # Fetch content
    status_code, content, error = await fetch_source_content(source)

    # Validate response
    assert error == "", f"Failed to fetch monosans: {error}"
    assert status_code == 200, f"monosans returned status {status_code}"

    # Validate format
    is_valid, format_error = validate_plain_text_format(content)
    assert is_valid, f"monosans format validation failed: {format_error}"

    # Count valid proxy lines (GitHub sources use IP:PORT format without scheme)
    lines = [
        line.strip() for line in content.split("\n") if line.strip() and not line.startswith("#")
    ]
    proxy_lines = [line for line in lines if ":" in line and line.split(":")[-1].isdigit()]
    assert len(proxy_lines) > 0, "monosans returned no valid proxy lines"


# =============================================================================
# Contract Tests - GitHub proxifly
# =============================================================================


@pytest.mark.network
async def test_github_proxifly_http_contract():
    """Test GitHub proxifly HTTP proxy list contract.

    Validates:
    - GitHub raw URL is accessible
    - Response is plain text format
    - Contains valid IP:PORT entries

    Note: GitHub sources return IP:PORT format without scheme prefix.
    """
    source = GITHUB_PROXIFLY_HTTP

    # Verify source configuration
    assert source.format.value == "plain_text", "proxifly should use plain_text format"

    # Fetch content
    status_code, content, error = await fetch_source_content(source)

    # Validate response
    assert error == "", f"Failed to fetch proxifly: {error}"
    assert status_code == 200, f"proxifly returned status {status_code}"

    # Validate format
    is_valid, format_error = validate_plain_text_format(content)
    assert is_valid, f"proxifly format validation failed: {format_error}"

    # Count valid proxy lines (GitHub sources use IP:PORT format without scheme)
    lines = [
        line.strip() for line in content.split("\n") if line.strip() and not line.startswith("#")
    ]
    proxy_lines = [line for line in lines if ":" in line and line.split(":")[-1].isdigit()]
    assert len(proxy_lines) > 0, "proxifly returned no valid proxy lines"


# =============================================================================
# Contract Tests - GitHub komutan
# =============================================================================


@pytest.mark.network
async def test_github_komutan_http_contract():
    """Test GitHub komutan HTTP proxy list contract.

    Validates:
    - GitHub raw URL is accessible
    - Response is plain text format
    - Contains valid IP:PORT entries

    Note: GitHub sources return IP:PORT format without scheme prefix.
    """
    source = GITHUB_KOMUTAN_HTTP

    # Verify source configuration
    assert source.format.value == "plain_text", "komutan should use plain_text format"

    # Fetch content
    status_code, content, error = await fetch_source_content(source)

    # Validate response
    assert error == "", f"Failed to fetch komutan: {error}"
    assert status_code == 200, f"komutan returned status {status_code}"

    # Validate format
    is_valid, format_error = validate_plain_text_format(content)
    assert is_valid, f"komutan format validation failed: {format_error}"

    # Count valid proxy lines (GitHub sources use IP:PORT format without scheme)
    lines = [
        line.strip() for line in content.split("\n") if line.strip() and not line.startswith("#")
    ]
    proxy_lines = [line for line in lines if ":" in line and line.split(":")[-1].isdigit()]
    assert len(proxy_lines) > 0, "komutan returned no valid proxy lines"


# =============================================================================
# Integration Test - All Sources Together
# =============================================================================


@pytest.mark.network
async def test_all_top_sources_together():
    """Integration test for all top 5 sources together.

    Validates:
    - All sources are accessible (HTTP 200)
    - All sources return proxy data in expected format
    - No exceptions raised during fetching
    - Sources can be fetched concurrently

    Note: This test validates the API contracts are still valid, not that
    the ProxyFetcher can parse all formats (GitHub sources use IP:PORT
    format that requires scheme prefix to be added before parsing).
    """
    sources = [
        PROXY_SCRAPE_HTTP,
        GEONODE_HTTP,
        GITHUB_MONOSANS_HTTP,
        GITHUB_PROXIFLY_HTTP,
        GITHUB_KOMUTAN_HTTP,
    ]

    # Fetch all sources concurrently

    async def check_source(source: ProxySourceConfig) -> tuple[ProxySourceConfig, bool, str]:
        """Check if source is healthy."""
        status_code, content, error = await fetch_source_content(source)
        url_str = str(source.url)

        if error:
            return source, False, f"Fetch error: {error}"

        if status_code != 200:
            return source, False, f"Status {status_code}"

        # Check for ProxyScrape rate limit
        if "proxyscrape" in url_str.lower() and "Invalid API request" in content:
            return source, False, "Rate limited"

        # Validate format
        if source.format.value == "plain_text":
            is_valid, format_error = validate_plain_text_format(content)
        elif source.format.value == "json":
            is_valid, format_error = validate_json_format(content)
        else:
            return source, False, f"Unknown format: {source.format}"

        if not is_valid:
            return source, False, f"Format error: {format_error}"

        return source, True, "OK"

    results = await asyncio.gather(*[check_source(src) for src in sources])

    # Report results
    healthy_count = sum(1 for _, is_healthy, _ in results if is_healthy)
    unhealthy = [(src, msg) for src, is_healthy, msg in results if not is_healthy]

    # Print summary
    print(f"\n{'=' * 80}")
    print(f"Source Health Check: {healthy_count}/{len(sources)} healthy")
    if unhealthy:
        print("\nUnhealthy sources:")
        for src, msg in unhealthy:
            url_str = str(src.url)
            name = url_str.split("/")[-1] if "github" in url_str else url_str.split("?")[0]
            print(f"  - {name}: {msg}")
    print(f"{'=' * 80}")

    # At least 60% of sources should be healthy (allows for temporary outages)
    health_ratio = healthy_count / len(sources)
    assert health_ratio >= 0.6, (
        f"Too many unhealthy sources ({len(sources) - healthy_count}/{len(sources)}). "
        f"Expected at least 60% healthy, got {health_ratio:.1%}"
    )


# =============================================================================
# Contract Validation Report
# =============================================================================


@pytest.mark.network
async def test_generate_contract_validation_report():
    """Generate a comprehensive contract validation report.

    This test validates all top sources and generates a detailed report
    showing which sources are healthy and which may have contract violations.
    """
    from proxywhirl.sources import validate_sources

    sources = [
        PROXY_SCRAPE_HTTP,
        GEONODE_HTTP,
        GITHUB_MONOSANS_HTTP,
        GITHUB_PROXIFLY_HTTP,
        GITHUB_KOMUTAN_HTTP,
    ]

    # Run validation
    report = await validate_sources(sources=sources, timeout=NETWORK_TIMEOUT, concurrency=5)

    # Print report (will show in pytest output with -v)
    print("\n" + "=" * 80)
    print("PROXY SOURCE CONTRACT VALIDATION REPORT")
    print("=" * 80)
    print(f"Total Sources: {report.total_sources}")
    print(f"Healthy: {report.healthy_sources}")
    print(f"Unhealthy: {report.unhealthy_sources}")
    print(f"Total Time: {report.total_time_ms:.2f}ms")
    print()

    if report.healthy:
        print("✓ HEALTHY SOURCES:")
        print("-" * 80)
        for result in report.healthy:
            print(f"  ✓ {result.name}")
            print(f"    - Status: {result.status_code}")
            print(f"    - Content Length: {result.content_length} bytes")
            print(f"    - Response Time: {result.response_time_ms:.2f}ms")
            print()

    if report.unhealthy:
        print("✗ UNHEALTHY SOURCES:")
        print("-" * 80)
        for result in report.unhealthy:
            print(f"  ✗ {result.name}")
            print(f"    - Status: {result.status_code}")
            print(f"    - Content Length: {result.content_length} bytes")
            print(f"    - Error: {result.error}")
            print()

    print("=" * 80)

    # Assert at least 80% of sources are healthy
    health_ratio = report.healthy_sources / report.total_sources
    assert health_ratio >= 0.8, (
        f"Too many unhealthy sources ({report.unhealthy_sources}/{report.total_sources}). "
        f"Expected at least 80% healthy, got {health_ratio:.1%}"
    )
