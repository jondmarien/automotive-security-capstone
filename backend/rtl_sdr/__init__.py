"""
RTL-SDR Hardware Integration Package

This package contains RTL-SDR hardware integration and signal processing components
for the automotive security capstone project.

Modules:
- rtl_tcp_server: RTL-SDR TCP server management and control
- signal_bridge: Signal processing and event bridge to detection
- automotive_signal_analyzer: Advanced automotive signal analysis
- enhanced_signal_bridge: Enhanced signal processing with threat detection
- signal_history_buffer: Signal history for replay detection
- startup_server: System startup orchestration and health checks
"""

from .signal_bridge import SignalBridge
from .rtl_tcp_server import RTLTCPServer
from .startup_server import StartupServer

__version__ = "0.1.0"
__all__ = [
    "SignalBridge",
    "RTLTCPServer", 
    "StartupServer",
]
