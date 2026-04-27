# TUI User Guide

ProxyWhirl's Terminal User Interface (TUI) provides a real-time dashboard for monitoring and managing proxy pools. This guide covers all available keybindings, views, and features.

## Starting the TUI

```bash
proxywhirl tui
```

The TUI launches in **Dashboard View** by default.

## Views

The TUI consists of multiple views accessible via keyboard shortcuts:

### Dashboard View (Home)
**Shortcut:** `H` or `Home`

Real-time overview of proxy pool status:
- **Pool Statistics**: Total proxies, healthy, unhealthy, by type (HTTP, SOCKS4, SOCKS5)
- **Rotation Metrics**: Current strategy, rotations/sec, average latency
- **Source Status**: Enabled sources and last fetch times
- **Performance Gauge**: Health percentage with color coding

**Dashboard Panels:**
- Top panel: Pool summary with color-coded health status
- Middle panel: Per-source statistics with fetch timestamps
- Bottom panel: Current strategy and rotation speed

### Proxy List View
**Shortcut:** `L` or `P`

Sortable, filterable list of all proxies:

**Columns:**
- `IP:Port`: Proxy address
- `Type`: HTTP/SOCKS4/SOCKS5
- `Status`: HEALTHY/UNHEALTHY/UNKNOWN
- `Latency`: Response time in milliseconds
- `Source`: Proxy source name
- `Last Check`: Time since last health check
- `Success Rate`: % of successful requests

**Keybindings:**
- `↑/↓` or `W/S`: Navigate proxy list
- `PgUp/PgDn`: Scroll by 10 rows
- `Home/End`: Jump to first/last proxy
- `R`: Reverse sort order
- `C`: Sort by column (cycle: IP, Status, Latency, Source, Success Rate)
- `Delete` or `D`: Remove selected proxy from pool
- `E`: Edit selected proxy
- `Space`: Select/deselect proxy (for batch operations)
- `Shift+Space`: Select all visible proxies

### Source Management View
**Shortcut:** `S`

Manage proxy sources and refresh scheduling:

**Columns:**
- `Source`: Source identifier
- `Status`: ACTIVE/INACTIVE/ERROR
- `Total`: Total proxies from source
- `New`: Proxies added in last refresh
- `Last Fetch`: Time of last update
- `Fetch Rate`: Refresh interval (seconds)
- `Success %`: % of successful fetches

**Keybindings:**
- `↑/↓` or `W/S`: Navigate sources
- `E`: Enable/disable source
- `R`: Manually refresh selected source
- `A`: Refresh all sources
- `Space`: View source details (URL, auth, proxy count)

### Health Monitor View
**Shortcut:** `M`

Detailed health check history and status:

**Columns:**
- `Proxy`: IP:Port
- `Status`: Current health status
- `Checks`: Total checks performed
- `Success Rate`: % successful health checks
- `Last Status`: Time of last check
- `Check Interval`: Seconds between checks
- `Errors`: Count of consecutive failures

**Keybindings:**
- `↑/↓` or `W/S`: Navigate proxies
- `T`: Trigger immediate health check for selected proxy
- `F`: View failure history for selected proxy
- `C`: Configure health check settings
- `E`: Edit health check interval for selected proxy

### Statistics View
**Shortcut:** `T`

Performance analytics and historical trends:

**Sections:**
- **Pool Stats**: Total/healthy/unhealthy counts, diversity metrics
- **Rotation Stats**: Total rotations, avg latency, peak rotations/sec
- **Source Stats**: Per-source success rates and latency
- **Time Series**: Charts of metrics over time (if terminal supports graphics)

**Keybindings:**
- `→/←` or `D/A`: Navigate between time ranges
- `1/2/3`: View 1-hour / 24-hour / 7-day metrics
- `R`: Refresh statistics
- `E`: Export statistics (JSON/CSV)

### Settings View
**Shortcut:** `Ctrl+S`

