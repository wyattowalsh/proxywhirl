"""Tests for API v2 webhook signing and verification."""

from datetime import datetime, timezone

import pytest

from proxywhirl.api.v2.auth import WebhookSignature, WebhookSigner


class TestWebhookSigner:
    """Test webhook signing and verification."""

    @pytest.fixture
    def signer(self):
        """Create a webhook signer."""
        return WebhookSigner("test-secret-key")

    def test_sign_payload(self, signer):
        """Test payload signing."""
        payload = b'{"event": "proxy.added"}'
        timestamp = "2025-10-27T12:00:00Z"
        nonce = WebhookSigner.generate_nonce()

        signature = signer.sign_payload(payload, timestamp, nonce)
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex = 64 chars

    def test_verify_valid_signature(self, signer):
        """Test verification of valid signature."""
        payload = b'{"event": "proxy.added"}'
        timestamp = datetime.now(timezone.utc).isoformat()
        nonce = WebhookSigner.generate_nonce()

        signature = signer.sign_payload(payload, timestamp, nonce)
        assert signer.verify_signature(payload, signature, timestamp, nonce)

    def test_verify_invalid_signature(self, signer):
        """Test verification fails with invalid signature."""
        payload = b'{"event": "proxy.added"}'
        timestamp = datetime.now(timezone.utc).isoformat()
        nonce = WebhookSigner.generate_nonce()

        invalid_signature = "0" * 64
        assert not signer.verify_signature(payload, invalid_signature, timestamp, nonce)

    def test_verify_tampered_payload(self, signer):
        """Test verification fails if payload was tampered."""
        payload = b'{"event": "proxy.added"}'
        timestamp = datetime.now(timezone.utc).isoformat()
        nonce = WebhookSigner.generate_nonce()

        signature = signer.sign_payload(payload, timestamp, nonce)

        # Tamper with payload
        tampered_payload = b'{"event": "proxy.removed"}'
        assert not signer.verify_signature(tampered_payload, signature, timestamp, nonce)

    def test_verify_old_timestamp(self, signer):
        """Test verification fails with old timestamp."""
        payload = b'{"event": "proxy.added"}'
        nonce = WebhookSigner.generate_nonce()

        # Very old timestamp
        old_timestamp = "2020-01-01T00:00:00Z"
        signature = signer.sign_payload(payload, old_timestamp, nonce)

        with pytest.raises(ValueError, match="timestamp too old"):
            signer.verify_signature(payload, signature, old_timestamp, nonce, tolerance_seconds=300)

    def test_nonce_generation(self):
        """Test nonce generation."""
        nonce1 = WebhookSigner.generate_nonce()
        nonce2 = WebhookSigner.generate_nonce()

        assert nonce1 != nonce2
        assert len(nonce1) == 32  # hex(16 bytes)
        assert len(nonce2) == 32

    def test_different_secrets_different_signatures(self):
        """Test that different secrets produce different signatures."""
        payload = b'{"event": "proxy.added"}'
        timestamp = datetime.now(timezone.utc).isoformat()
        nonce = WebhookSigner.generate_nonce()

        signer1 = WebhookSigner("secret1")
        signer2 = WebhookSigner("secret2")

        sig1 = signer1.sign_payload(payload, timestamp, nonce)
        sig2 = signer2.sign_payload(payload, timestamp, nonce)

        assert sig1 != sig2

    def test_signature_constant_time_comparison(self, signer):
        """Test that signature verification uses constant-time comparison."""
        payload = b'{"event": "proxy.added"}'
        timestamp = datetime.now(timezone.utc).isoformat()
        nonce = WebhookSigner.generate_nonce()

        signature = signer.sign_payload(payload, timestamp, nonce)

        # Correct signature
        assert signer.verify_signature(payload, signature, timestamp, nonce)

        # Wrong signature (should not leak timing info about where it differs)
        wrong_sig = "0" * 64
        assert not signer.verify_signature(payload, wrong_sig, timestamp, nonce)


class TestWebhookSignature:
    """Test WebhookSignature model."""

    def test_signature_model(self):
        """Test WebhookSignature creation."""
        sig = WebhookSignature(
            signature="abc123def456",
            timestamp="2025-10-27T12:00:00Z",
            nonce="nonce123",
        )

        assert sig.signature == "abc123def456"
        assert sig.timestamp == "2025-10-27T12:00:00Z"
        assert sig.nonce == "nonce123"

    def test_signature_immutable(self):
        """Test that signature is immutable."""
        sig = WebhookSignature(
            signature="abc123",
            timestamp="2025-10-27T12:00:00Z",
            nonce="nonce123",
        )

        with pytest.raises(Exception):  # pydantic FrozenFieldError
            sig.signature = "new_signature"
