"""
exit_dialog.py

Professional exit experience for the CLI dashboard with Rich dialogs and session data export.
Provides confirmation dialogs, data export options, and clean terminal restoration.

Part of the automotive security capstone project CLI dashboard improvements.
"""

import os
import sys
import json
import csv
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
import pyfiglet


def display_logo(console: Console):
    """Display the ASCII art logo for the Automotive Security PoC."""
    from rich.align import Align

    logo_text = pyfiglet.figlet_format("AutoSec Monitor", font="standard")
    console.print(Align.center(logo_text), style="bold cyan")
    console.print(
        "Automotive Cybersecurity Proof of Concept", style="dim white", justify="center"
    )
    console.print("=" * console.width, style="dim white")
    console.print()  # Add spacing


class ExitDialogManager:
    """
    Manages professional exit experience for the CLI dashboard.
    Provides Rich-based confirmation dialogs, export options, and clean terminal restoration.
    """

    def __init__(
        self,
        console: Console,
        events: List[Dict[str, Any]],
        dashboard_logger=None,
        synthetic_mode: bool = False,
    ):
        """
        Initialize the exit dialog manager.

        Args:
            console (Console): Rich console instance
            events (List[Dict]): List of detection events from the session
            dashboard_logger: Logger instance for recording exit actions
            synthetic_mode (bool): Whether synthetic mode is active
        """
        self.console = console
        self.events = events
        self.logger = dashboard_logger
        self.synthetic_mode = synthetic_mode

        # Create timestamped export directory with synthetic prefix if applicable
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_prefix = "synthetic_session" if synthetic_mode else "session"
        self.export_dir = Path("exports") / f"{session_prefix}_{timestamp}"
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def show_exit_confirmation(self) -> Tuple[bool, Dict[str, bool]]:
        """
        Show the exit confirmation dialog with export options.

        Returns:
            Tuple[bool, Dict[str, bool]]: (should_exit, export_options)
        """
        # Clear screen and show exit confirmation
        self.console.clear()

        # Display ASCII logo
        display_logo(self.console)

        # Header with better spacing
        header = Panel(
            Align.center(Text("Dashboard Exit Confirmation", style="bold red")),
            title="[bold red]Exit Dashboard[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
        self.console.print(header)
        self.console.print()  # Add spacing

        # Show session summary
        session_summary = self._create_session_summary()

        # Display header and summary
        self.console.print(session_summary)
        self.console.print()

        # Ask for exit confirmation
        try:
            should_exit = Confirm.ask(
                "[bold yellow]Are you sure you want to exit the dashboard?[/bold yellow]",
                default=False,
            )

            if not should_exit:
                return False, {}

            # If user wants to exit, ask about data export
            export_options = self._get_export_preferences()

            return True, export_options

        except KeyboardInterrupt:
            # Handle Ctrl+C during dialog
            self.console.print("\n[bold red]Exit cancelled by user.[/bold red]")
            return False, {}

    def _create_session_summary(self) -> Panel:
        """Create a summary panel of the current session."""

        # Calculate session statistics
        total_events = len(self.events)
        threat_counts = self._calculate_threat_counts()
        session_duration = self._calculate_session_duration()

        # Create summary table
        summary_table = Table(show_header=False, box=None, padding=(0, 2))
        summary_table.add_column("Metric", style="bold")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Session Duration:", session_duration)
        summary_table.add_row("Total Events:", str(total_events))
        summary_table.add_row(
            "Critical Threats:", str(threat_counts.get("critical", 0))
        )
        summary_table.add_row(
            "Malicious Events:", str(threat_counts.get("malicious", 0))
        )
        summary_table.add_row(
            "Suspicious Events:", str(threat_counts.get("suspicious", 0))
        )
        summary_table.add_row("Benign Events:", str(threat_counts.get("benign", 0)))

        return Panel(
            summary_table,
            title="[bold]Session Summary[/bold]",
            border_style="blue",
            padding=(1, 2),
        )

    def _calculate_threat_counts(self) -> Dict[str, int]:
        """Calculate threat level counts from events."""
        counts = {"critical": 0, "malicious": 0, "suspicious": 0, "benign": 0}

        for event in self.events:
            threat_level = event.get("threat_level", "").lower()
            if threat_level in counts:
                counts[threat_level] += 1
            elif event.get("threat", "").lower() in ["critical", "high"]:
                counts["critical"] += 1
            elif event.get("threat", "").lower() in ["malicious", "medium"]:
                counts["malicious"] += 1
            elif event.get("threat", "").lower() in ["suspicious", "low"]:
                counts["suspicious"] += 1
            else:
                counts["benign"] += 1

        return counts

    def _calculate_session_duration(self) -> str:
        """Calculate session duration from first to last event."""
        if not self.events:
            return "No events"

        try:
            # Get timestamps from first and last events
            first_time = self.events[0].get("timestamp", "")
            last_time = self.events[-1].get("timestamp", "")

            if first_time and last_time:
                # Parse timestamps (assuming ISO format)
                first_dt = datetime.fromisoformat(first_time.replace("Z", "+00:00"))
                last_dt = datetime.fromisoformat(last_time.replace("Z", "+00:00"))
                duration = last_dt - first_dt

                # Format duration nicely
                total_seconds = int(duration.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60

                if hours > 0:
                    return f"{hours}h {minutes}m {seconds}s"
                elif minutes > 0:
                    return f"{minutes}m {seconds}s"
                else:
                    return f"{seconds}s"
            else:
                return "Unknown"
        except Exception:
            return "Unknown"

    def _get_export_preferences(self) -> Dict[str, bool]:
        """Get user preferences for data export."""
        self.console.print("[bold cyan]Data Export Options[/bold cyan]")
        self.console.print("Choose what data you'd like to save before exiting:\n")

        export_options = {}

        try:
            # Event history export
            export_options["events"] = Confirm.ask(
                "📊 Export event history (JSON format)?", default=True
            )

            # CSV report export
            export_options["csv_report"] = Confirm.ask(
                "📈 Export summary report (CSV format)?", default=True
            )

            # Log files export
            export_options["logs"] = Confirm.ask(
                "📝 Copy current session logs?", default=False
            )

            # Session metadata export
            export_options["metadata"] = Confirm.ask(
                "⚙️  Export session metadata and configuration?", default=False
            )

        except KeyboardInterrupt:
            self.console.print(
                "\n[bold yellow]Using default export options...[/bold yellow]"
            )
            export_options = {
                "events": True,
                "csv_report": True,
                "logs": False,
                "metadata": False,
            }

        return export_options

    def export_session_data(self, export_options: Dict[str, bool]) -> bool:
        """
        Export session data based on user preferences.

        Args:
            export_options (Dict[str, bool]): Export preferences from user

        Returns:
            bool: True if export was successful, False otherwise
        """
        if not any(export_options.values()):
            self.console.print(
                "[yellow]No data export requested. Exiting cleanly.[/yellow]"
            )
            return True

        # Create timestamp for export files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_success = True

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            # Export events as JSON
            if export_options.get("events", False):
                task = progress.add_task("Exporting event history...", total=1)
                try:
                    file_prefix = (
                        "synthetic_events" if self.synthetic_mode else "events"
                    )
                    events_file = self.export_dir / f"{file_prefix}_{timestamp}.json"
                    with open(events_file, "w", encoding="utf-8") as f:
                        json.dump(self.events, f, indent=2, default=str)
                    progress.update(task, completed=1)
                    self.console.print(
                        f"✅ Events exported to: [green]{events_file}[/green]"
                    )
                    self.console.print()  # Add spacing
                except Exception as e:
                    self.console.print(f"❌ Failed to export events: [red]{e}[/red]")
                    export_success = False

            # Export CSV report
            if export_options.get("csv_report", False):
                task = progress.add_task("Generating CSV report...", total=1)
                try:
                    file_prefix = (
                        "synthetic_report" if self.synthetic_mode else "report"
                    )
                    csv_file = self.export_dir / f"{file_prefix}_{timestamp}.csv"
                    self._export_csv_report(csv_file)
                    progress.update(task, completed=1)
                    self.console.print(
                        f"✅ CSV report exported to: [green]{csv_file}[/green]"
                    )
                    self.console.print()  # Add spacing
                except Exception as e:
                    self.console.print(
                        f"❌ Failed to export CSV report: [red]{e}[/red]"
                    )
                    export_success = False

            # Copy log files
            if export_options.get("logs", False):
                task = progress.add_task("Copying log files...", total=1)
                try:
                    self._copy_log_files(timestamp)
                    progress.update(task, completed=1)
                    self.console.print("✅ Log files copied to exports directory")
                    self.console.print()  # Add spacing
                except Exception as e:
                    self.console.print(f"❌ Failed to copy log files: [red]{e}[/red]")
                    export_success = False

            # Export session metadata
            if export_options.get("metadata", False):
                task = progress.add_task("Exporting session metadata...", total=1)
                try:
                    metadata_file = self.export_dir / f"metadata_{timestamp}.json"
                    self._export_session_metadata(metadata_file)
                    progress.update(task, completed=1)
                    self.console.print(
                        f"✅ Metadata exported to: [green]{metadata_file}[/green]"
                    )
                    self.console.print()  # Add spacing
                except Exception as e:
                    self.console.print(f"❌ Failed to export metadata: [red]{e}[/red]")
                    export_success = False

        return export_success

    def _export_csv_report(self, csv_file: Path):
        """Export a CSV summary report of the session."""
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(
                [
                    "Timestamp",
                    "Event Type",
                    "Threat Level",
                    "Source",
                    "Frequency",
                    "RSSI",
                    "Description",
                    "Evidence Count",
                ]
            )

            # Write event data
            for event in self.events:
                writer.writerow(
                    [
                        event.get("timestamp", ""),
                        event.get("type", ""),
                        event.get("threat_level", event.get("threat", "")),
                        event.get("source", ""),
                        event.get("frequency", ""),
                        event.get("rssi", ""),
                        event.get("description", ""),
                        len(event.get("evidence", [])),
                    ]
                )

    def _copy_log_files(self, timestamp: str):
        """Copy current log files to exports directory."""

        # Dynamically discover all .log files in the current directory
        log_files = list(Path(".").glob("*.log"))

        for log_file in log_files:
            if log_file.is_file():
                dest_file = (
                    self.export_dir / f"{log_file.stem}_{timestamp}.log"
                )
                shutil.copy2(log_file, dest_file)

    def _export_session_metadata(self, metadata_file: Path):
        """Export session metadata and configuration."""
        metadata = {
            "export_timestamp": datetime.now().isoformat(),
            "session_summary": {
                "total_events": len(self.events),
                "threat_counts": self._calculate_threat_counts(),
                "session_duration": self._calculate_session_duration(),
                "first_event_time": self.events[0].get("timestamp", "")
                if self.events
                else "",
                "last_event_time": self.events[-1].get("timestamp", "")
                if self.events
                else "",
            },
            "export_info": {
                "dashboard_version": "0.1.0",
                "export_format_version": "1.0",
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            },
        }

        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, default=str)

    def show_export_summary(self, export_success: bool):
        """Show final export summary before exit."""
        self.console.print()  # Add spacing

        if export_success:
            # Create rich text with proper formatting
            summary_text = Text()
            summary_text.append(
                "✅ Data export completed successfully!\n\n", style="green"
            )
            summary_text.append(
                "All requested files have been saved to:\n", style="green"
            )
            summary_text.append(str(self.export_dir), style="bold cyan")

            summary_panel = Panel(
                Align.center(summary_text),
                title="[bold green]Export Complete[/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        else:
            # Create rich text with proper formatting
            summary_text = Text()
            summary_text.append("⚠️  Some export operations failed.\n\n", style="yellow")
            summary_text.append(
                "Check the console output above for details.\n", style="yellow"
            )
            summary_text.append("Partial files saved to:\n", style="yellow")
            summary_text.append(str(self.export_dir), style="bold cyan")

            summary_panel = Panel(
                Align.center(summary_text),
                title="[bold yellow]Export Completed with Warnings[/bold yellow]",
                border_style="yellow",
                padding=(1, 2),
            )

        self.console.print(summary_panel)
        self.console.print()
        self.console.print("[dim]Press any key to continue...[/dim]")

        # Wait for user acknowledgment - use getch for any key
        try:
            import msvcrt

            msvcrt.getch()  # Works with any key including space
        except ImportError:
            # Fallback for non-Windows systems
            input()
        except KeyboardInterrupt:
            pass

    def show_final_goodbye(self, exported_data=False):
        """Show final goodbye screen with ASCII logo.

        Args:
            exported_data (bool): Whether session data was actually exported
        """
        import time

        # Small delay to ensure clean screen transition
        time.sleep(0.5)
        self.console.clear()

        # Display ASCII logo
        display_logo(self.console)

        # Final goodbye message with rich text - each line centered individually
        lines = []
        lines.append(
            Align.center(
                Text(
                    "Thank you for using the Automotive Security Dashboard!",
                    style="bold green",
                )
            )
        )
        lines.append(Text())  # Empty line for spacing

        # Only show export message if data was actually exported
        if exported_data:
            lines.append(
                Align.center(
                    Text("Session data has been preserved and exported.", style="green")
                )
            )
        else:
            lines.append(
                Align.center(
                    Text("Session data remains in memory only.", style="yellow")
                )
            )

        lines.append(Text())  # Empty line for spacing
        lines.append(Align.center(Text("Stay secure!", style="bold green")))

        # Combine all lines into a single renderable
        from rich.console import Group

        goodbye_content = Group(*lines)

        goodbye_panel = Panel(
            goodbye_content,
            title="[bold green]Goodbye![/bold green]",
            border_style="green",
            padding=(2, 3),
        )

        self.console.print(goodbye_panel)
        self.console.print()
        self.console.print("[dim]Dashboard shutdown complete.[/dim]")
        self.console.print()

        # Brief pause to let user see the goodbye message
        time.sleep(1.5)

    def restore_terminal_state(self):
        """Restore clean terminal state on exit."""
        # Terminal state is already clean from show_final_goodbye()
        # No need to clear or show additional messages
        pass


def handle_professional_exit(
    console: Console,
    events: List[Dict[str, Any]],
    dashboard_logger=None,
    synthetic_mode: bool = False,
) -> bool:
    """
    Handle professional exit experience with Rich dialogs and export options.

    Args:
        console (Console): Rich console instance
        events (List[Dict]): List of detection events from the session
        dashboard_logger: Logger instance for recording exit actions
        synthetic_mode (bool): Whether synthetic mode is active

    Returns:
        bool: True if user confirms exit, False if cancelled
    """
    exit_manager = ExitDialogManager(console, events, dashboard_logger, synthetic_mode)

    # Show exit confirmation dialog
    should_exit, export_options = exit_manager.show_exit_confirmation()

    if not should_exit:
        return False

    # Perform exports if requested
    exported_data = False
    if any(export_options.values()):
        export_success = exit_manager.export_session_data(export_options)
        exit_manager.show_export_summary(export_success)
        exported_data = export_success  # Only consider it exported if successful

    # Show final goodbye screen with export status
    exit_manager.show_final_goodbye(exported_data)

    # Restore terminal state
    exit_manager.restore_terminal_state()

    return True
