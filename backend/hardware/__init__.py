"""Automotive Hardware Abstraction Layer.

This package provides a hardware abstraction layer (HAL) for automotive security
testing, supporting various hardware interfaces and components.
"""

# Core components
from hardware.core import (
    AntennaManager,
    EdgeDAO,
    EdgeDevice,
    HardwareFactory,
    Packet,
    SignalFilter,
    hardware_factory,
)

# Interfaces
from hardware.interfaces import MockRFInterface, RFInterface, StatusInterface

# Models
from hardware.models import RFConfig, SignalMetrics

__version__ = '0.1.0'
__all__ = [
    # Core components
    'AntennaManager',
    'EdgeDAO',
    'EdgeDevice',
    'HardwareFactory',
    'Packet',
    'SignalFilter',
    'hardware_factory',
    
    # Interfaces
    'MockRFInterface',
    'RFInterface',
    'StatusInterface',
    
    # Models
    'RFConfig',
    'SignalMetrics',
]