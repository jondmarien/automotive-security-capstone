"""RF Hardware Interface Definitions.

This module defines the abstract base class for all RF hardware implementations
in the automotive security system. The RFInterface provides a consistent API
for interacting with different RF hardware modules while abstracting away
their specific implementations.

Key Features:
    - Hardware-agnostic interface for RF operations
    - Support for both synchronous and asynchronous operations
    - Type hints for better IDE support and code clarity
    - MicroPython compatibility for embedded systems

Example:
    ```python
    # Example of implementing a custom RF interface
    class MyRFDongle(RFInterface):
        def __init__(self):
            self._initialized = False
            self._receiving = False

        async def initialize(self, config: RFConfig) -> None:
            # Hardware-specific initialization
            self._initialized = True

        # Implement other required methods...
    ```
"""

# pylint: disable=missing-class-docstring,missing-function-docstring,too-few-public-methods

# Type checking setup
try:
    from typing import TYPE_CHECKING, Any, Callable, Dict, Optional  # noqa: F401

    from typing_extensions import Protocol  # noqa: F401

    from ..models.models import RFConfig, SignalMetrics  # noqa: F401
    
    TYPING = True
except ImportError:
    # MicroPython compatibility
    TYPING = False
    TYPE_CHECKING = False
    Dict = dict  # type: ignore
    Any = object  # type: ignore
    Callable = object  # type: ignore
    Protocol = object  # type: ignore
    RFConfig = Dict[str, Any]  # type: ignore
    SignalMetrics = Dict[str, Any]  # type: ignore

# Define the protocol for type checking
if TYPING and TYPE_CHECKING:
    class _RFInterfaceProtocol(Protocol):
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
    _bases = (_RFInterfaceProtocol,)
else:
    class _RFInterfaceProtocol:  # type: ignore
        """Dummy protocol for non-type-checking environments."""
        pass
    _bases = (object,)

