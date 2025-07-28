# Technology Stack & Implementation Guide

## Core Technologies & Rationale

### Primary Programming Language
- **Python 3.11+**: Primary backend language
  - **Rationale**: Excellent ecosystem for signal processing, scientific computing, and rapid prototyping
  - **Key Features Used**: Type hints, asyncio, dataclasses, pathlib
  - **Performance**: Sufficient for real-time RF processing with NumPy acceleration
  - **Educational Value**: Widely used in cybersecurity and accessible to students

### Hardware Components

#### RTL-SDR V4 Dongle
- **Model**: RTL-SDR Blog V4 (R828D tuner + RTL2832U)
- **Frequency Range**: 500 kHz - 1.75 GHz (covers automotive frequencies)
- **Sample Rate**: Up to 3.2 MS/s (configurable)
- **Interface**: USB 3.0 for high-speed data transfer
- **Driver**: librtlsdr with Python bindings
- **Cost**: ~$30 USD (excellent price/performance ratio)
- **Automotive Relevance**: Covers key fob (315/433 MHz), TPMS (315/433 MHz), cellular (700-2100 MHz)

#### Raspberry Pi Pico W
- **MCU**: RP2040 dual-core ARM Cortex-M0+ @ 133MHz
- **Wireless**: 802.11n WiFi (2.4GHz band)
- **GPIO**: 26 programmable pins for LEDs, sensors, displays
- **Programming**: MicroPython for rapid development
- **Power**: USB or external 5V supply
- **Cost**: ~$6 USD (extremely cost-effective)
- **Role**: Dedicated alert system, NFC interface, physical indicators

### Signal Processing & Analysis Stack

#### NumPy Ecosystem
- **NumPy**: Core numerical computing, FFT operations, array processing
- **SciPy**: Advanced signal processing functions (filters, spectrograms)
- **Matplotlib**: Signal visualization and debugging (development only)
- **Performance**: Vectorized operations for real-time processing

#### RF Signal Processing Libraries
- **pyrtlsdr**: Python wrapper for RTL-SDR hardware
- **GNU Radio**: Optional advanced signal processing (future enhancement)
- **Custom DSP**: Tailored algorithms for automotive signal patterns

### User Interface & Visualization

#### Rich Terminal UI Framework
- **Rich**: Modern terminal UI with colors, tables, progress bars
- **Features**: Live updating displays, syntax highlighting, emoji support
- **Advantages**: Professional appearance, cross-platform, no GUI dependencies
- **Performance**: Minimal overhead, suitable for real-time updates
- **Demo-friendly**: Excellent for presentations and screenshots

#### Logging & Monitoring
- **Python logging**: Structured logging with configurable levels
- **File-based logs**: Persistent event storage for analysis
- **Real-time display**: Live event streaming in terminal
- **JSON formatting**: Machine-readable log format for future analysis

## Build System & Package Management

### Modern Python Tooling (Preferred)
- **UV**: Next-generation Python package manager
  - **Speed**: 10-100x faster than pip for dependency resolution
  - **Reliability**: Deterministic dependency resolution
  - **Compatibility**: Drop-in pip replacement
  - **Installation**: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Traditional Tooling (Fallback)
- **pip**: Standard Python package manager
- **venv**: Virtual environment management
- **requirements.txt**: Dependency specification

### Project Configuration
- **pyproject.toml**: Modern Python project configuration (PEP 518)
- **setup.py**: Legacy setup script (maintained for compatibility)
- **pytest.ini**: Test configuration and markers

## Key Libraries & Frameworks

### Web Framework (Future Expansion)
- **FastAPI**: Modern async web framework
  - **Features**: Automatic API documentation, type validation, async support
  - **Performance**: High-performance ASGI framework
  - **Integration**: Seamless Pydantic integration
  - **Future Use**: Web dashboard, REST API for external integrations

