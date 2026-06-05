# Security Best Practices

## Credential Management

### Encrypted Credentials

```python
from proxywhirl import encrypt_credentials, decrypt_credentials

# Store credentials securely
key = os.environ.get('PROXYWHIRL_KEY')
encrypted = encrypt_credentials(
    username='user',
    password='pass',
    key=key
)

# Retrieve credentials
decrypted = decrypt_credentials(encrypted, key=key)
```

### Environment Variables

```bash
# .env file (never commit)
export PROXYWHIRL_KEY=$(openssl rand -base64 32)
export PROXY_USERNAME=myuser
export PROXY_PASSWORD=mypass
```

### No Hardcoded Secrets

```python
# ❌ BAD
config = ProxyConfiguration(
    sources=[
        'http://api.example.com/proxies?key=secret123'
    ]
)

# ✅ GOOD
api_key = os.environ.get('API_KEY')
config = ProxyConfiguration(
    sources=[
        f'http://api.example.com/proxies?key={api_key}'
    ]
)
```

## Input Validation

### URL Validation

```python
from proxywhirl import is_valid_proxy_url

url = 'http://192.168.1.1:8080'
if is_valid_proxy_url(url):
    proxy = Proxy(url=url)
else:
    raise ValueError("Invalid proxy URL")
```

### Proxy Format Validation

```python
from proxywhirl import validate_proxy_model

proxy = Proxy(url='http://invalid', protocol='http')
try:
    validate_proxy_model(proxy)
except ValidationError:
    print("Invalid proxy")
```

## Rate Limiting & DDoS Protection

### Per-Client Rate Limiting

```python
from proxywhirl import PerClientRateLimiter

limiter = PerClientRateLimiter(
    requests_per_second=10,
    per_client_limit=5
)

def handle_request(client_id):
    if not limiter.is_allowed(client_id):
        raise TooManyRequestsError()
```

### Circuit Breaker

```python
from proxywhirl import CircuitBreaker

breaker = CircuitBreaker(
    failure_threshold=10,
    recovery_timeout=60
)
```

## Data Protection

### Secure Logging

```python
from loguru import logger
from proxywhirl import redact_url

def log_proxy_error(proxy, error):
    # redact_url removes credentials from logs
    safe_url = redact_url(proxy.url)
    logger.error(
        "Proxy failed",
        proxy=safe_url,
        error=str(error)
    )
```

### Cache Encryption

```python
from proxywhirl import CacheConfig

config = CacheConfig(
    compression_enabled=True,
    encryption_enabled=True,
    encryption_key=os.environ['ENCRYPTION_KEY']
)
```

### Database Encryption

```python
from sqlalchemy import create_engine

engine = create_engine(
    'sqlite:////encrypted/proxywhirl.db',
    connect_args={'check_same_thread': False}
)
```

## Network Security

### TLS/SSL Configuration

```python
import ssl
import httpx

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

client = httpx.Client(verify=ssl_context)
```

### Certificate Pinning

```python
from httpx import Client

client = Client(
    verify='/path/to/pinned/cert.pem'
)
```

## API Security

### API Key Management

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.environ.get('API_KEY'):
        raise HTTPException(status_code=403)
    return api_key
```

### Request Authentication

```python
from fastapi import Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.get('/proxies')
async def get_proxies(credentials = Depends(security)):
    # Verify credentials
    return rotator.get_proxies(count=5)
```

## Regular Security Audits

### Dependency Scanning

```bash
# Check for vulnerable dependencies
uvx safety check
```

### Secret Detection

```bash
# Install pre-commit hooks
pre-commit install

# Scan for secrets
git secrets --scan
```

## Deployment Security

### Containerization Security

```dockerfile
# Use non-root user
FROM python:3.11-slim
USER nobody

# Copy only necessary files
COPY --chown=nobody:nobody . /app
WORKDIR /app
```

### Kubernetes Security

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  capabilities:
    drop:
      - ALL
```
