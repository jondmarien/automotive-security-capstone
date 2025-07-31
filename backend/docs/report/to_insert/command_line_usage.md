# Command Line Usage Guide for Final Report

This section provides comprehensive documentation for running the automotive security monitoring system from the command line, including all scripts, tests, and operational modes.

## Core System Commands

### 1. Demo Mode (Recommended for Presentations)

#### Basic Demo Mode
```bash
# Navigate to backend directory
cd backend

# Start CLI dashboard with realistic mock events
uv run python cli_dashboard.py --mock

# Features:
# - No hardware required
# - Realistic automotive security events
# - Professional CLI interface
# - Event navigation with arrow keys
# - Press 'q' to quit
```

#### Advanced Demo Mode
```bash
# Advanced demo with synthetic signal generation
uv run python cli_dashboard.py --mock --synthetic

# Features:
# - Advanced synthetic signal testing
# - Realistic signal characteristics
# - Comprehensive attack scenarios
# - Technical evidence display
```

#### Specific Event Analysis
```bash
# View specific event for detailed analysis
uv run python cli_dashboard.py --mock --event 3

# Features:
# - Focus on specific event type
# - Detailed technical evidence
# - Signal analysis visualization
# - Perfect for demonstrations
```

### 2. Complete System Launch

#### Automatic System Launch (Recommended)
```bash
# Launch complete system with hardware detection
uv run python real_hardware_launcher.py

# Features:
# - Automatic RTL-SDR detection
# - Pico W connection management
# - Hardware failure recovery
# - Graceful fallback to mock mode
# - Comprehensive logging
```

#### System Launch Options
```bash
# Force demo mode for presentations
uv run python real_hardware_launcher.py --force-mock

# Custom frequency configuration (315MHz for North America)
uv run python real_hardware_launcher.py --frequency 315000000

# European frequency (433.92MHz - default)
uv run python real_hardware_launcher.py --frequency 433920000

# Custom sample rate
uv run python real_hardware_launcher.py --sample-rate 2048000
```

### 3. Manual Component Launch (Legacy)

#### RTL-SDR Server
```bash
# Start RTL-SDR TCP server
uv run python rtl_sdr/rtl_tcp_server.py

# Options:
# --port 1234          # TCP port (default: 1234)
# --frequency 433920000 # Center frequency in Hz
# --sample-rate 2048000 # Sample rate in Hz
# --gain auto          # Gain setting (auto or dB value)
```

#### Signal Processing Bridge
```bash
# Standard signal processing
uv run python rtl_sdr/signal_bridge.py

# Enhanced signal processing (recommended)
uv run python rtl_sdr/signal_bridge.py --enhanced

# Options:
# --host localhost     # RTL-TCP server host
# --port 1234         # RTL-TCP server port
# --enhanced          # Use enhanced automotive signal analysis
# --debug             # Enable debug logging
```

#### CLI Dashboard
```bash
# Connect to live TCP event stream
uv run python cli_dashboard.py --source tcp --tcp-host localhost --tcp-port 8888

# API polling mode (future)
uv run python cli_dashboard.py --source api --api-url http://localhost:8000/events

# Options:
# --source tcp|api|mock  # Event source type
# --tcp-host HOST       # TCP server hostname
# --tcp-port PORT       # TCP server port
# --mock               # Use mock events
# --synthetic          # Use synthetic signal generation
# --event N            # Focus on specific event type
```

## Hardware Management Commands

### RTL-SDR Hardware Testing

#### Basic Hardware Detection
```bash
# Test RTL-SDR hardware detection
rtl_test

# Extended hardware test with tuner information
rtl_test -t

# Test specific device
rtl_test -d 0
```

#### Manual RTL-TCP Server
```bash
# Start RTL-TCP server manually
rtl_tcp -a 127.0.0.1 -p 1234

# Options:
# -a ADDRESS    # Bind address (default: 127.0.0.1)
# -p PORT       # Port number (default: 1234)
# -f FREQ       # Center frequency in Hz
# -s RATE       # Sample rate in Hz
# -g GAIN       # Gain in dB
# -d DEVICE     # Device index
```

#### Frequency Analysis Tools
```bash
# Scan automotive frequency bands
rtl_power -f 300M:450M:1M -i 10

# Listen to specific frequency
rtl_fm -f 433.92M -M fm -s 200k

# Save IQ samples to file
rtl_sdr -f 433920000 -s 2048000 -n 1024000 samples.bin
```

### Pico W Deployment

#### Automated Deployment
```bash
# Automatic port detection and deployment
uv run python deploy_pico.py

# Manual port specification
uv run python deploy_pico.py COM3              # Windows
uv run python deploy_pico.py /dev/ttyACM0      # Linux
uv run python deploy_pico.py /dev/cu.usbmodem* # macOS

# Options:
# --port PORT          # Serial port
# --baudrate RATE      # Baud rate (default: 115200)
# --timeout SECONDS    # Connection timeout
# --test-connection    # Test connection only
```

