"""Custom exceptions for the hardware abstraction layer."""

class HardwareError(Exception):
    """Base exception for all hardware-related errors."""
    pass

class HardwareNotInitializedError(HardwareError):
    """Raised when hardware is accessed before initialization."""
    pass

class HardwareConfigurationError(HardwareError):
    """Raised when there is an error in hardware configuration."""
    pass

class HardwareCommunicationError(HardwareError):
    """Raised when there is an error communicating with hardware."""
    pass

class HardwareNotSupportedError(HardwareError):
    """Raised when a hardware feature is not supported."""
    pass

class HardwareTimeoutError(HardwareError):
    """Raised when a hardware operation times out."""
    pass

class HardwareBusyError(HardwareError):
    """Raised when the hardware is busy and cannot process the request."""
    pass
