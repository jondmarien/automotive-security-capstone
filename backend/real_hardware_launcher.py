#!/usr/bin/env python3
"""
Real Hardware Launcher for Automotive Security System

This script launches the complete automotive security monitoring system with
real RTL-SDR V4 and Raspberry Pi Pico 2 W hardware. It integrates our new
hardware detection and management system with the existing components.

Features:
- Automatic RTL-SDR V4 detection and configuration
- Real Pico W connection management with NFC support
- Hardware failure detection and recovery
- Graceful fallback to mock mode if hardware unavailable
- Comprehensive system health monitoring

Usage:
    uv run python real_hardware_launcher.py [--force-mock] [--frequency 433920000]

Example:
    # Launch with real hardware detection
    uv run python real_hardware_launcher.py

    # Force mock mode for demonstration
    uv run python real_hardware_launcher.py --force-mock

    # Use specific frequency (315MHz for North America)
    uv run python real_hardware_launcher.py --frequency 315000000
"""

import asyncio
import argparse
import logging
import signal
import sys
import time
from typing import Optional

# Import our new hardware management system
from hardware import HardwareManager

# Import existing components
from rtl_sdr.rtl_tcp_server import RTLTCPServerManager
from rtl_sdr.signal_bridge import SignalProcessingBridge

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("real_hardware_system.log")],
)
logger = logging.getLogger(__name__)


