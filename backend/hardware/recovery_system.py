"""
Hardware Failure Recovery System

This module provides comprehensive hardware failure detection and recovery
mechanisms for the automotive security monitoring system.

Features:
- Hardware disconnection detection algorithms
- Automatic reconnection attempts with exponential backoff
- Graceful degradation for partial hardware failures
- Seamless fallback to mock mode for demonstrations
- Recovery attempt tracking and limiting

Example:
    recovery = HardwareRecoverySystem(hardware_manager)
    await recovery.start_monitoring()

    # Manual recovery attempt
    success = await recovery.attempt_component_recovery('rtl_sdr')
"""

import asyncio
import logging
import time
import random
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass
from enum import Enum

from .rtl_sdr_interface import RTLSDRInterface
from .pico_connection_manager import PicoConnectionManager

logger = logging.getLogger(__name__)


class RecoveryStatus(Enum):
    """Recovery attempt status enumeration."""

    NOT_NEEDED = "not_needed"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    MAX_ATTEMPTS_REACHED = "max_attempts_reached"
    FALLBACK_ACTIVATED = "fallback_activated"


class FailureType(Enum):
    """Hardware failure type enumeration."""

    DISCONNECTION = "disconnection"
    TIMEOUT = "timeout"
    CONFIGURATION_ERROR = "configuration_error"
    COMMUNICATION_ERROR = "communication_error"
    UNKNOWN = "unknown"


@dataclass
class RecoveryAttempt:
    """Recovery attempt information."""

    component: str
    failure_type: FailureType
    attempt_number: int
    timestamp: float
    status: RecoveryStatus
    error_message: Optional[str] = None
    recovery_time: Optional[float] = None


@dataclass
class ComponentHealth:
    """Component health status."""

    component: str
    is_healthy: bool
    last_check: float
    failure_count: int
    recovery_attempts: int
    last_failure_time: Optional[float] = None
    last_recovery_time: Optional[float] = None


