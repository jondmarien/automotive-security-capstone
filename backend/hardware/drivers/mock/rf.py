"""Mock implementation of the RF interface for testing and development.

This module provides a mock implementation of the RF interface that simulates
RF communication without requiring actual hardware. It's primarily used for
testing and development purposes.
"""
from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

from hardware.exceptions import (
    BusyError,
    CommunicationError,
    ConfigurationError,
    InitializationError,
)
from hardware.models.models import RFConfig, SignalMetrics

if TYPE_CHECKING:
    from hardware.interfaces.rf import RFInterface  # noqa: F401

logger = logging.getLogger(__name__)


class MockRFInterface:
    """Mock implementation of the RF interface for testing and development.
    
    This class simulates an RF transceiver with the following features:
    - Simulates packet transmission and reception
    - Maintains signal metrics
    - Supports asynchronous operation
    - Thread-safe for testing concurrent scenarios
    
    Example:
        ```python
        config = RFConfig(
            frequency=868e6,
            power=14,
            data_rate=50000,
            modulation='FSK',
            bandwidth=125e3,
            devitation=50e3
        )
        
        rf = MockRFInterface()
        await rf.initialize(config)
        
        def packet_handler(packet: bytes) -> None:
            print(f"Received packet: {packet.hex()}")
        
        await rf.start_receiving(packet_handler)
        await rf.send_packet(b'test')
        ```
    
    Thread Safety:
        All public methods are thread-safe and can be called from multiple
        threads. Internal state is protected by asyncio primitives.
    """
    
    def __init__(self) -> None:
        """Initialize a new MockRFInterface instance.
        
        The interface starts in an uninitialized state and must be initialized
        with a valid RFConfig before use.
        """
        self._initialized = False
        self._receiving = False
        self._config: Optional[RFConfig] = None
        self._receive_callback: Optional[Callable[[bytes], None]] = None
        self._receive_task: Optional[asyncio.Task[None]] = None
        self._packet_queue: asyncio.Queue[bytes] = asyncio.Queue()
        self._lock = asyncio.Lock()
        logger.debug("Initialized new MockRFInterface")
    
    async def initialize(self, config: RFConfig) -> None:
        """Initialize the RF interface with the given configuration.
        
        Args:
            config: RF configuration parameters
                
        Raises:
            InitializationError: If the interface is already initialized
            ValueError: If the configuration is invalid
        """
        logger.debug("Initializing MockRFInterface with config: %s", config)
        
        async with self._lock:
            if self._initialized:
                error_msg = "RF interface already initialized"
                logger.error(error_msg)
                raise InitializationError(error_msg).with_details(
                    current_config=self._config.to_dict() if self._config else None,
                    new_config=config.to_dict()
                )
                
            if not isinstance(config, RFConfig):
                error_msg = f"Invalid configuration: must be an instance of RFConfig, got {type(config).__name__}"
                logger.error(error_msg)
                raise ConfigurationError(error_msg).with_details(actual_type=type(config).__name__)
                
            try:
                logger.debug("Setting configuration")
                self._config = config
                self._initialized = True
                logger.info("Successfully initialized MockRFInterface")
                logger.debug("Configuration: %s", config.to_dict() if hasattr(config, 'to_dict') else config)
            except Exception as e:
                logger.exception("Error during initialization")
                self._initialized = False
                raise
    
    async def start_receiving(self, callback: Callable[[bytes], None]) -> None:
        """Start receiving packets with the given callback.
        
        Args:
            callback: Function to call when a packet is received.
                The function should accept a single bytes argument.
                
        Raises:
            InitializationError: If the interface is not initialized
            RuntimeError: If already receiving
            ValueError: If callback is not callable
        """
        if not callable(callback):
            raise ValueError("callback must be callable")
            
        async with self._lock:
            if not self._initialized:
                raise InitializationError(
                    "Cannot start receiving: RF interface not initialized"
                )
                
            if self._receiving:
                raise BusyError("Already receiving packets")
                
            if not callable(callback):
                raise ConfigurationError(
                    "Invalid callback: must be callable"
                ).with_details(callback_type=type(callback).__name__)
                
            self._receive_callback = callback
            self._receiving = True
            self._receive_task = asyncio.create_task(
                self._receive_loop(),
                name="mock_rf_receive_loop"
            )
            logger.debug("Started receiving packets")
    
    async def stop_receiving(self) -> None:
        """Stop receiving packets.
        
        This method is idempotent and can be called multiple times safely.
        """
        async with self._lock:
            if not self._receiving or not self._receive_task:
                return
                
            self._receiving = False
            task = self._receive_task
            self._receive_task = None
            self._receive_callback = None
            
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception:  
                logger.exception("Error in receive loop")
                
            logger.debug("Stopped receiving packets")
    
    async def _receive_loop(self) -> None:
        """Background task that processes received packets.
        
        This loop runs continuously while receiving is enabled, processing
        any queued packets and calling the receive callback for each one.
        """
        logger.debug("Receive loop started")
        
        while self._receiving and self._receive_callback:
            try:
                # Process any queued packets with a small timeout to allow
                # for checking the running flag
                try:
                    packet = await asyncio.wait_for(
                        self._packet_queue.get(),
                        timeout=0.1
                    )
                    
                    if self._receive_callback:
                        try:
                            if asyncio.iscoroutinefunction(self._receive_callback):
                                await self._receive_callback(packet)
                            else:
                                loop = asyncio.get_running_loop()
                                await loop.run_in_executor(
                                    None, 
                                    self._receive_callback, 
                                    packet
                                )
                        except Exception:
                            logger.exception("Error in receive callback")
                except asyncio.TimeoutError:
                    continue
                    
            except asyncio.CancelledError:
                logger.debug("Receive loop cancelled")
                break
            except Exception as e:
                logger.exception("Unexpected error in receive loop")
                await asyncio.sleep(1)  # Prevent tight loop on errors
                break
            except Exception:  # noqa: BLE001
                logger.exception("Unexpected error in receive loop")
                await asyncio.sleep(1)  # Prevent tight loop on errors
    
    async def send_packet(self, data: bytes, timeout: float = 5.0) -> bool:
        """Send a packet of data over the RF interface.
        
        Args:
            data: The data to send as bytes
            timeout: Maximum time to wait for the send operation (unused in mock)
            
        Returns:
            bool: Always returns True for successful mock transmission
            
        Raises:
            InitializationError: If the interface is not initialized
            ValueError: If data is not bytes or is empty
            CommunicationError: For any transmission errors
        """
        if not self._initialized:
            raise InitializationError(
                "Cannot send packet: RF interface not initialized"
            )
            
        if not isinstance(data, bytes):
            raise ConfigurationError(
                "Invalid packet data: must be bytes"
            ).with_details(actual_type=type(data).__name__)
            
        if not data:
            raise ConfigurationError("Packet data cannot be empty")
            
        try:
            # In a real implementation, this would transmit the packet over RF
            # For the mock, we'll just queue it for reception
            if self._receiving and self._receive_callback:
                await self._packet_queue.put(data)
                logger.debug("Queued packet for reception: %d bytes", len(data))
            
            return True
            
        except Exception as e:
            logger.exception("Failed to send packet")
            raise CommunicationError(
                "Failed to send packet",
                cause=e,
                details={
                    'packet_length': len(data),
                    'initialized': self._initialized,
                    'receiving': self._receiving
                }
            ) from e
    
    def get_signal_metrics(self) -> SignalMetrics:
        """Get current signal metrics.
        
        Returns:
            SignalMetrics: Object containing signal metrics including:
                - rssi: Received Signal Strength Indicator in dBm
                - snr: Signal-to-Noise Ratio in dB
                - frequency: Current frequency in Hz
                - channel: Current channel number
                
        Raises:
            InitializationError: If the interface is not initialized
        """
        if not self._initialized:
            raise InitializationError("RF interface not initialized")
            
        # Return mock signal metrics
        metrics = SignalMetrics(
            rssi=-60.0,  # Typical good signal
            snr=25.0,    # Good SNR
            frequency=self._config.frequency if self._config else 0,
            channel=1    # Default channel
        )
        
        logger.debug("Current signal metrics: %s", metrics)
        return metrics
    
    @property
    def is_initialized(self) -> bool:
        """Check if the interface is initialized.
        
        Returns:
            bool: True if initialized, False otherwise
        """
        return self._initialized
    
    @property
    def is_receiving(self) -> bool:
        """Check if the interface is currently receiving.
        
        Returns:
            bool: True if receiving, False otherwise
        """
        return self._receiving and self._initialized
        
    async def __aenter__(self) -> 'MockRFInterface':
        """Async context manager entry.
        
        Returns:
            MockRFInterface: This instance
            
        Raises:
            InitializationError: If the interface is not initialized
        """
        if not self._initialized:
            raise InitializationError(
                "Cannot enter context: RF interface not initialized"
            )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit.
        
        Ensures proper cleanup of resources.
        """
        await self.stop_receiving()
        self._initialized = False
