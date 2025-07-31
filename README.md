# Automotive Security Capstone Project (2025)

This repository contains a comprehensive proof-of-concept (POC) automotive RF/NFC security monitoring system. The system uses RTL-SDR V4 hardware, advanced Python signal processing, and Raspberry Pi Pico W to detect, classify, and alert on suspicious automotive wireless activity in real-time. Features include multi-modal attack detection through NFC correlation, comprehensive hardware management with automatic recovery, and a professional CLI dashboard with technical evidence presentation.

**Latest Enhancements**: Advanced threat detection engine with temporal analysis, comprehensive hardware management system with automatic detection and recovery, synthetic signal generation for validation, organized logging infrastructure, and enhanced CLI dashboard with signal analysis visualization and event navigation.

---

<img width="1634" height="754" alt="image" src="https://github.com/user-attachments/assets/b2d988be-8661-441e-9f8b-632c85889117" />

## Project Structure

```sh
automotive-security-capstone/
├── backend/                  # Main Python backend system
│   ├── cli_dashboard.py                   # Enhanced Rich CLI dashboard with signal analysis
│   ├── real_hardware_launcher.py          # Complete system orchestration with hardware detection
│   ├── deploy_pico.py                     # Automated Pico W deployment tool
│   ├── demo_scenarios.py                  # Structured demonstration scenarios
│   ├── detection/            # Advanced threat detection engine
│   │   ├── security_analyzer.py           # Main security analysis engine
│   │   ├── jamming_detector.py            # RF jamming detection
│   │   ├── replay_attack_detector.py      # Replay attack detection
│   │   └── threat_levels.py               # Threat classification system
│   ├── rtl_sdr/              # RTL-SDR hardware integration and signal processing
│   │   ├── automotive_signal_analyzer.py  # Advanced automotive signal analysis
│   │   ├── enhanced_signal_bridge.py      # Enhanced signal processing bridge
│   │   ├── brute_force_detector.py        # Brute force attack detection
│   │   └── signal_history_buffer.py       # Signal history management
│   ├── hardware/             # Hardware abstraction and management layer
│   │   ├── hardware_manager.py            # Centralized hardware coordination
│   │   ├── rtl_sdr_interface.py           # RTL-SDR hardware abstraction
│   │   ├── pico_connection_manager.py     # Pico W connection management
│   │   └── recovery_system.py             # Hardware failure recovery
│   ├── pico/                 # Raspberry Pi Pico W embedded client
│   │   ├── main.py                        # MicroPython TCP client with NFC correlation
│   │   ├── NFC_PN532.py                   # NFC/RFID hardware interface
│   │   └── config.py                      # Pico W configuration management
│   ├── utils/                # Shared utilities and validation framework
│   │   ├── detection_accuracy.py          # Detection accuracy validation
│   │   ├── validate_detection_accuracy.py # Automated validation script
│   │   ├── logging_config.py              # Centralized logging system
│   │   └── signal_constants.py            # RF signal constants and parameters
│   ├── tests/                # Comprehensive test suite (60+ tests)
│   ├── docs/                 # Extensive project documentation
│   ├── logs/                 # Organized date-based logging
│   ├── results/              # Validation and performance results
│   └── requirements.txt                   # Python dependencies
└── README.md                 # (this file)
```

---

## System Architecture & Core Components

### RF Signal Processing Pipeline
- **RTL-SDR V4 Hardware**: Professional-grade RF capture (500 kHz - 1.75 GHz, up to 3.2 MS/s)
- **Advanced Signal Analysis**: Real-time FFT processing, automotive-specific pattern recognition, FSK detection
- **Automotive Signal Analyzer**: Specialized detection for key fobs (315/433 MHz), TPMS sensors, and RKE systems
- **Signal History Buffer**: Temporal analysis for replay attack detection and pattern correlation

### Comprehensive Threat Detection Engine
- **Multi-Algorithm Detection**: Replay attacks, jamming detection, brute force attempts, signal injection
- **Temporal Analysis**: Multi-window analysis for sophisticated attack pattern recognition
- **Threat Classification**: BENIGN → SUSPICIOUS → MODERATE → HIGH → CRITICAL with escalating responses
- **Evidence Collection**: Comprehensive technical evidence gathering for forensic analysis
- **Confidence Scoring**: Advanced multi-factor confidence calculation with >90% accuracy validation

