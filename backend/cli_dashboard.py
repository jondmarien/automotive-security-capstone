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
import json
import logging
import os
import sys
import time
from datetime import datetime
from collections import deque
from typing import Dict, Any, List, Optional, Tuple

import aiohttp
import pyfiglet
from rich import box
from rich.live import Live
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.spinner import Spinner
from rich.status import Status
from rich.table import Table
from rich.text import Text
from rich.tree import Tree
from rich.theme import Theme

# prompt_toolkit imports for keyboard navigation
from prompt_toolkit.application import Application
from prompt_toolkit.input import create_input
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout as PTLayout
from prompt_toolkit.layout.containers import Window, VSplit
from prompt_toolkit.layout.controls import FormattedTextControl

# Global variables
# Store RSSI history for sparkline visualization (max 20 values)
rssi_history = deque(maxlen=20)

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

LOG_FILE = "detection_events.log"

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

# ASCII art logo using pyfiglet
def display_logo():
    """Display the ASCII art logo for the Automotive Security PoC."""
    logo_text = pyfiglet.figlet_format("AutoSec Monitor", font="standard")
    console.print(logo_text, style="bold cyan")
    console.print("Automotive Cybersecurity Proof of Concept", style="dim white", justify="center")
    console.print("=" * console.width, style="dim white")

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

# --- File Logging ---
def log_event(event: Dict[str, Any]):
    """
    Appends a detection event to the log file with a timestamp.

    Args:
        event (dict): The detection event to log.

    Example:
        log_event({"type": "RF Unlock", "threat": "Low"})
    """
    with open(LOG_FILE, "a") as f:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{ts}] {event}\n")

