# Key Rotation Quick Start Guide

This guide shows you how to rotate encryption keys in ProxyWhirl without downtime or data loss.

## What is Key Rotation?

Key rotation is the process of changing encryption keys while maintaining access to data encrypted with old keys. ProxyWhirl uses [MultiFernet](https://cryptography.io/en/latest/fernet/#cryptography.fernet.MultiFernet) to support gradual key rotation.

## Why Rotate Keys?

- **Security Best Practice**: Regular rotation limits exposure if a key is compromised
- **Compliance**: Many security standards require periodic key rotation
- **Zero Trust**: Minimize blast radius of potential key leaks

## Quick Start

### Step 1: Check Current Setup

```bash
# Check if encryption key is set
echo $PROXYWHIRL_CACHE_ENCRYPTION_KEY

# If not set, generate one
export PROXYWHIRL_CACHE_ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
```

### Step 2: Generate New Key

```bash
NEW_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
echo "New key: $NEW_KEY"
```

### Step 3: Perform Rotation

**Option A: Programmatic (Recommended)**

```python
from cryptography.fernet import Fernet
from proxywhirl.cache.crypto import rotate_key

# Generate new key
new_key = Fernet.generate_key().decode()

# Rotate (this updates environment variables)
rotate_key(new_key)
```

**Option B: Manual**

```bash
# Move current key to previous
export PROXYWHIRL_CACHE_KEY_PREVIOUS=$PROXYWHIRL_CACHE_ENCRYPTION_KEY

# Set new key as current
export PROXYWHIRL_CACHE_ENCRYPTION_KEY=$NEW_KEY
```

### Step 4: Verify Rotation

```python
import os
from proxywhirl.cache.crypto import get_encryption_keys

# Should have 2 keys now
keys = get_encryption_keys()
print(f"Active keys: {len(keys)}")

# Verify environment
print(f"Current: {os.environ['PROXYWHIRL_CACHE_ENCRYPTION_KEY'][:20]}...")
print(f"Previous: {os.environ.get('PROXYWHIRL_CACHE_KEY_PREVIOUS', 'Not set')[:20]}...")
```

### Step 5: Test Backward Compatibility

```python
from pydantic import SecretStr
from proxywhirl.cache.crypto import CredentialEncryptor

# Create encryptor (uses both keys)
encryptor = CredentialEncryptor()

# Decrypt old data (encrypted with previous key)
# This happens automatically when accessing cached proxies
old_password = encryptor.decrypt(old_encrypted_data)

# Encrypt new data (uses current key)
new_encrypted = encryptor.encrypt(SecretStr("new_password"))
```

## Re-encryption Strategy

After rotation, gradually re-encrypt old data to remove dependency on the previous key:

```python
from proxywhirl.cache import CacheManager

manager = CacheManager(config)

# Re-encrypt all entries
count = 0
for key in manager.get_all_keys():
    entry = manager.get(key)
    if entry:
        # Get decrypts with previous key
        # Put re-encrypts with current key
        manager.put(key, entry)
        count += 1

print(f"Re-encrypted {count} entries")
```

## Production Deployment

### Using Environment Files

```bash
# .env.production
PROXYWHIRL_CACHE_ENCRYPTION_KEY=your-current-key-here
PROXYWHIRL_CACHE_KEY_PREVIOUS=your-previous-key-here
```

### Using Cloud Secret Managers

**AWS Secrets Manager:**

```python
import boto3
from proxywhirl.cache.crypto import rotate_key

# Load keys from AWS Secrets Manager
client = boto3.client('secretsmanager')
current_key = client.get_secret_value(SecretId='proxywhirl/encryption-key')['SecretString']
os.environ['PROXYWHIRL_CACHE_ENCRYPTION_KEY'] = current_key

# Rotate
new_key = Fernet.generate_key().decode()
rotate_key(new_key)

# Update secret in AWS
client.update_secret(SecretId='proxywhirl/encryption-key', SecretString=new_key)
```

**GCP Secret Manager:**

```python
from google.cloud import secretmanager
from proxywhirl.cache.crypto import rotate_key

client = secretmanager.SecretManagerServiceClient()
name = "projects/PROJECT_ID/secrets/proxywhirl-key/versions/latest"

# Get current key
response = client.access_secret_version(request={"name": name})
current_key = response.payload.data.decode('UTF-8')
os.environ['PROXYWHIRL_CACHE_ENCRYPTION_KEY'] = current_key

# Rotate and add new version
new_key = Fernet.generate_key().decode()
rotate_key(new_key)

parent = "projects/PROJECT_ID/secrets/proxywhirl-key"
client.add_secret_version(
    request={"parent": parent, "payload": {"data": new_key.encode('UTF-8')}}
)
```

## Rotation Schedule

**Recommended rotation frequency:**

- **Development**: 90 days
- **Staging**: 60 days
- **Production**: 30 days

**Automated rotation with cron:**

```bash
# /etc/cron.monthly/rotate-proxywhirl-key.sh
#!/bin/bash
set -e

# Generate new key
NEW_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Rotate
python -c "
from proxywhirl.cache.crypto import rotate_key
rotate_key('$NEW_KEY')
"

# Restart services
systemctl restart proxywhirl
```

## Troubleshooting

### "Decryption failed" after rotation

**Cause**: Previous key not set correctly

**Solution**:
```python
import os
# Verify both keys are set
print(f"Current: {os.environ.get('PROXYWHIRL_CACHE_ENCRYPTION_KEY', 'NOT SET')}")
print(f"Previous: {os.environ.get('PROXYWHIRL_CACHE_KEY_PREVIOUS', 'NOT SET')}")
```

### Key rotation not taking effect

**Cause**: Environment variables not refreshed

**Solution**: Restart application or reload configuration
```bash
# If using systemd
systemctl restart proxywhirl

# If using docker-compose
docker-compose restart
```

### Memory leak after rotation

**Cause**: Old keys not cleared after re-encryption

**Solution**: Clear previous key after all data re-encrypted
```bash
unset PROXYWHIRL_CACHE_KEY_PREVIOUS
```

## Best Practices

1. **Test in Development First**: Always test rotation in dev/staging before production
2. **Monitor Metrics**: Watch for decryption errors after rotation
3. **Keep Previous Key**: Don't remove `PROXYWHIRL_CACHE_KEY_PREVIOUS` until re-encryption complete
4. **Document Rotations**: Keep audit log of when keys were rotated
5. **Backup Keys**: Store old keys securely for disaster recovery

## See Also

- [Caching Guide](/docs/source/guides/caching.md) - Full caching documentation
- [Demo Script](/examples/key_rotation_demo.py) - Working example
- [Cryptography.io](https://cryptography.io/en/latest/fernet/) - Fernet documentation