### Hardware Management System
- **Centralized Coordination**: HardwareManager orchestrates all hardware components with health monitoring
- **Automatic Detection**: RTL-SDR and Pico W auto-discovery with capability validation
- **Failure Recovery**: Exponential backoff retry logic with graceful degradation to mock mode
- **Connection Management**: Robust TCP connection handling with heartbeat monitoring and auto-reconnection

### Multi-Modal Attack Detection
- **RF-NFC Correlation**: Correlates suspicious RF signals with physical NFC proximity events
- **Coordinated Attack Detection**: Identifies sophisticated multi-vector attacks combining wireless and physical access
- **Threat Escalation**: Automatic threat level escalation for correlated multi-modal events
- **Visual Indicators**: LED-based alert system with NFC correlation status display

### Professional CLI Dashboard
- **Real-Time Monitoring**: Live event streaming with color-coded threat levels and signal analysis
- **Technical Evidence Display**: Detailed attack-specific evidence presentation with proper formatting
- **Signal Visualization**: RSSI, SNR, modulation type, burst count with progress bars and metrics
- **Event Navigation**: Historical event analysis with keyboard controls and event selection
- **Demo Modes**: `--mock` for hardware-free demonstrations, `--synthetic` for advanced signal testing

### Embedded Alert System
- **Raspberry Pi Pico W**: Dedicated hardware for immediate threat response with WiFi connectivity
- **NFC Integration**: PN532 module for proximity-based interactions and correlation detection
- **Visual Alerts**: RGB LED indicators for threat levels with correlation status
- **Automated Deployment**: Streamlined firmware deployment with serial connection management

---

## Quick Start Guide

### 🎯 Instant Demo (RECOMMENDED for Presentations)
```bash
cd backend

# Professional demo with realistic automotive security events
uv run python cli_dashboard.py --mock

# Advanced demo with synthetic signal generation and validation
uv run python cli_dashboard.py --mock --synthetic

# View specific event with technical evidence
uv run python cli_dashboard.py --mock --event 3
```

### 🚀 Complete System Launch
```bash
# Automated system with hardware detection and recovery
uv run python real_hardware_launcher.py

# Force demo mode for presentations (system-wide fallback)
uv run python real_hardware_launcher.py --force-mock

# Custom frequency configuration (315MHz for North America)
uv run python real_hardware_launcher.py --frequency 315000000
```

### 🔧 Development Setup
```bash
# Environment setup with UV (recommended)
cd backend
uv venv
uv pip install -r requirements.txt

# Traditional setup (fallback)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 📊 Validation & Testing
```bash
# Validate >90% detection accuracy requirement
uv run python utils/validate_detection_accuracy.py

# Run comprehensive demonstration scenarios
uv run python demo_scenarios.py --scenario comprehensive

# Execute full test suite (63 tests)
uv run pytest tests/ -v

# Performance validation for real-time processing
uv run pytest tests/test_automotive_signal_analyzer.py::TestAutomotiveSignalAnalyzer::test_performance -v
```

### 📱 Pico W Deployment
```bash
# Automated deployment with port detection
uv run python deploy_pico.py

