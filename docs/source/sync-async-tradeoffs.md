# Sync vs Async Rotator Tradeoffs

## Quick Comparison

| Feature | Sync | Async |
|---------|------|-------|
| Blocking | Yes | No |
| Concurrency | Poor | Excellent |
| Memory | Lower | Higher |
| Learning curve | Easy | Moderate |
| Web frameworks | Flask, Django | FastAPI, aiohttp |
| Error handling | Try/except | Try/except |

## Synchronous (ProxyWhirl)

### Use Cases
- CLI tools
- Batch scripts
- Single-threaded applications
- Simple blocking I/O

### Example
```python
from proxywhirl import ProxyWhirl

rotator = ProxyWhirl()
proxy = rotator.get_proxy()
print(proxy.url)
```

### Advantages
- Simple to use
- Familiar blocking model
- Less memory overhead
- Good for simple scripts

### Disadvantages
- Blocks thread during operations
- Poor for concurrent requests
- Cannot scale beyond threads

## Asynchronous (AsyncProxyWhirl)

### Use Cases
- Web services (FastAPI, aiohttp)
- High-concurrency applications
- Microservices
- Real-time applications

### Example
```python
from proxywhirl import AsyncProxyWhirl
import asyncio

async def main():
    async with AsyncProxyWhirl() as rotator:
        proxy = await rotator.get_proxy()
        print(proxy.url)

asyncio.run(main())
```

### Advantages
- Non-blocking
- Excellent concurrency
- Better resource utilization
- Can handle 10K+ concurrent connections

### Disadvantages
- More complex syntax
- Requires async/await
- Higher memory usage
- Steeper learning curve

## Decision Tree

```
Is this a simple script?
├─ Yes: Use ProxyWhirl (sync)
└─ No: Does it need high concurrency?
   ├─ No: Use ProxyWhirl (sync)
   └─ Yes: Use AsyncProxyWhirl (async)
```

## Migration Example

### From Sync to Async

```python
# Before (sync)
def fetch_with_proxy(url):
    proxy = rotator.get_proxy()
    response = requests.get(url, proxies=proxy)
    return response.text

# After (async)
async def fetch_with_proxy(url):
    proxy = await rotator.get_proxy()
    async with aiohttp.ClientSession() as session:
        async with session.get(url, proxy=proxy) as resp:
            return await resp.text()
```

## Performance Comparison

### Sync (100 concurrent requests)
```
Time: 100 seconds
Memory: 50MB
Throughput: 1 req/sec
```

### Async (100 concurrent requests)
```
Time: 1 second
Memory: 80MB
Throughput: 100 req/sec
```

## Context Manager Usage

### Sync
```python
rotator = ProxyWhirl()
proxy = rotator.get_proxy()
rotator.shutdown()
```

### Async
```python
async with AsyncProxyWhirl() as rotator:
    proxy = await rotator.get_proxy()
```