### Data Validation & Settings
- **Pydantic**: Data validation using Python type annotations
  - **Use Cases**: Configuration management, API request/response validation
  - **Features**: Automatic validation, serialization, JSON schema generation
  - **Type Safety**: Runtime type checking with excellent IDE support

### Async HTTP & Networking
- **aiohttp**: Async HTTP client/server framework
  - **Use Cases**: External API calls, webhook integrations
  - **Performance**: Non-blocking I/O for concurrent operations
  - **Integration**: Native asyncio support

### Database (Future Integration)
- **Motor**: Async MongoDB driver
- **PyMongo**: Synchronous MongoDB driver (fallback)
- **Use Cases**: Event storage, historical analysis, configuration persistence
- **Current Status**: Not required for MVP, TCP streaming sufficient

### Testing Framework
- **pytest**: Modern testing framework
  - **Features**: Fixtures, parametrized tests, plugin ecosystem
  - **Async Support**: pytest-asyncio for testing async code
  - **Coverage**: pytest-cov for code coverage analysis
  - **Markers**: Custom test categories (hardware, integration, slow)

## Development Tools & Code Quality

### Code Formatting & Style
- **Black**: Uncompromising code formatter
  - **Configuration**: Line length 88, string normalization
  - **Integration**: Pre-commit hooks, IDE integration
  - **Benefits**: Consistent code style, reduced bike-shedding

- **isort**: Import statement organizer
  - **Configuration**: Black-compatible profile
  - **Features**: Automatic import sorting and grouping
  - **Integration**: Works seamlessly with Black

### Code Quality & Linting
- **flake8**: Style guide enforcement (PEP 8)
  - **Plugins**: Additional checks for complexity, naming, security
  - **Configuration**: Customized for project-specific rules
  - **CI Integration**: Automated checks in development workflow

- **mypy**: Static type checker
  - **Configuration**: Strict mode with gradual typing adoption
  - **Benefits**: Catch type-related bugs before runtime
  - **IDE Integration**: Real-time type checking in development

### Hardware Simulation & Testing
- **bless**: Bluetooth Low Energy server simulation
- **pywifi**: WiFi interface management for testing
- **cryptography**: Cryptographic operations for security testing
- **pyserial**: Serial communication for hardware interfaces

## System Architecture & Communication

### Network Architecture
- **TCP Streaming**: Primary inter-component communication
  - **RTL-TCP Server**: Port 1234 (RTL-SDR standard)
  - **Event Server**: Port 8888 (custom event streaming)
  - **Benefits**: Low latency, reliable delivery, simple implementation

### Asynchronous Programming
- **asyncio**: Core async framework
  - **Event Loop**: Single-threaded concurrent execution
  - **Coroutines**: Non-blocking I/O operations
  - **Tasks**: Concurrent execution of multiple operations
  - **Benefits**: Efficient resource utilization, responsive UI

### Data Models & Serialization
- **Pydantic Models**: Type-safe data structures
  - **Packet Class**: RF signal representation
  - **Event Class**: Security event representation
  - **Configuration**: System settings and parameters
  - **Validation**: Automatic data validation and conversion

## Common Commands & Workflows

### Environment Setup & Management
```bash
# Modern approach with UV (recommended)
uv venv                                    # Create virtual environment
uv pip install -r requirements.txt        # Install dependencies
uv pip install -e .                       # Install project in development mode

# Traditional approach with pip
python -m venv .venv                       # Create virtual environment
.venv\Scripts\activate                     # Activate (Windows)
source .venv/bin/activate                  # Activate (Linux/Mac)
pip install -r requirements.txt           # Install dependencies
pip install -e .                          # Install project in development mode
```

### System Operation Workflows

#### Development Mode (Mock Data)
```bash
# Start CLI dashboard with simulated data
python cli_dashboard.py --mock

# Benefits: No hardware required, predictable test data, demo-ready
```

