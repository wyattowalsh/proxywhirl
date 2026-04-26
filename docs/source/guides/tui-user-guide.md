---
title: TUI User Guide
---

# ProxyWhirl TUI User Guide

The ProxyWhirl Terminal User Interface (TUI) dashboard provides real-time monitoring and management of proxy pools, rotation strategies, performance metrics, and health status using a responsive text-based interface powered by Textual.

```{contents}
:local:
:depth: 2
```

## Overview

The TUI dashboard gives you a comprehensive view of your proxy infrastructure with:

- **Real-time metrics**: Live updates on proxy selection, rotation rate, success/failure counts
- **Pool visualization**: Current pool size, active proxies, health status breakdown
- **Performance graphs**: ASCII charts for latency trends, success rates, throughput
- **Strategy insights**: Current strategy, rotation patterns, weighted distribution
- **Search and filtering**: Find and manage proxies by URL, country, speed tier
- **Interactive controls**: Add/remove proxies, toggle strategies, reset metrics, tune parameters
- **Dark/light modes**: Configurable color schemes for comfortable viewing
- **Responsive design**: Adapts to terminal size from 80x24 to 4K displays

## Starting the Dashboard

### Basic Launch

```bash
proxywhirl tui
```

Launches the default dashboard with round-robin strategy and in-memory storage.

### With Custom Configuration

```bash
# Use specific configuration file
proxywhirl tui --config ./my-config.toml

# Use persistent SQLite database
proxywhirl tui --storage sqlite --db-path ./proxies.db

# Use weighted strategy
proxywhirl tui --strategy weighted

# Full options
proxywhirl tui \
  --config /etc/proxywhirl/config.toml \
  --storage sqlite \
  --db-path /var/lib/proxywhirl/proxies.db \
  --strategy performance-based \
  --theme dark \
  --refresh-rate 1.0
```

## Main Dashboard Screens

### 1. Overview Screen

The default dashboard shows:

**Top Section:**
- Header with ProxyWhirl version and current time
- Quick status: Total proxies, healthy count, unhealthy count
- Current strategy and rotation mode

**Left Panel - Pool Statistics:**
```
┌─ Pool Status ─────────────────┐
│ Total Proxies:    45          │
│ Healthy:          38 (84%)    │
│ Unhealthy:        7  (16%)    │
│ Rotating:         5/s         │
│ Avg Response:     245ms       │
└───────────────────────────────┘
```

**Center Panel - Performance Metrics:**
```
┌─ Last 60s Performance ────────────┐
│ Success Rate:    94.2%            │
│ Avg Latency:     234ms            │
│ P95 Latency:     890ms            │
│ P99 Latency:     2100ms           │
│ Requests/sec:    12.4             │
│ Bytes/sec:       2.3 MB/s         │
└───────────────────────────────────┘
```

**Right Panel - Health Breakdown:**
```
┌─ Health Status ───────────────┐
│ ✓ Healthy:    38              │
│ ⚠ Degraded:   5               │
│ ✗ Dead:       2               │
│ ⊚ Unknown:    0               │
└───────────────────────────────┘
```

**Bottom Section:**
- Real-time log viewer showing latest events and errors
- Status bar with keyboard help

### 2. Proxy List Screen

Sortable and filterable table of all proxies with:

**Columns:**
- `URL`: Proxy server address
- `Country`: IP geolocation (if available)
- `Speed`: Performance tier (Fast/Normal/Slow)
- `Status`: Health status indicator
- `Latency`: Last measured response time (ms)
- `Success`: Success rate (%)
- `Uses`: Total selections by rotator
- `Updated`: Last update timestamp

**Keyboard Controls:**
- `↑/↓`: Navigate proxy list
- `PgUp/PgDn`: Page through list
- `Home/End`: First/last proxy
- `/`: Open search filter
- `s`: Sort by selected column
- `r`: Reset metrics for selected proxy
- `d`: Delete/remove proxy
- `e`: Edit proxy (auth, country, speed tier)

### 3. Strategy Screen

View current strategy configuration and performance:

