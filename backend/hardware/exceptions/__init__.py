"""Hardware-related exceptions."""

from .exceptions import (
    CommunicationError,
    HardwareError,
    InitializationError,
    TimeoutError,
    UnsupportedOperationError,
)

__all__ = [
    'HardwareError',
    'InitializationError',
    'CommunicationError',
    'TimeoutError',
    'UnsupportedOperationError',
]
