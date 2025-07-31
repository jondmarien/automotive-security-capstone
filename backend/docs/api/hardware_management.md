# Hardware Management API Documentation

## Overview

The Hardware Management System provides comprehensive hardware abstraction, detection, configuration, and failure recovery for the automotive security monitoring system. It includes automatic RTL-SDR detection, Pico W connection management, and graceful fallback to mock mode for demonstrations.

## Core Components

### HardwareManager

Central coordinator for all hardware components with health monitoring and recovery.

```python
from hardware import HardwareManager, SystemStatus

# Initialize hardware manager
manager = HardwareManager(enable_auto_recovery=True)

# Initialize hardware (auto-detect or mock mode)
success = await manager.initialize(mock_mode=False)

# Start monitoring and recovery
await manager.start_monitoring()

# Get system health status
health = manager.get_health_status()
print(f"System Status: {health.system_status.value}")
print(f"RTL-SDR: {health.rtl_sdr_status.value}")
print(f"Pico W: {health.pico_connections}/{health.total_pico_devices}")
```

### RTLSDRInterface

RTL-SDR hardware detection and configuration with automotive-specific optimization.

```python
from hardware.rtl_sdr_interface import RTLSDRInterface

# Initialize RTL-SDR interface
rtl_sdr = RTLSDRInterface()

# Detect hardware
if rtl_sdr.detect_hardware():
    # Get capabilities
    caps = rtl_sdr.get_capabilities()
    print(f"Device: {caps.device_name}")
    print(f"Tuner: {caps.tuner_type}")
    print(f"Frequency Range: {caps.frequency_range}")
    
    # Configure for automotive monitoring
    rtl_sdr.configure_for_automotive('key_fob_eu')  # 433.92 MHz
    
    # Check health
    health = rtl_sdr.check_health()
    print(f"Hardware Detected: {health['hardware_detected']}")
```

### PicoConnectionManager

Comprehensive Pico W connection management with heartbeat monitoring.

```python
from hardware.pico_connection_manager import PicoConnectionManager

# Initialize connection manager
pico_manager = PicoConnectionManager(server_host='0.0.0.0', server_port=8888)

# Start TCP server
await pico_manager.start_server()

# Start connection monitoring
await pico_manager.start_monitoring()

# Broadcast to all connected devices
data = {'type': 'alert', 'threat_level': 'HIGH'}
sent_count = await pico_manager.broadcast_to_devices(data)
print(f"Alert sent to {sent_count} devices")

# Check health
health = await pico_manager.check_health()
print(f"Connected Devices: {health['connected_devices']}")
```

### HardwareRecoverySystem

Hardware failure detection and recovery with exponential backoff.

```python
from hardware.recovery_system import HardwareRecoverySystem

# Initialize recovery system
recovery = HardwareRecoverySystem(rtl_sdr, pico_manager)

# Start monitoring
await recovery.start_monitoring()

# Add failure callback
def on_failure(component, failure_type, details):
    print(f"Hardware failure: {component} - {failure_type.value}")

recovery.add_failure_callback(on_failure)

# Get system health summary
health = recovery.get_system_health_summary()
print(f"Monitoring Active: {health['monitoring_active']}")
print(f"Active Recoveries: {health['active_recoveries']}")
```

## System Status Enumeration

```python
from hardware import SystemStatus

# System status values
SystemStatus.INITIALIZING  # System starting up
SystemStatus.READY        # All hardware operational
SystemStatus.DEGRADED     # Some hardware issues
SystemStatus.FAILED       # Hardware failures
SystemStatus.MOCK_MODE    # Demo/testing mode
```

## Hardware Capabilities

### RTL-SDR Capabilities

```python
@dataclass
class RTLSDRCapabilities:
    device_index: int
    device_name: str
    tuner_type: str
    frequency_range: Tuple[int, int]  # (min_freq, max_freq) in Hz
    sample_rates: List[int]           # Supported sample rates
    gain_values: List[float]          # Supported gain values
    usb_vendor_id: str
    usb_product_id: str
    serial_number: Optional[str] = None
    
    def supports_automotive_frequencies(self) -> bool:
        """Check if device supports automotive frequency bands."""
```

### Automotive Frequency Bands

```python
AUTOMOTIVE_FREQUENCIES = {
    'key_fob_na': 315000000,      # 315 MHz - North American key fobs, TPMS
    'key_fob_eu': 433920000,      # 433.92 MHz - European key fobs, TPMS
    'ism_868': 868000000,         # 868 MHz - European ISM band
    'cellular_700': 700000000,    # 700 MHz - Cellular band
    'cellular_850': 850000000,    # 850 MHz - Cellular band
}
```

## Health Monitoring

### System Health Status

