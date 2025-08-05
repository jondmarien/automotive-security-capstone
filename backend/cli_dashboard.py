"""
cli_dashboard.py

A Rich-based CLI dashboard for real-time monitoring of automotive RF detection events.
Supports backend API polling, direct TCP/local stream, or mock data as event sources.
Detection events are also logged to a local file ('detection_events.log').

ENHANCED VERSION: Now includes detailed signal analysis display, technical evidence presentation,
RF signal feature visualization, and NFC correlation indicators.

Designed for a student-led POC in automotive security (4th year cybersecurity).

Usage:
    python cli_dashboard.py --source [api|tcp] [--api-url URL] [--tcp-host HOST] [--tcp-port PORT]
    python cli_dashboard.py --mock

Example (TCP):
    python cli_dashboard.py --source tcp --tcp-host 127.0.0.1 --tcp-port 8888
Example (mock/demo):
    python cli_dashboard.py --mock

See backend/README.md for full project context.
"""
import argparse
import asyncio
import time
from datetime import datetime
from collections import deque
from typing import Dict, Any

import aiohttp

# Import timestamp format constants
from utils.signal_constants import TIMESTAMP_FORMAT, TIMESTAMP_FORMAT_SHORT
from utils.exit_dialog import display_logo
from rich import box
from rich.live import Live
from rich.align import Align
from rich.console import Console, Group
from rich.text import Text
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.spinner import Spinner
from rich.table import Table
from rich.tree import Tree

# Import performance monitoring
from utils.simple_performance_monitor import get_performance_monitor
from rich.theme import Theme

# Import prompt_toolkit for key handling
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import Application
from prompt_toolkit.layout.containers import HSplit, Window, VSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout import Layout as PTLayout
from prompt_toolkit.input import create_input
from prompt_toolkit.output import create_output

# Import logging configuration
from utils.logging_config import (
    setup_dashboard_logging,
    log_event_detection,
    log_dashboard_action,
    log_performance_metrics,
    log_system_health
)

# Import professional exit dialog
from utils.exit_dialog import handle_professional_exit

# Global variables
# Store RSSI history for sparkline visualization (max 20 values)
rssi_history = deque(maxlen=20)

# Dashboard pagination configuration
MAX_EVENTS_PER_PAGE = 20

# --- Threat Counter Functions ---
def calculate_threat_statistics(events):
    """
    Calculate accurate threat statistics from events list.
    
    Per requirements:
    - Count all Suspicious, Malicious, and Critical events
    - Include all multi-modal attacks (even if marked benign)
    - Separate total event count from threat count
    - Validate threat levels properly
    
    Args:
        events (list): List of detection events
        
    Returns:
        dict: Statistics including total_events, threat_count, breakdown by level
    """
    if not events:
        return {
            'total_events': 0,
            'threat_count': 0,
            'benign_count': 0,
            'suspicious_count': 0,
            'malicious_count': 0,
            'critical_count': 0,
            'multi_modal_count': 0
        }
    
    stats = {
        'total_events': len(events),
        'threat_count': 0,
        'benign_count': 0,
        'suspicious_count': 0,
        'malicious_count': 0,
        'critical_count': 0,
        'multi_modal_count': 0
    }
    
    for event in events:
        # Skip error events
        if isinstance(event, dict) and "error" in event:
            continue
            
        threat_level = event.get("threat", "").strip()
        details = event.get("details", "")
        nfc_correlated = event.get("nfc_correlated", False)
        
        # Check if this is a multi-modal attack
        is_multi_modal = (
            "Multi-modal attack detected" in details or
            "multi_modal" in details.lower() or
            nfc_correlated or
            event.get("threat_category") == "multi_modal_attack"
        )
        
        # Track if this event is a threat (will be set to True for any threat condition)
        is_threat = False
        
        # Count by threat level first
        if threat_level.lower() == "benign":
            stats['benign_count'] += 1
            # Benign is only a threat if it's multi-modal
            if is_multi_modal:
                is_threat = True
        elif threat_level.lower() == "suspicious":
            stats['suspicious_count'] += 1
            is_threat = True
        elif threat_level.lower() == "malicious":
            stats['malicious_count'] += 1
            is_threat = True
        elif threat_level.lower() == "critical":
            stats['critical_count'] += 1
            is_threat = True
        else:
            # Unknown threat level - treat as suspicious for safety
            stats['suspicious_count'] += 1
            is_threat = True
        
        # Count multi-modal attacks separately (but don't double-count threats)
        if is_multi_modal:
            stats['multi_modal_count'] += 1
            # Multi-modal attacks are always threats per requirements
            is_threat = True
        
        # Increment threat count once per event if it qualifies as a threat
        if is_threat:
            stats['threat_count'] += 1
    
    return stats

def generate_sparkline(values, min_value=-90, max_value=-20, width=20):
    """
    Generate a sparkline visualization using Unicode block characters.
    
    Args:
        values (list): List of numerical values to visualize
        min_value (int): Minimum value for scaling (default: -90 dBm)
        max_value (int): Maximum value for scaling (default: -20 dBm)
        width (int): Width of the sparkline (default: 20 characters)
        
    Returns:
        str: Unicode sparkline representation
    """
    if not values:
        return "" 
    
    # Ensure we don't exceed the width
    if len(values) > width:
        values = values[-width:]
    
    # Unicode block characters for different heights (1/8, 2/8, ..., 8/8)
    blocks = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    
    # Scale values to 0-8 range for block selection
    range_size = max_value - min_value
    scaled_values = []
    
    for val in values:
        # Clamp value to min_value..max_value range
        clamped = max(min_value, min(max_value, val))
        # Scale to 0..8 range for block selection
        normalized = (clamped - min_value) / range_size
        block_idx = int(normalized * 8)
        scaled_values.append(block_idx)
    
    # Generate sparkline string
    sparkline = ''
    for idx in scaled_values:
        sparkline += blocks[idx]
    
    return sparkline

# Initialize dashboard logger (will be set up in main())
dashboard_logger = None

# Define a global theme for consistent styling
custom_theme = Theme({
    "header": "bold cyan",
    "threat.low": "green",
    "threat.medium": "yellow",
    "threat.high": "bold red",
    "threat.critical": "bold reverse red",
    "metric.label": "bold magenta",
    "table.border": "dim white",
    "table.header": "bold underline white"
})
console = Console(theme=custom_theme)

# ASCII art logo - now using the new implementation from utils.exit_dialog

