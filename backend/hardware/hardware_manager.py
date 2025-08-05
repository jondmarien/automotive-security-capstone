"""
Hardware Manager for Automotive Security System

This module provides centralized hardware management and coordination for:
- RTL-SDR hardware detection and configuration
- Pico W connection management and monitoring
- Hardware failure detection and recovery
- Seamless fallback to mock mode for demonstrations

The HardwareManager serves as the central coordinator for all hardware components,
providing unified status reporting, health monitoring, and recovery mechanisms.

Example:
    manager = HardwareManager()
    await manager.initialize()

    if manager.is_hardware_ready():
        await manager.start_monitoring()
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from .rtl_sdr_interface import RTLSDRInterface, RTLSDRStatus
from .pico_connection_manager import PicoConnectionManager
from .recovery_system import HardwareRecoverySystem, RecoveryStatus, FailureType

logger = logging.getLogger(__name__)


class SystemStatus(Enum):
    """Overall system hardware status."""

    INITIALIZING = "initializing"
    READY = "ready"
    DEGRADED = "degraded"
    FAILED = "failed"
    MOCK_MODE = "mock_mode"


@dataclass
class HardwareHealth:
    """Hardware health status information."""

    rtl_sdr_status: RTLSDRStatus
    pico_connections: int
    total_pico_devices: int
    system_status: SystemStatus
    uptime: float
    last_health_check: float
    errors: List[str]
    warnings: List[str]


class HardwareManager:
    """
    Centralized hardware management and coordination system.

    Manages all hardware components including RTL-SDR devices and Pico W connections,
    provides health monitoring, failure detection, and automatic recovery mechanisms.
    """

    def __init__(self, enable_auto_recovery: bool = True):
        """
        Initialize hardware manager.

        Args:
            enable_auto_recovery: Enable automatic hardware recovery mechanisms
        """
        self.rtl_sdr = RTLSDRInterface()
        self.pico_manager = PicoConnectionManager()

        self.system_status = SystemStatus.INITIALIZING
        self.enable_auto_recovery = enable_auto_recovery
        self.start_time = time.time()
        self.last_health_check = 0.0

        # Initialize recovery system
        self.recovery_system = HardwareRecoverySystem(self.rtl_sdr, self.pico_manager)

        # Health monitoring
        self.health_check_interval = 30.0  # seconds
        self.health_check_task: Optional[asyncio.Task] = None

        # Recovery settings (legacy - now handled by recovery system)
        self.max_recovery_attempts = 3
        self.recovery_backoff_base = 2.0  # exponential backoff base
        self.recovery_attempts = {}

        # Event callbacks
        self.status_change_callbacks: List[Callable[[SystemStatus], None]] = []
        self.hardware_failure_callbacks: List[
            Callable[[str, Dict[str, Any]], None]
        ] = []

        # Setup recovery system callbacks
        self.recovery_system.add_failure_callback(self._on_hardware_failure)
        self.recovery_system.add_recovery_callback(self._on_hardware_recovery)

        logger.info("Hardware manager initialized with recovery system")

    async def initialize(self, mock_mode: bool = False) -> bool:
        """
        Initialize all hardware components.

        Args:
            mock_mode: Start in mock mode for demonstrations

        Returns:
            bool: True if initialization successful, False otherwise
        """
        logger.info("Initializing hardware components...")

        if mock_mode:
            logger.info("Starting in mock mode")
            self.rtl_sdr.enable_mock_mode()
            await self.pico_manager.enable_mock_mode()
            self.system_status = SystemStatus.MOCK_MODE
            return True

        # Initialize RTL-SDR
        rtl_success = await self._initialize_rtl_sdr()

        # Initialize Pico W connections
        pico_success = await self._initialize_pico_connections()

        # Determine system status
        if rtl_success and pico_success:
            self.system_status = SystemStatus.READY
            logger.info("All hardware components initialized successfully")
        elif rtl_success or pico_success:
            self.system_status = SystemStatus.DEGRADED
            logger.warning(
                "Some hardware components failed to initialize - system degraded"
            )
        else:
            self.system_status = SystemStatus.FAILED
            logger.error("All hardware components failed to initialize")

            # Fallback to mock mode if all hardware fails
            if self.enable_auto_recovery:
                logger.info("Falling back to mock mode due to hardware failures")
                self.rtl_sdr.enable_mock_mode()
                await self.pico_manager.enable_mock_mode()
                self.system_status = SystemStatus.MOCK_MODE

        # Start health monitoring
        if self.health_check_task is None:
            self.health_check_task = asyncio.create_task(self._health_monitoring_loop())

        # Notify status change
        await self._notify_status_change(self.system_status)

        return self.system_status in [
            SystemStatus.READY,
            SystemStatus.DEGRADED,
            SystemStatus.MOCK_MODE,
        ]

    async def _initialize_rtl_sdr(self) -> bool:
        """Initialize RTL-SDR hardware."""
        try:
            logger.info("Detecting RTL-SDR hardware...")

            if self.rtl_sdr.detect_hardware():
                # Configure for automotive monitoring
                if self.rtl_sdr.configure_for_automotive("key_fob_eu"):
                    logger.info("RTL-SDR initialized and configured")
                    return True
                else:
                    logger.error("RTL-SDR detected but configuration failed")
                    return False
            else:
                logger.error("RTL-SDR hardware not detected")
                return False

        except Exception as e:
            logger.error(f"RTL-SDR initialization failed: {e}")
            return False

    async def _initialize_pico_connections(self) -> bool:
        """Initialize Pico W connection management."""
        try:
            logger.info("Initializing Pico W connection management...")

            # Start Pico connection server
            success = await self.pico_manager.start_server()

            if success:
                logger.info("Pico W connection manager started")
                return True
            else:
                logger.error("Failed to start Pico W connection manager")
                return False

        except Exception as e:
            logger.error(f"Pico W initialization failed: {e}")
            return False

    async def start_monitoring(self) -> None:
        """Start hardware monitoring and management."""
        logger.info("Starting hardware monitoring...")

        # Start Pico connection monitoring
        await self.pico_manager.start_monitoring()

        # Start recovery system monitoring if auto-recovery enabled
        if self.enable_auto_recovery:
            await self.recovery_system.start_monitoring()

        logger.info("Hardware monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop hardware monitoring and cleanup."""
        logger.info("Stopping hardware monitoring...")

        # Stop recovery system monitoring
        await self.recovery_system.stop_monitoring()

        # Stop health monitoring
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
            self.health_check_task = None

        # Stop Pico monitoring
        await self.pico_manager.stop_monitoring()

        logger.info("Hardware monitoring stopped")

    async def _health_monitoring_loop(self) -> None:
        """Continuous health monitoring loop."""
        logger.info("Starting health monitoring loop")

        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_check()

            except asyncio.CancelledError:
                logger.info("Health monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(5.0)  # Brief pause before retry

    async def _perform_health_check(self) -> None:
        """Perform comprehensive health check on all hardware."""
        self.last_health_check = time.time()

        # Check RTL-SDR health
        rtl_health = self.rtl_sdr.check_health()

        # Check Pico connections health
        pico_health = await self.pico_manager.check_health()

        # Determine if recovery is needed
        recovery_needed = []

        if (
            not rtl_health["hardware_detected"]
            and self.rtl_sdr.get_status() != RTLSDRStatus.MOCK_MODE
        ):
            recovery_needed.append("rtl_sdr")

        if (
            pico_health["connected_devices"] == 0
            and not self.pico_manager.is_mock_mode()
        ):
            recovery_needed.append("pico_connections")

        # Attempt recovery if enabled
        if recovery_needed and self.enable_auto_recovery:
            await self._attempt_recovery(recovery_needed)

        # Update system status
        await self._update_system_status(rtl_health, pico_health)

    async def _attempt_recovery(self, failed_components: List[str]) -> None:
        """
        Attempt recovery of failed hardware components.

        Args:
            failed_components: List of component names that need recovery
        """
        for component in failed_components:
            # Check recovery attempt count
            attempts = self.recovery_attempts.get(component, 0)

            if attempts >= self.max_recovery_attempts:
                logger.warning(f"Max recovery attempts reached for {component}")
                continue

            logger.info(f"Attempting recovery for {component} (attempt {attempts + 1})")

            # Calculate backoff delay
            backoff_delay = self.recovery_backoff_base**attempts
            await asyncio.sleep(backoff_delay)

            # Attempt component-specific recovery
            recovery_success = False

            if component == "rtl_sdr":
                recovery_success = await self._recover_rtl_sdr()
            elif component == "pico_connections":
                recovery_success = await self._recover_pico_connections()

            # Update recovery attempt count
            if recovery_success:
                logger.info(f"Recovery successful for {component}")
                self.recovery_attempts[component] = 0  # Reset on success
                await self._notify_hardware_recovery(component)
            else:
                self.recovery_attempts[component] = attempts + 1
                logger.warning(f"Recovery failed for {component}")
                await self._notify_hardware_failure(
                    component, {"attempts": attempts + 1}
                )

    async def _recover_rtl_sdr(self) -> bool:
        """Attempt RTL-SDR recovery."""
        try:
            # Re-detect hardware
            if self.rtl_sdr.detect_hardware():
                # Reconfigure for automotive
                if self.rtl_sdr.configure_for_automotive():
                    return True

            return False

        except Exception as e:
            logger.error(f"RTL-SDR recovery failed: {e}")
            return False

    async def _recover_pico_connections(self) -> bool:
        """Attempt Pico W connection recovery."""
        try:
            # Restart connection server
            await self.pico_manager.restart_server()

            # Wait for connections to establish
            await asyncio.sleep(5.0)

            # Check if any connections established
            health = await self.pico_manager.check_health()
            return health["connected_devices"] > 0

        except Exception as e:
            logger.error(f"Pico connection recovery failed: {e}")
            return False

    async def _update_system_status(
        self, rtl_health: Dict[str, Any], pico_health: Dict[str, Any]
    ) -> None:
        """Update overall system status based on component health."""
        previous_status = self.system_status

        # Determine new status
        if self.rtl_sdr.is_mock_mode() or self.pico_manager.is_mock_mode():
            new_status = SystemStatus.MOCK_MODE
        elif rtl_health["hardware_detected"] and pico_health["connected_devices"] > 0:
            new_status = SystemStatus.READY
        elif rtl_health["hardware_detected"] or pico_health["connected_devices"] > 0:
            new_status = SystemStatus.DEGRADED
        else:
            new_status = SystemStatus.FAILED

        # Update status if changed
        if new_status != previous_status:
            self.system_status = new_status
            logger.info(
                f"System status changed: {previous_status.value} -> {new_status.value}"
            )
            await self._notify_status_change(new_status)

    def get_health_status(self) -> HardwareHealth:
        """
        Get comprehensive hardware health status.

        Returns:
            HardwareHealth object with current status
        """
        pico_health = asyncio.create_task(self.pico_manager.check_health())

        # Get current health data (simplified for sync method)
        rtl_status = self.rtl_sdr.get_status()

        return HardwareHealth(
            rtl_sdr_status=rtl_status,
            pico_connections=len(self.pico_manager.get_connected_devices()),
            total_pico_devices=self.pico_manager.get_total_configured_devices(),
            system_status=self.system_status,
            uptime=time.time() - self.start_time,
            last_health_check=self.last_health_check,
            errors=[],  # Would be populated from component health checks
            warnings=[],
        )

    def is_hardware_ready(self) -> bool:
        """Check if hardware is ready for operation."""
        return self.system_status in [
            SystemStatus.READY,
            SystemStatus.DEGRADED,
            SystemStatus.MOCK_MODE,
        ]

    def is_mock_mode(self) -> bool:
        """Check if system is running in mock mode."""
        return self.system_status == SystemStatus.MOCK_MODE

    def get_rtl_sdr_interface(self) -> RTLSDRInterface:
        """Get RTL-SDR interface instance."""
        return self.rtl_sdr

    def get_pico_manager(self) -> PicoConnectionManager:
        """Get Pico connection manager instance."""
        return self.pico_manager

    def add_status_change_callback(
        self, callback: Callable[[SystemStatus], None]
    ) -> None:
        """Add callback for system status changes."""
        self.status_change_callbacks.append(callback)

    def add_hardware_failure_callback(
        self, callback: Callable[[str, Dict[str, Any]], None]
    ) -> None:
        """Add callback for hardware failure events."""
        self.hardware_failure_callbacks.append(callback)

    async def _notify_status_change(self, new_status: SystemStatus) -> None:
        """Notify registered callbacks of status changes."""
        for callback in self.status_change_callbacks:
            try:
                callback(new_status)
            except Exception as e:
                logger.error(f"Status change callback error: {e}")

    async def _notify_hardware_failure(
        self, component: str, details: Dict[str, Any]
    ) -> None:
        """Notify registered callbacks of hardware failures."""
        for callback in self.hardware_failure_callbacks:
            try:
                callback(component, details)
            except Exception as e:
                logger.error(f"Hardware failure callback error: {e}")

    async def _notify_hardware_recovery(self, component: str) -> None:
        """Notify registered callbacks of hardware recovery."""
        logger.info(f"Hardware component recovered: {component}")
        # Could add specific recovery callbacks if needed

    def _on_hardware_failure(
        self, component: str, failure_type: FailureType, details: Dict[str, Any]
    ) -> None:
        """Handle hardware failure notifications from recovery system."""
        logger.warning(
            f"Hardware failure detected by recovery system: {component} ({failure_type.value})"
        )

        # Notify registered callbacks
        asyncio.create_task(
            self._notify_hardware_failure(
                component, {"failure_type": failure_type.value, "details": details}
            )
        )

    def _on_hardware_recovery(
        self, component: str, status: RecoveryStatus, details: Dict[str, Any]
    ) -> None:
        """Handle hardware recovery notifications from recovery system."""
        if status == RecoveryStatus.SUCCESS:
            logger.info(f"Hardware recovery successful: {component}")
        elif status == RecoveryStatus.FALLBACK_ACTIVATED:
            logger.warning(f"Hardware fallback activated: {component}")
        else:
            logger.warning(f"Hardware recovery status: {component} - {status.value}")

    def get_recovery_system(self) -> HardwareRecoverySystem:
        """Get hardware recovery system instance."""
        return self.recovery_system

    def get_diagnostic_info(self) -> Dict[str, Any]:
        """
        Get comprehensive diagnostic information.

        Returns:
            Dictionary containing detailed diagnostic data
        """
        return {
            "system_status": self.system_status.value,
            "uptime": time.time() - self.start_time,
            "last_health_check": self.last_health_check,
            "recovery_enabled": self.enable_auto_recovery,
            "recovery_attempts": self.recovery_attempts,
            "rtl_sdr_diagnostics": self.rtl_sdr.get_diagnostic_info(),
            "pico_diagnostics": self.pico_manager.get_diagnostic_info(),
            "recovery_system_health": self.recovery_system.get_system_health_summary(),
            "health_check_interval": self.health_check_interval,
            "max_recovery_attempts": self.max_recovery_attempts,
        }
