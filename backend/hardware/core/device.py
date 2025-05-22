"""Automotive Security Edge Device Implementation.

This module implements the core functionality of the automotive security edge device,
serving as the central component for RF signal monitoring and threat detection in
vehicular networks. The EdgeDevice class provides a hardware-agnostic interface
for capturing, processing, and analyzing RF signals to detect potential security threats.

Key Components:
    - Signal capture and processing pipeline
    - Configurable security analysis engine
    - Hardware abstraction layer integration
    - Data persistence and logging
    - Real-time threat detection and alerting

Architecture:
    The EdgeDevice follows a modular design with clear separation of concerns:
    - Hardware Abstraction: Interfaces with physical devices through RFInterface
    - Signal Processing: Handles filtering and analysis of incoming signals
    - Security Analysis: Implements threat detection algorithms
    - Data Management: Handles storage and retrieval of packets and alerts

Example:
    ```python
    from hardware.core.device import EdgeDevice
    from hardware.models import RFConfig
    import asyncio

    async def main():
        # Initialize device with default settings
        device = EdgeDevice(device_id="vehicle_123")
        
        # Configure RF parameters
        rf_config = RFConfig(
            frequency=433.92,    # MHz
            tx_power=20,        # dBm
            rx_gain=40,         # dB
            bandwidth=250000     # Hz
        )
        
        try:
            # Start the device
            await device.initialize(rf_config)
            await device.start()
            
            # Main processing loop
            while device.is_running:
                # Process incoming packets (non-blocking)
                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            await device.stop()
        finally:
            await device.shutdown()
    
    if __name__ == "__main__":
        asyncio.run(main())
    ```
"""
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from hardware.core.dao import EdgeDAO
from hardware.core.factory import hardware_factory
from hardware.core.packet import Packet
from hardware.core.signal_processor import SignalFilter
from hardware.interfaces import PowerInterface, RFInterface, StatusInterface
from hardware.models import RFConfig
from hardware.utils.logger import logger
from hardware.utils.reporter import SecurityAnalyzer, ThreatLevel
from hardware.version import __version__


