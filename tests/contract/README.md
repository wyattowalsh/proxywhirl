# Contract Tests

Contract tests validate that external dependencies (APIs, proxy sources, etc.) still return data in the expected format. These tests ensure that third-party services haven't changed their API contracts in ways that would break proxywhirl's integrations.

## Purpose

Contract tests verify:

1. **External API availability** - Services are accessible and responding
2. **Response format stability** - Data structures match expectations
3. **Parsing compatibility** - Our parsers can still process the responses
4. **Integration health** - End-to-end integration still works

## Test Categories

### Proxy Source Contracts (`test_proxy_sources.py`)

Tests that validate external proxy list providers still return data in expected formats:

- **ProxyScrape API** - Plain text proxy lists
- **GeoNode API** - JSON-formatted proxy lists with metadata
- **GitHub monosans** - Plain text, validated every 5 minutes
- **GitHub proxifly** - Plain text, verified working proxies
- **GitHub komutan** - Plain text, updated every 2 minutes

Each test validates:
- HTTP 200 response status
- Content format (plain text or JSON)
- Presence of valid proxy data (IP:PORT format)
- Expected metadata fields (for JSON sources)

### API Endpoint Contracts

Tests in `test_api_*.py` validate the REST API contracts for proxywhirl's own API endpoints.

## Running Contract Tests

### Run All Contract Tests

```bash
# Run all contract tests
uv run pytest tests/contract/ -v -m network

# Run specific contract test file
uv run pytest tests/contract/test_proxy_sources.py -v -m network
```

### Skip Contract Tests (CI Mode)

Contract tests require network access and can be slow. Skip them in CI:

```bash
# Skip all network-dependent tests
uv run pytest -m "not network"

# Run only network tests (for dedicated contract test runs)
uv run pytest -m network
```

### Generate Contract Validation Report

```bash
# Run the comprehensive validation report
uv run pytest tests/contract/test_proxy_sources.py::test_generate_contract_validation_report -v -m network -s
```

This generates a detailed report showing:
- Total sources tested
- Healthy vs unhealthy sources
- Response times
- Error details for unhealthy sources

## Test Markers

Contract tests use pytest markers for selective execution:

- `@pytest.mark.network` - Tests requiring network access
- `@pytest.mark.slow` - Tests that take >1 second
- `@pytest.mark.integration` - Integration tests

## Expected Failures

Contract tests may fail due to:

1. **Temporary outages** - External services down temporarily
2. **Rate limiting** - API rate limits exceeded
3. **Network issues** - Connection timeouts, DNS failures
4. **Format changes** - Provider changed their API format (requires update)

The tests are designed to be tolerant of temporary failures:
- ProxyScrape is skipped if rate limited
- Integration test passes if 60%+ sources are healthy
- Validation report shows warnings but passes if 80%+ healthy

## Documented Contracts

All proxy source contracts are documented in `test_proxy_sources.py` with:

- Expected response format
- Required fields
- Rate limits
- Update frequencies
- Example responses

This documentation serves as a reference for understanding external dependencies.

## Adding New Contract Tests

When adding a new external proxy source:

1. **Add source to `proxywhirl/sources.py`**
2. **Create contract test in `test_proxy_sources.py`**:
   ```python
   @pytest.mark.network
   async def test_new_source_contract():
       """Test description."""
       source = NEW_SOURCE

       # Fetch content
       status_code, content, error = await fetch_source_content(source)

       # Validate response
       assert error == "", f"Failed to fetch: {error}"
       assert status_code == 200

       # Validate format
       is_valid, format_error = validate_plain_text_format(content)
       assert is_valid, f"Format validation failed: {format_error}"
   ```

3. **Document the contract** in the module docstring
4. **Add to integration test** in `test_all_top_sources_together()`
5. **Run tests** to verify

## Maintenance

Contract tests should be:

- **Run regularly** - Daily or before releases
- **Monitored** - Track failure patterns over time
- **Updated promptly** - When providers change formats
- **Documented** - Keep contract documentation current

## CI/CD Integration

In CI pipelines:

```yaml
# Regular test run (skip network tests)
- run: uv run pytest -m "not network"

# Nightly contract validation (include network tests)
- run: uv run pytest -m network --timeout=60
  schedule: "0 0 * * *"  # Daily at midnight
```

## Troubleshooting

### Test Failures

1. **Check network connectivity**
   ```bash
   curl -I https://proxylist.geonode.com/api/proxy-list?limit=1
   ```

2. **Run individual test for details**
   ```bash
   uv run pytest tests/contract/test_proxy_sources.py::test_geonode_http_contract -v -s
   ```

3. **Check validation report**
   ```bash
   uv run pytest tests/contract/test_proxy_sources.py::test_generate_contract_validation_report -v -s
   ```

### Rate Limiting

If seeing rate limit errors:

- **ProxyScrape** - May return "Invalid API request" when rate limited
- **GitHub** - Has rate limits on raw file access
- **GeoNode** - Unknown rate limits, use pagination

Solutions:
- Add delays between requests
- Use authenticated requests (if available)
- Reduce test frequency

## Best Practices

1. ✅ **Mark all network tests** with `@pytest.mark.network`
2. ✅ **Use reasonable timeouts** (30s for contract tests)
3. ✅ **Validate format, not content** (proxy lists change frequently)
4. ✅ **Document expected formats** in module docstrings
5. ✅ **Handle temporary failures** gracefully
6. ✅ **Generate reports** for monitoring trends

## Related Documentation

- [AGENTS.md](/AGENTS.md) - Agent development guidelines
- [Testing Guide](../README.md) - Overall testing strategy
- [ProxyFetcher](/proxywhirl/fetchers.py) - Fetcher implementation
- [Proxy Sources](/proxywhirl/sources.py) - Source configurations
