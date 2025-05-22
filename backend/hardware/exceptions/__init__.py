"""Hardware abstraction layer exceptions.

This module provides a clean interface to all hardware-related exceptions.
It re-exports exceptions with simpler names where appropriate.
"""
from .exceptions import HardwareBusyError as BusyError
from .exceptions import HardwareCommunicationError as CommunicationError
from .exceptions import HardwareConfigurationError as ConfigurationError
from .exceptions import HardwareError, HardwareStateError
from .exceptions import HardwareFirmwareError as FirmwareError
from .exceptions import HardwareNotInitializedError as InitializationError
from .exceptions import HardwareNotSupportedError as UnsupportedOperationError
from .exceptions import HardwarePermissionError as PermissionError
from .exceptions import HardwareResourceError as ResourceError
from .exceptions import HardwareTimeoutError as TimeoutError

__all__ = [
    # Base exceptions
    'HardwareError',
    'HardwareStateError',
    
    # Specific exceptions with simplified names
    'InitializationError',
    'BusyError',
    'ConfigurationError',
    'CommunicationError',
    'TimeoutError',
    'UnsupportedOperationError',
    'PermissionError',
    'ResourceError',
    'FirmwareError',
    
    # Original names (for backward compatibility)
    'HardwareNotInitializedError',
    'HardwareBusyError',
    'HardwareConfigurationError',
    'HardwareCommunicationError',
    'HardwareTimeoutError',
    'HardwareNotSupportedError',
    'HardwarePermissionError',
    'HardwareResourceError',
    'HardwareFirmwareError'
]
