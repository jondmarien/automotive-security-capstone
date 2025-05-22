"""Hardware Abstraction Layer (HAL) for Automotive Security.

This module provides a hardware-agnostic interface for interacting with various
hardware components used in automotive security applications. It includes
interfaces for RF communication, power management, and system status monitoring.

Key Components:
    - Interfaces: Abstract base classes defining hardware contracts
    - Core: Main device and factory implementations
    - Drivers: Hardware-specific implementations
    - Models: Data structures and configurations
    - Utils: Helper functions and utilities

Example:
    ```python
    from hardware import EdgeDevice, RFConfig
    
    # Create a device with default configuration
    device = EdgeDevice()
    
    # Configure RF settings
    rf_config = RFConfig(
        frequency=433.92,
        tx_power=20,
        rx_gain=40,
        bandwidth=250000
    )
    
    # Initialize the device
    await device.initialize(rf_config)
    
    # Start receiving packets
    await device.start_receiving()
    """

# Core components
from .core.antenna import AntennaManager  # noqa: E402
from .core.dao import EdgeDAO  # noqa: E402
from .core.device import EdgeDevice  # noqa: E402
from .core.factory import HardwareFactory, hardware_factory  # noqa: E402
from .core.packet import Packet  # noqa: E402
from .core.signal_processor import SignalFilter  # noqa: E402

# Exceptions
from .exceptions import (  # noqa: E402
    BusyError,
    CommunicationError,
    ConfigurationError,
    HardwareError,
    InitializationError,
    TimeoutError,
    UnsupportedOperationError,
)
from .exceptions import (
    FirmwareError as HardwareFirmwareError,
)
from .exceptions import (
    PermissionError as HardwarePermissionError,
)
from .exceptions import (
    ResourceError as HardwareResourceError,
)


# Define any missing exceptions that might be used in the codebase
class PowerError(HardwareError):
    """Raised when there is a power-related error."""
    pass

class RFError(HardwareError):
    """Raised when there is an RF communication error."""
    pass

class StatusError(HardwareError):
    """Raised when there is a device status error."""
    pass

class ValidationError(HardwareError):
    """Raised when there is a validation error."""
    pass

# Interfaces
from .interfaces import (  # noqa: E402
    PowerInterface,
    RFInterface,
    StatusInterface,
)

# Models
from .models import (  # noqa: E402
    DeviceStatus,
    MemoryUsage,
    PowerState,
    RFConfig,
    SignalMetrics,
)

# Utils
from .utils import (  # noqa: E402
    configure_logging,
    setup_logging,
)

# Version information
from .version import __version__  # noqa: F401

# Package level exports
__all__ = [
    # Core components
    'EdgeDevice',
    'EdgeDAO',
    'HardwareFactory',
    'hardware_factory',
    'AntennaManager',
    'Packet',
    'SignalFilter',
    
    # Interfaces
    'PowerInterface',
    'RFInterface',
    'StatusInterface',
    
    # Exceptions
    'HardwareError',
    'PowerError',
    'RFError',
    'StatusError',
    'InitializationError',
    'ConfigurationError',
    'CommunicationError',
    'TimeoutError',
    'BusyError',
    'FirmwareError',
    'HardwareFirmwareError',
    'HardwarePermissionError',
    'HardwareResourceError',
    'UnsupportedOperationError',
    'ValidationError',
    
    # Models
    'RFConfig',
    'SignalMetrics',
    'MemoryUsage',
    'PowerState',
    'DeviceStatus',
    
    # Utils
    'configure_logging',
    'setup_logging',
    
    # Version
    '__version__',
]