#### Manual Deployment Tools
```bash
# Using rshell for manual file transfer
rshell -p COM3
> cp backend/pico/main.py /pyboard/
> cp backend/pico/config.py /pyboard/
> cp backend/pico/NFC_PN532.py /pyboard/
> repl  # Enter REPL mode
```

## Testing and Validation Commands

### Unit Testing

#### Run All Tests
```bash
# Run complete test suite
uv run pytest tests/ -v

# Run tests with coverage report
uv run pytest tests/ --cov=backend --cov-report=html

# Run tests with coverage and generate XML report
uv run pytest tests/ --cov=backend --cov-report=xml --cov-report=term
```

#### Specific Test Categories
```bash
# Run unit tests only (fast)
uv run pytest tests/ -m unit -v

# Run integration tests
uv run pytest tests/ -m integration -v

# Skip hardware-dependent tests
uv run pytest tests/ -m "not hardware" -v

# Run only hardware tests (requires RTL-SDR)
uv run pytest tests/ -m hardware -v

# Run performance tests
uv run pytest tests/ -m slow -v
```

#### Specific Test Files
```bash
# Core signal processing tests
uv run pytest tests/test_automotive_signal_analyzer.py -v
uv run pytest tests/test_enhanced_signal_bridge.py -v
uv run pytest tests/test_signal_history_buffer.py -v

# Detection engine tests
uv run pytest tests/test_security_analyzer.py -v
uv run pytest tests/test_jamming_detector.py -v
uv run pytest tests/test_replay_attack_detector.py -v
uv run pytest tests/test_brute_force_detector.py -v

# Dashboard and UI tests
uv run pytest tests/test_cli_dashboard.py -v

# Hardware management tests
uv run pytest tests/test_hardware_manager.py -v
uv run pytest tests/test_rtl_sdr_interface.py -v
uv run pytest tests/test_pico_connection_manager.py -v

# NFC correlation tests
uv run pytest tests/test_pico_nfc_correlation.py -v
```

#### Test Output Options
```bash
# Verbose output with test names
uv run pytest tests/ -v

# Show print statements
uv run pytest tests/ -s

# Shorter traceback format
uv run pytest tests/ --tb=short

# Stop on first failure
uv run pytest tests/ -x

# Run specific test function
uv run pytest tests/test_automotive_signal_analyzer.py::TestAutomotiveSignalAnalyzer::test_fsk_detection -v
```

### Detection Accuracy Validation

#### Automated Validation
```bash
# Run detection accuracy validation (>90% requirement)
uv run python utils/validate_detection_accuracy.py

# Custom validation parameters
uv run python utils/validate_detection_accuracy.py --samples 200 --output-dir validation_results

# Comprehensive validation with detailed output
uv run python utils/validate_detection_accuracy.py --samples 500 --output-dir results --verbose
```

#### Manual Validation
```bash
# Generate confusion matrix and performance metrics
uv run python -c "
from utils.detection_accuracy import run_accuracy_validation
import asyncio
result = asyncio.run(run_accuracy_validation(num_samples=100))
print(f'Accuracy: {result[\"accuracy\"]:.2%}')
print(f'Meets requirement: {result[\"meets_accuracy_requirement\"]}')
"
```

### Demo Scenarios

#### Structured Demonstrations
```bash
# Run comprehensive demonstration scenario
uv run python demo_scenarios.py --scenario comprehensive

# Run specific attack scenarios
uv run python demo_scenarios.py --scenario replay
uv run python demo_scenarios.py --scenario jamming
uv run python demo_scenarios.py --scenario brute_force
uv run python demo_scenarios.py --scenario key_fob

# Save scenario events to file
uv run python demo_scenarios.py --scenario comprehensive --output demo_events.json

# Custom scenario parameters
uv run python demo_scenarios.py --scenario replay --duration 60 --events 20
```

## System Diagnostics and Monitoring

### Hardware Diagnostics

#### System Health Check
```bash
# Comprehensive system diagnostics
uv run python -c "
from hardware import HardwareManager
import asyncio
import json

async def diagnostics():
    manager = HardwareManager()
    await manager.initialize()
    health = manager.get_health_status()
    diag = manager.get_diagnostic_info()
    
    print(f'System Status: {health.system_status.value}')
    print(f'RTL-SDR Status: {health.rtl_sdr_status.value}')
    print(f'Pico W Connections: {health.pico_connections}/{health.total_pico_devices}')
    print(f'Uptime: {health.uptime:.1f}s')
    print(f'Diagnostics: {json.dumps(diag, indent=2)}')

asyncio.run(diagnostics())
"
```

