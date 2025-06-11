"""
cli_dashboard.py

A Rich-based CLI dashboard for real-time monitoring of automotive RF detection events.
Supports backend API polling, direct TCP/local stream, or mock data as event sources.
Detection events are also logged to a local file ('detection_events.log').

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
from typing import Dict, Any

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
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
def render_dashboard(events, status_text):
    """
    Renders the dashboard table and status panel using Rich.

    Args:
        events (list): List of detection event dicts.
        status_text (str): Status string for the dashboard subtitle.

    Returns:
        Panel: A Rich Panel object containing the event table.

    Example:
        panel = render_dashboard(events, "Source: MOCK DATA")
        console.print(panel)
    """
    table = Table(title="Automotive Security CLI Dashboard", expand=True)
    table.add_column("Time", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Threat", style="bold")
    table.add_column("Source", style="blue")
    table.add_column("Details", style="white")

    # Color mapping for threat levels
    colors = {"Low": "green", "Medium": "yellow", "High": "red", "Critical": "bold red"}

    for event in events[-15:]:
        time_str = event.get("time") or event.get("timestamp", "-")
        event_type = event.get("type", "-")
        threat = event.get("threat", "-")
        source = event.get("source", "-")
        details = event.get("details", "-")
        # Apply color to threat level
        threat_colored = f"[{colors.get(threat, 'white')}]" + threat + "[/]"
        table.add_row(time_str, event_type, threat_colored, source, details)

    panel = Panel(table, title="Detection Events", subtitle=status_text, border_style="bright_cyan")
    return panel

# --- Main Async Runner ---
async def main():
    """
    Main entrypoint for the CLI dashboard. Parses arguments, selects event source, and runs the dashboard loop.

    Usage:
        python cli_dashboard.py --source tcp --tcp-host localhost --tcp-port 8888
        python cli_dashboard.py --mock
    """
    parser = argparse.ArgumentParser(description="Automotive Security CLI Dashboard")
    parser.add_argument("--source", choices=["api", "tcp"], help="Event source: api or tcp")
    parser.add_argument("--api-url", type=str, default="http://localhost:8000/events", help="API URL (for --source api)")
    parser.add_argument("--tcp-host", type=str, default="localhost", help="TCP event stream host (default: localhost)")
    parser.add_argument("--tcp-port", type=int, default=1234, help="TCP event stream port (default: 1234)")
    parser.add_argument("--mock", action="store_true", help="Enable mock mode to simulate detection events for testing and demo purposes.")
    args = parser.parse_args()

    # If --mock is set, ignore --source
    if args.mock:
        args.source = None

    console = Console()
    events = []
    status_text = "Starting..."

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
        """
        api_error_count = 0
        MAX_API_ERRORS = 5
        try:
            async for event in event_gen:
                log_event(event)
                # Add timestamp if not present
                if "timestamp" not in event:
                    event["timestamp"] = datetime.now().strftime("%H:%M:%S")
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
                with Live(render_dashboard(events, status_text), refresh_per_second=2, console=console):
                    await asyncio.sleep(0.5)
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Dashboard interrupted by user (Ctrl+C). Exiting gracefully.[/bold yellow]")
        except Exception as e:
            console.print(f"\n[bold red]Unexpected error: {e}[/bold red]")

    await dashboard_loop()

# --- Mock Event Generator ---
async def generate_mock_events():
    """
    Async generator that yields simulated detection events for dashboard demo/testing.
    Produces realistic-looking mock events with varying types, threat levels, and sources.

    Yields:
        dict: Simulated detection event.

    Example:
        async for event in generate_mock_events():
            print(event)
    """
    event_types = ["RF Unlock", "RF Lock", "NFC Scan", "Jamming", "Replay Attack", "Unknown"]
    threat_levels = ["Low", "Medium", "High", "Critical"]
    sources = ["Pico-1", "Pico-2", "Simulated", "TestBench"]
    details = [
        "Detected valid unlock signal.",
        "Multiple unlock attempts detected.",
        "NFC tag read.",
        "RF jamming pattern detected!",
        "Replay attack signature.",
        "Unrecognized RF burst.",
        "Signal strength anomaly.",
        "Intermittent connection.",
        "Rapid burst pattern.",
        "All clear."
    ]
    
    counter = itertools.count(1)
    while True:
        # Simulate a new event every 1.5 seconds
        await asyncio.sleep(1.5)
        now = datetime.now().strftime("%H:%M:%S")
        event = {
            "time": now,
            "type": random.choice(event_types),
            "threat": random.choices(threat_levels, weights=[5, 3, 2, 1])[0],
            "source": random.choice(sources),
            "details": random.choice(details) + f" (event #{next(counter)})"
        }
        yield event

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        from rich.console import Console
        Console().print("\n[bold yellow]Dashboard interrupted by user (Ctrl+C). Exiting gracefully.[/bold yellow]")
