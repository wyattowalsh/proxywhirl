"""Tests for authentication module."""

from __future__ import annotations

import time

from proxywhirl.auth import (
    APIKeyManager,
    KeyRateLimiter,
    RateLimitQuota,
    WebhookSigner,
    WebhookVerifier,
)


class TestAPIKeyManager:
    """Test API key management."""

    def test_generate_key(self):
        """Test key generation."""
        manager = APIKeyManager()
        secret, api_key = manager.generate_key("test-key")

        assert api_key.name == "test-key"
        assert api_key.is_active is True
        assert secret != ""
        assert api_key.key_hash != ""

    def test_validate_key_success(self):
        """Test successful key validation."""
        manager = APIKeyManager()
        secret, api_key = manager.generate_key("test-key")

        validated = manager.validate_key(api_key.key_id, secret)
        assert validated is not None
        assert validated.key_id == api_key.key_id

    def test_validate_key_invalid_secret(self):
        """Test validation fails with wrong secret."""
        manager = APIKeyManager()
        secret, api_key = manager.generate_key("test-key")

        validated = manager.validate_key(api_key.key_id, "wrong-secret")
        assert validated is None

    def test_validate_key_unknown_id(self):
        """Test validation fails with unknown key ID."""
        manager = APIKeyManager()
        validated = manager.validate_key("unknown-id", "secret")
        assert validated is None

    def test_revoke_key(self):
        """Test key revocation."""
        manager = APIKeyManager()
        secret, api_key = manager.generate_key("test-key")

        assert manager.revoke_key(api_key.key_id) is True
        validated = manager.validate_key(api_key.key_id, secret)
        assert validated is None

    def test_list_keys(self):
        """Test listing keys."""
        manager = APIKeyManager()
        manager.generate_key("key1")
        manager.generate_key("key2")
        secret3, api_key3 = manager.generate_key("key3")

        keys = manager.list_keys()
        assert len(keys) == 3

        manager.revoke_key(api_key3.key_id)
        keys = manager.list_keys(active_only=True)
        assert len(keys) == 2

    def test_key_expiration(self):
        """Test key expiration."""
        manager = APIKeyManager()
        secret, api_key = manager.generate_key("test-key", expires_in_days=0)

        time.sleep(0.1)
        validated = manager.validate_key(api_key.key_id, secret)
        assert validated is None


class TestKeyRateLimiter:
    """Test per-key rate limiting."""

    def test_rate_limit_minute(self):
        """Test per-minute rate limit."""
        limiter = KeyRateLimiter()
        key_id = "test-key"

        for i in range(60):
            allowed, remaining = limiter.check_limit(key_id)
            assert allowed is True

        allowed, remaining = limiter.check_limit(key_id)
        assert allowed is False
        assert remaining["minute"] == 0

    def test_rate_limit_custom_quota(self):
        """Test custom quota."""
        limiter = KeyRateLimiter()
        key_id = "test-key"

        custom_quota = RateLimitQuota(
            requests_per_minute=10, requests_per_hour=100, requests_per_day=1000
        )
        limiter.set_quota(key_id, custom_quota)

        for i in range(10):
            allowed, _ = limiter.check_limit(key_id)
            assert allowed is True

        allowed, _ = limiter.check_limit(key_id)
        assert allowed is False

    def test_rate_limit_reset(self):
        """Test rate limit window reset."""
        limiter = KeyRateLimiter()
        key_id = "test-key"

        custom_quota = RateLimitQuota(
            requests_per_minute=2, requests_per_hour=100, requests_per_day=1000
        )
        limiter.set_quota(key_id, custom_quota)

        allowed1, _ = limiter.check_limit(key_id)
        allowed2, _ = limiter.check_limit(key_id)
        allowed3, _ = limiter.check_limit(key_id)

        assert allowed1 is True
        assert allowed2 is True
        assert allowed3 is False

    def test_get_reset_times(self):
        """Test getting reset times."""
        limiter = KeyRateLimiter()
        key_id = "test-key"

        limiter.check_limit(key_id)
        reset_times = limiter.get_reset_times(key_id)

        assert "minute" in reset_times
        assert "hour" in reset_times
        assert "day" in reset_times


class TestWebhookSigning:
    """Test webhook signing and verification."""

    def test_sign_payload(self):
        """Test payload signing."""
        signer = WebhookSigner(secret="test-secret")
        payload = b"test-payload"

        signature = signer.sign(payload)
        assert signature != ""
        assert len(signature) == 64  # SHA256 hex is 64 chars

    def test_sign_json(self):
        """Test JSON signing."""
        signer = WebhookSigner(secret="test-secret")
        json_str = '{"key": "value"}'

        signature = signer.sign_json(json_str)
        assert signature != ""

    def test_verify_valid_signature(self):
        """Test valid signature verification."""
        secret = "test-secret"
        signer = WebhookSigner(secret=secret)
        verifier = WebhookVerifier(secret=secret)

        payload = b"test-payload"
        signature = signer.sign(payload)

        assert verifier.verify(payload, signature) is True

    def test_verify_invalid_signature(self):
        """Test invalid signature verification."""
        secret = "test-secret"
        verifier = WebhookVerifier(secret=secret)

        payload = b"test-payload"
        assert verifier.verify(payload, "invalid-signature") is False

    def test_verify_request_valid(self):
        """Test valid request verification."""
        secret = "test-secret"
        signer = WebhookSigner(secret=secret)
        verifier = WebhookVerifier(secret=secret, timestamp_tolerance_seconds=10)

        payload = b"test-payload"
        signature = signer.sign(payload)

        import time

        timestamp = str(int(time.time()))
        is_valid, error = verifier.verify_request(payload, signature, timestamp)

        assert is_valid is True
        assert error is None

    def test_verify_request_timestamp_too_old(self):
        """Test timestamp validation."""
        secret = "test-secret"
        signer = WebhookSigner(secret=secret)
        verifier = WebhookVerifier(secret=secret, timestamp_tolerance_seconds=1)

        payload = b"test-payload"
        signature = signer.sign(payload)

        import time

        old_timestamp = str(int(time.time()) - 10)
        is_valid, error = verifier.verify_request(payload, signature, old_timestamp)

        assert is_valid is False
        assert "too old" in error.lower()
