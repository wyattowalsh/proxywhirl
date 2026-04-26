---
title: Security Model
---

# Security Model

ProxyWhirl handles proxy credentials, encrypts cached data, redacts sensitive information in logs, and protects against SSRF. This page explains the defense-in-depth approach.

## Credential Handling

Proxy credentials flow through multiple layers, each with appropriate protection:

### In Memory (Runtime)

Credentials are stored as Pydantic `SecretStr` fields:

```python
class Proxy(BaseModel):
    username: SecretStr | None = None
    password: SecretStr | None = None
```

`SecretStr` prevents accidental exposure:
- `str(proxy.password)` returns `'**********'`
- `proxy.model_dump()` redacts by default
- Loguru formatters never see the plaintext

### At Rest (L2/L3 Cache)

Credentials in the L2 disk cache and L3 SQLite database are encrypted with **Fernet** (symmetric AES-128-CBC with HMAC-SHA256):

```python
# Encryption key from environment
key = os.environ["PROXYWHIRL_CACHE_ENCRYPTION_KEY"]

# CredentialEncryptor handles encrypt/decrypt transparently
encryptor = CredentialEncryptor(key)
encrypted = encryptor.encrypt(credential_bytes)
```

Without the encryption key, L2/L3 store credentials in plaintext -- suitable for development but not production. The `PROXYWHIRL_CACHE_ENCRYPTION_KEY` should be a Fernet key generated via `cryptography.fernet.Fernet.generate_key()`.

### In Transit (Logs and Errors)

All log messages and exception objects pass through URL redaction:

```python
# Before: http://user:secret@proxy.example.com:8080
# After:  http://***:***@proxy.example.com:8080
redacted = redact_url(proxy_url)
```

The `redact_url()` utility in `exceptions.py` strips userinfo from URLs before they appear in:
- Log messages (Loguru)
- Exception messages (`ProxyWhirlError` and subclasses)
- API error responses
- CLI output

## SSRF Protection

The API server validates target URLs to prevent Server-Side Request Forgery:

- **Private IP ranges blocked**: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`
- **Metadata endpoints blocked**: AWS `169.254.169.254`, GCP metadata, Azure IMDS
- **Localhost blocked**: Prevents using the proxy to access internal services

The CLI provides `--allow-private` for testing against local services, but the API enforces restrictions by default.

## Encryption Architecture

```
Master Key (PROXYWHIRL_KEY)
├── CLI configuration encryption
└── Credential encryption in config files

Cache Key (PROXYWHIRL_CACHE_ENCRYPTION_KEY)
├── L2 disk cache credential fields
└── L3 SQLite credential BLOBs
```

Two separate keys isolate concerns: the master key protects configuration-level secrets, while the cache key protects runtime cached data. Rotation of one key doesn't require rotating the other.

## ReDoS Protection

User-provided regex patterns (e.g., for custom proxy parsers) are validated for complexity before execution via `safe_regex.py`:

- **Complexity analysis**: Detects patterns with exponential backtracking potential
- **Timeout enforcement**: Regex execution has a configurable timeout
- **Dedicated exceptions**: `RegexTimeoutError` and `RegexComplexityError` for clear error handling

This prevents a malicious or poorly-written regex from hanging the application.

## API Authentication

The REST API uses API key authentication via the `X-API-Key` header:

```bash
curl -H "X-API-Key: $PROXYWHIRL_API_KEY" http://localhost:8000/api/v1/proxies
```

The MCP server has its own key (`PROXYWHIRL_MCP_API_KEY`) to isolate AI assistant access from direct API access.

## Summary of Defenses

| Threat | Defense | Component |
|--------|---------|-----------|
| Credential leakage in logs | `SecretStr` + `redact_url()` | `models/core.py`, `exceptions.py` |
| Credential leakage at rest | Fernet encryption | `cache/crypto.py` |
| SSRF via proxy | Private IP blocking | `api/core.py` |
| ReDoS via regex | Complexity analysis + timeout | `safe_regex.py` |
| Unauthorized API access | API key authentication | `api/core.py`, `mcp/auth.py` |
| Configuration tampering | Master key encryption | `config.py`, `utils.py` |

## Further Reading

- {doc}`/guides/deployment-security` -- production deployment hardening
- {doc}`/reference/configuration` -- environment variable reference
- {doc}`/reference/exceptions` -- `redact_url()` and error handling