class HardwareRecoverySystem:
    """
    Comprehensive hardware failure detection and recovery system.

    Monitors hardware components for failures and automatically attempts
    recovery using exponential backoff and graceful degradation strategies.
    """

    def __init__(self, rtl_sdr: RTLSDRInterface, pico_manager: PicoConnectionManager):
        """
        Initialize hardware recovery system.

        Args:
            rtl_sdr: RTL-SDR interface instance
            pico_manager: Pico connection manager instance
        """
        self.rtl_sdr = rtl_sdr
        self.pico_manager = pico_manager

        # Recovery settings
        self.max_recovery_attempts = 5
        self.base_backoff_delay = 1.0  # seconds
        self.max_backoff_delay = 300.0  # 5 minutes
        self.backoff_multiplier = 2.0
        self.jitter_factor = 0.1  # Add randomness to prevent thundering herd

        # Health monitoring
        self.health_check_interval = 15.0  # seconds
        self.failure_threshold = 3  # consecutive failures before recovery

        # Component tracking
        self.component_health: Dict[str, ComponentHealth] = {
            "rtl_sdr": ComponentHealth("rtl_sdr", True, time.time(), 0, 0),
            "pico_connections": ComponentHealth(
                "pico_connections", True, time.time(), 0, 0
            ),
        }

        # Recovery tracking
        self.recovery_history: List[RecoveryAttempt] = []
        self.active_recoveries: Set[str] = set()

        # Monitoring task
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_monitoring = False

        # Callbacks
        self.failure_callbacks: List[
            Callable[[str, FailureType, Dict[str, Any]], None]
        ] = []
        self.recovery_callbacks: List[
            Callable[[str, RecoveryStatus, Dict[str, Any]], None]
        ] = []

        logger.info("Hardware recovery system initialized")

    async def start_monitoring(self) -> None:
        """Start continuous hardware monitoring and recovery."""
        if self.is_monitoring:
            logger.warning("Recovery monitoring already active")
            return

        logger.info("Starting hardware recovery monitoring")
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def stop_monitoring(self) -> None:
        """Stop hardware monitoring and recovery."""
        if not self.is_monitoring:
            return

        logger.info("Stopping hardware recovery monitoring")
        self.is_monitoring = False

        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None

    async def _monitoring_loop(self) -> None:
        """Continuous monitoring loop for hardware health."""
        logger.info("Hardware recovery monitoring loop started")

        while self.is_monitoring:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._check_all_components()

            except asyncio.CancelledError:
                logger.info("Hardware recovery monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in recovery monitoring loop: {e}")
                await asyncio.sleep(5.0)  # Brief pause before retry

    async def _check_all_components(self) -> None:
        """Check health of all hardware components."""
        current_time = time.time()

        # Check RTL-SDR health
        await self._check_rtl_sdr_health(current_time)

        # Check Pico connections health
        await self._check_pico_health(current_time)

        # Attempt recovery for failed components
        await self._attempt_pending_recoveries()

    async def _check_rtl_sdr_health(self, current_time: float) -> None:
        """Check RTL-SDR hardware health."""
        component = "rtl_sdr"
        health = self.component_health[component]
        health.last_check = current_time

        # Skip if in mock mode
        if self.rtl_sdr.is_mock_mode():
            health.is_healthy = True
            return

        # Check hardware status
        rtl_health = self.rtl_sdr.check_health()
        is_healthy = rtl_health.get("hardware_detected", False)

        if not is_healthy:
            await self._handle_component_failure(
                component, FailureType.DISCONNECTION, {"rtl_health": rtl_health}
            )
        else:
            # Reset failure count on successful check
            if not health.is_healthy:
                logger.info("RTL-SDR health restored")
                health.last_recovery_time = current_time

            health.is_healthy = True
            health.failure_count = 0

    async def _check_pico_health(self, current_time: float) -> None:
        """Check Pico W connections health."""
        component = "pico_connections"
        health = self.component_health[component]
        health.last_check = current_time

        # Skip if in mock mode
        if self.pico_manager.is_mock_mode():
            health.is_healthy = True
            return

        # Check connection status
        pico_health = await self.pico_manager.check_health()
        connected_devices = pico_health.get("connected_devices", 0)

        # Consider unhealthy if no devices connected
        is_healthy = connected_devices > 0

        if not is_healthy:
            await self._handle_component_failure(
                component, FailureType.DISCONNECTION, {"pico_health": pico_health}
            )
        else:
            # Reset failure count on successful check
            if not health.is_healthy:
                logger.info("Pico connections health restored")
                health.last_recovery_time = current_time

            health.is_healthy = True
            health.failure_count = 0

    async def _handle_component_failure(
        self, component: str, failure_type: FailureType, details: Dict[str, Any]
    ) -> None:
        """
        Handle component failure detection.

        Args:
            component: Component name
            failure_type: Type of failure detected
            details: Additional failure details
        """
        health = self.component_health[component]
        current_time = time.time()

        # Update failure tracking
        health.failure_count += 1
        health.last_failure_time = current_time

        if health.is_healthy:
            logger.warning(
                f"Component failure detected: {component} ({failure_type.value})"
            )
            health.is_healthy = False

            # Notify failure callbacks
            await self._notify_failure_callbacks(component, failure_type, details)

        # Trigger recovery if threshold reached and not already recovering
        if (
            health.failure_count >= self.failure_threshold
            and component not in self.active_recoveries
        ):
            logger.info(
                f"Failure threshold reached for {component}, triggering recovery"
            )
            await self._schedule_recovery(component, failure_type)

    async def _schedule_recovery(
        self, component: str, failure_type: FailureType
    ) -> None:
        """
        Schedule recovery attempt for a failed component.

        Args:
            component: Component name
            failure_type: Type of failure
        """
        health = self.component_health[component]

        # Check if max attempts reached
        if health.recovery_attempts >= self.max_recovery_attempts:
            logger.warning(
                f"Max recovery attempts reached for {component}, activating fallback"
            )
            await self._activate_fallback(component)
            return

        # Add to active recoveries
        self.active_recoveries.add(component)

        # Calculate backoff delay
        delay = self._calculate_backoff_delay(health.recovery_attempts)

        logger.info(
            f"Scheduling recovery for {component} in {delay:.1f} seconds (attempt {health.recovery_attempts + 1})"
        )

        # Schedule recovery task
        asyncio.create_task(self._execute_recovery(component, failure_type, delay))

    def _calculate_backoff_delay(self, attempt_number: int) -> float:
        """
        Calculate exponential backoff delay with jitter.

        Args:
            attempt_number: Current attempt number (0-based)

        Returns:
            Delay in seconds
        """
        # Exponential backoff
        delay = self.base_backoff_delay * (self.backoff_multiplier**attempt_number)

        # Cap at maximum delay
        delay = min(delay, self.max_backoff_delay)

        # Add jitter to prevent thundering herd
        jitter = delay * self.jitter_factor * (random.random() - 0.5)
        delay += jitter

        return max(0.1, delay)  # Minimum 100ms delay

    async def _execute_recovery(
        self, component: str, failure_type: FailureType, delay: float
    ) -> None:
        """
        Execute recovery attempt for a component.

        Args:
            component: Component name
            failure_type: Type of failure
            delay: Delay before attempting recovery
        """
        try:
            # Wait for backoff delay
            await asyncio.sleep(delay)

            health = self.component_health[component]
            health.recovery_attempts += 1

            # Create recovery attempt record
            attempt = RecoveryAttempt(
                component=component,
                failure_type=failure_type,
                attempt_number=health.recovery_attempts,
                timestamp=time.time(),
                status=RecoveryStatus.IN_PROGRESS,
            )

            self.recovery_history.append(attempt)

            logger.info(
                f"Attempting recovery for {component} (attempt {health.recovery_attempts})"
            )

            # Attempt component-specific recovery
            success = await self._attempt_component_recovery(component)

            if success:
                attempt.status = RecoveryStatus.SUCCESS
                attempt.recovery_time = time.time() - attempt.timestamp

                logger.info(
                    f"Recovery successful for {component} in {attempt.recovery_time:.1f}s"
                )

                # Reset recovery attempts on success
                health.recovery_attempts = 0
                health.last_recovery_time = time.time()

                # Notify recovery callbacks
                await self._notify_recovery_callbacks(
                    component,
                    RecoveryStatus.SUCCESS,
                    {
                        "attempt_number": attempt.attempt_number,
                        "recovery_time": attempt.recovery_time,
                    },
                )

            else:
                attempt.status = RecoveryStatus.FAILED
                attempt.error_message = (
                    f"Recovery attempt {health.recovery_attempts} failed"
                )

                logger.warning(
                    f"Recovery failed for {component} (attempt {health.recovery_attempts})"
                )

                # Schedule next attempt if not at max
                if health.recovery_attempts < self.max_recovery_attempts:
                    await self._schedule_recovery(component, failure_type)
                else:
                    logger.error(f"Max recovery attempts reached for {component}")
                    await self._activate_fallback(component)

                # Notify recovery callbacks
                await self._notify_recovery_callbacks(
                    component,
                    RecoveryStatus.FAILED,
                    {
                        "attempt_number": attempt.attempt_number,
                        "error": attempt.error_message,
                    },
                )

        except Exception as e:
            logger.error(f"Error during recovery execution for {component}: {e}")

        finally:
            # Remove from active recoveries
            self.active_recoveries.discard(component)

    async def _attempt_component_recovery(self, component: str) -> bool:
        """
        Attempt recovery for a specific component.

        Args:
            component: Component name

        Returns:
            bool: True if recovery successful, False otherwise
        """
        try:
            if component == "rtl_sdr":
                return await self._recover_rtl_sdr()
            elif component == "pico_connections":
                return await self._recover_pico_connections()
            else:
                logger.error(f"Unknown component for recovery: {component}")
                return False

        except Exception as e:
            logger.error(f"Recovery attempt failed for {component}: {e}")
            return False

    async def _recover_rtl_sdr(self) -> bool:
        """Attempt RTL-SDR recovery."""
        logger.info("Attempting RTL-SDR recovery...")

        try:
            # Re-detect hardware
            if self.rtl_sdr.detect_hardware():
                # Reconfigure for automotive
                if self.rtl_sdr.configure_for_automotive():
                    logger.info("RTL-SDR recovery successful")
                    return True
                else:
                    logger.warning("RTL-SDR detected but configuration failed")
                    return False
            else:
                logger.warning("RTL-SDR hardware still not detected")
                return False

        except Exception as e:
            logger.error(f"RTL-SDR recovery failed: {e}")
            return False

    async def _recover_pico_connections(self) -> bool:
        """Attempt Pico W connection recovery."""
        logger.info("Attempting Pico connections recovery...")

        try:
            # Restart connection server
            await self.pico_manager.restart_server()

            # Wait for connections to establish
            await asyncio.sleep(5.0)

            # Check if any connections established
            health = await self.pico_manager.check_health()
            connected = health.get("connected_devices", 0)

            if connected > 0:
                logger.info(
                    f"Pico connections recovery successful ({connected} devices)"
                )
                return True
            else:
                logger.warning(
                    "Pico connections recovery failed - no devices connected"
                )
                return False

        except Exception as e:
            logger.error(f"Pico connections recovery failed: {e}")
            return False

    async def _activate_fallback(self, component: str) -> None:
        """
        Activate fallback mode for a failed component.

        Args:
            component: Component name
        """
        logger.warning(f"Activating fallback mode for {component}")

        try:
            if component == "rtl_sdr":
                self.rtl_sdr.enable_mock_mode()
                logger.info("RTL-SDR fallback to mock mode activated")

            elif component == "pico_connections":
                await self.pico_manager.enable_mock_mode()
                logger.info("Pico connections fallback to mock mode activated")

            # Update component health
            health = self.component_health[component]
            health.is_healthy = True  # Mock mode is considered "healthy"
            health.failure_count = 0

            # Record fallback activation
            attempt = RecoveryAttempt(
                component=component,
                failure_type=FailureType.UNKNOWN,
                attempt_number=health.recovery_attempts + 1,
                timestamp=time.time(),
                status=RecoveryStatus.FALLBACK_ACTIVATED,
            )

            self.recovery_history.append(attempt)

            # Notify recovery callbacks
            await self._notify_recovery_callbacks(
                component, RecoveryStatus.FALLBACK_ACTIVATED, {"fallback_mode": "mock"}
            )

        except Exception as e:
            logger.error(f"Failed to activate fallback for {component}: {e}")

    async def _attempt_pending_recoveries(self) -> None:
        """Check for and attempt any pending recoveries."""
        # This method can be extended to handle more complex recovery scheduling
        pass

    async def _notify_failure_callbacks(
        self, component: str, failure_type: FailureType, details: Dict[str, Any]
    ) -> None:
        """Notify registered failure callbacks."""
        for callback in self.failure_callbacks:
            try:
                callback(component, failure_type, details)
            except Exception as e:
                logger.error(f"Failure callback error: {e}")

    async def _notify_recovery_callbacks(
        self, component: str, status: RecoveryStatus, details: Dict[str, Any]
    ) -> None:
        """Notify registered recovery callbacks."""
        for callback in self.recovery_callbacks:
            try:
                callback(component, status, details)
            except Exception as e:
                logger.error(f"Recovery callback error: {e}")

    def add_failure_callback(
        self, callback: Callable[[str, FailureType, Dict[str, Any]], None]
    ) -> None:
        """Add callback for hardware failure events."""
        self.failure_callbacks.append(callback)

    def add_recovery_callback(
        self, callback: Callable[[str, RecoveryStatus, Dict[str, Any]], None]
    ) -> None:
        """Add callback for recovery events."""
        self.recovery_callbacks.append(callback)

    def get_component_health(self, component: str) -> Optional[ComponentHealth]:
        """Get health status for a specific component."""
        return self.component_health.get(component)

    def get_recovery_history(
        self, component: Optional[str] = None
    ) -> List[RecoveryAttempt]:
        """
        Get recovery attempt history.

        Args:
            component: Filter by component name, or None for all

        Returns:
            List of recovery attempts
        """
        if component:
            return [
                attempt
                for attempt in self.recovery_history
                if attempt.component == component
            ]
        return self.recovery_history.copy()

    def get_system_health_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive system health summary.

        Returns:
            Dictionary containing health summary
        """
        current_time = time.time()

        return {
            "timestamp": current_time,
            "monitoring_active": self.is_monitoring,
            "components": {
                name: {
                    "is_healthy": health.is_healthy,
                    "failure_count": health.failure_count,
                    "recovery_attempts": health.recovery_attempts,
                    "last_check_age": current_time - health.last_check,
                    "last_failure_age": (current_time - health.last_failure_time)
                    if health.last_failure_time
                    else None,
                    "last_recovery_age": (current_time - health.last_recovery_time)
                    if health.last_recovery_time
                    else None,
                }
                for name, health in self.component_health.items()
            },
            "active_recoveries": list(self.active_recoveries),
            "total_recovery_attempts": len(self.recovery_history),
            "recent_failures": len(
                [
                    attempt
                    for attempt in self.recovery_history
                    if current_time - attempt.timestamp < 3600  # Last hour
                ]
            ),
        }