#### Hardware Mode (Live RF)
```bash
# Terminal 1: Start RTL-SDR server
python rtl_sdr/rtl_tcp_server.py

# Terminal 2: Start signal processing bridge
python rtl_sdr/signal_bridge.py

# Terminal 3: Start CLI dashboard
python cli_dashboard.py --source tcp --tcp-host localhost --tcp-port 8888

# Alternative: Use startup orchestration script
python rtl_sdr/startup_server.py
```

#### API Mode (Future)
```bash
# Start web API server
uvicorn main:app --reload --port 8000

# Start dashboard with API polling
python cli_dashboard.py --source api --api-url http://localhost:8000/events
```

### Testing & Quality Assurance
```bash
# Run complete test suite
pytest                                     # All tests
pytest --cov                              # With coverage report
pytest --cov-report=html                  # HTML coverage report

# Run specific test categories
pytest -m "not slow"                      # Skip slow tests (hardware)
pytest -m integration                     # Only integration tests
pytest -m hardware                        # Only hardware tests (requires RTL-SDR)
pytest -m unit                           # Only unit tests

# Run tests with verbose output
pytest -v                                 # Verbose test names
pytest -s                                # Show print statements
pytest --tb=short                        # Shorter traceback format
```

### Code Quality Checks
```bash
# Format code
black .                                   # Format all Python files
isort .                                   # Sort imports

# Check code quality
flake8                                    # Style and complexity checks
mypy .                                    # Type checking

# Run all quality checks
black . && isort . && flake8 && mypy .   # Complete quality pipeline
```

### Hardware Testing & Diagnostics
```bash
# Test RTL-SDR hardware connection
rtl_test                                  # Basic hardware test
rtl_test -t                              # Extended test with tuner info

# Manual RTL-TCP server (debugging)
rtl_tcp -a 127.0.0.1 -p 1234            # Standard RTL-TCP server
rtl_tcp -a 0.0.0.0 -p 1234              # Accept external connections

# Frequency scanning and analysis
rtl_power -f 300M:450M:1M -i 10          # Scan automotive frequencies
rtl_fm -f 433.92M -M fm -s 200k          # Listen to specific frequency
```

### Raspberry Pi Pico W Development
```bash
# Flash MicroPython firmware (one-time setup)
# 1. Hold BOOTSEL button while connecting USB
# 2. Copy micropython.uf2 to RPI-RP2 drive
# 3. Device will reboot with MicroPython

# Deploy code to Pico W
# Use Thonny IDE or rshell for file transfer
rshell -p COM3                           # Connect to Pico W (Windows)
rshell -p /dev/ttyACM0                   # Connect to Pico W (Linux)
```

## Performance Considerations & Optimization

### Real-time Processing Requirements
- **Latency Target**: <100ms from signal capture to threat detection
- **Throughput**: Handle 3.2 MS/s sample rate from RTL-SDR
- **Memory Usage**: Efficient buffer management for continuous operation
- **CPU Usage**: Optimize FFT operations and pattern matching

### Scalability Considerations
- **Multiple RTL-SDR**: Architecture supports multiple dongles
- **Distributed Processing**: TCP architecture enables remote processing
- **Event Buffering**: Handle burst events without data loss
- **Resource Monitoring**: Track system performance and health

### Error Handling & Reliability
- **Graceful Degradation**: Continue operation with reduced functionality
- **Hardware Disconnection**: Detect and handle hardware failures
- **Network Issues**: Robust TCP connection management
- **Data Validation**: Comprehensive input validation and sanitization

## Security & Privacy Considerations

### Data Handling
- **Local Processing**: All RF data processed locally (no cloud transmission)
- **Minimal Storage**: Only store essential event metadata
- **Encryption**: Future enhancement for sensitive data
- **Access Control**: File system permissions for log files

### Ethical Considerations
- **Educational Use**: System designed for learning and research
- **Legal Compliance**: Operates within legal RF monitoring boundaries
- **Responsible Disclosure**: Any vulnerabilities discovered should be reported responsibly
- **Privacy Respect**: No personal data collection or transmission monitoring