def render_landing_screen_content(args):
    """Render the landing screen content without progress bars for toggling in main dashboard."""
    # Create the landing screen content as a renderable
    from rich.columns import Columns
    
    # ASCII art logo using new implementation
    import pyfiglet
    
    # Create the logo content properly
    logo_text = pyfiglet.figlet_format("AutoSec Monitor", font="standard")
    
    logo_panel = Panel(
        Align.center(Group(
            Align.center(Text(logo_text, style="bold cyan")),
            Text("Automotive Cybersecurity Proof of Concept", style="dim white"),
            Text("4th Year Cybersecurity Capstone Project (2025)", style="italic dim")
        )),
        title="[bold blue]AutoSec Monitor[/bold blue]",
        border_style="cyan",
        padding=(1, 2)
    )
    
    # System information panel
    system_info = Table.grid(padding=1)
    system_info.add_column(justify="left", style="bold white")  # Labels stay left-aligned
    system_info.add_column(justify="center", style="white")  # Values are centered
    
    system_info.add_row("🖥️  System:", "Real-time RF/NFC Threat Detection & Analysis")
    system_info.add_row("📡 Hardware:", "RTL-SDR V4 + Raspberry Pi Pico W")
    system_info.add_row("🎯 Target:", "Automotive Wireless Attack Detection")
    system_info.add_row("📅 Timestamp:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    system_info.add_row("🔧 Version:", "AutoSec Monitor v1.0")
    
    system_panel = Panel(system_info, title="[bold]System Information[/bold]", 
                         border_style="blue", padding=(1, 2))
    
    # Configuration panel
    config_info = Table.grid(padding=1)
    config_info.add_column(justify="left", style="bold white")
    config_info.add_column(justify="center", style="green")  # Values are centered
    
    # Determine configuration mode and status
    if args.mock:
        if args.synthetic:
            mode = "🧪 SYNTHETIC SIGNALS"
            status = "Advanced testing mode with realistic signal characteristics"
            mode_color = "magenta"
        else:
            mode = "🎭 MOCK DATA"
            status = "Demo/testing mode with simulated events"
            mode_color = "yellow"
    elif args.source == "api":
        mode = "🌐 API POLLING"
        status = f"Backend API at {args.api_url}"
        mode_color = "cyan"
    elif args.source == "tcp":
        mode = "📡 TCP STREAM"
        status = f"Real-time TCP stream from {args.tcp_host}:{args.tcp_port}"
        mode_color = "green"
    else:
        mode = "🔄 AUTO DETECT"
        status = "Automatic event source detection"
        mode_color = "blue"
    
    config_info.add_row("🔧 Mode:", f"[{mode_color}]{mode}[/{mode_color}]")
    config_info.add_row("📊 Status:", status)
    config_info.add_row("🔍 Signal Analysis:", "✅ Enabled" if args.detailed else "❌ Disabled")
    config_info.add_row("📱 NFC Correlation:", "✅ Enabled" if args.nfc else "❌ Disabled")
    
    if args.event != -1:
        config_info.add_row("👁️  Event Focus:", f"Event #{args.event} (manual selection)")
    else:
        config_info.add_row("👁️  Event Focus:", "Latest event (real-time follow)")
    
    config_panel = Panel(config_info, title="[bold]Active Configuration[/bold]", 
                         border_style="green", padding=(1, 2))
    
    # Help information
    help_info = Table.grid(padding=1)
    help_info.add_column(justify="left", style="bold white")  # Emojis stay left-aligned
    help_info.add_column(justify="center", style="dim white")  # Descriptions are centered
    
    help_info.add_row("⬆️⬇️", "Navigate events (Up/Down arrows)")
    help_info.add_row("🏠🔚", "First/Latest event (Home/End)")
    help_info.add_row("⬅️➡️", "Previous/Next page (Left/Right arrows)")
    help_info.add_row("❓", "Toggle help display ('?' key)")
    help_info.add_row("🏁", "Toggle landing screen ('m' key)")
    help_info.add_row("🚪", "Exit dashboard ('q' key)")
    help_info.add_row(" ⚡", "Instant exit (Ctrl+C)")
    
    help_panel = Panel(help_info, title="[bold]Keyboard Controls[/bold]", 
                       border_style="yellow", padding=(1, 2))
    
    # Group and center the system and config panels
    info_panels_group = Align.center(
        Columns([system_panel, config_panel], equal=True, expand=False, padding=(0, 2))
    )
    
    # Center the keyboard controls panel
    centered_help_panel = Align.center(help_panel)
    
    # Combine all panels with proper spacing and centering
    panels = Group(
        logo_panel,
        "",  # Empty line for spacing
        info_panels_group,
        "",  # Empty line for spacing
        centered_help_panel,
        "",  # Empty line for spacing
        Align.center("[dim]Press 'm' to return to dashboard[/dim]")
    )
    
    return panels

def display_enhanced_startup_screen(args, startup_delay=2.5):
    """Display enhanced startup screen with ASCII art, system info, and configuration details."""
    console.clear()
    
    # Display ASCII art logo immediately (using new implementation)
    display_logo(console)
    console.print(Align.center("4th Year Cybersecurity Capstone Project (2025)"), style="italic dim")
    console.print("\n")
    
    # System information panel
    system_info = Table.grid(padding=1)
    system_info.add_column(justify="left", style="bold white")
    system_info.add_column(justify="left", style="white")
    
    system_info.add_row("🖥️  System:", "Real-time RF/NFC Threat Detection & Analysis")
    system_info.add_row("📡 Hardware:", "RTL-SDR V4 + Raspberry Pi Pico W")
    system_info.add_row("🎯 Target:", "Automotive Wireless Attack Detection")
    system_info.add_row("📅 Timestamp:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    console.print(Align.center(Panel(system_info, title="[bold]System Information[/bold]", 
                                     border_style="blue", padding=(1, 2))), "\n")
    
    # Configuration panel
    config_info = Table.grid(padding=1)
    config_info.add_column(justify="left", style="bold white")
    config_info.add_column(justify="center", style="green")  # Values are centered
    
    # Determine configuration mode and status
    if args.mock:
        if args.synthetic:
            mode = "🧪 SYNTHETIC SIGNALS"
            status = "Advanced testing mode with realistic signal characteristics"
            mode_color = "magenta"
        else:
            mode = "🎭 MOCK DATA"
            status = "Demo/testing mode with simulated events"
            mode_color = "yellow"
    elif args.source == "api":
        mode = "🌐 API POLLING"
        status = f"Backend API at {args.api_url}"
        mode_color = "cyan"
    elif args.source == "tcp":
        mode = "📡 TCP STREAM"
        status = f"Real-time TCP stream from {args.tcp_host}:{args.tcp_port}"
        mode_color = "green"
    else:
        mode = "🔄 AUTO DETECT"
        status = "Automatic event source detection"
        mode_color = "blue"
    
    config_info.add_row("🔧 Mode:", f"[{mode_color}]{mode}[/{mode_color}]")
    config_info.add_row("📊 Status:", status)
    config_info.add_row("🔍 Signal Analysis:", "✅ Enabled" if args.detailed else "❌ Disabled")
    config_info.add_row("📱 NFC Correlation:", "✅ Enabled" if args.nfc else "❌ Disabled")
    
    if args.event != -1:
        config_info.add_row("👁️  Event Focus:", f"Event #{args.event} (manual selection)")
    else:
        config_info.add_row("👁️  Event Focus:", "Latest event (real-time follow)")
    
    console.print(Align.center(Panel(config_info, title="[bold]Active Configuration[/bold]", 
                                     border_style="green", padding=(1, 2))), "\n")
    
    # Loading progress with countdown
    console.print(Align.center("[dim]Initializing threat detection systems...[/dim]"))
    console.print("\n")

    # Simulate startup delay (in seconds)
    startup_delay = 7  # Adjust as needed

    # Startup sequence
    startup_steps = [
        (10, "Initializing Rich console..."),
        (25, "Loading signal processing modules..."),
        (40, "Setting up event logging system..."),
        (55, "Configuring threat detection engine..."),
        (70, "Establishing event data source..."),
        (85, "Preparing real-time dashboard..."),
        (100, "Ready to monitor threats!")
    ]

    step_delay = startup_delay / len(startup_steps)

    # Create progress (no task yet)
    progress = Progress(
        TextColumn("[bold blue]{task.description}", justify="center"),
        BarColumn(bar_width=60),
        TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
        console=console,
        transient=True  # Auto-remove when done
    )

    # Function to get the centered panel (will be empty until task is added)
    def get_progress_panel():
        return Align.center(
            Panel(progress, expand=False, title="Startup Progress", border_style="blue")
        )

    # Now use Live to manage display
    with Live(get_progress_panel(), console=console, refresh_per_second=4) as live:
        # Add the task inside Live (starts displaying centered)
        task = progress.add_task(startup_steps[0][1], total=100)
    
        for percent, description in startup_steps:
            progress.update(task, completed=percent, description=f"[cyan]{description}")
            live.update(get_progress_panel())  # Refresh in place
            time.sleep(step_delay)
    
    # Final startup message
    console.print("\n")
    console.print(Align.center("[bold green]✅ System Ready![/bold green]"))
    console.print("\n")
    console.print(Align.center("[bold white]Press any key to launch dashboard, or 'q' to quit...[/bold white]"))
    console.print(Align.center("[dim](Arrow keys will navigate events once dashboard loads)[/dim]"))
    
    # Use prompt_toolkit input directly (no Application.run() to avoid asyncio conflicts)
    exit_app = False
    launch_dashboard = False
    
    # Simple prompt_toolkit key reading without Application
    import sys
    try:
        input_obj = create_input()
        key = input_obj.read_key()
        
        # Handle the key press
        if hasattr(key, 'data'):
            key_data = key.data.lower() if hasattr(key.data, 'lower') else str(key.data)
            if key_data == 'q':
                exit_app = True
            else:
                launch_dashboard = True
        elif hasattr(key, 'key'):
            from prompt_toolkit.keys import Keys
            if key.key == Keys.ControlC:
                exit_app = True
            else:
                launch_dashboard = True
        else:
            # Any other key launches dashboard
            launch_dashboard = True
            
        input_obj.close()
        
    except KeyboardInterrupt:
        exit_app = True
    except Exception:
        # Fallback - launch dashboard
        launch_dashboard = True
    
    if exit_app:
        console.print(Align.center("[dim]Goodbye![/dim]"))
        sys.exit(0)
    
    if launch_dashboard:
        # Clear and transition to dashboard
        console.clear()
        console.print("\n" + "=" * console.width, style="dim white")
        console.print(Align.center("[bold cyan]🚀 Launching Dashboard...[/bold cyan]"))
        console.print("=" * console.width, style="dim white")
        time.sleep(0.3)  # Brief visual transition

# Gradient header for dashboard title
def create_gradient_header():
    """Create a gradient header for the dashboard title."""
    title = "Automotive Security Monitor"
    # Build gradient by splitting title: first segment cyan, second segment magenta
    split_at = 10
    header_text = Text()
    header_text.append(title[:split_at], style="bold cyan")
    header_text.append(title[split_at:], style="bold magenta")
    return header_text

