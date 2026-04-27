# TUI Dashboard User Guide

## Starting the Dashboard

```bash
proxywhirl tui
```

## Main Dashboard

The TUI has five main sections:

### 1. Proxy List (Top Left)
- Shows current proxy pool
- Display: `PROTOCOL://IP:PORT COUNTRY TYPE STATUS`
- Status: ✓ (healthy), ✗ (unhealthy), ? (unknown)

**Navigation:**
- `↑/↓` - Scroll through proxies
- `Enter` - View details
- `r` - Refresh proxy list
- `d` - Delete selected proxy

### 2. Health Status (Top Right)
- Real-time health statistics
- Total proxies
- Healthy/unhealthy count
- Health check progress

**Actions:**
- `h` - Run health check on all
- `c` - Clear unhealthy proxies

### 3. Performance Metrics (Bottom Left)
- Selection time: Time to select a proxy
- Validation latency: Proxy validation time
- Cache hit rate: Percentage of cached hits
- Throughput: Proxies/second

### 4. Cache Statistics (Bottom Middle)
- Cache entries: Current count
- Hit rate: Cache effectiveness
- Size: Memory usage
- Tier breakdown: L1/L2/L3 distribution

**Actions:**
- `w` - Warm cache
- `x` - Clear cache

### 5. Source Status (Bottom Right)
- Available sources
- Last refresh time
- Proxy count per source
- Source health status

**Actions:**
- `s` - Refresh selected source
- `a` - Refresh all sources

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `q` | Quit |
| `?` | Help |
| `r` | Refresh |
| `h` | Health check |
| `c` | Clear unhealthy |
| `w` | Warm cache |
| `x` | Clear cache |
| `s` | Refresh source |
| `a` | Refresh all sources |
| `d` | Delete proxy |
| `↑/↓` | Navigate |
| `Enter` | View details |

## Proxy Details View

Press `Enter` on a proxy to see:

```
URL: http://192.168.1.1:8080
Protocol: HTTP
Country: US
Type: Residential
Anonymous: Yes
Last Checked: 2024-01-15 10:30:00
Health Status: HEALTHY
Performance: Good (45ms latency)
Last Used: 2024-01-15 10:31:15
Success Rate: 95%
```

**Actions:**
- `m` - Mark as healthy/unhealthy
- `r` - Run health check
- `d` - Delete
- `Esc` - Back

## Configuration Panel

Press `Ctrl+C` to show configuration menu:

```
Cache Configuration
├─ TTL: 3600s (editable)
├─ Max Entries: 1000 (editable)
└─ Compression: Yes (toggle)

Validation
├─ Level: strict (dropdown)
└─ Timeout: 30s (editable)

Strategy
├─ Current: round_robin (dropdown)
└─ Parameters: (editable)
```

## Statistics View

Press `Tab` to switch to detailed statistics:

- Request history (last 100)
- Performance timeline (graph)
- Error histogram
- Success rate trend

## Monitoring Mode

```bash
proxywhirl tui --monitor
```

Enters continuous monitoring mode with:
- Auto-refresh every 5 seconds
- Real-time metrics
- Performance graphs
- Alerts on threshold breaches

## Export Data

From any view, press `e` to export:

```
Export Format:
├─ JSON
├─ CSV
└─ YAML

Select destination and format to export.
```

## Alerts and Notifications

Red highlights indicate:
- ✗ Unhealthy proxies
- ⚠ Low cache hit rate (<50%)
- 🔴 All proxies unhealthy
- 💾 Cache full (auto-clear triggered)

## Color Scheme

- Green: Healthy, good performance
- Yellow: Degraded, needs attention
- Red: Errors, unhealthy
- Blue: Info, status

## Performance Tips

1. **Reduce refresh rate for large pools** (1000+ proxies)
   ```bash
   proxywhirl tui --refresh-interval 10
   ```

2. **Use monitor mode for continuous observation**
   ```bash
   proxywhirl tui --monitor
   ```

3. **Filter proxies by country**
   ```bash
   proxywhirl tui --country US
   ```

4. **Show only healthy proxies**
   ```bash
   proxywhirl tui --healthy-only
   ```

