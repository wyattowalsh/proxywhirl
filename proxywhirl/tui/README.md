# ProxyWhirl TUI Package

This directory contains the intelligently split TUI (Terminal User Interface) package for ProxyWhirl. The original monolithic `tui.py` file has been refactored into a well-organized package structure for better maintainability, testability, and code reuse.

## Package Structure

```text
proxywhirl/tui/
├── __init__.py          # Package exports and run_tui() function
├── app.py               # Main ProxyWhirlTUI application class
├── styles.py            # CSS styling constants
├── widgets/             # Reusable UI components
│   ├── __init__.py      # Widget package exports
│   ├── stats.py         # ProxyStatsWidget, EnhancedProgressWidget
│   └── tables.py        # ProxyDataTable, ProxyTableWidget
└── modals/              # Modal dialog components
    ├── __init__.py      # Modal package exports
    ├── export.py        # ExportModal - proxy export configuration
    ├── settings.py      # SettingsModal - application settings
    └── health.py        # HealthReportModal - health report display
```

## Components Overview

### Main Application (`app.py`)

- **ProxyWhirlTUI**: The main TUI application class with Textual framework
- Handles all application-level logic, routing, and coordination
- Manages reactive state and async operations
- Integrates all widgets and modals

### Widgets Package (`widgets/`)

- **ProxyStatsWidget**: Real-time proxy statistics with rich visualizations
  - Health indicators, sparklines, trend analysis
  - Success rate tracking, throughput metrics
- **EnhancedProgressWidget**: Progress tracking with ETA calculations
- **ProxyDataTable**: Enhanced data table with proxy-specific functionality
- **ProxyTableWidget**: Rich-formatted proxy display table

### Modals Package (`modals/`)

- **ExportModal**: Comprehensive proxy export configuration
  - Multiple format support (JSON, CSV, TXT, XML)
  - Filtering and volume controls
  - Real-time preview updates
- **SettingsModal**: Application settings configuration
  - Cache type selection, validation settings
  - Rotation strategy configuration
- **HealthReportModal**: Interactive health report display
  - Tabbed metrics view, source status
  - Export and refresh capabilities

### Styles (`styles.py`)

- **TUI_STYLES**: Complete CSS styling definitions
- Responsive design with dark/light theme support
- Enhanced visual indicators and animations

## Usage

The package maintains backward compatibility with the original interface:

```python
# Import the main function
from proxywhirl.tui import run_tui

# Or use the application class directly
from proxywhirl.tui.app import ProxyWhirlTUI

# Run the TUI
run_tui()
```

## Benefits of the New Structure

1. **Maintainability**: Logical separation of concerns makes code easier to maintain
2. **Testability**: Individual components can be tested in isolation
3. **Reusability**: Widgets and modals can be reused across different contexts
4. **Extensibility**: New components can be easily added without affecting existing code
5. **Code Clarity**: Each module has a single, well-defined responsibility
6. **Import Management**: Cleaner import structure reduces circular dependencies

## Development Notes

- All original functionality has been preserved
- The package uses proper type hints and modern Python patterns
- Async/await patterns are maintained for non-blocking operations
- Error handling and logging are consistent across all components
- The CSS styling maintains the beautiful, modern appearance

This refactoring transforms a single 1000+ line file into a well-organized package that follows Python best practices and modern software architecture principles.
