"""Hardware-related exceptions."""
from typing import Optional


class HardwareError(Exception):
    """Base class for all hardware-related exceptions."""
    def __init__(self, message: str, details: Optional[dict] = None):
        self.details = details or {}
        super().__init__(message)


class InitializationError(HardwareError):
    """Raised when hardware initialization fails."""
    pass


class CommunicationError(HardwareError):
    """Raised when communication with hardware fails."""
    pass


class TimeoutError(HardwareError):
    """Raised when a hardware operation times out."""
    pass


class UnsupportedOperationError(HardwareError):
    """Raised when an operation is not supported by the hardware."""
    pass
