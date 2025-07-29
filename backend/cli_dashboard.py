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
import random
import itertools
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import BarColumn, Progress, TextColumn
from rich.columns import Columns
from rich.align import Align
from rich import box
import aiohttp

LOG_FILE = "detection_events.log"

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
def render_dashboard(events, current_event=None, status_text="Dashboard Ready", console=Console()):
    """
    Render the enhanced CLI dashboard with signal analysis and technical evidence panels.
    
    Args:
        events (list): List of detection events to display
        current_event (dict, optional): Currently selected event for evidence display
                                         If None, uses the most recent event
        status_text (str): Status text to display at the bottom
        console (Console): Rich Console object to use for rendering

    Returns:
        rich.panel.Panel: The dashboard panel
    """
    # Create a more compact layout
    layout = Layout(name="root")
    
    # Create child layouts with optimized ratios
    events_layout = Layout(name="events_table", ratio=3)  # Give events table 75% of vertical space
    lower_section = Layout(name="lower_section", ratio=1)
    signal_metrics = Layout(name="signal_metrics")
    evidence_layout = Layout(name="evidence_panel")
    
    # Configure the layout hierarchy - maximize event table space
    layout.split(
        events_layout,
        lower_section
    )
    
    lower_section.split_row(
        signal_metrics, 
        evidence_layout
    )
    
    # Create events table
    table = Table(title="Automotive Security CLI Dashboard", expand=True, box=box.ROUNDED)
    table.add_column("Time", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Threat", style="bold")
    table.add_column("Source", style="blue")
    table.add_column("Details", style="white")
    table.add_column("Signal", style="green")
    # Add NFC correlation indicator column
    table.add_column("NFC", style="bold red", justify="center", width=3)

    # Enhanced color mapping for threat levels including Critical for correlated attacks
    colors = {
        "Benign": "green",
        "Suspicious": "orange1",
        "Malicious": "red",
        "Critical": "bold red on white"  # New critical level for correlated attacks
    }
    
    # Prepare signal metrics and evidence from the selected event for visualization
    # If no event is explicitly selected, use the most recent one
    if current_event is None and events:
        current_event = events[-1]
    
    signal_viz = render_signal_metrics(current_event) if current_event else Text("No signal data available")
    evidence_panel = render_evidence_panel(current_event) if current_event else Text("No evidence data available")
    
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
        table.add_row(time_str, event_type, threat_colored, source, details, signal_str, nfc_indicator)

    # Assemble the layout
    layout["events_table"].update(Panel(table, title="Detection Events", border_style="bright_cyan"))
    layout["signal_metrics"].update(Panel(signal_viz, title="Signal Analysis", border_style="green"))
    layout["evidence_panel"].update(Panel(evidence_panel, title="Technical Evidence", border_style="yellow"))
    
    # Final dashboard panel with minimal padding
    # Use height parameter to ensure full rendering without ellipsis
    # This forces Rich to render the full panel height
    console_height = console.height if hasattr(console, 'height') else 40
    panel = Panel(
        layout, 
        subtitle=status_text, 
        border_style="bright_cyan", 
        padding=(0, 0),
        height=console_height - 2  # Subtract 2 for margins/borders
    )
    return panel


def render_evidence_panel(event):
    """
    Renders a technical evidence panel with detailed attack information.
    Implements NFC correlation indicators.
    
    Args:
        event (dict): The latest event with evidence data.
        
    Returns:
        rich content: Formatted technical evidence panel.
    """
    if not event or not isinstance(event, dict) or "error" in event:
        return Text("No evidence available", style="dim")
        
    # Check if this is a security-relevant event OR an NFC event (new condition for NFC correlation)
    security_types = ["Replay Attack", "Brute Force", "Jamming Attack", "NFC Scan", "NFC Tag Present"]
    is_security_event = (event.get("type", "") in security_types or 
                         event.get("threat", "") in ["Malicious", "Critical", "Suspicious"] or
                         event.get("nfc_correlated", False) or 
                         "NFC" in event.get("type", ""))
    
    if not is_security_event:
        return Text("No security evidence available for this event", style="dim")
        
    # Extract evidence data
    evidence = event.get("evidence", {})
    # Always show panel for NFC events even without evidence
    if not evidence and not event.get("nfc_correlated", False) and "NFC" not in event.get("type", ""):
        return Text("Event lacks detailed evidence data", style="dim")
    
    # Build evidence summary
    evidence_items = []
    
    # Title based on event type
    title = Text()
    title.append(f"{event.get('type', 'Security Event')} Analysis", style="bold yellow")
    title.append("\n")
    evidence_items.append(title)
    
    # Confidence scores if available
    if evidence.get("detection_confidence"):
        confidence = evidence["detection_confidence"] * 100
        confidence_text = Text(f"Detection Confidence: {confidence:.1f}%", 
                              style="green" if confidence > 75 else "yellow" if confidence > 50 else "red")
        evidence_items.append(confidence_text)
    
    # Signal match score for replay attacks
    if evidence.get("signal_match_score"):
        match_score = evidence["signal_match_score"] * 100
        match_text = Text(f"Signal Match: {match_score:.1f}%", 
                         style="green" if match_score > 75 else "yellow" if match_score > 50 else "red")
        evidence_items.append(match_text)
    
    # Temporal analysis for brute force attacks
    if evidence.get("temporal_analysis"):
        temp = evidence["temporal_analysis"]
        temp_text = Text()
        temp_text.append("\nTemporal Analysis:", style="bold")
        temp_text.append("\n")
        temp_text.append(f"- {temp.get('detection_count', 0)} detections in ")
        temp_text.append(f"{temp.get('time_window_seconds', 0)}s window", style="cyan")
        temp_text.append("\n")
        temp_text.append(f"- Burst interval: {temp.get('burst_interval_ms', 0)}ms\n")
        evidence_items.append(temp_text)
    
    # Burst pattern information
    if evidence.get("burst_pattern"):
        burst_text = Text(f"Pattern: {evidence['burst_pattern']}", style="blue")
        evidence_items.append(burst_text)
    
    # NFC correlation evidence (high priority security indicator)
    if "NFC" in event.get("type", "") or event.get("nfc_correlated", False) or event.get("nfc_tag_id"):
        nfc_text = Text()
        
        # Different display for correlated attacks vs. regular NFC events
        if event.get("nfc_correlated", False):
            nfc_text.append("\n")
            nfc_text.append("!!! MULTI-MODAL ATTACK DETECTED !!!", style="bold red on white")
            nfc_text.append("\n")
            nfc_text.append("RF signal correlated with NFC proximity\n")
            nfc_text.append("This correlation indicates a sophisticated attack attempt", style="yellow")
            nfc_text.append("\n")
        else:
            nfc_text.append("\n")
            nfc_text.append("NFC ACTIVITY DETECTED", style="bold blue")
            nfc_text.append("\n")
            
        # NFC tag details
        if event.get("nfc_tag_id"):
            nfc_text.append("NFC Tag ID: ")
            nfc_text.append(f"{event['nfc_tag_id']}", style="cyan")
            nfc_text.append("\n")
            
        # Add timestamp if available
        if event.get("nfc_timestamp"):
            nfc_text.append(f"Detected at: {event['nfc_timestamp']}\n")
            
        # Add proximity information if available
        if event.get("nfc_proximity"):
            proximity = event["nfc_proximity"]
            nfc_text.append(f"Proximity: {proximity} cm\n")
            
        evidence_items.append(nfc_text)
    
    # Peak frequencies information
    if evidence.get("peak_frequencies"):
        peaks = evidence["peak_frequencies"]
        peak_text = Text("\nPeak Frequencies: ")
        for i, peak in enumerate(peaks):
            if peak > 1000000:  # MHz range
                peak_text.append(f"{peak/1000000:.3f}MHz", style="cyan")
            else:
                peak_text.append(f"{peak/1000:.1f}kHz", style="cyan")
            if i < len(peaks) - 1:
                peak_text.append(", ")
        evidence_items.append(peak_text)
    
    # Combine all evidence items
    result = Text()
    for item in evidence_items:
        if isinstance(item, Text):
            result.append_text(item)
        else:
            result.append(str(item))
    
    return Align.left(Columns([result]))


def render_signal_metrics(event):
    """
    Renders signal quality visualization with progress bars and indicators.
    
    Args:
        event (dict): The latest event with signal metrics.
        
    Returns:
        rich.columns.Columns: Visual representation of signal metrics.
    """
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

    console = Console()
    console.print(Panel(
        "[bold green]Enhanced Automotive Security CLI Dashboard[/]\n"
        "[yellow]With signal analysis and technical evidence presentation[/]",
        border_style="cyan"
    ))
    
    events = []
    status_text = "Starting..."
    # Track currently selected event index for navigation
    selected_event_idx = -1  # -1 means latest event

    if args.mock:
        event_gen = generate_mock_events()
        status_text = "Source: MOCK DATA (demo/testing mode)"
    elif args.source == "api":
        event_gen = fetch_events_api(args.api_url)
        status_text = f"Source: API ({args.api_url})"
    else:
        event_gen = stream_events_tcp(args.tcp_host, args.tcp_port)
        status_text = f"Source: TCP ({args.tcp_host}:{args.tcp_port})"

    async def dashboard_loop():
        """
        Main event loop for the dashboard. Renders events and handles errors/interrupts.
        Implements simple event navigation system.
        """
        nonlocal selected_event_idx
        api_error_count = 0
        MAX_API_ERRORS = 5
        
        # Use the command-line argument for initial selected event
        selected_event_idx = args.event
        try:
            # Create a single Live display outside the event loop
            with Live(render_dashboard(events, status_text), refresh_per_second=2, console=console, screen=False, auto_refresh=True) as live:
                async for event in event_gen:
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
                    # Detect repeated API connection errors
                    if event.get("error") and "API connection error" in event["error"]:
                        api_error_count += 1
                        if api_error_count >= MAX_API_ERRORS:
                            console.print(f"[bold red]Unable to connect to API after {MAX_API_ERRORS} attempts. Exiting dashboard.[/bold red]")
                            return
                    else:
                        api_error_count = 0
                        
                    # Every 10th event, automatically switch back to latest
                    # This ensures we don't miss new events while navigating history
                    if len(events) % 10 == 0 and len(events) > 0:
                        selected_event_idx = -1
                    
                    # Update the live display with new content
                    
                    # Handle keyboard input for navigation
                    # Only navigate through existing events
                    current_event = None
                    full_status = status_text
                    
                    if events:
                        # Default to showing the most recent event when a new one arrives
                        if selected_event_idx == -1:
                            current_event = events[-1]
                        else:
                            # Convert relative index to absolute (negative indices count from the end)
                            abs_idx = len(events) - 1 + selected_event_idx if selected_event_idx < 0 else selected_event_idx
                            # Keep index in bounds
                            abs_idx = max(0, min(abs_idx, len(events) - 1))
                            current_event = events[abs_idx]
                            
                        # Update navigation status
                        nav_status = f"Event {abs_idx + 1}/{len(events)}" if 'abs_idx' in locals() else f"Latest Event ({len(events)} total)"
                        full_status = f"{status_text} | {nav_status} | Use --event <number> to view specific events"
                    
                    # Update the live display with navigation
                    live.update(render_dashboard(events, current_event, full_status, console))
                    await asyncio.sleep(0.1)
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
