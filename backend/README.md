# Automotive Security Capstone Backend (2025)

This backend powers the Automotive Security Capstone POC, enabling real-time automotive RF and NFC event detection, logging, and demo visualization via an enhanced CLI dashboard with technical evidence presentation and signal analysis visualization.

## 🚘 Project Overview

- **RTL-SDR V4** dongle connects to a computer for RF signal capture.
- **Python signal processing** scripts analyze IQ samples and detect automotive events.
- **Detection events** are streamed over TCP to:
  - **Raspberry Pi Pico W** (for alerting/NFC)
  - **CLI Dashboard** (for real-time monitoring and demo)
- **No FastAPI/MongoDB backend** is required for the current MVP/POC.

## 🏗️ System Architecture

```
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

### Core System Components
- `rtl_tcp_server.py`: Manages RTL-SDR, launches `rtl_tcp`, listens for Pico clients and dashboard on TCP (default: 8888)
- `signal_bridge.py`: Reads IQ samples from RTL-SDR, detects events, sends to TCP server (supports enhanced mode)
- `cli_dashboard.py`: Rich-powered CLI dashboard for real-time event display with signal analysis details, technical evidence presentation, and event navigation; supports `--mock` for demo/testing and `--event` for specific event selection
- `pico/main.py`: MicroPython client for Pico W; connects to computer, receives events, triggers LEDs/NFC, and provides advanced RF-NFC correlation for multi-modal attack detection

### Enhanced Signal Processing & Threat Detection (NEW)
- `rtl_sdr/enhanced_signal_bridge.py`: **NEW** - Enhanced signal processing bridge with real-time IQ analysis and automotive signal detection
- `rtl_sdr/automotive_signal_analyzer.py`: Advanced automotive signal analysis with FSK detection and pattern recognition
- `rtl_sdr/brute_force_detector.py`: Enhanced brute force attack detector with temporal analysis, escalating threat levels, and improved test consistency handling
- `rtl_sdr/signal_history_buffer.py`: Signal history management for temporal analysis and replay detection

### Advanced Detection Modules
- `detection/jamming_detector.py`: Advanced jamming detection for RF interference patterns and denial-of-service attacks
- `detection/security_analyzer.py`: Comprehensive security analyzer for replay attacks, jamming, and brute force detection
- `detection/threat_levels.py`: Standardized threat level classification system (LOW, MEDIUM, HIGH, CRITICAL)
- `detection/replay_attack_detector.py`: Sophisticated replay attack detection with temporal analysis

## 🛠️ Setup & Usage

### 0. Key System Features

#### RF-NFC Correlation System
- **Function**: Correlates suspicious RF signals with NFC card/tag proximity
- **Operation**: Automatically activates when high-threat RF events are detected
- **Results**: Generates specialized `correlated_security_event` with comprehensive technical evidence
- **Configuration**: Default timeout of 30 seconds, automatically deactivates

### 1. Computer-Side (Windows/Linux)

1. **Install RTL-SDR drivers/tools** (see [docs/poc_migration_plan.md](../docs/poc_migration_plan.md))
2. **Set up Python environment**

```sh
   python -m venv .venv
   .venv\Scripts\activate  # (Windows) or source .venv/bin/activate (Linux)
   pip install -r requirements.txt
```

3. **Start RTL-TCP server and event bridge**

```sh
   # Standard mode (legacy signal processing)
   python rtl_tcp_server.py
   python signal_bridge.py
   
   # Enhanced mode (advanced automotive signal analysis)
   python rtl_tcp_server.py
   python signal_bridge.py --enhanced
   
   # Or use startup orchestration:
   python startup_server.py
```

4. **Run the CLI dashboard (real events or mock mode)**

```sh
   # For live events (requires running TCP server with events):
   python cli_dashboard.py --source tcp --tcp-host localhost --tcp-port 8888
   # For demo/testing (no hardware required):
   python cli_dashboard.py --mock
   # To view a specific event by index:
   python cli_dashboard.py --mock --event 3