# --- Event Source Abstractions ---
async def fetch_events_api(api_url: str):
    """
    Polls a backend API for new detection events (JSON list).
    Yields events as dictionaries.

    Args:
        api_url (str): URL to poll for events (expects JSON array of dicts).

    Yields:
        dict: Each detection event from the API.

    Example:
        async for event in fetch_events_api("http://localhost:8000/events"):
            print(event)
    """
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(api_url) as resp:
                    if resp.status == 200:
                        events = await resp.json()
                        for event in events:
                            yield event
                    else:
                        yield {"error": f"API error: {resp.status}"}
            except Exception as e:
                yield {"error": f"API connection error: {e}"}
            await asyncio.sleep(2)  # Poll interval

async def stream_events_tcp(host: str, port: int):
    """
    Connects to a TCP server that streams JSON detection events (newline-delimited).
    Yields events as dictionaries.

    Args:
        host (str): TCP server host (e.g., 'localhost')
        port (int): TCP server port (e.g., 8888)

    Yields:
        dict: Each detection event received as a JSON object.

    Example:
        async for event in stream_events_tcp('localhost', 8888):
            print(event)
    """
    while True:
        try:
            reader, _ = await asyncio.open_connection(host, port)
            buffer = ""
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                buffer += data.decode()
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            import json
                            event = json.loads(line)
                            yield event
                        except Exception as e:
                            yield {"error": f"Invalid JSON: {e}"}
        except Exception as e:
            yield {"error": f"TCP connection error: {e}"}
            await asyncio.sleep(2)  # Retry interval

# --- Enhanced Logging ---
def log_event(event: Dict[str, Any]):
    """
    Log detection events using the enhanced logging system.

    Args:
        event (dict): The detection event to log.

    Example:
        log_event({"type": "RF Unlock", "threat": "Low"})
    """
    global dashboard_logger
    if dashboard_logger:
        log_event_detection(dashboard_logger, event, "CLI Dashboard")