Configure TUI behavior and global settings:

**Options:**
- **Auto-refresh interval**: Seconds between dashboard updates (1-60)
- **Proxy list page size**: Rows per page (10-100)
- **Show unhealthy proxies**: Toggle visibility
- **Sort order**: Ascending/descending
- **Default view**: Dashboard/Proxy List/Health Monitor
- **Color theme**: Default/Dark/Light
- **Log level**: DEBUG/INFO/WARNING/ERROR

**Keybindings:**
- `↑/↓` or `W/S`: Navigate settings
- `Space`: Toggle boolean settings
- `←/→` or `A/D`: Adjust numeric values
- `Enter`: Edit selected setting
- `R`: Reset to defaults
- `S`: Save settings

### Search & Filter View
**Shortcut:** `F` or `/`

Filter proxies by various criteria:

**Filter Options:**
- **IP Address**: Exact match or CIDR range (e.g., `192.168.0.0/24`)
- **Type**: HTTP / SOCKS4 / SOCKS5
- **Status**: HEALTHY / UNHEALTHY / UNKNOWN
- **Source**: Filter by specific source
- **Latency**: Range filter (e.g., `0-100ms`)
- **Country**: By geolocation (if geo-enrichment enabled)
- **ASN**: By autonomous system

**Keybindings:**
- `↑/↓` or `W/S`: Navigate filter fields
- `Space`: Toggle filter criteria
- `Enter`: Apply filters
- `Ctrl+X`: Clear filters
- `S`: Save filter preset

### Alerts View
**Shortcut:** `N` (Notifications)

Monitor system alerts and warnings:

**Alert Types:**
- **CRITICAL**: Pool capacity < 10% healthy proxies
- **WARNING**: Source fetch error, health check failures
- **INFO**: Source refreshed, proxy added/removed
- **DEBUG**: Health check passed, rotations/sec updates

**Keybindings:**
- `↑/↓` or `W/S`: Navigate alerts (newest first)
- `C`: Clear current alert
- `Ctrl+X`: Clear all alerts
- `M`: Mute alert type (hide for this session)
- `S`: Configure alert thresholds

## Global Keybindings

These shortcuts work from any view:

| Binding | Action |
|---------|--------|
| `H` / `Home` | Go to Dashboard view |
| `L` / `P` | Go to Proxy List view |
| `S` | Go to Source Management view |
| `M` | Go to Health Monitor view |
| `T` | Go to Statistics view |
| `F` / `/` | Open Search & Filter |
| `N` | Go to Alerts view |
| `Ctrl+S` | Go to Settings view |
| `Q` / `Ctrl+C` | Quit TUI |
| `?` / `Ctrl+H` | Show help (this guide) |
| `Space` | Pause/resume auto-refresh |
| `Ctrl+R` | Force refresh current view |
| `Ctrl+L` | Clear screen |
| `Ctrl+D` | Toggle dark mode |
| `Tab` | Cycle through panels (in multi-panel views) |
| `Shift+Tab` | Reverse cycle through panels |
| `↑/↓` / `W/S` | Navigate up/down in lists |
| `←/→` / `A/D` | Navigate left/right between columns |
| `PgUp` / `PgDn` | Scroll by page |
| `Home` / `End` | Jump to first/last item |

## Column Customization

In **List Views** (Proxy List, Sources, Health Monitor):

1. Press `C` to open column selector
2. Use `↑/↓` to navigate columns
3. Press `Space` to show/hide column
4. Press `Enter` to confirm and apply
5. Columns are automatically saved in settings

## Batch Operations

Select multiple proxies using `Space` in the **Proxy List View**:

- `Space`: Toggle selection on current proxy
- `Shift+Space`: Select/deselect all visible
- `Ctrl+Space`: Invert selection

Then perform batch actions:
- `Delete`: Remove all selected proxies
- `B`: Ban selected proxies (prevent rotation)
- `U`: Unban selected proxies
- `R`: Recheck health for all selected
- `E`: Edit metadata for all selected (bulk edit)

