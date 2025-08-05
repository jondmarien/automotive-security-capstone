"""
Pico W Connection Manager

This module provides comprehensive Pico W connection management including:
- Automatic WiFi connection with retry logic
- TCP connection management with heartbeat monitoring
- Connection recovery for network interruptions
- Connection status reporting and diagnostics

The PicoConnectionManager handles all aspects of Pico W connectivity,
ensuring reliable communication between the main system and Pico W devices.

Example:
    manager = PicoConnectionManager()
    await manager.start_server()
    await manager.start_monitoring()
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PicoStatus(Enum):
    """Pico W connection status enumeration."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    HEARTBEAT_TIMEOUT = "heartbeat_timeout"
    ERROR = "error"
    MOCK = "mock"


@dataclass
class PicoDevice:
    """Pico W device information and status."""

    device_id: str
    address: str
    port: int
    status: PicoStatus
    connected_at: Optional[float] = None
    last_heartbeat: Optional[float] = None
    last_message: Optional[Dict[str, Any]] = None
    connection_attempts: int = 0
    total_messages: int = 0
    reader: Optional[asyncio.StreamReader] = None
    writer: Optional[asyncio.StreamWriter] = None


class PicoConnectionManager:
    """
    Comprehensive Pico W connection management system.

    Manages TCP connections to Pico W devices with automatic reconnection,
    heartbeat monitoring, and connection health diagnostics.
    """

    def __init__(self, server_host: str = "0.0.0.0", server_port: int = 8888):
        """
        Initialize Pico connection manager.

        Args:
            server_host: Host address for TCP server
            server_port: Port for TCP server
        """
        self.server_host = server_host
        self.server_port = server_port

        # Connection management
        self.connected_devices: Dict[str, PicoDevice] = {}
        self.server: Optional[asyncio.Server] = None
        self.server_task: Optional[asyncio.Task] = None

        # Monitoring settings
        self.heartbeat_interval = 30.0  # seconds
        self.heartbeat_timeout = 60.0  # seconds
        self.connection_timeout = 10.0  # seconds
        self.monitoring_task: Optional[asyncio.Task] = None

        # Retry settings
        self.max_connection_attempts = 5
        self.retry_backoff_base = 2.0
        self.retry_max_delay = 60.0

        # Mock mode
        self.mock_mode = False
        self.mock_devices: Dict[str, PicoDevice] = {}

        logger.info(
            f"Pico connection manager initialized on {server_host}:{server_port}"
        )

    async def start_server(self) -> bool:
        """
        Start TCP server for Pico W connections.

        Returns:
            bool: True if server started successfully, False otherwise
        """
        try:
            if self.mock_mode:
                logger.info("Starting Pico connection server in mock mode")
                await self._create_mock_devices()
                return True

            logger.info(
                f"Starting Pico connection server on {self.server_host}:{self.server_port}"
            )

            self.server = await asyncio.start_server(
                self._handle_pico_connection, self.server_host, self.server_port
            )

            logger.info(
                f"Pico connection server listening on {self.server_host}:{self.server_port}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to start Pico connection server: {e}")
            return False

    async def stop_server(self) -> None:
        """Stop TCP server and close all connections."""
        logger.info("Stopping Pico connection server...")

        # Close all device connections
        for device in list(self.connected_devices.values()):
            await self._disconnect_device(device.device_id)

        # Stop server
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None

        logger.info("Pico connection server stopped")

    async def restart_server(self) -> bool:
        """Restart TCP server."""
        logger.info("Restarting Pico connection server...")

        await self.stop_server()
        await asyncio.sleep(1.0)  # Brief pause
        return await self.start_server()

    async def start_monitoring(self) -> None:
        """Start connection monitoring and heartbeat checking."""
        if self.monitoring_task is None:
            logger.info("Starting Pico connection monitoring")
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def stop_monitoring(self) -> None:
        """Stop connection monitoring."""
        if self.monitoring_task:
            logger.info("Stopping Pico connection monitoring")
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None

    async def _handle_pico_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """
        Handle incoming Pico W connection.

        Args:
            reader: Asyncio stream reader
            writer: Asyncio stream writer
        """
        addr = writer.get_extra_info("peername")
        device_id = f"pico_{addr[0]}_{addr[1]}_{int(time.time())}"

        logger.info(f"Pico W connected from {addr} (ID: {device_id})")

        # Create device record
        device = PicoDevice(
            device_id=device_id,
            address=addr[0],
            port=addr[1],
            status=PicoStatus.CONNECTED,
            connected_at=time.time(),
            last_heartbeat=time.time(),
            reader=reader,
            writer=writer,
        )

        self.connected_devices[device_id] = device

        try:
            # Send initial configuration
            await self._send_initial_config(device)

            # Handle messages
            await self._handle_device_messages(device)

        except Exception as e:
            logger.error(f"Error handling Pico connection {device_id}: {e}")
        finally:
            await self._disconnect_device(device_id)

    async def _send_initial_config(self, device: PicoDevice) -> None:
        """
        Send initial configuration to newly connected Pico W.

        Args:
            device: PicoDevice instance
        """
        config = {
            "type": "config",
            "device_id": device.device_id,
            "heartbeat_interval": self.heartbeat_interval,
            "server_info": {
                "version": "0.1.0",
                "capabilities": ["rf_monitoring", "nfc_detection", "led_alerts"],
            },
            "timestamp": time.time(),
        }

        await self._send_to_device(device, config)
        logger.info(f"Initial configuration sent to {device.device_id}")

    async def _handle_device_messages(self, device: PicoDevice) -> None:
        """
        Handle messages from a connected Pico W device.

        Args:
            device: PicoDevice instance
        """
        buffer = ""

        while device.status == PicoStatus.CONNECTED:
            try:
                # Check if reader is available
                if device.reader is None:
                    logger.warning(
                        f"Reader not available for device {device.device_id}"
                    )
                    break

                # Read data with timeout
                data = await asyncio.wait_for(
                    device.reader.read(1024), timeout=self.connection_timeout
                )

                if not data:
                    logger.info(f"Pico {device.device_id} disconnected")
                    break

                buffer += data.decode("utf-8", errors="ignore")

                # Process complete messages (newline-delimited JSON)
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()

                    if line:
                        try:
                            message = json.loads(line)
                            await self._process_device_message(device, message)
                        except json.JSONDecodeError as e:
                            logger.warning(
                                f"Invalid JSON from {device.device_id}: {line} - {e}"
                            )

            except asyncio.TimeoutError:
                logger.warning(f"Connection timeout for {device.device_id}")
                device.status = PicoStatus.HEARTBEAT_TIMEOUT
                break
            except Exception as e:
                logger.error(f"Error reading from {device.device_id}: {e}")
                device.status = PicoStatus.ERROR
                break

    async def _process_device_message(
        self, device: PicoDevice, message: Dict[str, Any]
    ) -> None:
        """
        Process a message received from a Pico W device.

        Args:
            device: PicoDevice instance
            message: Parsed JSON message
        """
        device.last_message = message
        device.total_messages += 1

        message_type = message.get("type", "unknown")

        if message_type == "heartbeat":
            device.last_heartbeat = time.time()
            logger.debug(f"Heartbeat received from {device.device_id}")

            # Send heartbeat response
            response = {"type": "heartbeat_ack", "timestamp": time.time()}
            await self._send_to_device(device, response)

        elif message_type == "status":
            logger.info(f"Status update from {device.device_id}: {message}")

        elif message_type == "nfc_detection":
            logger.info(f"NFC detection from {device.device_id}: {message}")

        elif message_type == "error":
            logger.warning(f"Error reported by {device.device_id}: {message}")

        else:
            logger.debug(
                f"Unknown message type from {device.device_id}: {message_type}"
            )

    async def _send_to_device(self, device: PicoDevice, data: Dict[str, Any]) -> bool:
        """
        Send data to a Pico W device.

        Args:
            device: PicoDevice instance
            data: Data to send (will be JSON-encoded)

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            if device.writer and not device.writer.is_closing():
                json_data = json.dumps(data) + "\n"
                device.writer.write(json_data.encode("utf-8"))
                await device.writer.drain()
                return True
            else:
                logger.warning(f"Cannot send to {device.device_id} - connection closed")
                return False

        except Exception as e:
            logger.error(f"Failed to send to {device.device_id}: {e}")
            return False

    async def broadcast_to_devices(self, data: Dict[str, Any]) -> int:
        """
        Broadcast data to all connected Pico W devices.

        Args:
            data: Data to broadcast

        Returns:
            int: Number of devices that received the message
        """
        if self.mock_mode:
            # Simulate broadcast to mock devices
            logger.debug(
                f"Mock broadcast to {len(self.mock_devices)} devices: {data.get('type', 'unknown')}"
            )
            return len(self.mock_devices)

        sent_count = 0

        for device in list(self.connected_devices.values()):
            if device.status == PicoStatus.CONNECTED:
                if await self._send_to_device(device, data):
                    sent_count += 1

        return sent_count

    async def _disconnect_device(self, device_id: str) -> None:
        """
        Disconnect a Pico W device and cleanup resources.

        Args:
            device_id: Device identifier
        """
        if device_id in self.connected_devices:
            device = self.connected_devices[device_id]

            logger.info(f"Disconnecting Pico {device_id}")

            # Close connection
            if device.writer and not device.writer.is_closing():
                device.writer.close()
                try:
                    await device.writer.wait_closed()
                except Exception as e:
                    logger.warning(f"Error closing connection to {device_id}: {e}")

            # Update status
            device.status = PicoStatus.DISCONNECTED
            device.reader = None
            device.writer = None

            # Remove from connected devices
            del self.connected_devices[device_id]

    async def _monitoring_loop(self) -> None:
        """Continuous monitoring loop for connection health."""
        logger.info("Starting Pico connection monitoring loop")

        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                await self._check_device_health()

            except asyncio.CancelledError:
                logger.info("Pico connection monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Pico monitoring error: {e}")
                await asyncio.sleep(5.0)

    async def _check_device_health(self) -> None:
        """Check health of all connected devices."""
        current_time = time.time()

        for device_id, device in list(self.connected_devices.items()):
            # Check heartbeat timeout
            if (
                device.last_heartbeat
                and (current_time - device.last_heartbeat) > self.heartbeat_timeout
            ):
                logger.warning(f"Heartbeat timeout for {device_id}")
                device.status = PicoStatus.HEARTBEAT_TIMEOUT
                await self._disconnect_device(device_id)

            # Send periodic heartbeat request
            elif device.status == PicoStatus.CONNECTED:
                heartbeat_request = {
                    "type": "heartbeat_request",
                    "timestamp": current_time,
                }
                await self._send_to_device(device, heartbeat_request)

    async def enable_mock_mode(self) -> None:
        """Enable mock mode for demonstrations."""
        logger.info("Enabling Pico connection mock mode")
        self.mock_mode = True
        await self._create_mock_devices()

    async def _create_mock_devices(self) -> None:
        """Create mock Pico W devices for testing."""
        mock_device_configs = [
            {"id": "mock_pico_1", "address": "192.168.1.101"},
            {"id": "mock_pico_2", "address": "192.168.1.102"},
        ]

        for config in mock_device_configs:
            device = PicoDevice(
                device_id=config["id"],
                address=config["address"],
                port=8888,
                status=PicoStatus.CONNECTED,
                connected_at=time.time(),
                last_heartbeat=time.time(),
            )

            self.mock_devices[config["id"]] = device
            logger.info(f"Created mock Pico device: {config['id']}")

    def is_mock_mode(self) -> bool:
        """Check if manager is in mock mode."""
        return self.mock_mode

    def get_connected_devices(self) -> List[str]:
        """Get list of connected device IDs."""
        if self.mock_mode:
            return list(self.mock_devices.keys())
        return [
            device_id
            for device_id, device in self.connected_devices.items()
            if device.status == PicoStatus.CONNECTED
        ]

    def get_total_configured_devices(self) -> int:
        """Get total number of configured devices."""
        if self.mock_mode:
            return len(self.mock_devices)
        return len(self.connected_devices)

    def get_device_status(self, device_id: str) -> Optional[PicoStatus]:
        """Get status of a specific device."""
        if self.mock_mode and device_id in self.mock_devices:
            return self.mock_devices[device_id].status
        elif device_id in self.connected_devices:
            return self.connected_devices[device_id].status
        return None

    async def check_health(self) -> Dict[str, Any]:
        """
        Perform health check on Pico connections.

        Returns:
            Dictionary containing health status and diagnostics
        """
        current_time = time.time()

        if self.mock_mode:
            return {
                "timestamp": current_time,
                "mock_mode": True,
                "connected_devices": len(self.mock_devices),
                "total_devices": len(self.mock_devices),
                "server_running": True,
                "errors": [],
            }

        connected_count = len(
            [
                d
                for d in self.connected_devices.values()
                if d.status == PicoStatus.CONNECTED
            ]
        )

        errors = []
        for device in self.connected_devices.values():
            if device.status in [PicoStatus.ERROR, PicoStatus.HEARTBEAT_TIMEOUT]:
                errors.append(f"Device {device.device_id}: {device.status.value}")

        return {
            "timestamp": current_time,
            "mock_mode": False,
            "connected_devices": connected_count,
            "total_devices": len(self.connected_devices),
            "server_running": self.server is not None,
            "monitoring_active": self.monitoring_task is not None,
            "errors": errors,
        }

    def get_diagnostic_info(self) -> Dict[str, Any]:
        """
        Get comprehensive diagnostic information.

        Returns:
            Dictionary containing detailed diagnostic data
        """
        device_info = {}

        devices_to_check = (
            self.mock_devices if self.mock_mode else self.connected_devices
        )

        for device_id, device in devices_to_check.items():
            device_info[device_id] = {
                "address": device.address,
                "port": device.port,
                "status": device.status.value,
                "connected_at": device.connected_at,
                "last_heartbeat": device.last_heartbeat,
                "connection_attempts": device.connection_attempts,
                "total_messages": device.total_messages,
            }

        return {
            "server_host": self.server_host,
            "server_port": self.server_port,
            "server_running": self.server is not None,
            "monitoring_active": self.monitoring_task is not None,
            "mock_mode": self.mock_mode,
            "heartbeat_interval": self.heartbeat_interval,
            "heartbeat_timeout": self.heartbeat_timeout,
            "connection_timeout": self.connection_timeout,
            "max_connection_attempts": self.max_connection_attempts,
            "connected_devices_count": len(self.get_connected_devices()),
            "total_devices_count": self.get_total_configured_devices(),
            "devices": device_info,
        }
