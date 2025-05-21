"""RF hardware interface definitions.

This module defines the RFInterface that serves as an interface for all RF hardware
implementations. It's designed to work with both Python and MicroPython.
"""

# pylint: disable=missing-class-docstring,missing-function-docstring,too-few-public-methods

# Type checking setup
try:
    from typing import TYPE_CHECKING

    TYPING = True
except ImportError:
    # MicroPython compatibility
    TYPING = False
    TYPE_CHECKING = False

# Type-related imports
if TYPING and TYPE_CHECKING:
    try:
        from typing import Any, Callable, Dict

        from typing_extensions import Protocol

        from ..models.models import RFConfig, SignalMetrics
    except ImportError:
        TYPING = False

# Define the base interface that works in both Python and MicroPython
class RFInterface:
    """Base class for RF hardware interfaces.

    This class defines the interface that all RF hardware implementations must follow.
    It supports both synchronous and asynchronous operations.
    """
    
    async def initialize(self, config) -> None:
        """Initialize the RF hardware with the given configuration.

        Args:
            config: Configuration for the RF interface.
                Expected to have frequency, tx_power, and other RF settings.
        """
        raise NotImplementedError("Subclasses must implement initialize()")
    
    async def start_receiving(self, callback) -> None:
        """Start receiving packets with the given callback.

        Args:
            callback: Function to call when a packet is received.
                The function should accept a single bytes argument.
                Example: def on_packet_received(data: bytes) -> None:
        """
        raise NotImplementedError("Subclasses must implement start_receiving()")
    
    async def stop_receiving(self) -> None:
        """Stop receiving packets."""
        raise NotImplementedError("Subclasses must implement stop_receiving()")
    
    async def send_packet(self, data, timeout=5.0) -> bool:
        """Send a packet.

        Args:
            data: The data to send (bytes).
            timeout: Maximum time to wait for the send to complete, in seconds.
            
        Returns:
            bool: True if the packet was sent successfully, False otherwise.
        """
        raise NotImplementedError("Subclasses must implement send_packet()")
    
    def get_signal_metrics(self) -> Dict[str, Any]:
        """Get current signal metrics.

        Returns:
            dict: A dictionary containing signal metrics (RSSI, SNR, etc.)
        """
        raise NotImplementedError("Subclasses must implement get_signal_metrics()")
    
    @property
    def is_initialized(self) -> bool:
        """Check if the interface is initialized."""
        raise NotImplementedError("Subclasses must implement is_initialized property")
    
    @property
    def is_receiving(self) -> bool:
        """Check if the interface is currently receiving."""
        raise NotImplementedError("Subclasses must implement is_receiving property")

# Add Protocol for type checking if available
if TYPING and TYPE_CHECKING:
    class RFInterfaceProtocol(Protocol):
        """Protocol for type checking RF interface implementations."""
        async def initialize(self, config: RFConfig) -> None: ...
        async def start_receiving(self, callback: Callable[[bytes], None]) -> None: ...
        async def stop_receiving(self) -> None: ...
        async def send_packet(self, data: bytes, timeout: float = 5.0) -> bool: ...
        def get_signal_metrics(self) -> SignalMetrics: ...
        @property
        def is_initialized(self) -> bool: ...
        @property
        def is_receiving(self) -> bool: ...
    
    # Make the base class implement the protocol for type checking
    RFInterface.__bases__ = (RFInterfaceProtocol,)
