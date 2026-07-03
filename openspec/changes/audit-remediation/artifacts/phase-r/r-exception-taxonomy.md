# R-004: Exception Narrowing Taxonomy

See `openspec/changes/audit-remediation/artifacts/phase-v/v-rv004-matrix.csv` for the full per-line
narrowing decisions. Summary taxonomy applied across `fetchers.py` and `storage.py`:

| Domain | Concrete exception types | Source |
| ------ | ------------------------ | ------ |
| Network / HTTP | `httpx.HTTPError` (base of `httpx.RequestError`, `httpx.HTTPStatusError`, `httpx.TimeoutException`) | httpx |
| Socket / filesystem I/O | `OSError` (covers `IOError`, `ConnectionError`, `FileNotFoundError`, `PermissionError`) | stdlib |
| Timeout | `TimeoutError` (stdlib; distinct from `proxywhirl.exceptions.TimeoutError` which is only raised internally) | stdlib |
| Parsing / validation | `ValueError`, `TypeError`, `KeyError` | stdlib + pydantic `ValidationError` (subclasses `ValueError`) |
| Domain errors | `ProxyFetchError`, `ProxyValidationError`, `ProxyStorageError` | `proxywhirl/exceptions.py` |
| Crypto | `ValueError` (raised by `CredentialEncryptor`/`get_encryption_keys` on invalid Fernet key/decrypt failure) | `proxywhirl/cache/crypto.py` |

## Principle applied

Prefer the narrowest type that is actually raised by the code in the `try` block, confirmed by reading
the callee implementation (not guessed). Where a boundary wraps genuinely pluggable/external code
(e.g., custom parser classes in `ProxyFetcher.fetch_from_source`), narrow to the taxonomy of exceptions
that boundary is documented to convert (`ProxyFetchError`/`ProxyValidationError`/parsing errors) rather
than a bare `Exception`, so unrelated programming errors (e.g. `ImportError`, `RecursionError`) are not
silently swallowed.