# Define the base interface that works in both Python and MicroPython
class RFInterface(*_bases):
    """Abstract base class for RF hardware interfaces.
    
    This class defines the interface that all RF hardware implementations must follow.
    It provides methods for initializing the hardware, sending/receiving packets,
    and querying signal metrics.
    
    Implementations should inherit from this class and override all abstract methods.
    The interface is designed to work in both standard Python and MicroPython
    environments, with appropriate fallbacks for type checking.
    
    Thread Safety:
        Implementations should be thread-safe if they are intended to be used
        from multiple threads. All methods that modify shared state should be
        protected with appropriate synchronization primitives.
        
    Error Handling:
        Methods should raise appropriate exceptions (e.g., RuntimeError) for
        hardware-specific errors. The caller is responsible for handling these
        exceptions.
    """
    
    async def initialize(self, config: 'RFConfig') -> None:
        """Initialize the RF hardware with the given configuration.
        
        This method should perform any necessary hardware initialization,
        such as setting up communication channels, configuring registers,
        and verifying hardware presence.
        
        Args:
            config: RF configuration object containing parameters like:
                - frequency: Operating frequency in Hz
                - tx_power: Transmission power in dBm
                - bandwidth: Channel bandwidth in Hz
                - Other hardware-specific settings
                
        Raises:
            RuntimeError: If hardware initialization fails
            ValueError: If configuration parameters are invalid
            
        Note:
            This method should be idempotent - calling it multiple times
            should have the same effect as calling it once.
        """
        raise NotImplementedError("Subclasses must implement initialize()")
    
    async def start_receiving(self, callback: 'Callable[[bytes], None]') -> None:
        """Start receiving packets with the given callback.
        
        This method should start the hardware's receive mode and register
        the provided callback to be called whenever a new packet is received.
        The callback will be called from a background task or interrupt
        context, so it should be kept short and non-blocking.
        
        Args:
            callback: Function to call when a packet is received.
                The function should accept a single bytes argument containing
                the received packet data.
                
        Raises:
            RuntimeError: If the hardware fails to start receiving
            RuntimeError: If called when already receiving
            
        Example:
            ```python
            def packet_handler(data: bytes) -> None:
                print(f"Received {len(data)} bytes: {data.hex()}")
                
            await rf_interface.start_receiving(packet_handler)
            ```
        """
        raise NotImplementedError("Subclasses must implement start_receiving()")
    
    async def stop_receiving(self) -> None:
        """Stop receiving packets."""
        raise NotImplementedError("Subclasses must implement stop_receiving()")
    
    async def send_packet(self, data: bytes, timeout: float = 5.0) -> bool:
        """Send a packet of data over the RF interface.
        
        This method should block until the packet has been transmitted or
        the specified timeout has elapsed. The implementation should handle
        any necessary packet formatting, encoding, or modulation.
        
        Args:
            data: The raw bytes to transmit. The maximum supported length is
                implementation-dependent but should be documented by the
                specific hardware implementation.
            timeout: Maximum time to wait for the transmission to complete,
                in seconds. If the transmission doesn't complete within this
                time, the method should return False.
                
        Returns:
            bool: True if the packet was successfully transmitted, False if
                the operation timed out or failed.
                
        Raises:
            ValueError: If the data is too large or otherwise invalid
            RuntimeError: If the hardware is not initialized or encounters an error
            
        Note:
            The implementation should ensure that the radio is in the correct
            state (e.g., TX mode) before attempting to transmit.
        """
        raise NotImplementedError("Subclasses must implement send_packet()")
    
    def get_signal_metrics(self) -> 'SignalMetrics':
        """Get current signal metrics from the RF hardware.
        
        This method should return the most recent signal quality measurements
        from the RF hardware, such as received signal strength (RSSI), signal-
        to-noise ratio (SNR), and other relevant metrics.
        
        Returns:
            SignalMetrics: A dataclass or dictionary-like object containing:
                - rssi: Received Signal Strength Indicator in dBm
                - snr: Signal-to-Noise Ratio in dB
                - frequency_error: Frequency error in Hz (if available)
                - Other hardware-specific metrics
                
        Note:
            The exact set of available metrics depends on the hardware
            capabilities. Unavailable metrics should be returned as None.
            
        Example:
            ```python
            metrics = rf_interface.get_signal_metrics()
            print(f"RSSI: {metrics.rssi} dBm, SNR: {metrics.snr} dB")
            ```
        """
        raise NotImplementedError("Subclasses must implement get_signal_metrics()")
    
    @property
    def is_initialized(self) -> bool:
        """Check if the interface is initialized and ready for use.
        
        Returns:
            bool: True if the interface has been successfully initialized
                and is ready for operation, False otherwise.
                
        Note:
            This property should be checked before calling other methods
            that depend on hardware initialization.
        """
        raise NotImplementedError("Subclasses must implement is_initialized property")
    
    @property
    def is_receiving(self) -> bool:
        """Check if the interface is currently in receive mode.
        
        Returns:
            bool: True if the interface is actively receiving packets,
                False otherwise.
                
        Note:
            This indicates whether the interface is configured to receive
            packets, not whether it is currently receiving a packet.
        """
        raise NotImplementedError("Subclasses must implement is_receiving property")
    
    @property
    def is_initialized(self) -> bool:
        """Check if the interface is initialized and ready for use.
        
        Returns:
            bool: True if the interface has been successfully initialized
                and is ready for operation, False otherwise.
                    
            Note:
                This property should be checked before calling other methods
                that depend on hardware initialization.
            """
        raise NotImplementedError("Subclasses must implement is_initialized property")
        
    @property
    def is_receiving(self) -> bool:
        """Check if the interface is currently in receive mode.
        
        Returns:
            bool: True if the interface is actively receiving packets,
                    False otherwise.
                    
            Note:
                This indicates whether the interface is configured to receive
                packets, not whether it is currently receiving a packet.
            """
        raise NotImplementedError("Subclasses must implement is_receiving property")