# --- Dashboard Rendering ---
def render_dashboard(events, selected_event, status_text, console, selected_event_idx=-1, status_only=False, show_help=False, current_page=0, force_refresh=False):
    """
    Render the enhanced CLI dashboard with signal analysis and technical evidence panels.
    
    Args:
        events (list): List of detection events to display
        selected_event (dict, optional): Currently selected event for evidence display
                                         If None, uses the most recent event
        status_text (str): Status text to display at the bottom
        console (Console): Rich Console object to use for rendering
        selected_event_idx (int): Index of the currently selected event
        status_only (bool): If True, only update the status bar for better performance
    
    Returns:
        rich.panel.Panel: The dashboard panel
    """
    # Get console dimensions
    width = console.width
    height = console.height
    
    # Create full layout for normal refresh
    layout = Layout()
    # Make footer expandable based on help display
    footer_size = 3 if show_help else 1
    layout.split_column(
        Layout(name="header", size=4),  # Increased to accommodate threat counter
        Layout(name="body"),
        Layout(name="footer", size=footer_size)
    )

    # Split body into main event table (70%) and bottom section (30%)
    layout["body"].split_column(
        Layout(name="events_table", ratio=7),  # Maximize event table space
        Layout(name="bottom_panels", ratio=3)  # Increased bottom section for analysis and evidence
    )
    
    # Split bottom panels into signal metrics and evidence panel
    layout["bottom_panels"].split_row(
        Layout(name="signal_metrics", ratio=1),
        Layout(name="evidence_panel", ratio=1)
    )
    
    # Calculate threat statistics for display
    threat_stats = calculate_threat_statistics(events)
    
    # Create threat counter display
    threat_counter_text = Text()
    threat_counter_text.append("📊 ", style="bold yellow")
    threat_counter_text.append(f"Events: {threat_stats['total_events']} ", style="bright_white")
    threat_counter_text.append("| ", style="dim white")
    threat_counter_text.append(f"Threats: {threat_stats['threat_count']} ", style="bold red")
    threat_counter_text.append("[", style="dim white")
    threat_counter_text.append(f"Suspicious: {threat_stats['suspicious_count']}", style="orange1")
    threat_counter_text.append(" | ", style="dim white")
    threat_counter_text.append(f"Malicious: {threat_stats['malicious_count']}", style="red")
    threat_counter_text.append(" | ", style="dim white")
    threat_counter_text.append(f"Critical: {threat_stats['critical_count']}", style="bold red")
    if threat_stats['multi_modal_count'] > 0:
        threat_counter_text.append(" | ", style="dim white")
        threat_counter_text.append(f"Multi-Modal: {threat_stats['multi_modal_count']}", style="bold magenta")
    threat_counter_text.append("]", style="dim white")
    
    # Combine gradient header with threat counter
    header_content = Group(
        create_gradient_header(),
        Align.center(threat_counter_text)
    )
    
    # Header with gradient title and threat counter
    header_panel = Panel(
        header_content,
        border_style="bright_cyan",
        expand=True,
        height=4,  # Increased height to accommodate threat counter
        padding=(0, 2),  # Increased horizontal padding
        title="Automotive Security",
        subtitle="Real-time Monitoring"
    )
    layout["header"].update(header_panel)

    # Create events table with enhanced styling
    table = Table(
        title="Automotive Security CLI Dashboard", 
        expand=True, 
        box=box.SIMPLE,  # More minimal box style
        padding=(0, 1),  # Reduced padding
        collapse_padding=True,  # Help with multi-line content
        highlight=True,  # Highlight rows on hover
        header_style="bold bright_white on dark_blue",  # Enhanced header styling
        border_style="bright_blue"
    )
    table.add_column("Time", style="cyan", no_wrap=True, justify="center")
    table.add_column("Type", style="magenta", no_wrap=True, justify="center")
    table.add_column("Threat", style="threat.low", no_wrap=True, justify="center")
    table.add_column("Source", style="blue", no_wrap=True, justify="center")
    table.add_column("Details", style="bright_white", width=30)  # Fixed width for details to prevent affecting other columns
    table.add_column("Signal", style="green", no_wrap=True, justify="center")
    # Add NFC correlation indicator column
    table.add_column("NFC", style="bold red", justify="center", width=3, no_wrap=True)

    # Enhanced color mapping for threat levels including Critical for correlated attacks
    colors = {
        "Benign": "green",
        "Suspicious": "orange1",
        "Malicious": "red",
        "Critical": "bold red on white"  # New critical level for correlated attacks
    }
    
    # Prepare signal metrics and evidence from the selected event for visualization
    # Use selected_event_idx to determine which event to show in details
    if selected_event is None and events:
        if selected_event_idx != -1 and abs(selected_event_idx) <= len(events):
            # Use the event at the selected index
            selected_event = events[selected_event_idx]
        else:
            # Default to most recent event
            selected_event = events[-1]
    
    # Pass console width for consistent sizing across screen sizes
    signal_viz = render_signal_metrics(selected_event, console_width=width) if selected_event else Align.center(Text("No signal data available"))
    evidence_panel = render_evidence_panel(selected_event, console_width=width) if selected_event else Align.center(Text("No evidence data available"))
    
    # Pagination: Show events per page (configured by MAX_EVENTS_PER_PAGE)
    # NOTE: Current custom pagination works well for our needs, but if future requirements demand more
    # advanced features, we should consider migrating to Rich's Pager component for large-table navigation.
    # See: https://rich.readthedocs.io/en/latest/console.html#paging
    total_pages = max(1, (len(events) + MAX_EVENTS_PER_PAGE - 1) // MAX_EVENTS_PER_PAGE)
    
    # Ensure current_page is valid
    current_page = max(0, min(current_page, total_pages - 1))
    
    # Calculate the start and end indices for the current page
    start_idx = max(0, len(events) - (current_page + 1) * MAX_EVENTS_PER_PAGE)
    end_idx = max(0, len(events) - current_page * MAX_EVENTS_PER_PAGE)
    
    # Get events for the current page (most recent events first)
    page_events = events[start_idx:end_idx]
    for i, event in enumerate(page_events):
        # If event is an error dict (e.g., {"error": ...}), render as a single-row error
        if isinstance(event, dict) and "error" in event:
            table.add_row("-", "ERROR", "[red]Error[/]", "-", str(event["error"]), "-")
            continue
            
        time_str = event.get("time") or event.get("timestamp", "-")
        event_type = event.get("type", "-")
        threat = event.get("threat", "-")
        source = event.get("source", "-")
        details = event.get("details", "-")
        
        # Signal details column
        signal_str = get_signal_summary(event)
        
        # NFC correlation indicator
        nfc_indicator = ""
        if event.get("nfc_correlated", False):
            nfc_indicator = "[bold red]! [/]"
        elif "NFC" in event.get("type", ""):
            nfc_indicator = "[blue]*[/]"
            
        # Apply color to threat level
        threat_colored = f"[{colors.get(threat, 'white')}]" + threat + "[/]"
        
        # Handle multi-line details more gracefully
        # This prevents a single column from forcing all others to expand vertically
        formatted_details = details.replace("\n", " ") if isinstance(details, str) else str(details)
        
        # Check if this is the selected event for highlighting
        # Calculate the actual index in the events list
        actual_event_index = start_idx + i
        
        # Fix highlighting logic to work consistently with both mock and synthetic events
        is_selected = False
        if selected_event_idx == -1:
            # For latest event (-1), highlight the last row on the first page
            is_selected = (current_page == 0 and i == len(page_events) - 1)
        else:
            # For specific event index, calculate position accurately
            target_index = len(events) + selected_event_idx if selected_event_idx < 0 else selected_event_idx
            is_selected = (actual_event_index == target_index)
        
        # Apply highlighting to selected row
        if is_selected:
            # Add background highlighting to all columns for selected row
            # Use a more visible highlighting style with bright background
            time_str = f"[bold white on blue]{time_str}[/]"
            event_type = f"[bold white on blue]{event_type}[/]"
            # Keep threat color visible but make background blue
            threat_colored = f"[bold white on blue]{threat}[/]"
            source = f"[bold white on blue]{source}[/]"
            formatted_details = f"[bold white on blue]{formatted_details}[/]"
            signal_str = f"[bold white on blue]{signal_str}[/]"
            nfc_indicator = f"[bold white on blue]{nfc_indicator}[/]"
        
        table.add_row(time_str, event_type, threat_colored, source, formatted_details, signal_str, nfc_indicator)

    # Assemble the layout
    # Enhanced panel styling with consistent borders and padding
    # Add page counter to the subtitle - always show page info, even with only one page
    page_info = f"Page {current_page + 1}/{total_pages}"
    
    layout["events_table"].update(Panel(
        table, 
        title="Detection Events", 
        border_style="bright_cyan",
        padding=(0, 1),
        subtitle=f"↑/↓: Navigate | ←/→: Pages | End: Latest | {page_info}"
    ))
    
    # Calculate consistent panel heights based on console size
    # This prevents panels from expanding too much on larger screens
    bottom_panel_height = max(8, min(12, height // 4))  # Between 8-12 lines based on screen height
    
    layout["signal_metrics"].update(Panel(
        signal_viz, 
        title="Signal Analysis", 
        border_style="green",
        padding=(1, 1),
        subtitle="RSSI Trend ↔",
        height=bottom_panel_height
    ))
    
    layout["evidence_panel"].update(Panel(
        evidence_panel, 
        title="Technical Evidence", 
        border_style="yellow",
        padding=(1, 1),
        subtitle="Attack Details",
        height=bottom_panel_height
    ))
    # Create footer with spinner and performance metrics
    performance_monitor = get_performance_monitor()
    performance_summary = performance_monitor.get_dashboard_summary()
    
    # Add event count from the same source as header to maintain consistency
    event_count_text = f"Events: {len(events)}"
    
    # Combine status text with event count and performance metrics
    if performance_summary and performance_summary != 'Monitoring...':
        enhanced_status_text = f"{status_text} | {event_count_text} | {performance_summary}"
    else:
        enhanced_status_text = f"{status_text} | {event_count_text}"
    
    # Create a properly centered and grouped footer
    if show_help:
        # Single-line footer with help information
        help_text = Text()
        help_text.append("📋 HELP - ", style="bold yellow")
        help_text.append("↑/↓: Navigate  ", style="cyan")
        help_text.append("Home/End: First/Last  ", style="cyan")
        help_text.append("←/→: Pages  ", style="cyan")
        help_text.append("?: Help  ", style="cyan")
        help_text.append("m: Landing Screen  ", style="cyan")
        help_text.append("q: Quit  ", style="cyan")
        help_text.append("Ctrl+C: Instant Exit", style="red")
        
        # Create a responsive footer layout
        status_spinner = Spinner('dots', text=enhanced_status_text, style="cyan")
        
        # Use Group to stack elements vertically and center them
        footer_group = Group(
            Align.center(status_spinner),
            Text(""),  # Spacing
            Align.center(help_text)
        )
        footer_content = footer_group
    else:
        # Single line footer - centered
        spinner = Spinner('dots', text=enhanced_status_text, style="cyan")
        footer_content = Align.center(spinner)
    
    layout["footer"].update(footer_content)
    
    # Final dashboard panel with minimal padding
    # Use height parameter to ensure full rendering without ellipsis
    # This forces Rich to render the full panel height
    console_height = console.height if hasattr(console, 'height') else 40
    panel = Panel(
        layout, 
        title="Automotive Security Dashboard",
        subtitle=None,  # Remove subtitle to avoid duplication with footer
        border_style="bright_cyan", 
        padding=(0, 0),
        height=console_height - 2  # Subtract 2 for margins/borders
    )
    return panel


def render_evidence_panel(event, console_width=None):
    """
    Renders a technical evidence panel as a collapsible tree with enhanced styling and icons.
    
    Args:
        event (dict): The event with evidence data.
        console_width (int, optional): Console width for consistent sizing across screen sizes.
        
    Returns:
        rich.tree.Tree or rich.text.Text: Formatted evidence tree or status text.
    """
    if not event or not isinstance(event, dict) or "error" in event:
        return Align.center(Text("No evidence available", style="dim italic"))

    security_types = ["Replay Attack", "Brute Force", "Jamming Attack", "NFC Scan", "NFC Tag Present"]
    is_security_event = (event.get("type", "") in security_types or 
                         event.get("threat", "") in ["Malicious", "Critical", "Suspicious"] or
                         event.get("nfc_correlated", False) or 
                         "NFC" in event.get("type", ""))

    if not is_security_event:
        return Align.center(Text("No security evidence for this event", style="dim italic"))

    # Extract evidence data
    evidence = event.get("evidence", {})
    technical_evidence = event.get("technical_evidence", {})
    
    # Always show panel for NFC events even without evidence
    if not evidence and not technical_evidence and not event.get("nfc_correlated", False) and "NFC" not in event.get("type", ""):
        return Align.center(Text("Event lacks detailed evidence", style="dim italic"))

    # Create a more detailed tree with better visual structure and icons
    tree = Tree(f"🛡️  [bold yellow]{event.get('type', 'Security Event')} Analysis[/]", guide_style="bright_blue")

    if evidence.get("detection_confidence"):
        confidence = evidence["detection_confidence"] * 100
        style = "green" if confidence > 75 else "yellow" if confidence > 50 else "red"
        tree.add(f"[bold]Confidence:[/] [{style}]{confidence:.1f}%[/]")

    if evidence.get("signal_match_score"):
        match_score = evidence["signal_match_score"] * 100
        style = "green" if match_score > 75 else "yellow" if match_score > 50 else "red"
        tree.add(f"[bold]Signal Match:[/] [{style}]{match_score:.1f}%[/]")

    if evidence.get("temporal_analysis"):
        temp = evidence["temporal_analysis"]
        temp_branch = tree.add(":stopwatch: [bold]Temporal Analysis[/]")
        temp_branch.add(f"{temp.get('detection_count', 0)} detections in {temp.get('time_window_seconds', 0)}s")
        temp_branch.add(f"Burst interval: {temp.get('burst_interval_ms', 0)}ms")

    if evidence.get("burst_pattern"):
        tree.add(f":chart_increasing: [bold]Pattern:[/] [blue]{evidence['burst_pattern']}[/]")

    if "NFC" in event.get("type", "") or event.get("nfc_correlated", False) or event.get("nfc_tag_id"):
        nfc_branch = tree.add("📶  [bold blue]NFC Activity[/]")
        if event.get("nfc_correlated", False):
            nfc_branch.label = "⚠️  [bold red on white]MULTI-MODAL ATTACK[/]"
            nfc_branch.add("🚨  RF signal correlated with NFC proximity")
        if event.get("nfc_tag_id"):
            nfc_branch.add(f"💳  Tag ID: [cyan]{event['nfc_tag_id']}[/]")
        if event.get("nfc_timestamp"):
            nfc_branch.add(f"🕒  Timestamp: {event['nfc_timestamp']}")
        if event.get("nfc_proximity"):
            nfc_branch.add(f"📯  Proximity: {event['nfc_proximity']} cm")

    if evidence.get("peak_frequencies"):
        peaks = evidence["peak_frequencies"]
        peak_str = ", ".join([f"{p/1e6:.3f}MHz" if p > 1e6 else f"{p/1e3:.1f}kHz" for p in peaks])
        tree.add(f"📡  [bold]Peak Frequencies:[/] [cyan]{peak_str}[/]")
        
    # Add technical evidence details if available
    if technical_evidence:
        tech_branch = tree.add("🔍  [bold yellow]Technical Details[/]")
        
        # Evidence type icons
        evidence_icons = {
            "signal_analysis": "📡",  # antenna
            "packet_capture": "📥",  # inbox
            "frequency_scan": "🎛",  # control knobs
            "cryptographic": "🔑",   # key
            "nfc_correlation": "📶",  # signal
            "timing_analysis": "🕰",  # clock
            "default": "📊"         # chart
        }
        
        # Add technical evidence items with icons and better formatting
        for item in technical_evidence:
            # Get item type and details
            item_type = item.get("type", "Unknown")
            details = item.get("details", {})
            
            # Select appropriate icon
            icon = evidence_icons.get(item_type.lower().replace(" ", "_"), evidence_icons["default"])
            
            # Create branch for this evidence item with icon
            branch = tech_branch.add(f"[bold cyan]{icon} {item_type}")
            
            # Add details as sub-branches with better formatting
            for key, value in details.items():
                formatted_key = key.replace("_", " ").title()
                branch.add(f"[green]{formatted_key}:[/green] [bright_white]{value}[/bright_white]")

    # Return tree centered for better visual alignment
    return Align.center(tree)


def render_signal_metrics(event, console_width=None):
    """
    Renders signal quality visualization with progress bars, indicators, and sparklines.
    
    Args:
        event (dict): The latest event with signal metrics.
        console_width (int, optional): Console width for consistent sizing across screen sizes.
        
    Returns:
        rich.console.Group: Visual representation of signal metrics.
    """
    global rssi_history
    
    if not event or not isinstance(event, dict) or "error" in event:
        return Align.center(Text("No signal data available", style="dim"))
    
    # Check if this is a technical signal event
    technical_types = ["RF", "Jamming", "Replay", "Brute Force", "NFC", "TPMS"]
    is_technical = any(tech in event.get("type", "") for tech in technical_types)
    
    if not is_technical:
        return Align.center(Text("Event does not contain RF signal metrics", style="dim"))
    
    # Extract signal metrics
    rssi = event.get("rssi")
    snr = event.get("snr")
    frequency = event.get("frequency")
    mod_type = event.get("modulation_type", "Unknown")
    burst_count = event.get("burst_count", 0)
    
    # Update RSSI history for sparkline if we have a valid RSSI value
    if isinstance(rssi, (int, float)):
        rssi_history.append(rssi)
    
    # Create frequency text
    freq_text = ""  
    if frequency:
        if frequency > 1000000:  # MHz range
            freq_text = f"{frequency/1000000:.3f} MHz"
        else:
            freq_text = f"{frequency/1000:.1f} kHz"
    
    # Create RSSI progress bar (typically -100 to -20 dBm for RF signals)
    rssi_progress = None
    if isinstance(rssi, (int, float)):
        # Normalize RSSI to 0-100 scale (-100dBm = 0%, -20dBm = 100%)
        rssi_percent = min(100, max(0, (rssi + 100) * 1.25))  # Scale from -100..-20 to 0..100%
        rssi_color = "green" if rssi_percent > 70 else "yellow" if rssi_percent > 30 else "red"
        
        # Create progress bar with fixed width to prevent duplication issues
        # Use a conservative fixed width that works well on all screen sizes
        bar_width = 30  # Fixed width to prevent Rich layout issues
        
        rssi_progress = Progress(
            TextColumn("RSSI:"),
            BarColumn(bar_width=bar_width, style=rssi_color),
            TextColumn("{task.description}"),
            expand=False,  # Prevent expansion that can cause duplication
            disable=False,
            transient=False
        )
        rssi_task = rssi_progress.add_task(f"[{rssi_color}]{rssi} dBm[/]", total=100, completed=rssi_percent)    
    
    # Create SNR progress bar (typically 0 to 30 dB for RF signals)
    snr_progress = None
    if isinstance(snr, (int, float)):
        # Normalize SNR to 0-100 scale (0dB = 0%, 30dB = 100%)
        snr_percent = min(100, max(0, snr * 3.33))  # Scale from 0..30 to 0..100%
        snr_color = "green" if snr_percent > 70 else "yellow" if snr_percent > 30 else "red"
        
        # Create progress bar with consistent width regardless of screen size
        snr_progress = Progress(
            TextColumn("SNR: "),
            BarColumn(bar_width=bar_width, style=snr_color),
            TextColumn("{task.description}"),
            expand=False,  # Prevent expansion that can cause duplication
            disable=False,
            transient=False
        )
        snr_task = snr_progress.add_task(f"[{snr_color}]{snr} dB[/]", total=100, completed=snr_percent)
    
    # Create burst count visualization if available
    burst_viz = None
    if burst_count > 0:
        burst_blocks = "#" * min(burst_count, 20)  # Limit to 20 blocks max, using ASCII hash instead of block
        burst_viz = Text(f"Burst Count: {burst_blocks} ({burst_count})", style="blue")
    
    # Generate RSSI sparkline if we have history
    rssi_sparkline = None
    if len(rssi_history) > 1:
        sparkline = generate_sparkline(list(rssi_history))
        rssi_sparkline = Text()
        rssi_sparkline.append("RSSI Trend: ", style="bold")
        rssi_sparkline.append(sparkline, style="cyan")
        
        # Add min/max indicators
        if rssi_history:
            min_rssi = min(rssi_history)
            max_rssi = max(rssi_history)
            rssi_sparkline.append(f" [{min_rssi}..{max_rssi} dBm]", style="dim")
    
    # Build the metric elements list with available metrics (original approach)
    metric_elements = []
    
    # Add modulation and frequency info
    header_text = Text()
    if mod_type:
        header_text.append("Modulation: ", style="bold")
        header_text.append(f"{mod_type}", style="cyan")
        header_text.append(" | ")
    if freq_text:
        header_text.append("Frequency: ", style="bold")
        header_text.append(f"{freq_text}", style="cyan")
    
    if header_text.plain:  # Only add if there's actual content
        metric_elements.append(Align.center(header_text))
    
    # Add the progress bars and other visualizations if available
    if rssi_progress:
        metric_elements.append(Align.center(rssi_progress))
    if rssi_sparkline:  # Add sparkline visualization after RSSI progress bar
        metric_elements.append(Align.center(rssi_sparkline))
    if snr_progress:
        metric_elements.append(Align.center(snr_progress))
    if burst_viz:
        metric_elements.append(Align.center(burst_viz))
    
    # Add NFC correlation indicator if present
    if event.get("nfc_correlated", False):
        nfc_text = Text("!!! NFC+RF CORRELATION DETECTED !!!", style="bold red")
        metric_elements.append(Align.center(nfc_text))
    
    # Return visualization components as a vertical group to prevent duplication
    # The key fix: Use Group with explicit width constraint to prevent Rich from wrapping
    if not metric_elements:
        return Align.center(Text("No signal data available", style="dim"))
    
    # Calculate a reasonable max width to prevent wrapping issues on larger screens
    max_width = min(80, console_width - 10) if console_width else 70
    
    # Create a constrained group that won't expand beyond reasonable limits
    # Group is already imported at the top of the file
    
    # The key fix: Create a group with fixed width to prevent wrapping and duplication
    # Set a reasonable fixed width that works on all screen sizes
    
    # Add spacing between elements to prevent them from running together
    spaced_elements = []
    for i, element in enumerate(metric_elements):
        spaced_elements.append(element)
        # Add spacing between elements except after the last one
        if i < len(metric_elements) - 1:
            spaced_elements.append(Text(""))  # Empty line for spacing
    
    # Wrap in a panel with fixed width to prevent Rich from making poor layout decisions
    constrained_group = Group(*spaced_elements)
    
    # Return the group directly - let the parent panel handle the sizing
    return constrained_group

def get_signal_summary(event):
    """
    Creates a compact summary of signal details for the dashboard table.
    Foundation for signal analysis display.
    
    Args:
        event (dict): Event data containing signal details
        
    Returns:
        str: Formatted signal summary
    """
    if not isinstance(event, dict):
        return "-"
        
    # Check if we have signal details
    if "modulation_type" not in event and "frequency" not in event and "rssi" not in event:
        return "-"
    
    # Extract key signal parameters
    mod_type = event.get("modulation_type", "")
    freq = event.get("frequency", 0)
    rssi = event.get("rssi", 0)
    snr = event.get("snr", 0)
    
    # Format frequency if present
    freq_str = ""
    if freq:
        if freq > 1000000:  # MHz range
            freq_str = f"{freq/1000000:.1f}MHz"
        else:
            freq_str = f"{freq/1000:.1f}kHz"
    
    # Create compact signal summary
    summary_parts = []
    if mod_type:
        summary_parts.append(f"{mod_type}")
    if freq_str:
        summary_parts.append(freq_str)
    if isinstance(rssi, (int, float)):
        summary_parts.append(f"{rssi:.1f}dBm")
    
    # Check for NFC correlation
    if event.get("nfc_correlated", False):
        return "[bold red]NFC+RF[/] " + "/".join(summary_parts)
    
    return "/".join(summary_parts) if summary_parts else "-"

# --- Main Async Runner ---
async def main():
    """
    Main entrypoint for the CLI dashboard. Parses arguments, selects event source, and runs the dashboard loop.
    Includes event navigation with arrow keys to view historical event evidence.

    Usage:
        python cli_dashboard.py --source tcp --tcp-host localhost --tcp-port 8888
        python cli_dashboard.py --mock
    """
    # Flag to control the main loop
    running = True
    
    # Flag to control auto-follow behavior (automatically show latest event)
    auto_follow = True
    
    # Flag to track if first absolute event was requested (via Home key)
    first_absolute_event_requested = False
    
    parser = argparse.ArgumentParser(description="Automotive Security Enhanced CLI Dashboard")
    parser.add_argument("--source", choices=["api", "tcp"], help="Event source: api or tcp")
    parser.add_argument("--api-url", type=str, default="http://localhost:8000/events", help="API URL (for --source api)")
    parser.add_argument("--tcp-host", type=str, default="localhost", help="TCP event stream host (default: localhost)")
    parser.add_argument("--tcp-port", type=int, default=8888, help="TCP event stream port (default: 8888)")
    parser.add_argument("--mock", action="store_true", help="Enable mock mode to simulate detection events for testing and demo purposes.")
    parser.add_argument("--synthetic", action="store_true", help="Enable synthetic signal generation for advanced testing (requires --mock)")
    parser.add_argument("--detailed", action="store_true", default=True, help="Enable detailed signal analysis (default: True)")
    parser.add_argument("--nfc", action="store_true", default=True, help="Enable NFC correlation detection (default: True)")
    parser.add_argument("--event", type=int, default=-1, help="Select a specific event to view (negative index counts from latest, default: -1 shows latest)")
    args = parser.parse_args()

    # If --mock is set, ignore --source
    if args.mock:
        args.source = None
        
    # Validate that --synthetic is only used with --mock
    if args.synthetic and not args.mock:
        console.print("[bold red]Error:[/] --synthetic flag requires --mock flag. Exiting.", style="bold red")
        return

    # Setup enhanced logging system
    global dashboard_logger
    log_level = "DEBUG" if args.detailed else "INFO"
    dashboard_logger = setup_dashboard_logging(
        log_level=log_level,
        log_name="dashboard",
        console_output=False  # Keep console clean for dashboard UI
    )
    
    # Log startup information
    dashboard_logger.info("CLI Dashboard starting up")
    dashboard_logger.info(f"Arguments: {vars(args)}")
    
    # Display enhanced startup screen with ASCII art, system info, and configuration details
    display_enhanced_startup_screen(args, startup_delay=2.5)

    events = []
    status_text = "Starting..."
    # Track currently selected event index for navigation
    selected_event_idx = -1  # -1 means latest event
    # Flag to track if we should follow the latest event
    follow_latest = False
    # Flag to track help display state
    show_help = False
    # Flag to track landing screen display state
    show_landing = False
    # Current page for pagination
    current_page = 0
    # Timestamp of the last full refresh
    last_full_refresh = time.time()
    # Flag to track if a full refresh is needed
    needs_full_refresh = False
    # Flag to track if first absolute event is requested (for home key)
    first_absolute_event_requested = False
    # Flag to track if professional exit was requested
    exit_requested = False
    # Flag to track if instant exit (Ctrl+C) was requested
    instant_exit_requested = False

    if args.mock:
        # Pass synthetic flag to generate_mock_events
        event_gen = generate_mock_events(synthetic=args.synthetic)
        if args.synthetic:
            status_text = "Source: SYNTHETIC SIGNALS (advanced testing mode)"
            dashboard_logger.info("Using synthetic signal generator with advanced testing features")
        else:
            status_text = "Source: MOCK DATA (demo/testing mode)"
            dashboard_logger.info("Using mock event generator for demo/testing")
    elif args.source == "api":
        event_gen = fetch_events_api(args.api_url)
        status_text = f"Source: API ({args.api_url})"
        dashboard_logger.info(f"Using API event source: {args.api_url}")
    else:
        event_gen = stream_events_tcp(args.tcp_host, args.tcp_port)
        status_text = f"Source: TCP ({args.tcp_host}:{args.tcp_port})"
        dashboard_logger.info(f"Using TCP event source: {args.tcp_host}:{args.tcp_port}")
    
    # Set up prompt_toolkit key bindings for keyboard navigation
    bindings = KeyBindings()
    
    @bindings.add('up')
    def handle_up(event):
        nonlocal selected_event_idx, follow_latest, first_absolute_event_requested
        if not events:
            return
        # Move selection up (earlier in time)
        selected_event_idx -= 1
        # Ensure we don't go out of bounds
        selected_event_idx = max(-len(events), min(-1, selected_event_idx))
        # Disable follow latest when manually navigating
        follow_latest = False
        # Reset the first absolute event flag when using regular navigation
        first_absolute_event_requested = False
        # Log navigation action
        if dashboard_logger:
            log_dashboard_action(dashboard_logger, "navigation", f"Up arrow - selected event index: {selected_event_idx}")
    
    @bindings.add('down')
    def handle_down(event):
        nonlocal selected_event_idx, follow_latest, first_absolute_event_requested
        if not events:
            return
        # Move selection down (later in time)
        if selected_event_idx < -1:
            selected_event_idx += 1
        # Ensure we don't go out of bounds
        selected_event_idx = max(-len(events), min(-1, selected_event_idx))
        # Disable follow latest when manually navigating
        follow_latest = False
        # Reset the first absolute event flag when using regular navigation
        first_absolute_event_requested = False
        # Log navigation action
        if dashboard_logger:
            log_dashboard_action(dashboard_logger, "navigation", f"Down arrow - selected event index: {selected_event_idx}")
    
    @bindings.add('home')
    def handle_home(event):
        nonlocal selected_event_idx, follow_latest, first_absolute_event_requested, current_page
        # Calculate which page contains the first event
        if events:
            current_page = (len(events) - 1) // 10
        if events:
            # Store that we want to view the first event (event 0)
            # We'll use a special flag to indicate we want the first absolute event
            # Rather than setting to a potentially huge negative number
            selected_event_idx = -len(events)  # Start with oldest in buffer
            # Set a flag to indicate we want the first absolute event
            first_absolute_event_requested = True
            # Disable follow latest when manually navigating
            follow_latest = False
            # Log navigation action
            if dashboard_logger:
                log_dashboard_action(dashboard_logger, "navigation", f"Home key - selected event index: {selected_event_idx}")
    
    @bindings.add('end')
    def handle_end(event):
        nonlocal selected_event_idx, follow_latest, first_absolute_event_requested, current_page
        # Reset to first page when jumping to latest event
        current_page = 0
        # Go to latest event and enable follow latest
        selected_event_idx = -1
        follow_latest = True
        # Reset the first absolute event flag
        first_absolute_event_requested = False
        # Log navigation action
        if dashboard_logger:
            log_dashboard_action(dashboard_logger, "navigation", "End key - jumped to latest event (auto-follow enabled)")
    
    @bindings.add('q')
    @bindings.add('Q')
    def handle_quit(event):
        # Set flag to request professional exit (avoid deadlock with Live display)
        nonlocal running, first_absolute_event_requested, exit_requested
        
        # Log quit action
        if dashboard_logger:
            log_dashboard_action(dashboard_logger, "quit", "User initiated dashboard shutdown")
        
        # Set exit request flag - will be handled after Live display closes
        exit_requested = True
        running = False
        first_absolute_event_requested = False
        event.app.exit()
    
    @bindings.add('c-c')  # Ctrl+C - Instant exit
    def handle_instant_exit(event):
        # Instant exit without confirmation dialog
        nonlocal running, first_absolute_event_requested, exit_requested, instant_exit_requested
        
        # Log instant exit action
        if dashboard_logger:
            log_dashboard_action(dashboard_logger, "instant_exit", "User initiated instant shutdown (Ctrl+C)")
        
        # Set flags for instant exit (bypass confirmation)
        exit_requested = True
        instant_exit_requested = True
        running = False
        first_absolute_event_requested = False
        event.app.exit()
    
    @bindings.add('left')
    def handle_previous_page(event):
        nonlocal current_page, selected_event_idx, follow_latest, needs_full_refresh
        if not events:
            return
        # Move to previous page
        current_page = min((len(events) - 1) // MAX_EVENTS_PER_PAGE, current_page + 1)
        # Adjust selected event index to be on the new page
        page_start_idx = max(0, len(events) - (current_page + 1) * MAX_EVENTS_PER_PAGE)
        selected_event_idx = -len(events) + page_start_idx
        # Disable follow latest when manually navigating
        follow_latest = False
        # Set flag to force a full refresh on next update cycle
        needs_full_refresh = True
        # Log navigation action
        if dashboard_logger:
            log_dashboard_action(dashboard_logger, "navigation", f"Left arrow - moved to page {current_page + 1}")

    @bindings.add('right')
    def handle_next_page(event):
        nonlocal current_page, selected_event_idx, follow_latest, needs_full_refresh
        if not events:
            return
        # Move to next page
        current_page = max(0, current_page - 1)
        # Adjust selected event index to be on the new page
        page_start_idx = max(0, len(events) - (current_page + 1) * MAX_EVENTS_PER_PAGE)
        selected_event_idx = -len(events) + page_start_idx
        # Enable follow latest if we're on the first page
        if current_page == 0:
            follow_latest = True
            selected_event_idx = -1
        # Set flag to force a full refresh on next update cycle
        needs_full_refresh = True
        # Log navigation action
        if dashboard_logger:
            log_dashboard_action(dashboard_logger, "navigation", f"Right arrow - moved to page {current_page + 1}")

    @bindings.add('?')
    def handle_help(event):
        nonlocal show_help, first_absolute_event_requested
        # Toggle help display
        show_help = not show_help
        # Reset the first absolute event flag
        first_absolute_event_requested = False
        # Log help action
        if dashboard_logger:
            log_dashboard_action(dashboard_logger, "help_toggle", f"Help display {'enabled' if show_help else 'disabled'}")
    
    @bindings.add('m')
    @bindings.add('M')
    def handle_main_menu(event):
        nonlocal show_landing, first_absolute_event_requested
        # Toggle the landing screen display (different from help)
        show_landing = not show_landing
        # Reset the first absolute event flag
        first_absolute_event_requested = False
        # Log main menu action
        if dashboard_logger:
            log_dashboard_action(dashboard_logger, "landing_screen_toggle", f"Landing screen display {'enabled' if show_landing else 'disabled'}")

    # Create a prompt_toolkit application with a proper layout for keyboard input
    # This ensures key bindings are properly processed
    input_field = Window(height=1, content=FormattedTextControl(
        "[Press Up/Down to navigate, Home/End for first/last event, q to quit]"))
    
    root_container = VSplit([
        input_field,
    ])
    
    app = Application(
        layout=PTLayout(root_container),
        key_bindings=bindings,
        full_screen=False,  # Don't take over the full screen
        mouse_support=True
    )

    async def dashboard_loop():
        """
        Main event loop for the dashboard. Renders events and handles errors/interrupts.
        Implements keyboard navigation system with prompt_toolkit.
        """
        nonlocal selected_event_idx, status_text
        api_error_count = 0
        MAX_API_ERRORS = 5
        
        # Track total events processed, not just buffer size
        total_events_processed = 0
        
        # Use the command-line argument for initial selected event
        selected_event_idx = args.event
        
        # Ensure auto-follow is enabled by default for a better UX
        follow_latest = (selected_event_idx == -1)
        
        # Flag to force a full refresh when page navigation occurs
        needs_full_refresh = False
        
        try:
            
            # Create a single Live display outside the event loop
            # Lower refresh rate and disable auto-refresh to prevent shaking
            with Live(render_dashboard(events, None, status_text, console, selected_event_idx, show_help=show_help, current_page=current_page), 
                      refresh_per_second=2, console=console, screen=True, 
                      vertical_overflow="visible", auto_refresh=False) as live:
                
                # Create async tasks for event fetching and rendering
                
                async def event_fetcher():
                    nonlocal selected_event_idx, follow_latest, total_events_processed, first_absolute_event_requested
                    
                    async for event in event_gen:
                        # Check if we should exit
                        if not running:
                            break
                        
                        log_event(event)
                        # Unpack signal_detection events with nested detections
                        if event.get('type') == 'signal_detection' and 'detections' in event:
                            for detection in event['detections']:
                                # Add timestamp if not present
                                if 'timestamp' not in detection:
                                    detection['timestamp'] = event.get('timestamp', datetime.now().strftime(TIMESTAMP_FORMAT))
                                events.append(detection)
                                if len(events) > 100:
                                    events.pop(0)
                                    # No adjustment needed - negative indices maintain relative position automatically
                        else:
                            # Add timestamp if not present
                            if "timestamp" not in event:
                                event["timestamp"] = datetime.now().strftime(TIMESTAMP_FORMAT)
                            
                            # Enhance with additional signal processing details if missing
                            event = enhance_event_with_signal_details(event)
                                
                            events.append(event)
                            total_events_processed += 1
                            if len(events) > 100:
                                events.pop(0)
                                # No adjustment needed - negative indices maintain relative position automatically
                        
                        # Keep selected_event_idx stable unless explicitly following latest
                        # Don't reset the index when new events arrive - preserve manual selection
                        # Detect repeated API connection errors
                        if event.get("error") and "API connection error" in event["error"]:
                            api_error_count += 1
                            if api_error_count >= MAX_API_ERRORS:
                                console.print(f"[bold red]Unable to connect to API after {MAX_API_ERRORS} attempts. Exiting dashboard.[/bold red]")
                                return
                        else:
                            api_error_count = 0
                
                async def renderer():
                    nonlocal total_events_processed, first_absolute_event_requested, needs_full_refresh, follow_latest, selected_event_idx
                    # Variables to control refresh rates
                    last_full_refresh = time.time()
                    last_status_refresh = time.time()
                    last_performance_log = time.time()
                    
                    # Define different refresh rates (in seconds)
                    FULL_REFRESH_RATE = 1.0  # Slower refresh for evidence trees (1 second)
                    STATUS_REFRESH_RATE = 0.2  # Faster refresh for status updates (200ms)
                    PERFORMANCE_LOG_RATE = 30.0  # Log performance metrics every 30 seconds
                    
                    while running:
                        current_time = time.time()
                        # Determine which event to display in detail panels
                        selected_event = None
                        full_status = status_text
                        
                        if events:
                            # Handle event selection based on user navigation
                            # Ensure selected_event_idx is within valid bounds
                            selected_event_idx = max(-len(events), min(-1, selected_event_idx))
                            
                            # Calculate absolute index
                            abs_idx = len(events) + selected_event_idx
                            
                            # Handle special case for home key (first absolute event)
                            if first_absolute_event_requested:
                                # Show the oldest available event and indicate it's the first absolute event
                                selected_event = events[0]
                                # Add a note to the event that it's representing the first absolute event
                                selected_event = dict(selected_event)  # Make a copy to avoid modifying the original
                                selected_event['details'] = f"[First event (0/{total_events_processed})] {selected_event.get('details', '')}"
                                abs_idx = 0
                            else:
                                # Show the selected event at the current index position
                                selected_event = events[abs_idx]
                            
                            # Update navigation status with absolute event numbers
                            event_num = abs_idx + 1  # Simple 1-based indexing from current events
                            nav_status = f"Event {event_num}/{len(events)}"
                            if selected_event_idx == -1:
                                nav_status += " (Latest)"
                            
                            # Get current time for footer
                            display_time = datetime.now().strftime(TIMESTAMP_FORMAT)
                            
                            # Format event counter with light blue color - use same logic as header
                            # Use len(events) to match header counter and prevent reset on exit cancel
                            current_position = abs_idx + 1  # Simple 1-based indexing
                            event_status = f"[cyan1]Events: {current_position}/{len(events)}"
                            if selected_event_idx == -1:
                                event_status += " (Latest)[/cyan1]"
                            else:
                                event_status += "[/cyan1]"
                            
                            # Format timestamp with light green color
                            time_status = f"[spring_green3]Time: {display_time}[/spring_green3]"
                            
                            # Get accurate threat counter using same logic as header
                            threat_stats = calculate_threat_statistics(events)
                            threats_status = f"[bold red]Threats: {threat_stats['threat_count']}[/bold red]" if threat_stats['threat_count'] > 0 else "[green]No Active Threats[/green]"
                            
                            # Comprehensive status with all elements and colors
                            source_text = "Source: SYNTHETIC SIGNALS (advanced testing)" if args.synthetic else "Source: MOCK DATA (demo/testing mode)"
                            status_parts = [
                                source_text,
                                event_status,
                                threats_status,
                                time_status,
                                "Press ? for help"
                            ]
                            # Filter out empty parts
                            status_parts = [part for part in status_parts if part]
                            full_status = " | ".join(status_parts)
                        
                        # Determine if we should do a full refresh or just update the status bar
                        if needs_full_refresh or current_time - last_full_refresh >= FULL_REFRESH_RATE:
                            # Check if landing screen should be displayed
                            if show_landing:
                                # Display the landing screen content instead of dashboard
                                landing_content = render_landing_screen_content(args)
                                live.update(Panel(landing_content, title="[bold blue]AutoSec Monitor - Landing Screen[/bold blue]", border_style="cyan"))
                            else:
                                # Full refresh including evidence trees and page navigation
                                live.update(render_dashboard(events, selected_event, full_status, console, selected_event_idx, show_help=show_help, current_page=current_page, force_refresh=needs_full_refresh))
                            last_full_refresh = current_time
                            last_status_refresh = current_time
                            # Reset the flag after refresh
                            needs_full_refresh = False
                        elif current_time - last_status_refresh >= STATUS_REFRESH_RATE:
                            # Check if landing screen should be displayed
                            if show_landing:
                                # Display the landing screen content instead of dashboard
                                landing_content = render_landing_screen_content(args)
                                live.update(Panel(landing_content, title="[bold blue]AutoSec Monitor - Landing Screen[/bold blue]", border_style="cyan"))
                            else:
                                # Only update status bar (more frequent)
                                status_only = render_dashboard(events, None if selected_event else None, full_status, console, selected_event_idx, status_only=True, show_help=show_help, current_page=current_page)
                                live.update(status_only)
                            # Force refresh to ensure UI updates properly
                            live.refresh()
                            last_status_refresh = current_time
                        
                        # Log performance metrics periodically
                        if current_time - last_performance_log >= PERFORMANCE_LOG_RATE:
                            performance_monitor = get_performance_monitor()
                            metrics = performance_monitor.get_current_metrics()
                            if dashboard_logger:
                                log_performance_metrics(dashboard_logger, metrics)
                                log_system_health(dashboard_logger, {
                                    'total_events': len(events),
                                    'events_processed': total_events_processed,
                                    'selected_event_idx': selected_event_idx,
                                    'follow_latest': follow_latest,
                                    'show_help': show_help
                                })
                            last_performance_log = current_time
                                
                        # Sleep a small amount to prevent CPU hogging
                        await asyncio.sleep(0.05)
                
                # Create a background task for input handling
                async def input_handler():
                    nonlocal selected_event_idx, auto_follow, running, first_absolute_event_requested
                    while running:
                        # Process a single key press without blocking
                        await app.run_async(pre_run=lambda: asyncio.sleep(0.1))
                        await asyncio.sleep(0.01)  # Small delay to prevent CPU hogging
                
                # Create tasks for event fetching, rendering, and input handling
                fetch_task = asyncio.create_task(event_fetcher())
                render_task = asyncio.create_task(renderer())
                input_task = asyncio.create_task(input_handler())
                
                # Wait for all tasks to complete (or until running=False)
                try:
                    await asyncio.gather(fetch_task, render_task, input_task)
                except asyncio.CancelledError:
                    pass
                finally:
                    # Ensure all tasks are properly cancelled when exiting
                    for task in [fetch_task, render_task, input_task]:
                        if not task.done():
                            task.cancel()
                
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Dashboard interrupted by user (Ctrl+C). Exiting gracefully.[/bold yellow]")
            if dashboard_logger:
                dashboard_logger.warning("Dashboard interrupted by user (Ctrl+C)")
            # Set exit_requested flag for handling after dashboard loop
            exit_requested = True
        except Exception as e:
            console.print(f"\n[bold red]Unexpected error: {e}[/bold red]")
            if dashboard_logger:
                dashboard_logger.error(f"Unexpected error in dashboard: {e}", exc_info=True)
        finally:
            if dashboard_logger:
                dashboard_logger.info("CLI Dashboard shutting down")
                dashboard_logger.info("=" * 60)
    
    # Main dashboard loop with exit handling
    while True:
        await dashboard_loop()
        
        # Handle exit after dashboard loop completes
        if exit_requested:
            try:
                if instant_exit_requested:
                    # Instant exit (Ctrl+C) - bypass confirmation dialog
                    from utils.exit_dialog import ExitDialogManager
                    exit_manager = ExitDialogManager(console, events, dashboard_logger)
                    exit_manager.show_final_goodbye(exported_data=False)  # No export on instant exit
                    break
                else:
                    # Regular exit (q/Q) - show confirmation dialog
                    should_exit = handle_professional_exit(console, events, dashboard_logger)
                    if should_exit:
                        # User confirmed exit - break out of main loop
                        break
                    else:
                        # User cancelled exit - restart dashboard
                        console.print("[green]Returning to dashboard...[/green]")
                        exit_requested = False  # Reset the flag
                        instant_exit_requested = False  # Reset instant exit flag too
                        running = True  # Reset running flag
                        # Brief pause before restarting
                        await asyncio.sleep(1)
                        continue
            except Exception as e:
                console.print(f"[bold red]Error in exit dialog: {e}[/bold red]")
                if dashboard_logger:
                    dashboard_logger.error(f"Error in exit dialog: {e}", exc_info=True)
                break
        else:
            # No exit requested, normal shutdown
            break

# --- Mock Event Generator ---
# --- Detection Adapter Integration ---
from cli_dashboard_detection_adapter import generate_detection_event, generate_synthetic_event

async def generate_mock_events(synthetic=False):
    """
    Async generator that yields simulated detection events for dashboard demo/testing.
    Uses legacy detection logic and hardware mocks for realistic event types and threat levels.
    
    When synthetic flag is True, delegates to the synthetic event generator for advanced
    testing scenarios with realistic signal characteristics.

    Args:
        synthetic (bool): When True, use synthetic event generator with advanced scenarios

    Yields:
        dict: Simulated detection event using detection logic.

    Example:
        async for event in generate_mock_events():
            print(event)
    """
    if synthetic:
        # Delegate to synthetic event generator for advanced testing
        async for event in generate_synthetic_event():
            yield event
    else:
        # Use standard mock event generation
        while True:
            await asyncio.sleep(1.5)
            event = generate_detection_event()
            yield event

# Synthetic event generation has been moved to cli_dashboard_detection_adapter.py
# and is now accessed through the generate_mock_events function with synthetic=True

def enhance_event_with_signal_details(event):
    """
    Enhances event with additional signal processing details if they're missing.
    Implementation for NFC correlation and event enrichment.
    
    Args:
        event (dict): The event to enhance
        
    Returns:
        dict: Enhanced event with additional signal details
    """
    # Skip error events
    if not isinstance(event, dict) or "error" in event:
        return event
    
    # If not a technical event type, skip enhancement
    technical_types = ["RF", "Jamming", "Replay", "Brute Force", "NFC", "TPMS", "signal_detection"]
    is_technical = any(tech in event.get("type", "") for tech in technical_types)
    
    if not is_technical:
        return event
        
    # Only add if not already present
    enhanced = dict(event)
    
    # For NFC events or correlated events, enhance with NFC data
    if "NFC" in enhanced.get("type", "") or enhanced.get("nfc_correlated", False):
        if "nfc_tag_id" not in enhanced and "NFC" in enhanced.get("type", ""):
            import random
            # Generate a mock NFC tag ID for NFC events if not present
            enhanced["nfc_tag_id"] = f"TAG_{random.randint(10000, 99999)}"
            
        # For correlated attacks, ensure the correlation flag is set
        if enhanced.get("threat", "") in ["Malicious", "Suspicious"] and random.random() < 0.4:
            enhanced["nfc_correlated"] = True
            # Update threat level for correlated attacks
            enhanced["threat"] = "Critical"
    
    # Add indicators to highlight NFC correlation in the dashboard
    if enhanced.get("nfc_correlated", False):
        # Add visual indicators for correlation
        enhanced["details"] = f"[bold red]!!! [/] {enhanced.get('details', 'Multi-modal attack detected')}"
        
        # Add proximity information if not present (for demo purposes)
        if "nfc_proximity" not in enhanced:
            import random
            enhanced["nfc_proximity"] = round(random.uniform(0.5, 10.0), 1)  # cm
    
    return enhanced


def flatten_detection(event, detection):
    """Flatten detection dict for dashboard row."""
    flat = {
        "Time": event.get("timestamp", ""),
        "Type": detection.get("signal_type", detection.get("event_type", "unknown")),
        "Threat": detection.get("threat_level", "-"),
        "Source": event.get("source", "-"),
        "Details": detection.get("burst_pattern", detection.get("details", "-")),
        "Signal": f"{detection.get('modulation_type', '-')}/{detection.get('power_db', '-')}dBm",
        "Power": detection.get("power_db", "-"),
        "PeakCount": detection.get("peak_count", "-"),
        "Signal Quality": f"[green]{detection.get('signal_quality', '-'):.1f}[/green]" if detection.get("signal_quality", "-") > 0.5 else f"[red]{detection.get('signal_quality', '-'):.1f}[/red]",
        "Signal Strength": f"[green]{detection.get('signal_strength', '-'):.1f}[/green]" if detection.get("signal_strength", "-") > 0.5 else f"[red]{detection.get('signal_strength', '-'):.1f}[/red]",
        # NFC correlation information
        "NFC": "",
    }
    
    # Add NFC correlation indicator
    if event.get("nfc_correlated", False):
        flat["NFC"] = "!!!"
        flat["Threat"] = "Critical"  # Upgrade threat level for correlated attacks
    elif "NFC" in flat["Type"]:
        flat["NFC"] = "*"
    
    return flat

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDashboard stopped. Exiting.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
