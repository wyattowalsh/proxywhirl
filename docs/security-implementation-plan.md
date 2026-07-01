# Security Tasks Implementation Plan

> Historical implementation checklist for security hardening tasks. For current guidance, see [security-best-practices](source/security-best-practices.md) and [devops-security-hardening](devops-security-hardening.md).

## Task 1: SSRF Protection with IP Blocklist
- Location: proxywhirl/utils.py, proxywhirl/api/core.py
- Status: EXISTING validate_target_url_safe() exists but needs enhanced blocklist
- Action: Add comprehensive IP blocklist + block private proxies with PrivateIP enum
- Tests: test_security_ssrf_blocklist.py

## Task 2: Credential Redaction in Logs
- Location: proxywhirl/utils.py, proxywhirl/logging_config.py
- Status: EXISTING _redact_sensitive_data() function exists
- Action: Create LoggingFilter class + update logging configuration
- Tests: test_security_credential_redaction.py

## Task 3: Comprehensive Input Validation
- Location: proxywhirl/api/core.py, proxywhirl/models/
- Status: EXISTING validation exists but needs expansion
- Action: Add request validators for all API endpoints
- Tests: test_security_input_validation.py

## Task 4: TLS Certificate Verification
- Location: proxywhirl/fetchers.py, proxywhirl/rotator/
- Status: EXISTING verify_ssl config exists
- Action: Ensure TLS verification enabled by default + CA bundle handling
- Tests: test_security_tls_verification.py

## Task 5: Debug Logging Redaction
- Location: proxywhirl/logging_config.py
- Status: PARTIAL redaction in utils.py
- Action: Create debug filter + ensure sensitive data never logged
- Tests: test_security_debug_logging.py
