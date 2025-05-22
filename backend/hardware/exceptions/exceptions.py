"""Custom exceptions for the hardware abstraction layer.

This module defines a comprehensive hierarchy of exceptions for handling
hardware-related errors. The hierarchy is organized by error type, making it
easy to catch specific types of errors while maintaining the ability to
catch all hardware-related errors with the base HardwareError class.
"""
from typing import Any, Dict, Optional, TypeVar

T = TypeVar('T', bound='HardwareError')

class HardwareError(Exception):
    """Base exception for all hardware-related errors.
    
    This exception serves as the base class for all hardware-related exceptions.
    It includes an optional details dictionary for storing additional error context.
    
    Args:
        message: Human-readable error message
        details: Optional dictionary with additional error details
        cause: Optional exception that caused this one
    """
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        self.details = details or {}
        self.cause = cause
        super().__init__(message)
    
    def with_details(self: T, **kwargs: Any) -> T:
        """Add details to the exception and return self for chaining.
        
        Returns:
            Self: The exception instance for method chaining
        """
        self.details.update(kwargs)
        return self


class HardwareStateError(HardwareError):
    """Base class for hardware state-related errors."""
    pass


class HardwareNotInitializedError(HardwareStateError):
    """Raised when hardware is accessed before initialization.
    
    This typically occurs when a method is called that requires the hardware
    to be initialized first.
    """
    pass


class HardwareBusyError(HardwareStateError):
    """Raised when the hardware is busy and cannot process the request.
    
    This might occur when trying to perform an operation while another
    operation is still in progress.
    """
    pass


class HardwareConfigurationError(HardwareError):
    """Raised when there is an error in hardware configuration.
    
    This typically indicates invalid or incompatible configuration parameters.
    """
    pass


class HardwareCommunicationError(HardwareError):
    """Raised when there is an error communicating with hardware.
    
    This is a general communication error that might indicate a physical
    connection issue or protocol error.
    """
    pass


class HardwareTimeoutError(HardwareCommunicationError):
    """Raised when a hardware operation times out.
    
    This is a specific type of communication error that occurs when an
    operation takes longer than the allowed time.
    """
    pass


class HardwareNotSupportedError(HardwareError):
    """Raised when a hardware feature is not supported.
    
    This indicates that the requested operation or feature is not available
    on the current hardware or in the current configuration.
    """
    pass


class HardwarePermissionError(HardwareError):
    """Raised when there are permission issues accessing hardware.
    
    This might occur when the application doesn't have sufficient permissions
    to access the hardware device.
    """
    pass


class HardwareResourceError(HardwareError):
    """Raised when a required hardware resource is not available.
    
    This might include missing dependencies, unavailable devices, or
    insufficient resources.
    """
    pass


class HardwareFirmwareError(HardwareError):
    """Raised when there is an issue with the hardware firmware.
    
    This might indicate outdated, corrupted, or incompatible firmware.
    """
    pass