# Manual port specification
uv run python deploy_pico.py COM3  # Windows
uv run python deploy_pico.py /dev/ttyACM0  # Linux
```

---

## Technology Stack & Architecture

### Core Technologies
- **Python 3.11+**: Primary backend language with modern type hints and asyncio support
- **RTL-SDR V4**: Professional RF hardware (R828D tuner + RTL2832U, USB 3.0)
- **Raspberry Pi Pico W**: RP2040 dual-core MCU with 802.11n WiFi
- **PN532 NFC Module**: 13.56 MHz NFC/RFID interface for proximity detection

### Signal Processing & Analysis
- **NumPy/SciPy**: Vectorized operations, FFT analysis, advanced signal processing functions
- **Custom DSP**: Tailored algorithms for automotive signal patterns and FSK detection
- **Real-Time Processing**: <100ms latency for threat detection with optimized performance

### User Interface & Visualization
- **Rich Terminal UI**: Modern CLI dashboard with colors, tables, progress bars, signal visualization
- **Professional Display**: Live updating displays, technical evidence presentation, event navigation
- **Demo-Friendly**: Excellent for presentations with `--mock` and `--synthetic` modes

### Development & Quality Assurance
- **UV Package Manager**: Next-generation Python dependency management (10-100x faster than pip)
- **pytest Framework**: Comprehensive testing with 63 tests covering signal processing and NFC correlation
- **Type Safety**: Full type hints with mypy static analysis
- **Code Quality**: Black formatting, isort, flake8 linting for professional standards

### Hardware Integration
- **Asynchronous Architecture**: Non-blocking I/O for real-time performance with asyncio
- **TCP Event Streaming**: Efficient inter-component communication without database dependency
- **Hardware Abstraction**: Clean separation between hardware and logic layers for testing
- **Automatic Recovery**: Exponential backoff retry logic with graceful degradation

### Security & Validation
- **Multi-Modal Detection**: RF-NFC correlation for coordinated attack identification
- **Temporal Analysis**: Multi-window analysis for sophisticated attack pattern recognition
- **Evidence Collection**: Comprehensive technical evidence gathering for forensic analysis
- **Accuracy Validation**: >90% detection accuracy with confusion matrix generation and benchmarking

---

## Key Features & Capabilities

### 🔍 Advanced Threat Detection
- **Replay Attack Detection**: Signal similarity analysis with temporal clustering and evidence collection
- **Jamming Detection**: Four pattern types (continuous, pulse, sweep, spot) with confidence scoring
- **Brute Force Detection**: Multi-window temporal analysis with escalating threat levels
- **Signal Injection**: Pattern recognition for unauthorized signal injection attempts
- **Multi-Modal Correlation**: RF-NFC coordinated attack detection with automatic threat escalation

### 🎛️ Professional CLI Dashboard
- **Real-Time Monitoring**: Live event streaming with color-coded threat levels and professional styling
- **Signal Analysis Visualization**: RSSI, SNR, modulation type, burst count with progress bars
- **Technical Evidence Display**: Attack-specific evidence presentation with detailed formatting
- **Event Navigation**: Historical event analysis with keyboard controls and event selection
- **Performance Metrics**: System health monitoring with processing latency and accuracy counters

### 🔧 Comprehensive Hardware Management
- **Automatic Detection**: RTL-SDR and Pico W auto-discovery with capability validation
- **Health Monitoring**: Continuous hardware status monitoring with diagnostic reporting
- **Failure Recovery**: Exponential backoff retry logic with graceful degradation
- **Mock Mode Fallback**: Seamless transition to demonstration mode when hardware unavailable

### 📊 Validation & Testing Framework
- **Detection Accuracy**: >90% accuracy validation with confusion matrix generation
- **Synthetic Signal Generation**: Advanced test signal creation for validation and demonstrations
- **Performance Benchmarking**: Real-time processing validation (<100ms latency requirements)
- **Comprehensive Test Suite**: 63 tests covering all components with extensive coverage

## Documentation & Resources

### 📚 Core Documentation
- **Backend Implementation**: [`backend/README.md`](backend/README.md) - Detailed setup and usage guide
- **Hardware Setup Guide**: [`backend/docs/REAL_HARDWARE_SETUP.md`](backend/docs/REAL_HARDWARE_SETUP.md) - Complete hardware configuration
- **System Changelog**: [`backend/docs/CHANGELOG.md`](backend/docs/CHANGELOG.md) - Version history and updates
- **Testing Guide**: [`backend/docs/testing_guide.md`](backend/docs/testing_guide.md) - Comprehensive testing procedures

### 🔧 Technical References
- **Project Specifications**: [`.kiro/specs/rtl-sdr-nfc-integration/`](.kiro/specs/rtl-sdr-nfc-integration/) - Implementation plans and requirements
- **Development Guidelines**: [`.kiro/steering/`](.kiro/steering/) - Best practices and architectural guidance
- **API Documentation**: [`backend/docs/api/`](backend/docs/api/) - System APIs and interfaces
- **Deployment Guides**: [`backend/docs/deployment/`](backend/docs/deployment/) - Production deployment procedures

### 🎯 Getting Started Resources
- **Quick Demo**: Use `uv run python cli_dashboard.py --mock` for immediate demonstration
- **Hardware Testing**: Use `uv run python real_hardware_launcher.py` for complete system
- **Validation**: Use `uv run python utils/validate_detection_accuracy.py` for accuracy testing
- **Development**: See [`backend/README.md`](backend/README.md) for detailed development setup

---

**Academic Context**: This is a 4th year cybersecurity capstone project (2025) demonstrating practical application of cybersecurity principles in automotive contexts. The system addresses real-world automotive security challenges as vehicles become increasingly connected, providing a comprehensive monitoring solution for detecting and classifying potentially malicious RF/NFC activity targeting automotive systems.

For questions, demo support, or technical assistance, see the project documentation or contact the project maintainers.
