# Security Best Practices

ProxyWhirl handles credentials, URLs, and user-supplied patterns. This guide covers the built-in security utilities and recommended practices for production deployments.

## Credential Protection

### Encryption at Rest

Use `CredentialEncryptor` to store proxy passwords securely before writing them to disk or databases.

```python
from proxywhirl.utils import CredentialEncryptor, generate_encryption_key

key = generate_encryption_key()  # Store in PROXYWHIRL_KEY env var
encryptor = CredentialEncryptor(key)

cipher = encryptor.encrypt("my_secret_password")
plain = encryptor.decrypt(cipher)
```

Never commit encryption keys to version control. Load them from environment variables.

### Masking in Logs

ProxyWhirl automatically redacts credentials in log output when `redact_credentials=True` is passed to `configure_logging`.

```python
from proxywhirl.utils import configure_logging

configure_logging(
    level="INFO",
    redact_credentials=True,
)
```

For one-off URL sanitization, use `mask_proxy_url` or `sanitize_url_for_display`:

```python
from proxywhirl.utils import mask_proxy_url, sanitize_url_for_display

masked = mask_proxy_url("http://user:pass@proxy.com:8080")
# http://***:***@proxy.com:8080

safe = sanitize_url_for_display("http://user:pass@proxy.com:8080/path")
# http://proxy.com:8080/path
```

## Regex Safety

User-provided regex patterns are a common source of ReDoS (Regular Expression Denial of Service). ProxyWhirl provides `safe_compile_regex` and `validate_regex_pattern` to guard against catastrophic backtracking.

```python
from proxywhirl.safe_regex import safe_compile_regex, RegexComplexityError

try:
    pattern = safe_compile_regex(r"(a+)+b", max_complexity=100)
except RegexComplexityError:
    raise ValueError("Pattern is too complex and may cause ReDoS")
```

Always validate externally supplied patterns before using them in parsers or filters.

## URL Validation

Before adding a proxy to the pool, validate its URL structure to prevent injection or malformed requests.

```python
from proxywhirl.utils import is_valid_proxy_url, parse_proxy_url

if not is_valid_proxy_url(url):
    raise ValueError(f"Invalid proxy URL: {url}")

components = parse_proxy_url(url)
# Returns scheme, host, port, username, password
```

## Environment Variable Isolation

ProxyWhirl recognizes several environment variables for sensitive configuration. Keep these isolated per deployment:

| Variable                                      | Purpose                                                    |
| --------------------------------------------- | ---------------------------------------------------------- |
| `PROXYWHIRL_KEY`                              | Master encryption key for credentials                      |
| `PROXYWHIRL_CACHE_ENCRYPTION_KEY`             | L2 cache Fernet key                                        |
| `PROXYWHIRL_API_KEY`                          | API authentication key                                     |
| `PROXYWHIRL_MCP_API_KEY`                      | MCP server auth key                                        |
| `PROXYWHIRL_MCP_ALLOW_UNAUTHENTICATED_WRITES` | Local-dev/test MCP write override; never set in production |

Use a secrets manager (e.g., AWS Secrets Manager, HashiCorp Vault) rather than `.env` files in production.

## MCP Server Authentication

When `PROXYWHIRL_MCP_API_KEY` is configured, MCP clients should send credentials out-of-band via MCP metadata or transport headers such as `Authorization: Bearer <key>` or `X-API-Key: <key>`. The `proxywhirl` tool schema intentionally does not expose an `api_key` argument to the model.

Mutating MCP actions (`add`, `remove`, `reset_cb`, `fetch`, `validate`, and `set_strategy`) fail closed when no API key is configured unless `PROXYWHIRL_MCP_ALLOW_UNAUTHENTICATED_WRITES=1` is explicitly set for local development or tests. Do not enable that override in production.

MCP responses strip credentials from proxy URLs, including exception text returned to clients. Keep credentialed proxy URLs out of prompts and prefer secret stores or client-side metadata for credentials.

## Input Validation

ProxyWhirl models use `pydantic` with `ConfigDict(extra="forbid")`. This prevents typos and unexpected fields from silently being ignored.

```python
from proxywhirl import ProxyConfiguration

# Raises validation error because 'timeoutt' is a typo
config = ProxyConfiguration(timeoutt=30)
```

## Summary Checklist

- [ ] Encryption keys loaded from environment, never hardcoded.
- [ ] Logging configured with `redact_credentials=True`.
- [ ] User-supplied regex validated with `safe_compile_regex`.
- [ ] Proxy URLs validated with `is_valid_proxy_url` before use.
- [ ] Secrets managed via a secrets manager, not `.env` files in prod.
- [ ] Pydantic `extra="forbid"` enabled to catch misconfigurations.
