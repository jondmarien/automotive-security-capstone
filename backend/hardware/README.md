# Hardware Abstraction Layer (HAL)

## Overview
The Hardware Abstraction Layer (HAL) provides a unified interface for interacting with various hardware components used in automotive security applications. It's designed to be modular, extensible, and hardware-agnostic.

## Key Components

### 1. Core Components
- `EdgeDevice`: Main device class that coordinates hardware components
- `EdgeDAO`: Data Access Object for storing and retrieving device data
- `HardwareFactory`: Factory for creating hardware interface instances
- `AntennaManager`: Manages antenna configurations and operations
- `SignalFilter`: Filters and processes incoming RF signals

### 2. Interfaces
- `RFInterface`: Abstract base class for RF hardware
- `PowerInterface`: Manages power states and battery information
- `StatusInterface`: Provides system status and metrics

### 3. Models
- `RFConfig`: Configuration for RF hardware
- `SignalMetrics`: Metrics for signal analysis
- `PowerState`: Power state information
- `MemoryUsage`: System memory usage statistics

## Getting Started

### Installation
```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest tests/
```

### Basic Usage
```python
from hardware import EdgeDevice, RFConfig

# Create and configure a device
device = EdgeDevice()
rf_config = RFConfig(
    frequency=433.92,
    tx_power=20,
    rx_gain=40,
    bandwidth=250000
)

# Initialize and start the device
await device.initialize(rf_config)
await device.start_receiving()

# Process incoming packets
packet = await device.receive_packet()
print(f"Received packet: {packet}")
```

## Development

### Adding New Hardware
1. Create a new driver in `drivers/`
2. Implement the relevant interface(s)
3. Update the factory to support the new hardware
4. Add tests in `tests/hardware/`

### Testing
Run the test suite:
```bash
poetry run pytest tests/
```

## Documentation
Detailed API documentation is available in the `docs/` directory.

## License
MIT License

## Contributing
Contributions are welcome! Please read our contributing guidelines before submitting pull requests.