#### Real-time Health Monitoring
```bash
# Monitor system health in real-time
uv run python -c "
from hardware import HardwareManager
import asyncio

async def monitor():
    manager = HardwareManager()
    await manager.initialize()
    await manager.start_monitoring()
    
    print('Starting real-time health monitoring (Ctrl+C to stop)...')
    try:
        while True:
            health = manager.get_health_status()
            print(f'[{health.timestamp}] Status: {health.system_status.value}, '
                  f'RTL-SDR: {health.rtl_sdr_status.value}, '
                  f'Pico W: {health.pico_connections}, '
                  f'Uptime: {health.uptime:.1f}s')
            await asyncio.sleep(30)
    except KeyboardInterrupt:
        print('Monitoring stopped.')

asyncio.run(monitor())
"
```

### Performance Testing

#### Signal Processing Performance
```bash
# Test signal processing performance
uv run pytest tests/test_automotive_signal_analyzer.py::TestAutomotiveSignalAnalyzer::test_performance -v

# Test real-time processing requirements
uv run pytest tests/test_enhanced_signal_bridge.py::TestEnhancedSignalBridge::test_real_time_processing -v

# Memory usage testing
uv run pytest tests/test_signal_history_buffer.py::TestSignalHistoryBuffer::test_memory_management -v
```

#### System Load Testing
```bash
# Run performance validation
uv run python -c "
from utils.detection_accuracy import run_performance_validation
import asyncio
result = asyncio.run(run_performance_validation())
print(f'Average processing time: {result[\"avg_processing_time_ms\"]:.1f}ms')
print(f'Meets performance requirement: {result[\"meets_performance_requirement\"]}')
"
```

## Code Quality and Linting

### Code Formatting
```bash
# Format code with Black
uv run black .

# Sort imports with isort
uv run isort .

# Combined formatting
uv run black . && uv run isort .
```

### Code Quality Checks
```bash
# Style and complexity checking with flake8
uv run flake8

# Type checking with mypy
uv run mypy .

# Security scanning with bandit
uv run bandit -r backend/

# Dependency vulnerability checking
uv run safety check
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files

# Update pre-commit hooks
pre-commit autoupdate
```

## Logging and Debug Commands

### Log Management
```bash
# View recent dashboard logs
tail -f logs/dashboard-$(date +%Y-%m-%d)/dashboard-*.log

# View system logs
tail -f logs/real_hardware_system.log

# Search logs for errors
grep -r "ERROR" logs/

# Search logs for specific events
grep -r "MALICIOUS" logs/
```

### Debug Mode
```bash
# Run with debug logging
LOG_LEVEL=DEBUG uv run python cli_dashboard.py --mock

# Run with verbose output
uv run python real_hardware_launcher.py --verbose

# Enable debug mode for specific components
DEBUG_MODE=true uv run python rtl_sdr/signal_bridge.py --enhanced
```

## Utility Scripts

### Signal Analysis Tools
```bash
# Generate synthetic signals for testing
uv run python -c "
from utils.signal_generator import generate_key_fob_signal
signal = generate_key_fob_signal()
print(f'Generated signal: {len(signal[\"samples\"])} samples at {signal[\"sample_rate\"]} Hz')
"

# Analyze recorded signals
uv run python utils/signal_analyzer.py --input samples.bin --sample-rate 2048000
```

### Configuration Management
```bash
# Validate configuration files
uv run python -c "
from utils.config_manager import validate_config
result = validate_config('config/default.yaml')
print(f'Configuration valid: {result}')
"

# Generate default configuration
uv run python utils/config_manager.py --generate-default --output config/new_config.yaml
```

## Environment and Package Management

### UV Package Manager Commands
```bash
# Create virtual environment
uv venv

# Install dependencies
uv pip install -r requirements.txt

# Install development dependencies
uv pip install -r requirements-dev.txt

# Update dependencies
uv pip install --upgrade -r requirements.txt

# List installed packages
uv pip list

# Show package information
uv pip show numpy

# Generate requirements file
uv pip freeze > requirements-current.txt
```

### Traditional pip Commands
```bash
# Activate virtual environment
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Update all packages
pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U
```

## Quick Reference Commands

### Most Common Operations
```bash
# Quick demo (most common)
uv run python cli_dashboard.py --mock

# Complete system launch
uv run python real_hardware_launcher.py

# Run all tests
uv run pytest tests/ -v

# Validate detection accuracy
uv run python utils/validate_detection_accuracy.py

# Deploy Pico W
uv run python deploy_pico.py

# Check system health
uv run python -c "from hardware import HardwareManager; import asyncio; asyncio.run(HardwareManager().initialize())"
```

### Emergency Commands
```bash
# Force stop all processes
pkill -f "python.*automotive"  # Linux/macOS
taskkill /f /im python.exe     # Windows

# Reset RTL-SDR device
sudo rmmod dvb_usb_rtl28xxu rtl2832 rtl2830  # Linux
sudo modprobe dvb_usb_rtl28xxu

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +  # Linux/macOS
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"  # Windows
```

This comprehensive command line usage guide covers all aspects of operating the automotive security monitoring system from the command line, including testing, validation, deployment, and troubleshooting.