class RealHardwareSystem:
    """
    Complete real hardware system coordinator.

    Integrates the new hardware management system with existing components
    to provide a seamless real hardware experience.
    """

    def __init__(self, force_mock: bool = False, frequency: Optional[int] = None):
        """
        Initialize real hardware system.

        Args:
            force_mock: Force mock mode even if hardware is available
            frequency: Override default frequency (Hz)
        """
        self.force_mock = force_mock
        self.frequency = frequency or 433920000  # Default to 433.92 MHz

        # Initialize hardware manager
        self.hardware_manager = HardwareManager(enable_auto_recovery=True)

        # Legacy components (will be integrated with new system)
        self.rtl_tcp_manager: Optional[RTLTCPServerManager] = None
        self.signal_bridge: Optional[SignalProcessingBridge] = None

        # System state
        self.running = False
        self.startup_complete = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("Real hardware system initialized")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False

    async def start_system(self) -> bool:
        """
        Start the complete real hardware system.

        Returns:
            bool: True if system started successfully, False otherwise
        """
        logger.info("Starting Automotive Security Real Hardware System...")

        try:
            # Step 1: Initialize hardware detection and management
            logger.info("Step 1: Initializing hardware detection...")

            if self.force_mock:
                logger.info("🎭 Force mock mode enabled - skipping hardware detection")
                success = await self.hardware_manager.initialize(mock_mode=True)
            else:
                logger.info("Detecting real hardware...")
                success = await self.hardware_manager.initialize(mock_mode=False)

            if not success:
                logger.error("❌ Hardware initialization failed")
                return False

            # Report hardware status
            await self._report_hardware_status()

            # Step 2: Start hardware monitoring
            logger.info("Step 2: Starting hardware monitoring...")
            await self.hardware_manager.start_monitoring()

            # Step 3: Initialize RTL-SDR TCP server with detected hardware
            logger.info("Step 3: Starting RTL-SDR TCP server...")
            if not await self._start_rtl_tcp_server():
                logger.error("❌ Failed to start RTL-SDR TCP server")
                return False

            # Step 4: Start signal processing bridge
            logger.info("Step 4: Starting signal processing bridge...")
            if not await self._start_signal_bridge():
                logger.error("❌ Failed to start signal processing bridge")
                return False

            # Step 5: Wait for Pico connections
            logger.info("Step 5: Waiting for Pico W connections...")
            await self._wait_for_pico_connections()

            self.running = True
            self.startup_complete = True

            logger.info("✅ Real hardware system startup complete!")
            await self._print_system_summary()

            return True

        except Exception as e:
            logger.error(f"❌ System startup failed: {e}")
            return False

    async def _report_hardware_status(self):
        """Report detected hardware status."""
        rtl_sdr = self.hardware_manager.get_rtl_sdr_interface()
        pico_manager = self.hardware_manager.get_pico_manager()

        logger.info("Hardware Detection Results:")
        logger.info(f"   System Status: {self.hardware_manager.system_status.value}")
        logger.info(f"   RTL-SDR Status: {rtl_sdr.get_status().value}")

        if rtl_sdr.get_capabilities():
            caps = rtl_sdr.get_capabilities()
            logger.info(f"   RTL-SDR Device: {caps.device_name}")
            logger.info(f"   Tuner Type: {caps.tuner_type}")
            logger.info(
                f"   Frequency Range: {caps.frequency_range[0] / 1e6:.1f} - {caps.frequency_range[1] / 1e6:.1f} MHz"
            )

        pico_health = await pico_manager.check_health()
        logger.info(
            f"   Pico W Status: {pico_health['connected_devices']} devices connected"
        )

        if self.hardware_manager.is_mock_mode():
            logger.info("🎭 System running in MOCK MODE for demonstration")
        else:
            logger.info("System running with REAL HARDWARE")

    async def _start_rtl_tcp_server(self) -> bool:
        """Start RTL-SDR TCP server with detected hardware configuration."""
        try:
            rtl_sdr = self.hardware_manager.get_rtl_sdr_interface()
            config = rtl_sdr.get_configuration()

            # Use configuration from hardware detection
            frequency = config.get("frequency", self.frequency)
            sample_rate = config.get("sample_rate", 2048000)
            gain = config.get("gain", "auto")

            # Convert 'auto' gain to numeric value for legacy server
            if gain == "auto":
                gain = 25  # Default gain value

            logger.info("RTL-SDR Configuration:")
            logger.info(f"   Frequency: {frequency / 1e6:.3f} MHz")
            logger.info(f"   Sample Rate: {sample_rate / 1e6:.3f} MS/s")
            logger.info(f"   Gain: {gain} dB")

            # Initialize RTL-TCP server manager
            self.rtl_tcp_manager = RTLTCPServerManager(
                frequency=frequency, sample_rate=sample_rate, gain=gain
            )

            # Start RTL-TCP server (this will use mock mode if hardware not available)
            if rtl_sdr.is_mock_mode():
                logger.info("🎭 RTL-TCP server starting in mock mode")
                # For mock mode, we'll simulate the server
                return True
            else:
                logger.info("Starting real RTL-TCP server...")
                success = self.rtl_tcp_manager.start_rtl_tcp_server()
                if success:
                    logger.info("RTL-TCP server started successfully")
                    return True
                else:
                    logger.error("❌ RTL-TCP server failed to start")
                    # Try to fallback to mock mode
                    logger.info("🔄 Attempting fallback to mock mode...")
                    rtl_sdr.enable_mock_mode()
                    return True

        except Exception as e:
            logger.error(f"❌ RTL-TCP server startup error: {e}")
            return False

    async def _start_signal_bridge(self) -> bool:
        """Start signal processing bridge."""
        try:
            if not self.rtl_tcp_manager:
                logger.error("❌ RTL-TCP manager not initialized")
                return False

            # Initialize signal bridge with enhanced mode if available
            self.signal_bridge = SignalProcessingBridge(
                self.rtl_tcp_manager,
                enhanced_mode=True,  # Use enhanced signal processing
            )

            logger.info("Starting signal processing bridge...")

            # Start signal processing in background
            asyncio.create_task(self.signal_bridge.start_signal_processing())

            # Give it a moment to initialize
            await asyncio.sleep(2)

            logger.info("Signal processing bridge started")
            return True

        except Exception as e:
            logger.error(f"❌ Signal bridge startup error: {e}")
            return False

    async def _wait_for_pico_connections(self):
        """Wait for Pico W connections and report status."""
        pico_manager = self.hardware_manager.get_pico_manager()

        logger.info("Waiting for Pico W connections (timeout: 30s)...")

        # Wait up to 30 seconds for connections
        for i in range(30):
            health = await pico_manager.check_health()
            connected = health["connected_devices"]

            if connected > 0:
                logger.info(f"✅ {connected} Pico W device(s) connected!")
                break

            if i % 5 == 0:  # Log every 5 seconds
                logger.info(
                    f"Still waiting for Pico W connections... ({30 - i}s remaining)"
                )

            await asyncio.sleep(1)
        else:
            # Timeout reached
            if pico_manager.is_mock_mode():
                logger.info("🎭 Mock Pico W devices available for demonstration")
            else:
                logger.warning(
                    "⚠️  No real Pico W devices connected - system will continue without alerts"
                )

    async def _print_system_summary(self):
        """Print comprehensive system summary."""
        logger.info("=" * 60)
        logger.info("🎯 AUTOMOTIVE SECURITY SYSTEM - READY")
        logger.info("=" * 60)

        health = self.hardware_manager.get_health_status()

        logger.info(f"📊 System Status: {health.system_status.value.upper()}")
        logger.info(f"🔧 RTL-SDR: {health.rtl_sdr_status.value}")
        logger.info(
            f"📱 Pico W: {health.pico_connections}/{health.total_pico_devices} connected"
        )
        logger.info(f"⏱️  Uptime: {health.uptime:.1f} seconds")

        if self.hardware_manager.is_mock_mode():
            logger.info("🎭 DEMO MODE: Perfect for presentations and testing!")
        else:
            logger.info("🔧 LIVE MODE: Monitoring real RF spectrum!")

        logger.info("")
        logger.info("🎮 Next Steps:")
        logger.info("   1. Start CLI Dashboard: python cli_dashboard.py --source tcp")
        logger.info("   2. Monitor RF activity in real-time")
        logger.info("   3. Test with key fobs, TPMS sensors, or NFC tags")
        logger.info("   4. Watch for security events and alerts")
        logger.info("")
        logger.info("📝 Logs: real_hardware_system.log")
        logger.info("🛑 Stop: Ctrl+C for graceful shutdown")
        logger.info("=" * 60)

    async def run_system(self):
        """Run the system main loop with health monitoring."""
        logger.info("🔄 Starting system main loop...")

        # Health monitoring interval
        health_check_interval = 30.0  # seconds
        last_health_check = time.time()

        try:
            while self.running:
                current_time = time.time()

                # Periodic health reporting
                if current_time - last_health_check >= health_check_interval:
                    await self._report_system_health()
                    last_health_check = current_time

                # Brief sleep to prevent busy waiting
                await asyncio.sleep(1.0)

        except KeyboardInterrupt:
            logger.info("🛑 Keyboard interrupt received")
        except Exception as e:
            logger.error(f"❌ System loop error: {e}")
        finally:
            await self._shutdown_system()

    async def _report_system_health(self):
        """Report periodic system health."""
        try:
            health = self.hardware_manager.get_health_status()
            recovery_health = (
                self.hardware_manager.get_recovery_system().get_system_health_summary()
            )

            logger.info(
                f"💓 Health Check - Status: {health.system_status.value}, "
                f"RTL-SDR: {health.rtl_sdr_status.value}, "
                f"Pico: {health.pico_connections}/{health.total_pico_devices}, "
                f"Uptime: {health.uptime:.0f}s"
            )

            # Report any recovery activity
            if recovery_health["active_recoveries"]:
                logger.info(
                    f"🔄 Active recoveries: {recovery_health['active_recoveries']}"
                )

            if recovery_health["recent_failures"] > 0:
                logger.warning(
                    f"⚠️  Recent failures: {recovery_health['recent_failures']}"
                )

        except Exception as e:
            logger.error(f"❌ Health check error: {e}")

    async def _shutdown_system(self):
        """Gracefully shutdown the system."""
        logger.info("🛑 Initiating graceful system shutdown...")

        try:
            # Stop hardware monitoring
            await self.hardware_manager.stop_monitoring()

            # Stop signal processing
            if self.signal_bridge:
                self.signal_bridge.processing_active = False

            # Stop RTL-TCP server
            if self.rtl_tcp_manager and self.rtl_tcp_manager.rtl_process:
                self.rtl_tcp_manager.rtl_process.terminate()
                try:
                    self.rtl_tcp_manager.rtl_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.rtl_tcp_manager.rtl_process.kill()

            logger.info("✅ System shutdown complete")

        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")


async def main():
    """Main entry point for real hardware launcher."""
    parser = argparse.ArgumentParser(
        description="Launch Automotive Security System with Real Hardware",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python real_hardware_launcher.py                    # Auto-detect hardware
  python real_hardware_launcher.py --force-mock      # Force demo mode
  python real_hardware_launcher.py --frequency 315000000  # Use 315 MHz
        """,
    )

    parser.add_argument(
        "--force-mock",
        action="store_true",
        help="Force mock mode even if real hardware is available",
    )

    parser.add_argument(
        "--frequency",
        type=int,
        help="Override RF frequency in Hz (default: 433920000 for 433.92 MHz)",
    )

    args = parser.parse_args()

    # Create and start system
    system = RealHardwareSystem(force_mock=args.force_mock, frequency=args.frequency)

    # Start system
    if await system.start_system():
        # Run main loop
        await system.run_system()
    else:
        logger.error("❌ Failed to start system")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
