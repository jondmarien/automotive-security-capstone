"""
Hardware abstraction layer for automotive security monitoring system.

This package provides hardware interfaces and abstractions for:
- RTL-SDR V4 dongles for RF signal capture
- Raspberry Pi Pico W for alert systems
- Mock implementations for testing and demonstrations
"""

from .rtl_sdr_interface import RTLSDRInterface, RTLSDRCapabilities, RTLSDRStatus
from .pico_connection_manager import PicoConnectionManager, PicoStatus
from .recovery_system import HardwareRecoverySystem, RecoveryStatus, FailureType
from .hardware_manager import HardwareManager, SystemStatus

__all__ = [
    'RTLSDRInterface',
    'RTLSDRCapabilities',
    'RTLSDRStatus',
    'PicoConnectionManager', 
    'PicoStatus',
    'HardwareRecoverySystem',
    'RecoveryStatus',
    'FailureType',
    'HardwareManager',
    'SystemStatus'
]