```
┌─ Current Strategy: Performance-Based ────────────────┐
│                                                      │
│ Configuration:                                       │
│   • EMA Window: 100                                  │
│   • Weight Decay: 0.95                               │
│   • Selection Mode: Probability-based                │
│   • Update Interval: 5s                              │
│                                                      │
│ Recent Selections:                                   │
│   [████████░░░░░░░░░░] proxy1 (45%)                  │
│   [██████░░░░░░░░░░░░] proxy2 (28%)                  │
│   [████░░░░░░░░░░░░░░] proxy3 (18%)                  │
│   [██░░░░░░░░░░░░░░░░] proxy4 (9%)                   │
│                                                      │
│ Strategy Options:                                    │
│   [S]witch to... [C]onfigure [R]eset [Q]uit          │
└──────────────────────────────────────────────────────┘
```

### 4. Monitoring Screen

Real-time graphs and trends:

- **Latency Trend**: ASCII graph of response times over last 5 minutes
- **Success Rate**: Line graph showing success percentage
- **Throughput**: Bar chart of requests per second
- **Error Rate**: Breakdown by error type (timeout, connection, auth, etc.)
- **Health Timeline**: Color-coded health status changes

### 5. Settings Screen

Configure runtime parameters:

```
┌─ Settings ──────────────────────────────┐
│                                         │
│ Display:                                │
│   [✓] Show grid lines                   │
│   [✓] Auto-refresh metrics              │
│   [ ] Dark mode (currently: Light)      │
│   Refresh interval: 1.0 second          │
│                                         │
│ Behavior:                               │
│   [✓] Auto-add healthy proxies          │
│   [✓] Remove dead proxies               │
│   [ ] Pause rotation (currently: Off)   │
│   [ ] Filter unhealthy (currently: Off) │
│                                         │
│ Performance:                            │
│   Max connections: 100                  │
│   Timeout: 30 seconds                   │
│   Retry attempts: 3                     │
│                                         │
│ [S]ave [R]eset [←] Back                 │
└─────────────────────────────────────────┘
```

## Navigation and Keyboard Controls

### Global Commands

| Key | Action |
|-----|--------|
| `Tab` | Switch between screens |
| `Ctrl+C` / `Q` | Quit dashboard |
| `H` | Show help overlay |
| `?` | Show keyboard shortcuts |
| `Ctrl+L` | Clear logs |
| `Ctrl+R` | Force refresh metrics |
| `/` | Search/filter current view |
| `Esc` | Close modals, cancel actions |

### Proxy List Navigation

| Key | Action |
|-----|--------|
| `↑` / `↓` | Navigate proxies |
| `PgUp` / `PgDn` | Page scroll |
| `Home` / `End` | First/last proxy |
| `Space` | Select/deselect proxy |
| `Ctrl+A` | Select all proxies |
| `d` | Delete selected proxy(ies) |
| `e` | Edit selected proxy |
| `r` | Reset metrics for proxy |

### Search and Filter

| Key | Action |
|-----|--------|
| `/` | Open search |
| `Enter` | Execute search |
| `Ctrl+U` | Clear search |
| `Esc` | Close search |

Supports filtering by:
- URL pattern: `/proxy.*example`
- Country: `/country:US`
- Speed: `/speed:fast`
- Status: `/status:healthy`

### Strategy Operations

| Key | Action |
|-----|--------|
| `S` | Switch strategy |
| `C` | Configure current strategy |
| `R` | Reset strategy state |
| `P` | Pause/resume rotation |

## Common Tasks

### Adding Proxies

**Via Menu:**
1. Press `A` to open "Add Proxy" dialog
2. Enter proxy URL (e.g., `http://proxy1.example.com:8080`)
3. Optionally set country, speed tier, credentials
4. Press `Enter` to add

**From File:**
1. Press `I` for "Import Proxies"
2. Select file format (plain text, JSON, CSV, HTML)
3. Choose file path
4. Review parsed proxies
5. Confirm import

### Removing Proxies