```python
@dataclass
class HardwareHealth:
    rtl_sdr_status: RTLSDRStatus
    pico_connections: int
    total_pico_devices: int
    system_status: SystemStatus
    uptime: float
    last_health_check: float
    errors: List[str]
    warnings: List[str]
```

### Health Check Methods

```python
# Hardware manager health check
health = manager.get_health_status()

# RTL-SDR specific health check
rtl_health = rtl_sdr.check_health()

# Pico connections health check
pico_health = await pico_manager.check_health()

# Recovery system health summary
recovery_health = recovery.get_system_health_summary()
```

## Recovery Configuration

### Recovery Settings

```python
# Recovery system configuration
recovery_system = HardwareRecoverySystem(rtl_sdr, pico_manager)
recovery_system.max_recovery_attempts = 5
recovery_system.base_backoff_delay = 1.0  # seconds
recovery_system.max_backoff_delay = 300.0  # 5 minutes
recovery_system.backoff_multiplier = 2.0
recovery_system.health_check_interval = 15.0  # seconds
```

### Failure Types

```python
from hardware.recovery_system import FailureType

FailureType.DISCONNECTION        # Hardware disconnected
FailureType.TIMEOUT             # Communication timeout
FailureType.CONFIGURATION_ERROR # Configuration failure
FailureType.COMMUNICATION_ERROR # Communication failure
FailureType.UNKNOWN            # Unknown failure type
```

## Mock Mode Support

### Enabling Mock Mode

```python
# Enable mock mode for RTL-SDR
rtl_sdr.enable_mock_mode()

# Enable mock mode for Pico connections
await pico_manager.enable_mock_mode()

# Initialize hardware manager in mock mode
await manager.initialize(mock_mode=True)
```

### Mock Capabilities

- Complete hardware simulation without physical devices
- Realistic device capabilities and responses
- Demonstration-ready event generation
- Full API compatibility with real hardware

## Error Handling

### Exception Types

```python
# Hardware detection failures
try:
    if not rtl_sdr.detect_hardware():
        print("RTL-SDR not detected")
except Exception as e:
    print(f"Hardware detection error: {e}")

# Connection failures
try:
    await pico_manager.start_server()
except Exception as e:
    print(f"Server start error: {e}")
```

### Graceful Degradation

The system automatically handles hardware failures:

1. **Detection Phase**: Attempts hardware detection with timeout
2. **Configuration Phase**: Validates hardware capabilities
3. **Recovery Phase**: Automatic recovery attempts with exponential backoff
4. **Fallback Phase**: Graceful fallback to mock mode if recovery fails

## Integration Examples

### Complete System Initialization

```python
async def initialize_system():
    # Create hardware manager
    manager = HardwareManager(enable_auto_recovery=True)
    
    # Initialize hardware
    if await manager.initialize():
        print("Hardware initialized successfully")
        
        # Start monitoring
        await manager.start_monitoring()
        
        # Get interfaces
        rtl_sdr = manager.get_rtl_sdr_interface()
        pico_manager = manager.get_pico_manager()
        
        # Check if ready
        if manager.is_hardware_ready():
            print("System ready for operation")
            return manager
    
    return None
```

### Health Monitoring Loop

```python
async def monitor_system_health(manager):
    while True:
        health = manager.get_health_status()
        
        print(f"System Status: {health.system_status.value}")
        print(f"Uptime: {health.uptime:.1f}s")
        
        if health.errors:
            print(f"Errors: {health.errors}")
        
        await asyncio.sleep(30)  # Check every 30 seconds
```

## Best Practices

1. **Always use the HardwareManager** for coordinated hardware access
2. **Enable auto-recovery** for production deployments
3. **Check system status** before performing operations
4. **Use mock mode** for demonstrations and testing
5. **Monitor health regularly** for early failure detection
6. **Handle graceful degradation** when hardware fails
7. **Use appropriate timeouts** for hardware operations
8. **Log hardware events** for debugging and analysis

## Troubleshooting

### Common Issues

1. **RTL-SDR not detected**
   - Check USB connection and drivers
   - Verify rtl_test executable exists
   - Check device permissions

2. **Pico W connection failures**
   - Verify WiFi credentials in config.py
   - Check network connectivity
   - Ensure TCP port is available

3. **Recovery failures**
   - Check hardware connections
   - Verify driver installation
   - Review recovery attempt logs

### Diagnostic Commands

```python
# Get comprehensive diagnostic info
diagnostics = manager.get_diagnostic_info()
print(json.dumps(diagnostics, indent=2))

# Check RTL-SDR diagnostics
rtl_diagnostics = rtl_sdr.get_diagnostic_info()

# Check Pico connection diagnostics
pico_diagnostics = pico_manager.get_diagnostic_info()
```