## Color Coding

### Status Colors
- 🟢 **Green**: HEALTHY proxies
- 🔴 **Red**: UNHEALTHY proxies
- 🟡 **Yellow**: UNKNOWN / UNVERIFIED proxies
- ⚫ **Gray**: DISABLED proxies

### Performance Colors
- 🟢 **Green**: Latency < 200ms or success rate > 90%
- 🟡 **Yellow**: Latency 200-500ms or success rate 70-90%
- 🔴 **Red**: Latency > 500ms or success rate < 70%

## Tips & Tricks

### Performance
- Hide unhealthy proxies in settings to reduce UI update time
- Use filters to focus on specific proxy types
- Disable auto-refresh (`Space`) on large pools (1000+ proxies)

### Workflow
1. Start with **Dashboard** for overall health
2. Use **Health Monitor** to identify failing proxies
3. Use **Source Management** to refresh or disable problematic sources
4. Check **Alerts** for recent issues
5. Use **Statistics** for trend analysis

### Data Export
From **Statistics View**, press `E` to export:
- **JSON**: Full metrics with timestamps
- **CSV**: Flattened format for spreadsheets
- **YAML**: Human-readable configuration

### Remote Usage
The TUI supports SSH/tmux sessions:

```bash
ssh user@host 'proxywhirl tui'
tmux new-session -d -s proxy 'proxywhirl tui'
```

For best experience over SSH, set `TERM=screen-256color` and disable graphics.

## Troubleshooting

**TUI won't start:**
```bash
export TERM=xterm-256color
proxywhirl tui
```

**Display corruption:**
- Press `Ctrl+L` to clear screen
- Resize terminal to trigger redraw
- Restart TUI: `Q` then `proxywhirl tui`

**High CPU usage:**
- Disable auto-refresh: Press `Space`
- Increase refresh interval in Settings
- Hide unhealthy proxies in Settings

**Slow rendering:**
- Use `--no-colors` flag: `proxywhirl tui --no-colors`
- Disable sorting/filtering
- Reduce page size in Settings

## Keyboard Layout Variants

The TUI supports multiple keyboard layouts:

**QWERTY (default):**
- W/A/S/D for navigation
- Q to quit

**Vim-style (optional via settings):**
- H/J/K/L for navigation
- :q to quit
- / to search

**Arrows-only (accessible):**
- Use arrow keys instead of WASD
- All shortcuts available

## Accessibility

The TUI supports:
- **Screen readers**: Text-based descriptions of all elements
- **High contrast**: Set via `--high-contrast` flag
- **Large fonts**: Terminal font size affects TUI scaling
- **Keyboard-only navigation**: All functions accessible without mouse

## Configuration File

TUI settings are saved to:
```
~/.config/proxywhirl/tui.toml
```

Example:
```toml
[tui]
auto_refresh_interval = 5
show_unhealthy = false
default_view = "dashboard"
color_theme = "dark"
page_size = 25
sort_order = "ascending"
```

## API Integration

While using the TUI, the REST API remains fully functional:

```bash
# In another terminal:
curl http://localhost:8000/api/v1/proxy
```

TUI changes are immediately reflected in API responses, and API changes appear in TUI on next refresh.

## Advanced Usage

### Custom Alerting
Configure alerts in settings to trigger external webhooks:

```toml
[alerts]
webhook_url = "https://your-webhook/endpoint"
alert_types = ["CRITICAL"]
```

### Metrics Collection
Export metrics while TUI runs:

```bash
# In another terminal:
while true; do
  curl http://localhost:8000/metrics | tee -a metrics.log
  sleep 60
done
```

### Scripting
Control TUI via stdin (for automation):

```bash
echo "S" | proxywhirl tui  # Go to Sources view
echo "R" | proxywhirl tui  # Refresh all sources
```