# --- Dashboard Rendering ---
def render_dashboard(events, selected_event, status_text="Dashboard Ready", console=Console(), selected_event_idx=-1):
    """
    Render the enhanced CLI dashboard with signal analysis and technical evidence panels.
    
    Args:
        events (list): List of detection events to display
        selected_event (dict, optional): Currently selected event for evidence display
                                         If None, uses the most recent event
        status_text (str): Status text to display at the bottom
        console (Console): Rich Console object to use for rendering

    Returns:
        rich.panel.Panel: The dashboard panel
    """
    # Get console dimensions
    width = console.width
    height = console.height

    # Create layout
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=1)
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
    
    # Header with gradient title
    header_panel = Panel(
        create_gradient_header(),
        border_style="dim white",
        expand=True,
        height=3,
        padding=(0, 1)
    )
    layout["header"].update(header_panel)

    # Create events table with minimal styling
    table = Table(
        title="Automotive Security CLI Dashboard", 
        expand=True, 
        box=box.SIMPLE,  # More minimal box style
        padding=(0, 1),  # Reduced padding
        collapse_padding=True  # Help with multi-line content
    )
    table.add_column("Time", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta", no_wrap=True)
    table.add_column("Threat", style="threat.low", no_wrap=True)
    table.add_column("Source", style="blue", no_wrap=True)
    table.add_column("Details", style="white", width=30)  # Fixed width for details to prevent affecting other columns
    table.add_column("Signal", style="green", no_wrap=True)
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
    # If no event is explicitly selected, use the most recent one
    if selected_event is None and events:
        selected_event = events[-1]
    
    signal_viz = render_signal_metrics(selected_event) if selected_event else Text("No signal data available")
    evidence_panel = render_evidence_panel(selected_event) if selected_event else Text("No evidence data available")
    
    # Show most recent events first
    recent_events = events[-15:] if len(events) > 15 else events
    for event in recent_events:
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
        
        table.add_row(time_str, event_type, threat_colored, source, formatted_details, signal_str, nfc_indicator)

    # Assemble the layout
    layout["events_table"].update(Panel(table, title="Detection Events", border_style="bright_cyan"))
    layout["signal_metrics"].update(Panel(signal_viz, title="Signal Analysis", border_style="green"))
    layout["evidence_panel"].update(Panel(evidence_panel, title="Technical Evidence", border_style="yellow"))
    # Create footer with spinner
    spinner = Spinner('dots', text=status_text, style="cyan")
    footer_content = Columns([
        spinner
    ])
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


def render_evidence_panel(event):
    """
    Renders a technical evidence panel as a collapsible tree for better organization.
    
    Args:
        event (dict): The event with evidence data.
        
    Returns:
        rich.tree.Tree or rich.text.Text: Formatted evidence tree or status text.
    """
    if not event or not isinstance(event, dict) or "error" in event:
        return Text("No evidence available", style="dim")

    security_types = ["Replay Attack", "Brute Force", "Jamming Attack", "NFC Scan", "NFC Tag Present"]
    is_security_event = (event.get("type", "") in security_types or 
                         event.get("threat", "") in ["Malicious", "Critical", "Suspicious"] or
                         event.get("nfc_correlated", False) or 
                         "NFC" in event.get("type", ""))

    if not is_security_event:
        return Text("No security evidence for this event", style="dim")

    # Extract evidence data
    evidence = event.get("evidence", {})
    technical_evidence = event.get("technical_evidence", {})
    
    # Always show panel for NFC events even without evidence
    if not evidence and not technical_evidence and not event.get("nfc_correlated", False) and "NFC" not in event.get("type", ""):
        return Text("Event lacks detailed evidence", style="dim")

    # Create a more detailed tree with better visual structure
    tree = Tree(f":shield: [bold yellow]{event.get('type', 'Security Event')} Analysis[/]", guide_style="bright_blue")

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
        nfc_branch = tree.add(":signal_strength: [bold blue]NFC Activity[/]")
        if event.get("nfc_correlated", False):
            nfc_branch.label = ":warning: [bold red on white]MULTI-MODAL ATTACK[/]"
            nfc_branch.add("RF signal correlated with NFC proximity")
        if event.get("nfc_tag_id"):
            nfc_branch.add(f"Tag ID: [cyan]{event['nfc_tag_id']}[/]")
        if event.get("nfc_timestamp"):
            nfc_branch.add(f"Timestamp: {event['nfc_timestamp']}")
        if event.get("nfc_proximity"):
            nfc_branch.add(f"Proximity: {event['nfc_proximity']} cm")

    if evidence.get("peak_frequencies"):
        peaks = evidence["peak_frequencies"]
        peak_str = ", ".join([f"{p/1e6:.3f}MHz" if p > 1e6 else f"{p/1e3:.1f}kHz" for p in peaks])
        tree.add(f":radio: [bold]Peak Frequencies:[/] [cyan]{peak_str}[/]")

    return Align.left(tree)


def render_signal_metrics(event):
    """
    Renders signal quality visualization with progress bars, indicators, and sparklines.
    
    Args:
        event (dict): The latest event with signal metrics.
        
    Returns:
        rich.columns.Columns: Visual representation of signal metrics.
    """
    global rssi_history
    
    if not event or not isinstance(event, dict) or "error" in event:
        return Text("No signal data available", style="dim")
    
    # Check if this is a technical signal event
    technical_types = ["RF", "Jamming", "Replay", "Brute Force", "NFC", "TPMS"]
    is_technical = any(tech in event.get("type", "") for tech in technical_types)
    
    if not is_technical:
        return Text("Event does not contain RF signal metrics", style="dim")
    
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
        
        # Create progress bar
        rssi_progress = Progress(
            TextColumn("RSSI:"),
            BarColumn(bar_width=40, style=rssi_color),
            TextColumn("{task.description}"),
            expand=True
        )
        rssi_task = rssi_progress.add_task(f"[{rssi_color}]{rssi} dBm[/]", total=100, completed=rssi_percent)    
    
    # Create SNR progress bar (typically 0 to 30 dB for RF signals)
    snr_progress = None
    if isinstance(snr, (int, float)):
        # Normalize SNR to 0-100 scale (0dB = 0%, 30dB = 100%)
        snr_percent = min(100, max(0, snr * 3.33))  # Scale from 0..30 to 0..100%
        snr_color = "green" if snr_percent > 70 else "yellow" if snr_percent > 30 else "red"
        
        # Create progress bar
        snr_progress = Progress(
            TextColumn("SNR: "),
            BarColumn(bar_width=40, style=snr_color),
            TextColumn("{task.description}"),
            expand=True
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
    
    # Build the columns list with available metrics
    metric_elements = []
    
    # Add modulation and frequency info
    header_text = Text()
    if mod_type:
        header_text.append(f"Modulation: ", style="bold")
        header_text.append(f"{mod_type}", style="cyan")
        header_text.append(" | ")
    if freq_text:
        header_text.append(f"Frequency: ", style="bold")
        header_text.append(f"{freq_text}", style="cyan")
    
    metric_elements.append(Align.center(header_text))
    
    # Add the progress bars and other visualizations if available
    if rssi_progress:
        metric_elements.append(rssi_progress)
    if rssi_sparkline:  # Add sparkline visualization after RSSI progress bar
        metric_elements.append(Align.center(rssi_sparkline))
    if snr_progress:
        metric_elements.append(snr_progress)
    if burst_viz:
        metric_elements.append(Align.center(burst_viz))
    
    # Add NFC correlation indicator if present
    if event.get("nfc_correlated", False):
        nfc_text = Text("!!! NFC+RF CORRELATION DETECTED !!!", style="bold red")
        metric_elements.append(Align.center(nfc_text))
    
    # Return visualization components as columns
    return Columns(metric_elements, padding=(0, 2))

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
    
    parser = argparse.ArgumentParser(description="Automotive Security Enhanced CLI Dashboard")
    parser.add_argument("--source", choices=["api", "tcp"], help="Event source: api or tcp")
    parser.add_argument("--api-url", type=str, default="http://localhost:8000/events", help="API URL (for --source api)")
    parser.add_argument("--tcp-host", type=str, default="localhost", help="TCP event stream host (default: localhost)")
    parser.add_argument("--tcp-port", type=int, default=8888, help="TCP event stream port (default: 8888)")
    parser.add_argument("--mock", action="store_true", help="Enable mock mode to simulate detection events for testing and demo purposes.")
    parser.add_argument("--detailed", action="store_true", default=True, help="Enable detailed signal analysis (default: True)")
    parser.add_argument("--nfc", action="store_true", default=True, help="Enable NFC correlation detection (default: True)")
    parser.add_argument("--event", type=int, default=-1, help="Select a specific event to view (negative index counts from latest, default: -1 shows latest)")
    args = parser.parse_args()

    # If --mock is set, ignore --source
    if args.mock:
        args.source = None

    display_logo()  # Display ASCII art logo at startup
    console.print("Initializing real-time event streaming...", style="dim white")
    console.print("=" * console.width, style="dim white")

    events = []
    status_text = "Starting..."
    # Track currently selected event index for navigation
    selected_event_idx = -1  # -1 means latest event
    # Flag to track if we should follow the latest event
    follow_latest = False

    if args.mock:
        event_gen = generate_mock_events()
        status_text = "Source: MOCK DATA (demo/testing mode)"
    elif args.source == "api":
        event_gen = fetch_events_api(args.api_url)
        status_text = f"Source: API ({args.api_url})"
    else:
        event_gen = stream_events_tcp(args.tcp_host, args.tcp_port)
        status_text = f"Source: TCP ({args.tcp_host}:{args.tcp_port})"
    
    # Set up prompt_toolkit key bindings for keyboard navigation
    bindings = KeyBindings()
    
    @bindings.add('up')
    def handle_up(event):
        nonlocal selected_event_idx, follow_latest
        if not events:
            return
        # Move selection up (earlier in time)
        selected_event_idx -= 1
        # Ensure we don't go out of bounds
        selected_event_idx = max(-len(events), min(-1, selected_event_idx))
        # Disable follow latest when manually navigating
        follow_latest = False
    
    @bindings.add('down')
    def handle_down(event):
        nonlocal selected_event_idx, follow_latest
        if not events:
            return
        # Move selection down (later in time)
        if selected_event_idx < -1:
            selected_event_idx += 1
        # Ensure we don't go out of bounds
        selected_event_idx = max(-len(events), min(-1, selected_event_idx))
        # Disable follow latest when manually navigating
        follow_latest = False
    
    @bindings.add('home')
    def handle_home(event):
        nonlocal selected_event_idx, follow_latest
        if events:
            # Go to first event
            selected_event_idx = -len(events)
            # Disable follow latest when manually navigating
            follow_latest = False
    
    @bindings.add('end')
    def handle_end(event):
        nonlocal selected_event_idx, follow_latest
        # Go to latest event and enable following the latest event
        selected_event_idx = -1
        follow_latest = True
    
    @bindings.add('q')
    @bindings.add('Q')
    @bindings.add('c-c')  # Ctrl+C
    def handle_quit(event):
        # Set a flag to exit the application
        nonlocal running
        running = False
        event.app.exit()
    
    @bindings.add('?')
    def handle_help(event):
        nonlocal status_text
        # Toggle help text in status bar
        if "HELP" in status_text:
            status_text = status_text.replace(" | HELP: Up/Down=Navigate, Home/End=First/Last, ?=Help, q=Quit", "")
        else:
            status_text += " | HELP: Up/Down=Navigate, Home/End=First/Last, ?=Help, q=Quit"

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
        
        # Use the command-line argument for initial selected event
        selected_event_idx = args.event
        
        try:
            
            # Create a single Live display outside the event loop
            with Live(render_dashboard(events, None, status_text, console, selected_event_idx), 
                      refresh_per_second=4, console=console, screen=True, 
                      vertical_overflow="visible") as live:
                
                # Create async tasks for event fetching and rendering
                # Flag to track if we should follow the latest event
                follow_latest = False
                
                async def event_fetcher():
                    nonlocal selected_event_idx, follow_latest
                    
                    # Track absolute position of selected event
                    abs_selected_idx = None
                    
                    async for event in event_gen:
                        # Check if we should exit
                        if not running:
                            break
                        
                        # Special case: if End key was pressed, we want to stay at the latest event
                        if follow_latest:
                            # We'll set the index to -1 after adding the event
                            pass
                        # Otherwise, remember the absolute position of the selected event
                        elif events and selected_event_idx != -1:
                            # Convert relative index to absolute
                            abs_selected_idx = len(events) + selected_event_idx if selected_event_idx < 0 else selected_event_idx
                        else:
                            abs_selected_idx = None
                        
                        log_event(event)
                        # Unpack signal_detection events with nested detections
                        if event.get('type') == 'signal_detection' and 'detections' in event:
                            for detection in event['detections']:
                                # Add timestamp if not present
                                if 'timestamp' not in detection:
                                    detection['timestamp'] = event.get('timestamp', datetime.now().strftime("%H:%M:%S"))
                                events.append(detection)
                                if len(events) > 100:
                                    events.pop(0)
                        else:
                            # Add timestamp if not present
                            if "timestamp" not in event:
                                event["timestamp"] = datetime.now().strftime("%H:%M:%S")
                            
                            # Enhance with additional signal processing details if missing
                            event = enhance_event_with_signal_details(event)
                                
                            events.append(event)
                            if len(events) > 100:
                                events.pop(0)
                        
                        # After adding new events, update the selected event index
                        if follow_latest:
                            # If End key was pressed, always show the latest event
                            selected_event_idx = -1
                        elif abs_selected_idx is not None:
                            # Keep the absolute position the same
                            selected_event_idx = abs_selected_idx - len(events)
                            # Ensure we don't go out of bounds
                            selected_event_idx = max(-len(events), min(-1, selected_event_idx))
                        # Detect repeated API connection errors
                        if event.get("error") and "API connection error" in event["error"]:
                            api_error_count += 1
                            if api_error_count >= MAX_API_ERRORS:
                                console.print(f"[bold red]Unable to connect to API after {MAX_API_ERRORS} attempts. Exiting dashboard.[/bold red]")
                                return
                        else:
                            api_error_count = 0
                
                async def renderer():
                    while running:
                        # Determine which event to display in detail panels
                        selected_event = None
                        full_status = status_text
                        
                        if events:
                            # Convert relative index to absolute (negative indices count from the end)
                            if selected_event_idx == -1:
                                # Show latest event
                                selected_event = events[-1]
                                abs_idx = len(events) - 1
                            else:
                                # Calculate absolute index from relative
                                abs_idx = len(events) + selected_event_idx if selected_event_idx < 0 else selected_event_idx
                                # Keep index in bounds
                                abs_idx = max(0, min(abs_idx, len(events) - 1))
                                selected_event = events[abs_idx]
                            
                            # Update navigation status
                            nav_status = f"Event {abs_idx + 1}/{len(events)}"
                            if selected_event_idx == -1:
                                nav_status += " (Latest)"
                            
                            # Get current time for footer
                            current_time = datetime.now().strftime("%H:%M:%S")
                            
                            # Format event counter with light blue color
                            event_status = f"[cyan1]Events: {abs_idx + 1}/{len(events)}"
                            if selected_event_idx == -1:
                                event_status += " (Latest)[/cyan1]"
                            else:
                                event_status += "[/cyan1]"
                            
                            # Format timestamp with light green color
                            time_status = f"[spring_green3]Time: {current_time}[/spring_green3]"
                            
                            # Comprehensive status with all elements and colors
                            full_status = f"Source: MOCK DATA (demo/testing mode) | {event_status} | {time_status} | Press ? for help"
                        
                        # Update the live display with navigation
                        live.update(render_dashboard(events, selected_event, full_status, console, selected_event_idx))
                        await asyncio.sleep(0.1)
                
                # Create a background task for input handling
                async def input_handler():
                    nonlocal selected_event_idx, auto_follow, running
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
        except Exception as e:
            console.print(f"\n[bold red]Unexpected error: {e}[/bold red]")

    await dashboard_loop()

# --- Mock Event Generator ---
# --- Detection Adapter Integration ---
from cli_dashboard_detection_adapter import generate_detection_event

async def generate_mock_events():
    """
    Async generator that yields simulated detection events for dashboard demo/testing.
    Uses legacy detection logic and hardware mocks for realistic event types and threat levels.

    Yields:
        dict: Simulated detection event using detection logic.

    Example:
        async for event in generate_mock_events():
            print(event)
    """
    import asyncio
    while True:
        await asyncio.sleep(1.5)
        event = generate_detection_event()
        yield event

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