**Individual:**
1. Navigate to proxy in list
2. Press `d` to delete
3. Confirm deletion

**Bulk:**
1. Press `/` and filter proxies
2. Press `Ctrl+A` to select all filtered
3. Press `d` to delete all selected

### Switching Strategies

1. Press `S` on Overview screen
2. Select strategy from list
3. Review configuration changes
4. Confirm switch

Available strategies:
- Round-Robin (default)
- Random
- Weighted
- Least-Used
- Performance-Based
- Session-Persistence
- Geo-Targeted
- Cost-Aware

### Tuning Performance Strategy

1. Go to Strategy screen
2. Press `C` to configure
3. Adjust parameters:
   - **EMA Window**: Adjust responsiveness to recent performance
   - **Weight Decay**: Control balance between recent and historical performance
   - **Update Interval**: How often performance scores recalculate
4. Apply changes

## Tips and Best Practices

### Monitoring Health

- Watch the health breakdown in overview for sudden changes
- Check the error rate graph for error patterns
- Review logs at bottom for specific error messages
- Use the proxy list's "Status" column to identify problems

### Performance Tuning

- Monitor latency trend graph for performance degradation
- Use success rate graph to identify unreliable proxies
- Adjust strategy parameters if certain proxies dominate selection
- Check throughput graph to ensure adequate capacity

### Regular Maintenance

- Review and update proxy sources monthly
- Remove dead proxies (status filter: `/status:dead`)
- Monitor cost metrics if using cost-aware strategy
- Archive old logs for compliance (if enabled)

### Automation

- Run TUI in a tmux/screen session for persistent monitoring
- Export metrics to external monitoring system via API
- Set up alerts for unhealthy proxy counts
- Schedule regular proxy source refreshes

## Troubleshooting

### Dashboard Not Responding

**Problem**: TUI is frozen or unresponsive

**Solution**:
1. Press `Ctrl+C` to force quit
2. Check logs: `tail -f ~/.proxywhirl/logs/tui.log`
3. Verify database is not locked: `lsof ~/.proxywhirl/proxies.db`
4. Restart: `proxywhirl tui --fresh`

### Metrics Not Updating

**Problem**: Numbers on dashboard are stale

**Solution**:
1. Press `Ctrl+R` to force refresh
2. Check refresh rate in Settings (default 1s)
3. Verify proxies are being used (check rotation rate)
4. Check system CPU/memory usage

### Search Not Working

**Problem**: Filtering returns no results

**Solution**:
1. Press `Esc` to clear search
2. Verify filter syntax (use `/` to open search help)
3. Check that proxies exist with those criteria
4. Try simpler filter pattern

### Colors Not Displaying

**Problem**: Dashboard looks garbled or monochrome

**Solution**:
1. Set `TERM` environment variable: `export TERM=xterm-256color`
2. Use TUI argument: `proxywhirl tui --theme auto`
3. Check terminal color support: `echo $COLORTERM`
4. Try different theme: `proxywhirl tui --theme dark`

## Performance Considerations

The TUI is optimized for responsiveness:

- **Sampling**: Metrics are updated at configurable intervals (default 1s)
- **Windowing**: Charts display last 5 minutes of data (reducing memory usage)
- **Lazy rendering**: Only visible portions of large lists are rendered
- **Async updates**: Metric collection doesn't block user input
- **Low overhead**: TUI adds <5% CPU on typical workloads

For very large proxy pools (>10,000 proxies), consider:
- Filtering the view to relevant proxies
- Increasing refresh interval to 5-10 seconds
- Exporting metrics to external monitoring instead

## API Integration

The TUI uses the same internal APIs as the Python library:

```python
from proxywhirl import ProxyWhirl

# These APIs power the TUI under the hood
pool = rotator.get_pool()
stats = rotator.get_metrics()
health = rotator.get_health_status()
```

For programmatic access to the same data, use these APIs directly.

## See Also

- {doc}`cli-reference` for command-line proxy management
- {doc}`performance-tuning` for optimization strategies
- {doc}`integration-examples` for building custom dashboards
