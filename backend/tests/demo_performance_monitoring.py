#!/usr/bin/env python3
"""
demo_performance_monitoring.py

Demonstration script for the lightweight performance monitoring system.
Shows how performance metrics are collected and displayed for automotive security monitoring.

Usage:
    python demo_performance_monitoring.py [--duration SECONDS] [--events COUNT]

Example:
    python demo_performance_monitoring.py --duration 30 --events 50
"""

import asyncio
import argparse
import time
import random
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.text import Text

from utils.simple_performance_monitor import (
    get_performance_monitor,
    reset_performance_monitor,
)


class PerformanceMonitoringDemo:
    """
    Demonstration of lightweight performance monitoring for automotive security.

    Simulates realistic automotive security monitoring scenarios and shows
    how performance metrics are collected and displayed.
    """

    def __init__(self, duration_seconds: int = 30, num_events: int = 50):
        """
        Initialize the demonstration.

        Args:
            duration_seconds: How long to run the demo
            num_events: Number of events to simulate
        """
        self.duration_seconds = duration_seconds
        self.num_events = num_events
        self.console = Console()

        # Reset performance monitor for clean demo
        reset_performance_monitor()
        self.monitor = get_performance_monitor()

        print("🚗 Automotive Security Performance Monitoring Demo")
        print(f"   Duration: {duration_seconds} seconds")
        print(f"   Events: {num_events} events")
        print("=" * 60)

    async def run_demo(self):
        """Run the complete demonstration."""
        try:
            await self._run_monitoring_simulation()
            await self._display_final_results()
        except KeyboardInterrupt:
            print("\\n⏹️  Demo interrupted by user")
            await self._display_final_results()

    async def _run_monitoring_simulation(self):
        """Run the main monitoring simulation with live display."""

        # Create layout for live display
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="metrics", size=12),
            Layout(name="events", size=8),
            Layout(name="footer", size=3),
        )

        start_time = time.time()
        events_generated = 0

        with Live(
            self._create_display(layout, 0, 0),
            refresh_per_second=4,
            console=self.console,
        ) as live:
            while (
                time.time() - start_time < self.duration_seconds
                and events_generated < self.num_events
            ):
                current_time = time.time()
                elapsed = current_time - start_time

                # Simulate signal processing with realistic timing
                processing_time = self._simulate_signal_processing()
                self.monitor.record_signal_processed(processing_time)

                # Occasionally generate events
                if random.random() < 0.3:  # 30% chance of event
                    event_type = self._generate_random_event()
                    self.monitor.record_event_generated(event_type)
                    events_generated += 1

                # Update system health periodically
                if int(elapsed) % 5 == 0:  # Every 5 seconds
                    self._update_system_health()

                # Update display
                live.update(self._create_display(layout, elapsed, events_generated))

                # Wait before next iteration
                await asyncio.sleep(0.2)

    def _simulate_signal_processing(self) -> float:
        """Simulate signal processing with realistic timing variations."""
        # Base processing time with some variation
        base_time = 45.0  # 45ms base
        variation = random.uniform(-15.0, 25.0)  # ±15-25ms variation

        # Occasionally simulate slower processing (system load)
        if random.random() < 0.1:  # 10% chance of slow processing
            variation += random.uniform(50.0, 100.0)

        return max(10.0, base_time + variation)  # Minimum 10ms

    def _generate_random_event(self) -> str:
        """Generate a random automotive security event."""
        event_types = [
            "key_fob_transmission",
            "key_fob_transmission",
            "key_fob_transmission",  # Most common
            "tpms_transmission",
            "tpms_transmission",
            "replay_attack",  # Threat
            "jamming_attack",  # Threat
            "brute_force_attack",  # Threat
            "unknown_signal",
        ]

        return random.choice(event_types)

    def _update_system_health(self):
        """Update system health with realistic values."""
        # Simulate RTL-SDR connection (usually connected)
        rtl_connected = random.random() > 0.05  # 95% uptime

        # Simulate Pico W connection (usually connected)
        pico_connected = random.random() > 0.1  # 90% uptime

        # Simulate memory usage (gradually increasing)
        base_memory = 85.0
        memory_variation = random.uniform(-10.0, 30.0)
        memory_usage = max(50.0, base_memory + memory_variation)

        self.monitor.update_system_health(
            rtl_sdr_connected=rtl_connected,
            pico_w_connected=pico_connected,
            memory_usage_mb=memory_usage,
        )

    def _create_display(
        self, layout: Layout, elapsed_time: float, events_generated: int
    ) -> Layout:
        """Create the live display layout."""

        # Header
        header_text = Text(
            "🚗 Automotive Security Performance Monitor", style="bold cyan"
        )
        header_text.append(
            f" | Elapsed: {elapsed_time:.1f}s | Events: {events_generated}", style="dim"
        )
        layout["header"].update(Panel(header_text, border_style="cyan"))

        # Metrics table
        metrics_table = self._create_metrics_table()
        layout["metrics"].update(
            Panel(metrics_table, title="Performance Metrics", border_style="green")
        )

        # Recent events
        events_display = self._create_events_display()
        layout["events"].update(
            Panel(events_display, title="System Status", border_style="yellow")
        )

        # Footer with dashboard summary
        dashboard_summary = self.monitor.get_dashboard_summary()
        footer_text = Text(f"Dashboard Summary: {dashboard_summary}", style="cyan")
        layout["footer"].update(Panel(footer_text, border_style="cyan"))

        return layout

    def _create_metrics_table(self) -> Table:
        """Create a table showing current performance metrics."""
        metrics = self.monitor.get_current_metrics()

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", width=25)
        table.add_column("Value", style="green", width=15)
        table.add_column("Status", style="yellow", width=15)

        # Processing metrics
        table.add_row("Signals Processed", str(metrics["signals_processed"]), "✓")
        table.add_row("Events Generated", str(metrics["events_generated"]), "✓")
        table.add_row("Events/Minute", f"{metrics['events_per_minute']:.1f}", "✓")

        # Performance metrics
        latency_status = (
            "✓"
            if metrics["average_latency_ms"] < 100
            else "⚠️"
            if metrics["average_latency_ms"] < 200
            else "❌"
        )
        table.add_row(
            "Avg Latency", f"{metrics['average_latency_ms']:.1f}ms", latency_status
        )
        table.add_row("Peak Latency", f"{metrics['peak_latency_ms']:.1f}ms", "📊")
        table.add_row("Performance", metrics["performance_status"], latency_status)

        # Detection metrics
        table.add_row("Threats Detected", str(metrics["threats_detected"]), "🔍")
        table.add_row("Key Fob Signals", str(metrics["key_fob_detections"]), "🔑")
        table.add_row("Replay Attacks", str(metrics["replay_attacks"]), "🔄")

        return table

    def _create_events_display(self) -> Table:
        """Create a display showing system status."""
        metrics = self.monitor.get_current_metrics()

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Component", style="cyan", width=20)
        table.add_column("Status", style="green", width=15)
        table.add_column("Details", style="yellow", width=20)

        # System health
        rtl_status = (
            "🟢 Connected"
            if metrics["rtl_sdr_status"] == "Connected"
            else "🔴 Disconnected"
        )
        table.add_row("RTL-SDR V4", rtl_status, "433.92 MHz")

        pico_status = (
            "🟢 Connected"
            if metrics["pico_w_status"] == "Connected"
            else "🔴 Disconnected"
        )
        table.add_row("Pico W", pico_status, "Alert System")

        # Memory usage
        memory_status = (
            "🟢 Normal"
            if metrics["memory_usage_mb"] < 200
            else "🟡 High"
            if metrics["memory_usage_mb"] < 500
            else "🔴 Critical"
        )
        table.add_row(
            "Memory Usage", memory_status, f"{metrics['memory_usage_mb']:.1f} MB"
        )

        # Uptime
        table.add_row("System Uptime", "🟢 Running", metrics["uptime_formatted"])

        return table

    async def _display_final_results(self):
        """Display final performance results."""
        print("\\n" + "=" * 60)
        print("📊 Final Performance Report")
        print("=" * 60)

        # Get detailed report
        detailed_report = self.monitor.get_detailed_report()
        summary = detailed_report["summary"]
        analysis = detailed_report["analysis"]

        # Summary table
        summary_table = Table(
            title="Performance Summary", show_header=True, header_style="bold green"
        )
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row(
            "Total Signals Processed", str(summary["signals_processed"])
        )
        summary_table.add_row(
            "Total Events Generated", str(summary["events_generated"])
        )
        summary_table.add_row("Threats Detected", str(summary["threats_detected"]))
        summary_table.add_row(
            "Average Latency", f"{summary['average_latency_ms']:.1f}ms"
        )
        summary_table.add_row("Peak Latency", f"{summary['peak_latency_ms']:.1f}ms")
        summary_table.add_row("Performance Grade", analysis["performance_grade"])
        summary_table.add_row("System Uptime", summary["uptime_formatted"])

        self.console.print(summary_table)

        # Analysis
        if analysis["bottlenecks"]:
            print("\\n⚠️  Performance Bottlenecks Detected:")
            for bottleneck in analysis["bottlenecks"]:
                print(f"   • {bottleneck}")

        if analysis["recommendations"]:
            print("\\n💡 Recommendations:")
            for recommendation in analysis["recommendations"]:
                print(f"   • {recommendation}")

        print("\\n✅ Demo completed successfully!")
        print(f"   Performance Grade: {analysis['performance_grade']}")
        print(f"   Dashboard Summary: {self.monitor.get_dashboard_summary()}")


async def main():
    """Main demonstration entry point."""
    parser = argparse.ArgumentParser(description="Performance Monitoring Demo")
    parser.add_argument("--duration", type=int, default=30, help="Duration in seconds")
    parser.add_argument(
        "--events", type=int, default=50, help="Number of events to simulate"
    )

    args = parser.parse_args()

    demo = PerformanceMonitoringDemo(args.duration, args.events)
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())
