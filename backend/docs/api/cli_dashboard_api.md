# CLI Dashboard API Reference

This document provides comprehensive API documentation for the CLI dashboard module and its enhanced features, including the professional exit experience and synthetic event generation.

## Overview

The CLI dashboard provides a real-time monitoring interface for automotive RF security events with enhanced user experience features, professional exit handling, and advanced synthetic event generation for testing and demonstration purposes.

## Core Modules

### cli_dashboard.py

Main dashboard interface with enhanced startup experience, event navigation, and professional exit handling.

#### Key Functions

##### render_dashboard()

Renders the enhanced CLI dashboard with signal analysis and event navigation.

```python
def render_dashboard(
    events: List[Dict[str, Any]], 
    selected_event: Dict[str, Any], 
    status_text: str, 
    console: Console, 
    selected_event_idx: int = -1, 
    status_only: bool = False, 
    show_help: bool = False, 
    current_page: int = 0, 
    force_refresh: bool = False
) -> None
```

**Parameters:**

- `events`: List of security events to display
- `selected_event`: Currently selected event for detailed view
- `status_text`: Current system status message
- `console`: Rich console instance for rendering
- `selected_event_idx`: Index of selected event (-1 for latest)
- `status_only`: If True, only update status without full refresh
- `show_help`: Display help panel
- `current_page`: Current page for event pagination (20 events per page)
- `force_refresh`: Force complete dashboard refresh

**Features:**

- Enhanced startup screens with ASCII art and system information
- Event pagination with 20 events per page
- Professional signal analysis with technical evidence panels
- Real-time threat level visualization
- Sparkline signal metrics visualization

##### main()

Enhanced main function with professional startup experience and exit handling.

```python
async def main() -> None
```

**Features:**

- Professional ASCII art startup with timing effects
- Enhanced loading screens and menu presentation
- Integrated exit dialog manager for graceful shutdown
- Session data export capabilities
- Clean terminal state restoration

### utils/exit_dialog.py

Professional exit experience manager with Rich-based dialogs and data export.

#### Classes

##### ExitDialogManager

Manages professional exit experience for the CLI dashboard.

```python
class ExitDialogManager:
    """
    Manages professional exit experience for the CLI dashboard.
    Provides Rich-based confirmation dialogs, export options, and clean terminal restoration.
    """
    
    def __init__(self, console: Console):
        self.console = console
        self.export_dir = Path("exports")
```

**Methods:**

###### show_exit_confirmation()

Display professional exit confirmation dialog.

```python
def show_exit_confirmation(self) -> bool
```

**Returns:** `True` if user confirms exit, `False` to continue

**Features:**

- Rich-based confirmation dialog with ASCII art branding
- Professional presentation with centered layout
- Clear exit options (Yes/No)

###### show_export_options()

Display data export options dialog.

```python
def show_export_options(self, events: List[Dict[str, Any]], dashboard_logger=None) -> bool
```

**Parameters:**

- `events`: List of events to potentially export
- `dashboard_logger`: Logger instance for system logs

**Returns:** `True` if export completed, `False` if skipped

**Export Options:**

- **Event History**: JSON and CSV formats with timestamps
- **System Logs**: Timestamped log files with filtering options
- **Performance Reports**: System metrics and statistics
- **Complete Session**: All data combined with metadata

#### Utility Functions

##### handle_professional_exit()

Main function for handling professional exit experience.

```python
def handle_professional_exit(
    console: Console, 
    events: List[Dict[str, Any]], 
    dashboard_logger=None, 
    synthetic_mode: bool = False
) -> bool
```

**Parameters:**

- `console`: Rich console instance
- `events`: Current events list for export
- `dashboard_logger`: Logger for system information
- `synthetic_mode`: Whether running in synthetic mode

**Returns:** `True` if exit confirmed, `False` to continue

**Process Flow:**

1. Display exit confirmation dialog
2. Offer data export options if confirmed
3. Execute selected exports with progress indicators
4. Clean terminal state restoration
5. Display professional goodbye message

### cli_dashboard_detection_adapter.py

Enhanced synthetic event generation with realistic attack scenarios.

#### Key Functions

##### generate_synthetic_event()

Advanced synthetic event generator with realistic attack scenarios.

```python
async def generate_synthetic_event() -> AsyncGenerator[Dict[str, Any], None]
```

**Yields:** Realistic synthetic security events

**Enhanced Features:**

- **Uncapped Event Limits**: No restrictions on event generation for comprehensive testing
- **Critical Event Generation**: Proper categorization of high-severity threats
- **Advanced Attack Scenarios**:
  - Realistic replay attack sequences with signal degradation
  - Advanced jamming patterns (continuous, pulse, sweep, spot)
  - Multi-step brute force attacks with escalating threat levels
  - Signal cloning attacks with characteristic analysis
  - Relay attacks with signal amplification detection
  - Critical vulnerability exploits and zero-day scenarios
  - Advanced Persistent Threat (APT) attack simulations
  - Multi-modal attacks combining RF and NFC vectors

**Technical Improvements:**

- Enhanced modulation type variety (OOK, ASK, FSK, GFSK)
- Realistic signal characteristics and degradation patterns
- Improved NFC correlation simulation
- Better technical evidence generation for validation
- Advanced threat progression modeling

