# Automotive Security Capstone Backend (2025)

Real-time automotive RF/NFC security monitoring system with RTL-SDR V4 integration, multi-modal attack detection, and professional CLI dashboard.

## 🚀 Quick Start & Installation

### Prerequisites

- **Python 3.11+** (required)
- **uv package manager** (recommended) - [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- **RTL-SDR V4 dongle** (for real hardware mode)
- **Raspberry Pi Pico W** (optional, for alerting/NFC)

### Installation with uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/jondmarien/automotive-security-capstone.git
cd automotive-security-capstone/backend

# Install dependencies with uv (lightning fast!)
uv sync

# Build the project (native uv build backend - <1 second!)
uv build
```

### Available CLI Commands

After installation, you can run these CLI tools:

```bash
# Main dashboard (interactive monitoring)
uv run autosec-dashboard

# Demo modes for presentations
uv run autosec-demo-mock          # Dashboard with mock data
uv run autosec-demo-synthetic     # Dashboard with synthetic attack scenarios

# Hardware deployment
uv run autosec-deploy-pico        # Deploy code to Raspberry Pi Pico W

# Demo scenarios
uv run autosec-demo               # Run structured demo scenarios

# Hardware launcher
uv run autosec-hardware           # Launch with real hardware detection
```

### Build System Features

- ⚡ **Lightning-fast builds** with native uv build backend (<1 second)
- 🔧 **Modern Python packaging** with pyproject.toml configuration
- 📦 **Automatic dependency management** with uv.lock
- 🛠️ **CLI entry points** for all major tools
- 🚀 **Rust-powered performance** for build operations

## 🚘 Project Overview

- **RTL-SDR V4** dongle connects to a computer for RF signal capture.
- **Python signal processing** scripts analyze IQ samples and detect automotive events.
- **Detection events** are streamed over TCP to:
  - **Raspberry Pi Pico W** (for alerting/NFC)
  - **CLI Dashboard** (for real-time monitoring and demo)
- **No FastAPI/MongoDB backend** is required for the current MVP/POC.

## 🏗️ System Architecture

```sh
RTL-SDR V4
   │
   ▼
Computer (Windows/Linux)
 ├── rtl_tcp (raw IQ data server, port 1234)
 ├── signal_bridge.py (RF analysis, event detection)
 ├── rtl_tcp_server.py (TCP event server, port 8888)
 ├── cli_dashboard.py (Rich-based CLI dashboard, supports --mock mode)
 └── [optionally] startup_server.py (launches everything)
   │
   ▼
Raspberry Pi Pico W (TCP client, receives events, handles alerting/NFC)
```

## 📦 Key Components

### Core Components

- **`rtl_tcp_server.py`**: RTL-SDR management, TCP server (port 8888)
- **`signal_bridge.py`**: IQ sample processing, event detection (supports `--enhanced` mode)
- **`cli_dashboard.py`**: Rich CLI dashboard with navigation, export, mock/synthetic modes
- **`real_hardware_launcher.py`**: System orchestration with auto-detection and fallback
- **`hardware/`**: Hardware management (RTL-SDR interface, Pico connection, recovery system)
- **`pico/main.py`**: MicroPython client with NFC correlation and LED alerts

### Detection & Signal Processing

- **`detection/`**: Security analyzer, jamming/replay/brute-force detectors, threat classification
- **`rtl_sdr/`**: Automotive signal analyzer, enhanced signal bridge, history buffer
- **`utils/`**: Logging config, validation tools, performance monitoring
- **`deploy_pico.py`**: Automated Pico W deployment with serial management

### Enhanced Signal Processing & Threat Detection (NEW)

- `rtl_sdr/enhanced_signal_bridge.py`: **NEW** - Enhanced signal processing bridge with real-time IQ analysis and automotive signal detection
- `rtl_sdr/automotive_signal_analyzer.py`: Advanced automotive signal analysis with FSK detection and pattern recognition
- `rtl_sdr/brute_force_detector.py`: Enhanced brute force attack detector with temporal analysis, escalating threat levels, and improved test consistency handling
- `rtl_sdr/signal_history_buffer.py`: Signal history management for temporal analysis and replay detection

## 🛠️ Setup & Usage

### Quick Demo

```bash
uv run python cli_dashboard.py --mock              # Professional demo
uv run python cli_dashboard.py --mock --synthetic  # Advanced scenarios
```

### Full System

```bash
uv run python real_hardware_launcher.py           # Auto hardware detection
uv run python real_hardware_launcher.py --force-mock  # Force demo mode
```

### Manual Components (legacy)

```bash
uv run python rtl_tcp_server.py
uv run python signal_bridge.py --enhanced
uv run python cli_dashboard.py --source tcp
```

### Pico W Deployment

```sh
# Automatic deployment with port detection
uv run python deploy_pico.py

# Manual port specification
uv run python deploy_pico.py COM3  # Windows
uv run python deploy_pico.py /dev/ttyACM0  # Linux
```

#### Manual Setup (LEGACY)

- Flash MicroPython firmware
- Upload `main.py` and required libraries (see [docs/plans/migration_old/poc_migration_plan.md](docs/plans/migration_old/poc_migration_plan.md))
- Configure WiFi and server IP/port in `pico/config.py`
- Pico will connect to computer, receive detection events, and trigger alerts/NFC

#### Configuration

Update `pico/config.py` with your network settings:

```python
WIFI_SSID = "your_network_name"
WIFI_PASSWORD = "your_password"
TCP_HOST = "192.168.1.100"  # Your computer's IP
```

#### Deployment

```bash
uv run python deploy_pico.py              # Auto port detection
uv run python deploy_pico.py COM3         # Manual port
```

**Config**: Update `pico/config.py` with WiFi credentials and TCP_HOST IP

## Detection Capabilities

### CLI Dashboard Features

- Event navigation with technical evidence display
- Real-time signal visualization (RSSI, SNR, modulation, burst count)
- RF-NFC correlation indicators and professional UI layout

### Threat Detection

- **Replay Attacks**: Signal similarity analysis with temporal clustering
- **Jamming**: 4 pattern types (continuous, pulse, sweep, spot)
- **Brute Force**: Multi-window temporal analysis with escalating levels
- **RF-NFC Correlation**: Multi-modal attack detection with automatic escalation

### Threat Levels

`BENIGN` → `SUSPICIOUS` → `MODERATE` → `HIGH` → `CRITICAL`

## Testing & Validation

### Core Testing

```bash
# Full test suite with coverage
uv run pytest tests/ --cov=rtl_sdr --cov=detection --cov-report=html

# Detection accuracy validation (>90% requirement)
uv run python utils/validate_detection_accuracy.py

# Demo scenarios
uv run python demo_scenarios.py --scenario comprehensive
```

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test files
uv run pytest tests/test_signal_bridge.py -v
uv run pytest tests/test_cli_dashboard.py -v
uv run pytest tests/test_automotive_signal_analyzer.py -v
uv run pytest tests/test_brute_force_detector.py -v
uv run pytest tests/test_jamming_detector.py -v
uv run pytest tests/test_replay_attack_detector.py -v
uv run pytest tests/test_security_analyzer.py -v
uv run pytest tests/test_threat_levels.py -v
uv run pytest tests/test_signal_history_buffer.py -v
uv run pytest tests/test_enhanced_signal_bridge.py -v
uv run pytest tests/test_pico_nfc_correlation.py -v

# Run tests with coverage
uv run pytest tests/ --cov=rtl_sdr --cov-report=html
```

### Testing & Quality Assurance

- **89 comprehensive tests** with 100% pass rate
- **Enhanced test coverage** with realistic signal data and proper timestamps
- **Performance validation** with <100ms latency requirements
- **Mock hardware simulation** for testing without physical devices
- **Thread-safe operations** with concurrent access validation
- **>90% code coverage** for detection and signal processing modules

## Troubleshooting

### Common Issues

- **RTL-SDR not detected?** Use `rtl_test` to verify driver installation, or run `python real_hardware_launcher.py --force-mock` for demo mode
- **Pico W won't connect?** Check WiFi credentials in `pico/config.py` and ensure TCP_HOST matches your computer's IP address
- **Hardware failures?** The system includes automatic recovery - check logs for recovery attempts and fallback to mock mode

### System Issues

- **No events in dashboard?** Use the new `uv run python real_hardware_launcher.py` for automatic system orchestration, or ensure all components are running manually
- **Testing without hardware?** Use `uv run python cli_dashboard.py --mock` (RECOMMENDED) or `uv run python real_hardware_launcher.py --force-mock` for demo mode
- **Firewall issues?** Allow port 8888 for incoming TCP connections
- **Performance issues?** Check system health with the hardware manager's diagnostic tools

### Logging & Debugging

- **System logs**: Check `logs/dashboard-YYYY-MM-DD/` for organized log files with timestamps
- **Hardware diagnostics**: Use `uv run python real_hardware_launcher.py` for comprehensive hardware status reporting
- **Validation issues**: Run `uv run python utils/validate_detection_accuracy.py` to verify >90% detection accuracy requirement

## Technical Notes

- **Architecture**: Pure TCP streaming, no web API or database required
- **Hardware setup**: See [`docs/plans/migration_old/poc_migration_plan.md`](docs/plans/migration_old/poc_migration_plan.md)
- **References**: [RTL-SDR Guide](https://www.rtl-sdr.com/rtl-sdr-quick-start-guide/), [Pico W MicroPython](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)
