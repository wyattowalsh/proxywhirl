"""Tests for TTL expiration functionality."""

from datetime import datetime, timedelta, timezone

from proxywhirl.models import Proxy


class TestTTLExpiration:
    """Test TTL expiration tracking and enforcement."""

    def test_proxy_is_expired(self) -> None:
        """Test that proxy correctly reports as expired when past expires_at."""
        # Create proxy that expired 1 hour ago
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        proxy = Proxy(url="http://expired.proxy.com:8080", expires_at=past_time)

        assert proxy.is_expired is True

    def test_proxy_not_expired(self) -> None:
        """Test that proxy correctly reports as not expired when before expires_at."""
        # Create proxy that expires 1 hour from now
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        proxy = Proxy(url="http://valid.proxy.com:8080", expires_at=future_time)

        assert proxy.is_expired is False

    def test_proxy_no_expiration_set(self) -> None:
        """Test that proxy without TTL/expires_at never expires."""
        proxy = Proxy(url="http://permanent.proxy.com:8080")

        assert proxy.expires_at is None
        assert proxy.is_expired is False

    def test_ttl_sets_expires_at(self) -> None:
        """Test that setting ttl automatically calculates expires_at."""
        ttl_seconds = 3600  # 1 hour
        proxy = Proxy(url="http://ttl.proxy.com:8080", ttl=ttl_seconds)

        assert proxy.expires_at is not None
        # expires_at should be created_at + ttl
        expected_expires = proxy.created_at + timedelta(seconds=ttl_seconds)
        assert abs((proxy.expires_at - expected_expires).total_seconds()) < 1  # Within 1 second

    def test_explicit_expires_at_overrides_ttl(self) -> None:
        """Test that explicit expires_at is used over ttl."""
        ttl_seconds = 3600
        explicit_expires = datetime.now(timezone.utc) + timedelta(hours=2)
        proxy = Proxy(
            url="http://explicit.proxy.com:8080", ttl=ttl_seconds, expires_at=explicit_expires
        )

        # Should use explicit expires_at, not calculate from ttl
        assert proxy.expires_at == explicit_expires

    def test_proxy_just_expired(self) -> None:
        """Test edge case: proxy that just expired (within last second)."""
        # Create proxy that expired 0.5 seconds ago
        just_expired = datetime.now(timezone.utc) - timedelta(seconds=0.5)
        proxy = Proxy(url="http://just-expired.proxy.com:8080", expires_at=just_expired)

        assert proxy.is_expired is True

    def test_proxy_about_to_expire(self) -> None:
        """Test edge case: proxy that's about to expire (within next second)."""
        # Create proxy that expires in 0.5 seconds
        about_to_expire = datetime.now(timezone.utc) + timedelta(seconds=0.5)
        proxy = Proxy(url="http://about-to-expire.proxy.com:8080", expires_at=about_to_expire)

        assert proxy.is_expired is False  # Still valid for now

    def test_ttl_zero_seconds(self) -> None:
        """Test TTL of 0 seconds (immediately expired)."""
        proxy = Proxy(url="http://instant-expire.proxy.com:8080", ttl=0)

        # Should have expires_at set to created_at (immediately expired)
        assert proxy.expires_at == proxy.created_at
        # Might be expired depending on timing
        # Not asserting is_expired since it depends on microsecond timing

    def test_ttl_negative_seconds(self) -> None:
        """Test TTL with negative seconds (already expired)."""
        proxy = Proxy(url="http://past-expire.proxy.com:8080", ttl=-3600)

        assert proxy.expires_at is not None
        assert proxy.expires_at < proxy.created_at
        assert proxy.is_expired is True
