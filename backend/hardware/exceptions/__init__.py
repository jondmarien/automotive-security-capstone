"""Hardware abstraction layer exceptions."""
from .exceptions import HardwareBusyError, HardwareConfigurationError, HardwareError
from .exceptions import HardwareCommunicationError as CommunicationError
from .exceptions import HardwareNotInitializedError as InitializationError
from .exceptions import HardwareNotSupportedError as UnsupportedOperationError
from .exceptions import HardwareTimeoutError as TimeoutError

__all__ = [
    'HardwareError',
    'InitializationError',
    'HardwareConfigurationError',
    'CommunicationError',
    'UnsupportedOperationError',
    'TimeoutError',
    'HardwareBusyError'
]