```

### 2. Pico-Side (Raspberry Pi Pico W)

- Flash MicroPython firmware
- Upload `main.py` and required libraries (see [docs/poc_migration_plan.md](../docs/poc_migration_plan.md))
- Configure WiFi and server IP/port (default: 8888)
- Pico will connect to computer, receive detection events, and trigger alerts/NFC

## 🔍 Detection Capabilities & Dashboard Features

### Enhanced CLI Dashboard
- **Event Navigation**: Navigate through event history using arrow keys to view technical evidence for previous events
- **Signal Analysis Visualization**: Real-time visualization of signal metrics including RSSI, SNR, modulation type, and burst count
- **Technical Evidence Panel**: Detailed presentation of attack-specific technical evidence with proper formatting
- **NFC Correlation Indicators**: Visual indicators showing RF-NFC correlation status
- **Optimized Layout**: Maximized event table space (75%) with analysis panels at bottom
- **Professional UI**: Minimalistic event table with proper styling and no wrapping issues

### Enhanced Threat Detection Engine
The system now includes sophisticated multi-layer threat detection with temporal analysis and escalating threat levels.

### RF-NFC Correlation System (NEW)
- **Multi-Modal Attack Detection**: Correlates RF attacks with physical proximity NFC activity
- **Threat Escalation Logic**: Automatically increases threat level when RF and NFC activities coincide
- **Technical Evidence Collection**: Comprehensive evidence gathering for correlated security events
- **Automatic Timeout Management**: Self-deactivates correlation mode after configurable timeout
- **Enhanced Security Events**: Generates specialized `correlated_security_event` with technical evidence

### Detection Types
- **Rolling Code Replay Attacks**: Advanced detection using signal similarity analysis and temporal clustering
- **Jamming Detection**: Comprehensive RF interference detection with four pattern types:
  - **Continuous Jamming**: Sustained high power with low variance detection
  - **Pulse Jamming**: Periodic high-power bursts with regular timing analysis  
  - **Sweep Jamming**: Systematic frequency progression with directional consistency
  - **Spot Jamming**: Narrow-band high power with >10:1 peak-to-average ratio
- **Brute Force Attacks**: Enhanced detection with temporal analysis and escalating threat levels (suspicious → moderate → high → critical)
- **Signal Injection**: Identifies unauthorized signal injection attempts with pattern recognition
- **RF Interference**: Monitors for general RF interference with confidence scoring

### Threat Level Classification
- **BENIGN**: Normal automotive signal activity
- **SUSPICIOUS**: Potential threat requiring monitoring
- **MODERATE**: Clear indicators of malicious activity
- **HIGH**: Active attack with significant threat level
- **CRITICAL**: Immediate threat requiring urgent response

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_signal_bridge.py -v
python -m pytest tests/test_cli_dashboard.py -v
python -m pytest tests/test_automotive_signal_analyzer.py -v
python -m pytest tests/test_brute_force_detector.py -v
python -m pytest tests/test_jamming_detector.py -v
python -m pytest tests/test_replay_attack_detector.py -v
python -m pytest tests/test_security_analyzer.py -v
python -m pytest tests/test_threat_levels.py -v
python -m pytest tests/test_signal_history_buffer.py -v
python -m pytest tests/test_enhanced_signal_bridge.py -v
python -m pytest tests/test_pico_nfc_correlation.py -v

# Run tests with coverage
python -m pytest tests/ --cov=rtl_sdr --cov-report=html
```

### Enhanced Test Categories
- **Unit Tests**: Individual component testing for all new detection modules
- **Integration Tests**: System integration testing with enhanced signal processing
- **Mock Tests**: Hardware-free testing using mock data and synthetic signals
- **Performance Tests**: Signal processing performance validation for real-time analysis
- **Security Tests**: Comprehensive threat detection validation with temporal analysis
- **Signal Analysis Tests**: Automotive signal feature extraction and classification testing
- **Correlation Tests**: Validation of RF-NFC correlation system and multi-modal attack detection

### Test Quality Improvements
- **Enhanced Test Coverage**: 63 comprehensive tests with 100% pass rate across all components
- **Realistic Signal Data**: Tests use proper Unix timestamps and chronological ordering for accurate temporal analysis
- **Comprehensive Coverage**: >90% code coverage for detection and signal processing modules
- **Mock Hardware**: Complete hardware simulation for testing without physical devices
- **Performance Testing**: Real-time processing validation (<100ms latency) and memory usage monitoring
- **Thread Safety Testing**: Concurrent access validation for signal history buffer operations

## ⚡ Troubleshooting

- **No events in dashboard?** Ensure `rtl_tcp_server.py` and `signal_bridge.py` are running, and Pico/dashboard are connecting to the correct port (default: 8888).
- **Testing without hardware?** Use `python cli_dashboard.py --mock` for demo mode.
- **RTL-SDR not detected?** Use `rtl_test` to verify driver installation.
- **Firewall issues?** Allow port 8888 for incoming TCP connections.

- **Comprehensive Coverage**: >90% code coverage for detection and signal processing modules
- **Mock Hardware**: Complete hardware simulation for testing without physical devices
- **Performance Testing**: Real-time processing validation (<100ms latency) and memory usage monitoring
- **Thread Safety Testing**: Concurrent access validation for signal history buffer operations

## 🗒️ Notes

- **No FastAPI or MongoDB**: This MVP/POC does not require a web API or database. All event streaming is via TCP.
- **For full hardware setup and wiring, see**: [`docs/poc_migration_plan.md`](../docs/poc_migration_plan.md)

## 📚 References
- [RTL-SDR Quick Start Guide](https://www.rtl-sdr.com/rtl-sdr-quick-start-guide/)
- [MicroPython for Pico W](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)

---

For questions or demo support, see the project documentation or contact the project maintainers.