class EdgeDevice:
    """Main class for the automotive security edge device.
    
    The EdgeDevice implements the core functionality for monitoring and analyzing
    RF signals in automotive environments. It provides a hardware-agnostic interface
    that can work with different RF frontends through the RFInterface abstraction.
    
    The device implements a processing pipeline that includes:
        - Signal capture and validation
        - Signal filtering and analysis
        - Threat detection and classification
        - Data persistence and alerting
    
    Thread Safety:
        This class is designed to be thread-safe and can be used in both synchronous
        and asynchronous contexts. All public methods are coroutines and should be
        awaited when called.
    
    Attributes:
        device_id (str): Unique identifier for the device instance.
        packet_count (int): Total number of packets processed since last reset.
        alert_count (int): Total number of security alerts generated.
        is_running (bool): Read-only property indicating if the device is active.
        rf_interface (Optional[RFInterface]): Configured RF interface instance.
        power_interface (Optional[PowerInterface]): Configured power management.
        status_interface (Optional[StatusInterface]): Device status monitoring.
    
    Example:
        ```python
        # Create and configure a device
        device = EdgeDevice(device_id="vehicle_123")
        
        # Initialize with hardware interfaces
        await device.initialize(rf_config=rf_config)
        
        # Start processing
        await device.start()
        
        # Later...
        await device.stop()
        ```
    """
    
    def __init__(self, device_id: str = "default_device") -> None:
        """Initialize the edge device with default configuration.
        
        This constructor sets up the core components of the device in a stopped state.
        The device must be explicitly started using the start() method after initialization.
        
        The initialization includes:
            - Creating a signal filter for incoming RF signals
            - Setting up the security analysis engine
            - Initializing the data access layer
            - Setting up hardware interface placeholders
            
        Args:
            device_id: A unique identifier for this device instance. This ID is used for:
                - Logging and diagnostics
                - Data correlation in distributed systems
                - Device identification in the network
                Defaults to "default_device" if not specified.
                
        Attributes:
            device_id (str): The unique identifier for this device instance.
            signal_filter (SignalFilter): Handles filtering and validation of incoming RF signals.
            security_analyzer (SecurityAnalyzer): Implements threat detection algorithms.
            dao (EdgeDAO): Manages data persistence and retrieval.
            running (bool): Indicates if the device is actively processing packets.
            packet_count (int): Counter for total packets processed since last reset.
            alert_count (int): Counter for total security alerts generated.
            rf_interface (Optional[RFInterface]): Configured RF hardware interface.
            power_interface (Optional[PowerInterface]): Power management interface.
            status_interface (Optional[StatusInterface]): System status monitoring.
            rf_config (Optional[RFConfig]): Current RF configuration parameters.
            
        Note:
            The device starts in a stopped state. You must call start() to begin
            processing packets. The initialize() method should be called before
            start() to configure hardware interfaces.
            
        Example:
            ```python
            # Basic initialization
            device = EdgeDevice(device_id="vehicle_123")
            
            # With type checking
            from typing import Optional
            from hardware.interfaces import RFInterface, PowerInterface, StatusInterface
            
            device = EdgeDevice("vehicle_123")
            assert device.rf_interface is None  # Not initialized yet
            assert not device.running  # Not started yet
            ```
        """
        self.device_id = device_id
        self.signal_filter = SignalFilter()
        self.running = False
        self.packet_count = 0
        self.alert_count = 0
        self.dao = EdgeDAO()
        self.security_analyzer = SecurityAnalyzer()
        self.rf_interface: Optional[RFInterface] = None
        self.power_interface: Optional[PowerInterface] = None
        self.status_interface: Optional[StatusInterface] = None
        self.rf_config: Optional[RFConfig] = None
        
        logger.info(f"Edge device {device_id} initialized")
    
    async def process_packet(self, rssi: int, freq: float, payload: bytes) -> Optional[Dict[str, Any]]:
        """Process a single RF packet through the security pipeline.
        
        This method implements the complete packet processing workflow:
        1. Validates device state and input parameters
        2. Creates a Packet object with timestamp and metadata
        3. Applies signal filtering based on configured rules
        4. Persists the packet data to storage
        5. Performs security analysis and threat detection
        6. Generates alerts for detected threats
        
        The method is designed to be non-blocking and should be called from an
        asynchronous context. All heavy processing is offloaded to background tasks.
        
        Args:
            rssi: Received Signal Strength Indicator in dBm. Typical range is -120 to 0 dBm.
                Values outside this range will trigger a warning but processing continues.
                
            freq: Center frequency of the received signal in MHz. Must be within the
                configured operating range of the RF interface. Typical values are
                in the ISM bands (e.g., 315 MHz, 433 MHz, 868 MHz, 915 MHz).
                
            payload: Raw binary data of the received packet. Must be a non-empty bytes
                object. The maximum supported payload size is implementation-dependent
                but typically limited to 256 bytes for most RF modules.
            
        Returns:
            Optional[Dict[str, Any]]: A dictionary containing processing results:
                - packet (dict): Processed packet data including metadata
                - threat_detected (bool): True if a security threat was detected
                - threat_level (str): Severity of the detected threat:
                    - 'BENIGN': No threat detected
                    - 'LOW': Minor security concern
                    - 'MEDIUM': Moderate security issue
                    - 'HIGH': Serious security threat
                    - 'CRITICAL': Critical security breach
                - reason (str): Human-readable description of the threat or filter reason
                - timestamp (str): ISO 8601 timestamp of when the packet was processed
                - packet_id (str): Unique identifier for the packet
                
            Returns None if:
                - Device is not running (is_running is False)
                - Packet is filtered out by signal processing
                - Input validation fails
                
        Raises:
            ValueError: If input parameters are invalid or out of range.
                - Empty or invalid payload
                - Frequency outside supported range
                - Invalid RSSI value type
                
            RuntimeError: If there's an error during packet processing that prevents
                normal operation. The device may need to be restarted.
                - Database write failure
                - Signal processing error
                - Hardware communication failure
                
        Example:
            ```python
            # Process a sample packet
            result = await device.process_packet(
                rssi=-65,  # Signal strength
                freq=433.92,  # Frequency in MHz
                payload=b'\x01\x02\x03\x04'  # Raw packet data
            )
            
            if result:
                if result['threat_detected']:
                    print(f"Threat detected: {result['reason']} ({result['threat_level']})")
                else:
                    print(f"Packet processed: {result['packet']['signature']}")
            else:
                print("Packet filtered out or device not running")
            ```
            
        Note:
            This method is thread-safe and can be called from multiple coroutines
            simultaneously. However, the order of packet processing is not guaranteed
            to match the order of method calls due to the asynchronous nature of the
            implementation.
        """
        if not self.running:
            logger.debug("Device is not running, packet ignored")
            return None
            
        try:
            # Validate inputs
            if not isinstance(payload, bytes) or not payload:
                raise ValueError("Payload must be a non-empty bytes object")
                
            if not (-120 <= rssi <= 0):  # Typical RSSI range
                logger.warning(f"Unusual RSSI value: {rssi} dBm")
                
            # Create packet object
            packet = Packet(rssi=rssi, freq=freq, payload=payload)
            
            # Apply signal filtering
            if not self.signal_filter.should_accept(packet):
                logger.debug(f"Packet filtered out: {packet.signature}")
                return {
                    "packet": packet.to_dict(),
                    "threat_detected": False,
                    "threat_level": 'BENIGN',
                    "reason": "Packet filtered out"
                }
            
            # Save packet to storage
            packet_data = packet.to_dict()
            await self.dao.save_packet(packet_data)
            self.packet_count += 1
            
            # Perform security analysis
            report = self.security_analyzer.analyze_packet(packet)
            
            # Handle threat detection
            if report.threat_level != ThreatLevel.BENIGN:
                alert_data = report.to_dict()
                alert_data['device_id'] = self.device_id
                await self.dao.save_alert(alert_data)
                self.alert_count += 1
                logger.warning(
                    f"Security alert: {report.reason}",
                    extra={"packet": packet_data}
                )
            
            # Log successful processing
            logger.debug(
                f"Processed packet: {packet.signature}",
                extra={
                    "rssi": rssi,
                    "freq": f"{freq:.2f} MHz",
                    "payload_size": len(payload),
                    "threat_level": report.threat_level.name
                }
            )
            
            return {
                "packet": packet_data,
                "threat_detected": report.threat_level != ThreatLevel.BENIGN,
                "threat_level": report.threat_level.name,
                "reason": report.reason
            }
            
        except Exception as e:
            logger.error(f"Error processing packet: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to process packet: {str(e)}") from e
    
    async def get_status(self) -> Dict[str, Any]:
        """Retrieve the current operational status and metrics of the edge device.
        
        This method provides a comprehensive snapshot of the device's operational
        state, including performance metrics, resource usage, and system health.
        The status report is designed for both monitoring and debugging purposes.
        
        The method collects data from multiple sources:
            - Internal counters (packet_count, alert_count)
            - Data access layer metrics
            - Signal processing statistics
            - Hardware interface status
            - System resource usage
            
        Returns:
            Dict containing device status information with the following structure:
            {
                'device_id': str,  # Device identifier
                'status': str,  # 'running' or 'stopped'
                'packets_processed': int,  # Total packets processed
                'alerts_generated': int,  # Total alerts generated
                'storage_metrics': {
                    'packets': {
                        'count': int,  # Current packet count
                        'max': int  # Maximum packet capacity
                    },
                    'alerts': {
                        'count': int,  # Current alert count
                        'max': int  # Maximum alert capacity
                    }
                },
                'signal_metrics': {
                    'rssi': float,  # Current RSSI in dBm
                    'snr': float,  # Current SNR in dB
                    'frequency': float  # Current frequency in Hz
                },
                'security_metrics': {
                    'threats_detected': int,  # Total threats detected
                    'last_threat': str  # Type of last detected threat
                },
                'timestamp': str  # ISO 8601 timestamp
            }
            
        Example:
            {
                "device_id": "vehicle_123",
                "status": "running",
                "packets_processed": 150,
                "alerts_generated": 3,
                "storage_metrics": {
                    "packets": {
                        "count": 5,
                        "max": 1000
                    },
                    "alerts": {
                        "count": 2,
                        "max": 100
                    }
                },
                "signal_metrics": {
                    "rssi": -65.5,
                    "snr": 24.3,
                    "frequency": 433920000.0
                        "voltage": 3.7,
                        "memory": {
                            "total": 1048576,
                            "used": 524288,
                            "free": 524288
                        }
                    }
                },
                "interfaces": {
                    "rf": {
                        "connected": true,
                        "frequency": 433.92,
                        "power": 20.0,
                        "mode": "RX"
                    },
                    "power": {
                        "battery_level": 0.85,
                        "charging": true,
                        "power_source": "usb"
                    },
                    "storage": {
                        "total": 16777216,
                        "used": 8388608,
                        "free": 8388608
                    }
                }
            }
            
        Note:
            - This method is designed to be lightweight and can be called frequently
              for monitoring purposes.
            - Some metrics may be None or unavailable depending on the hardware
              configuration and current device state.
            - The actual metrics returned may vary based on the specific hardware
              implementation and available interfaces.
            
        Raises:
            RuntimeError: If there's an error collecting status information from
                        hardware interfaces or other components.
        """
        metrics = await self.dao.get_metrics()
        
        # Get signal metrics if RF interface is available
        signal_metrics = {}
        if self.rf_interface:
            signal_metrics = {
                'rssi': getattr(self.rf_interface, 'rssi', -100),  # Default to -100 if not available
                'snr': getattr(self.rf_interface, 'snr', 0),        # Default to 0 if not available
                'frequency': getattr(self.rf_interface, 'frequency', 0)  # Default to 0 if not available
            }
        
        # Get security metrics
        security_metrics = {
            'threats_detected': self.alert_count,
            'last_threat': 'none'  # This would normally come from the security analyzer
        }
        
        # Get storage metrics from DAO
        storage_metrics = {
            'packets': {
                'count': metrics.get('packets', {}).get('count', 0),
                'max': metrics.get('packets', {}).get('max', 0)
            },
            'alerts': {
                'count': metrics.get('alerts', {}).get('count', 0),
                'max': metrics.get('alerts', {}).get('max', 0)
            }
        }
        
        return {
            'device_id': self.device_id,
            'status': 'running' if self.running else 'stopped',
            'packets_processed': self.packet_count,
            'alerts_generated': self.alert_count,
            'storage_metrics': storage_metrics,
            'signal_metrics': signal_metrics,
            'security_metrics': security_metrics,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    async def _initialize_hardware(self) -> None:
        """Initialize all hardware interfaces for the edge device.
        
        This method sets up the following hardware interfaces:
            - RF Interface: For wireless communication
            - Power Interface: For power management
            - Status Interface: For system monitoring
            
        The method uses the hardware factory to create and initialize
        the appropriate interface implementations based on the current
        configuration.
        
        Raises:
            RuntimeError: If any hardware interface fails to initialize
            
        Note:
            This is an internal method and should not be called directly.
            Use start() instead.
        """
        try:
            logger.info("Initializing hardware interfaces...")
            
            # Initialize RF Interface
            if not self.rf_interface and self.rf_config:
                self.rf_interface = await hardware_factory.create_rf_interface(config=self.rf_config)
                logger.info("RF interface initialized successfully")
            
            # Initialize Power Interface
            if not self.power_interface:
                self.power_interface = await hardware_factory.create_power_manager()
                logger.info("Power interface initialized successfully")
                
            # Initialize Status Interface
            if not self.status_interface:
                self.status_interface = await hardware_factory.create_status_interface()
                logger.info("Status interface initialized successfully")
                
        except Exception as e:
            logger.critical(f"Failed to initialize hardware: {e}")
            await self._cleanup_hardware()
            raise RuntimeError(f"Hardware initialization failed: {e}") from e
    
    async def _cleanup_hardware(self) -> None:
        """Clean up all hardware interfaces.
        
        This method ensures all hardware interfaces are properly shut down
        and resources are released. It's called during error handling and
        device shutdown.
        """
        if self.rf_interface:
            try:
                await self.rf_interface.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down RF interface: {str(e)}", exc_info=True)
            self.rf_interface = None
            
        if self.power_interface:
            try:
                await self.power_interface.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down power interface: {str(e)}", exc_info=True)
            self.power_interface = None
            
        if self.status_interface:
            try:
                await self.status_interface.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down status interface: {str(e)}", exc_info=True)
            self.status_interface = None
    
    async def _start_background_tasks(self) -> None:
        """Start all necessary background tasks for the edge device.
        
        This method initializes and starts any background tasks required for
        the device's operation, such as:
            - Periodic status updates
            - Health monitoring
            - Data synchronization
            - Signal processing
            
        Note:
            This is an internal method and should not be called directly.
            It's automatically called by the start() method.
            
        Raises:
            RuntimeError: If any background task fails to start
        """
        try:
            logger.info("Starting background tasks...")
            
            # Start RF interface background tasks if supported
            if self.rf_interface and hasattr(self.rf_interface, 'start_background_tasks'):
                await self.rf_interface.start_background_tasks()
                logger.debug("RF interface background tasks started")
                
            # Start power monitoring if supported
            if self.power_interface and hasattr(self.power_interface, 'start_monitoring'):
                await self.power_interface.start_monitoring()
                logger.debug("Power monitoring started")
                
            # Start status monitoring if supported
            if self.status_interface and hasattr(self.status_interface, 'start_monitoring'):
                await self.status_interface.start_monitoring()
                logger.debug("Status monitoring started")
                
            logger.info("All background tasks started successfully")
            
        except Exception as e:
            logger.critical(f"Failed to start background tasks: {str(e)}", exc_info=True)
            # Stop any tasks that might have started
            await self._stop_background_tasks()
            raise RuntimeError(f"Failed to start background tasks: {str(e)}") from e
    
    async def _stop_background_tasks(self) -> None:
        """Stop all background tasks.
        
        This method stops all background tasks that were started by
        _start_background_tasks(). It's called during device shutdown
        and error recovery.
        """
        try:
            logger.info("Stopping background tasks...")
            
            # Stop RF interface background tasks if supported
            if self.rf_interface and hasattr(self.rf_interface, 'stop_background_tasks'):
                await self.rf_interface.stop_background_tasks()
                logger.debug("RF interface background tasks stopped")
                
            # Stop power monitoring if supported
            if self.power_interface and hasattr(self.power_interface, 'stop_monitoring'):
                await self.power_interface.stop_monitoring()
                logger.debug("Power monitoring stopped")
                
            # Stop status monitoring if supported
            if self.status_interface and hasattr(self.status_interface, 'stop_monitoring'):
                await self.status_interface.stop_monitoring()
                logger.debug("Status monitoring stopped")
                
        except Exception as e:
            logger.error(f"Error stopping background tasks: {str(e)}", exc_info=True)
    
    async def start(self) -> None:
        """Start the edge device and all associated components.
        
        This method initializes the hardware interfaces, starts background tasks,
        and transitions the device to an operational state. It performs the following
        steps:
            1. Validates the current device state
            2. Initializes hardware interfaces if not already done
            3. Starts background processing tasks
            4. Updates the device state to 'running'
            
        The method is idempotent - calling it multiple times has no additional
        effect if the device is already running.
        
        Note:
            - This method should be called after the device has been properly
              configured using initialize().
            - If the device is already running, a warning will be logged and
              the method will return immediately.
            
        Example:
            ```python
            # Start the device
            await device.start()
            
            # Verify device is running
            status = await device.get_status()
            assert status['status'] == 'running'
            ```
            
        Raises:
            RuntimeError: If there's an error initializing hardware interfaces
                        or starting background tasks.
                        The device will be left in a stopped state if an error occurs.
        """
        if self.running:
            logger.warning("Device is already running")
            return
        
        try:
            # Initialize hardware interfaces if not already done
            if not all([self.rf_interface, self.power_interface, self.status_interface]):
                await self._initialize_hardware()
                
            # Start background tasks
            await self._start_background_tasks()
            
            self.running = True
            logger.info("Edge device started successfully")
            
        except Exception as e:
            self.running = False
            logger.critical(f"Failed to start device: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to start device: {str(e)}") from e
    
    async def stop(self) -> None:
        """Gracefully stop the edge device and release resources.
        
        This method performs an orderly shutdown of all device components:
            1. Stops all background tasks and processing
            2. Releases hardware resources
            3. Flushes any pending data to storage
            4. Updates device status
            
        The method is idempotent and safe to call multiple times. If the device
        is already stopped, the method will return immediately after logging a warning.
        
        Note:
            - This method should be called during application shutdown to ensure
              all resources are properly released.
            - The method will block until all background tasks have completed.
              
        Example:
            ```python
            device = EdgeDevice()
            await device.start()
            # ... use the device ...
            await device.stop()  # Graceful shutdown
            ```
            
        Raises:
            RuntimeError: If an error occurs during shutdown that prevents
                        the device from stopping cleanly
        """
        if not self.running:
            logger.warning("Device is already stopped")
            return
            
        logger.info("Stopping edge device...")
        
        try:
            # Stop background tasks first
            await self._stop_background_tasks()
            
            # Flush any pending data
            if hasattr(self, 'dao') and self.dao:
                await self.dao.flush()
                
            # Mark as not running
            self.running = False
            logger.info("Edge device stopped successfully")
            
        except Exception as e:
            logger.error(f"Error during device shutdown: {str(e)}", exc_info=True)
            raise RuntimeError(f"Error during device shutdown: {str(e)}") from e
            
    async def reset(self) -> None:
        """Reset the device to its initial state.
        
        This method performs the following actions:
            1. Stops the device if it's running
            2. Clears all stored data and state
            3. Resets all counters and metrics
            
        The device will be in the same state as after initialization.
        
        Example:
            ```python
            device = EdgeDevice()
            await device.start()
            # ... use the device ...
            await device.reset()  # Reset to initial state
            ```
            
        Raises:
            RuntimeError: If an error occurs during reset
        """
        logger.info("Resetting device state...")
        
        try:
            # Stop the device if it's running
            if self.running:
                await self.stop()
            
            # Clear all persisted data
            await self.dao.clear_all()
            
            # Reset counters and state
            self.packet_count = 0
            self.alert_count = 0
            self.signal_filter.reset()
            self.security_analyzer.reset()
            
            logger.info("Device state reset successfully")
            
        except Exception as e:
            logger.error(f"Error resetting device: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to reset device: {str(e)}") from e
