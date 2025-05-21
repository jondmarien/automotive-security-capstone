"""Mock implementation of the RF interface for testing.

This module provides a mock implementation of the RF interface that simulates
RF hardware behavior for testing and development purposes.
"""

import asyncio
import random
import time

# Import type hints conditionally
try:
    from typing import Callable, List
    TYPING = True
except ImportError:
    # MicroPython compatibility
    TYPING = False

# Import required modules with fallbacks
try:
    from ..exceptions.exceptions import CommunicationError, InitializationError
    from ..models.models import RFConfig, SignalMetrics
except ImportError as e:
    if TYPING:
        raise ImportError(f"Failed to import required modules: {e}") from e

from ..interfaces.rf import RFInterface


class MockRF(RFInterface):
    """Mock implementation of the RF interface for testing."""

    def __init__(self):
        """Initialize the mock RF interface."""
        self._initialized = False
        self._receiving = False
        self._receive_callback = None
        self._receive_task = None
        self._config = None
        self._packet_history = []
        self._packet_counter = 0
        self._stop_event = asyncio.Event()

    async def initialize(self, config: RFConfig) -> None:
        """Initialize the mock RF hardware with the given configuration.
        
        Args:
            config: The RF configuration to use
            
        Raises:
            InitializationError: If already initialized or simulation fails
        """
        if self._initialized:
            raise InitializationError("RF interface already initialized")
        
        self._config = config
        self._initialized = True
        
        # Simulate hardware initialization delay
        await asyncio.sleep(0.1)

        # Randomly fail initialization 5% of the time
        if random.random() < 0.05:
            self._initialized = False
            raise InitializationError(
                "Failed to initialize RF hardware (simulated error)"
            )

    async def start_receiving(self, callback: Callable[[bytes], None]) -> None:
        """Start receiving packets."""
        if not self._initialized:
            raise CommunicationError("RF interface not initialized")
        
        if self._receiving:
            raise CommunicationError("Already receiving")
        
        self._receive_callback = callback
        self._receiving = True
        self._receive_task = asyncio.create_task(self._receive_loop())

    async def stop_receiving(self) -> None:
        """Stop receiving packets."""
        if not self._receiving:
            return
            
        self._receiving = False
        self._stop_event.set()
        
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
            self._receive_task = None
            
        self._receive_callback = None
        self._stop_event.clear()

    async def _receive_loop(self):
        """Mock receive loop that generates random packets."""
        try:
            while self._receiving and not self._stop_event.is_set():
                # 10% chance of receiving a packet each second
                if random.random() < 0.1:
                    # Create a mock packet
                    packet_id = self._packet_counter
                    self._packet_counter += 1
                    packet_data = "MOCK_PKT_{}".format(packet_id).encode()
                    
                    # Add to history and call callback
                    self._packet_history.append((time.time(), packet_data))
                    if self._receive_callback:
                        try:
                            # Check if the callback is a coroutine function
                            if hasattr(asyncio, 'iscoroutinefunction') and \
                               asyncio.iscoroutinefunction(self._receive_callback):
                                await self._receive_callback(packet_data)
                            else:
                                # For backward compatibility with sync callbacks
                                self._receive_callback(packet_data)
                        except Exception as e:  # pylint: disable=broad-except
                            print("Error in receive callback: {}".format(e))
                
                # Sleep for a bit with cancellation support
                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=1.0
                    )
                    break
                except asyncio.TimeoutError:
                    continue
        except asyncio.CancelledError:
            # Task was cancelled, clean up
            self._stop_event.clear()
            raise


    async def send_packet(self, data: bytes, timeout: float = 5.0) -> bool:
        """Send a packet.
        
        Args:
            data: The data to send as bytes
            timeout: Maximum time to wait for transmission (in seconds)
            
        Returns:
            bool: True if transmission was successful, False otherwise
            
        Raises:
            CommunicationError: If interface is not initialized
            ValueError: If data is not bytes
        """
        if not self._initialized:
            raise CommunicationError("RF interface not initialized")
            
        if not isinstance(data, bytes):
            raise ValueError("Data must be bytes")
            
        # Simulate transmission delay
        await asyncio.sleep(0.05)
        
        # 5% chance of transmission failure
        if random.random() < 0.05:
            return False
            
        # Add to history
        self._packet_history.append((time.time(), data))
        return True

    def get_signal_metrics(self) -> SignalMetrics:
        """Get current signal metrics."""
        if not self._initialized:
            raise CommunicationError("RF interface not initialized")
            
        # Return random but realistic values
        return SignalMetrics(
            rssi=random.uniform(-90, -30),  # dBm
            snr=random.uniform(5, 30),      # dB
            frequency=self._config.frequency if self._config else 0,
            channel=random.randint(0, 15)
        )

    @property
    def is_initialized(self) -> bool:
        """Check if the interface is initialized."""
        return self._initialized

    @property
    def is_receiving(self) -> bool:
        """Check if the interface is currently receiving."""
        return self._receiving
        
    def get_packet_history(self) -> List[tuple]:
        """Get the history of sent and received packets.
        
        Returns:
            List of (timestamp, packet_data) tuples
        """
        return self._packet_history.copy()