## Usage Examples

### Basic Dashboard Operation

```python
# Enhanced CLI dashboard with professional experience
uv run python cli_dashboard.py --mock

# Advanced synthetic event testing
uv run python cli_dashboard.py --mock --synthetic

# TCP stream mode with professional features
uv run python cli_dashboard.py --source tcp --tcp-host 127.0.0.1 --tcp-port 8888
```

### Professional Exit Experience

```python
# During dashboard operation:
# Press 'q' or Ctrl+C for graceful exit
# Choose export options:
# - Event history (JSON/CSV)
# - System logs (timestamped)
# - Performance reports (metrics)
# - Complete session data
```

### Programmatic Integration

```python
from utils.exit_dialog import ExitDialogManager, handle_professional_exit
from rich.console import Console

console = Console()
exit_manager = ExitDialogManager(console)

# Handle professional exit
should_exit = handle_professional_exit(
    console=console,
    events=current_events,
    dashboard_logger=logger,
    synthetic_mode=True
)
```

## Configuration Options

### Dashboard Settings

- **Event Pagination**: 20 events per page (configurable)
- **Refresh Rate**: Configurable update intervals
- **Display Modes**: Full dashboard, status-only, help overlay
- **Export Directory**: `exports/` (auto-created)

### Exit Dialog Settings

- **Confirmation Timeout**: 30 seconds default
- **Export Formats**: JSON, CSV, TXT
- **Progress Indicators**: Rich progress bars for exports
- **Terminal Cleanup**: Automatic state restoration

### Synthetic Event Generation

- **Event Types**: 15+ different attack scenarios
- **Generation Rate**: Configurable intervals
- **Threat Levels**: Automatic escalation patterns
- **Technical Evidence**: Realistic signal characteristics

## Error Handling

### Exit Dialog Errors

```python
try:
    should_exit = handle_professional_exit(console, events, logger)
except KeyboardInterrupt:
    # Handle forced exit
    console.print("[red]Force exit detected. Cleaning up...[/red]")
except ExportError as e:
    # Handle export failures
    console.print(f"[yellow]Export failed: {e}[/yellow]")
```

### Dashboard Errors

```python
try:
    render_dashboard(events, selected_event, status, console)
except RenderError as e:
    # Handle rendering issues
    console.print(f"[red]Dashboard render error: {e}[/red]")
except PaginationError as e:
    # Handle pagination issues
    console.print(f"[yellow]Pagination error: {e}[/yellow]")
```

## Performance Considerations

### Memory Management

- **Event Buffer**: Limited to prevent memory leaks
- **Export Streaming**: Large datasets exported in chunks
- **Terminal Cleanup**: Proper resource deallocation

### Rendering Optimization

- **Selective Updates**: Status-only updates for performance
- **Force Refresh**: Only when necessary
- **Pagination**: Efficient large dataset handling

### Export Performance

- **Async Operations**: Non-blocking export processes
- **Progress Tracking**: Real-time export progress
- **Format Optimization**: Efficient serialization

## Integration Notes

### Rich Library Integration

The CLI dashboard extensively uses the Rich library for:

- Professional ASCII art presentation
- Progress bars and status indicators
- Confirmation dialogs and user input
- Terminal state management
- Color-coded threat level visualization

### Logging Integration

- **Dashboard Logger**: Integrated with exit dialog export
- **Event Logging**: Comprehensive event history tracking
- **System Metrics**: Performance and resource monitoring
- **Export Logging**: Detailed export operation logs

### Hardware Integration

- **RTL-SDR Support**: Enhanced hardware detection and management
- **TCP Stream**: Improved connection handling and error recovery
- **Mock Mode**: Comprehensive testing without hardware requirements
- **Synthetic Mode**: Advanced testing scenario generation

## Migration Guide

### From Previous Versions

1. **Exit Handling**: Replace basic exit with `handle_professional_exit()`
2. **Event Navigation**: Update pagination to use 20 events per page
3. **Export Features**: Integrate new export capabilities
4. **Startup Experience**: Update to use enhanced ASCII art and loading

### Configuration Updates

```python
# Old configuration
dashboard_config = {
    "events_per_page": 10,
    "exit_handler": "basic"
}

# New configuration
dashboard_config = {
    "events_per_page": 20,
    "exit_handler": "professional",
    "export_enabled": True,
    "ascii_art": True,
    "progress_indicators": True
}
```

## Future Enhancements

### Planned Features

- **Custom Export Templates**: User-defined export formats
- **Advanced Filtering**: Enhanced event filtering and search
- **Dashboard Themes**: Customizable color schemes and layouts
- **Remote Monitoring**: Web-based dashboard interface
- **AI-Powered Analysis**: Machine learning threat detection integration

### API Stability

- **Core Functions**: Stable API with backward compatibility
- **Export Formats**: Additional formats planned (XML, YAML)
- **Integration Points**: Enhanced plugin architecture
- **Configuration**: Extended configuration options

## See Also

- [Detection API Reference](detection_api.md) - Core detection algorithms
- [Hardware Management API](hardware_management.md) - Hardware integration
- [Validation Framework API](validation_framework.md) - Testing and validation
- [Backend README](../../README.md) - System overview and setup
- [CHANGELOG](../CHANGELOG.md) - Recent updates and changes
