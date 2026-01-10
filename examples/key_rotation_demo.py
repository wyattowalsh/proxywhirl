#!/usr/bin/env python3
"""
Demo: Key Rotation for Cache Encryption

Demonstrates how to use MultiFernet for gradual key rotation in the
proxywhirl cache encryption system.

Usage:
    python examples/key_rotation_demo.py
"""

import os

from cryptography.fernet import Fernet
from pydantic import SecretStr

from proxywhirl.cache.crypto import CredentialEncryptor, rotate_key


def main() -> None:
    """Demonstrate key rotation workflow."""
    print("=== ProxyWhirl Key Rotation Demo ===\n")

    # Step 1: Start with initial key
    print("Step 1: Create initial encryption key")
    key1 = Fernet.generate_key().decode()
    os.environ["PROXYWHIRL_CACHE_ENCRYPTION_KEY"] = key1
    print(f"  Initial key: {key1[:20]}...\n")

    # Encrypt some data with the first key
    encryptor1 = CredentialEncryptor()
    password1 = SecretStr("my_secret_password")
    encrypted1 = encryptor1.encrypt(password1)
    print(f"  Encrypted password: {encrypted1[:40]}...\n")

    # Step 2: Rotate to a new key
    print("Step 2: Rotate to new encryption key")
    key2 = Fernet.generate_key().decode()
    rotate_key(key2)
    print(f"  New key: {key2[:20]}...")
    print(f"  Previous key: {os.environ['PROXYWHIRL_CACHE_KEY_PREVIOUS'][:20]}...\n")

    # Step 3: Create new encryptor with rotated keys
    print("Step 3: Verify backward compatibility")
    encryptor2 = CredentialEncryptor()

    # Should still decrypt old data
    decrypted1 = encryptor2.decrypt(encrypted1)
    print(f"  Old password decrypted: {decrypted1.get_secret_value()}")

    # New data encrypted with new key
    password2 = SecretStr("new_password_after_rotation")
    encrypted2 = encryptor2.encrypt(password2)
    decrypted2 = encryptor2.decrypt(encrypted2)
    print(f"  New password decrypted: {decrypted2.get_secret_value()}\n")

    # Step 4: Environment variables
    print("Step 4: Current environment state")
    print(f"  PROXYWHIRL_CACHE_ENCRYPTION_KEY: {key2[:20]}... (current)")
    print(f"  PROXYWHIRL_CACHE_KEY_PREVIOUS: {key1[:20]}... (previous)\n")

    print("✓ Key rotation complete!")
    print("\nKey Points:")
    print("  - Old data can still be decrypted with previous key")
    print("  - New data is encrypted with current key")
    print("  - No downtime during key rotation")
    print("  - Gradual migration path for re-encrypting old data")


if __name__ == "__main__":
    main()
