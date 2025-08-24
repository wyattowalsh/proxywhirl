# Proxy Lists

This directory contains automatically generated and validated proxy lists, updated every 6 hours.

## 📁 File Structure

- `proxies.json` - Complete list in JSON format with full metadata
- `proxies.csv` - Spreadsheet-friendly format with headers
- `proxies-hostport.txt` - Simple host:port format (healthy only)
- `proxies-uri.txt` - Full URI format (scheme://host:port)

### Filtered Lists
- `proxies-premium.txt` - Top 25% quality proxies
- `proxies-fast.txt` - Fast proxies (response time < 2s)
- `proxies-us.txt` - US proxies only
- `proxies-http.txt` - HTTP/HTTPS proxies only
- `proxies-socks.txt` - SOCKS4/5 proxies only

### Metadata
- `README.md` - This file with usage documentation
- `checksums.sha256` - File integrity verification

## 🔄 Update Schedule

These lists are automatically updated every 6 hours (00:00, 06:00, 12:00, 18:00 UTC) via GitHub Actions.

## ⚠️ Usage Notes

1. **Validation**: All proxies are validated before inclusion
2. **Quality**: Lists are sorted by quality score (best first)
3. **Availability**: Proxy availability can change rapidly
4. **Verification**: Always validate proxies before production use

## 🚀 Quick Usage

### Python
```python
import requests
import json

# Load premium proxies
with open('proxies-premium.txt', 'r') as f:
    proxies = f.read().strip().split('\n')

# Use first proxy
proxy = proxies[0]
response = requests.get('http://example.com', 
                       proxies={'http': f'http://{proxy}'})
```

### Shell/cURL
```bash
# Use fastest proxy
PROXY=$(head -1 proxies-fast.txt)
curl --proxy "$PROXY" http://example.com
```
