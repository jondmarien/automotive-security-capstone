# Automotive Security Capstone Project (2025)

This repository contains a comprehensive proof-of-concept (POC) automotive RF/NFC security monitoring system. The system uses RTL-SDR V4 hardware, advanced Python signal processing, and Raspberry Pi Pico W to detect, classify, and alert on suspicious automotive wireless activity in real-time. Features include multi-modal attack detection through NFC correlation, comprehensive hardware management with automatic recovery, and a professional CLI dashboard with technical evidence presentation.

**Key Features**: Professional CLI dashboard with enhanced startup experience and graceful exit handling, advanced synthetic event generation with realistic attack scenarios, comprehensive session data export capabilities, improved event navigation with pagination, and enhanced user experience with Rich-based dialogs and ASCII art presentation.

---
<details>
<summary>Loading Screen</summary>

<img width="1100" height="1009" alt="Loading Screen" src="https://github.com/user-attachments/assets/cdaf5e7a-c4b9-4adf-91fc-686aa3587074" />

</details>

<details>
<summary>Menu Screen</summary>

<img width="2508" height="990" alt="Menu Screen" src="https://github.com/user-attachments/assets/ed963dcd-5128-49f3-a676-5f48a335b443" />

</details>

<details>
<summary>Main Screen</summary>

<img width="2520" height="1174" alt="Main Screen" src="https://github.com/user-attachments/assets/a4548a29-b0b3-4a50-a32e-40fdd27b995d" />

</details>

<details>
<summary>Exit Dashboard</summary>

<img width="2514" height="1197" alt="Exit Dashboard" src="https://github.com/user-attachments/assets/2899421c-7f26-4d99-922b-e7ba5b5ddd47" />

</details>

<details>
<summary>Goodbye Screen</summary>

<img width="2504" height="474" alt="Goodbye Screen" src="https://github.com/user-attachments/assets/43d67e15-d56e-497f-a383-20c215454991" />

</details>

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

### Core Capabilities

- **RF Signal Processing**: RTL-SDR V4 hardware with real-time FFT analysis for automotive frequencies (315/433 MHz)
- **Threat Detection**: Multi-algorithm detection for replay attacks, jamming, brute force, and signal injection
- **RF-NFC Correlation**: Multi-modal attack detection combining wireless and physical proximity events
- **Professional Dashboard**: Rich CLI interface with real-time monitoring and technical evidence display
- **Hardware Management**: Auto-discovery, health monitoring, and graceful failure recovery
- **Embedded Alerts**: Raspberry Pi Pico W with NFC integration and visual threat indicators

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
# Modern setup with uv (recommended - lightning fast!)
cd backend
uv sync  # Installs all dependencies from pyproject.toml

# Build the project (native uv build backend)
uv build  # Creates wheel in dist/

# Install CLI tools globally
uv tool install .

# Traditional setup (fallback)
uv venv
uv pip install -e .
```

### 📊 Testing & Validation

```bash
# Run full test suite with coverage
uv run pytest tests/ --cov=rtl_sdr --cov=detection --cov-report=html

# Validate >90% detection accuracy
uv run python utils/validate_detection_accuracy.py

# Performance benchmarks
uv run python demo_scenarios.py --scenario comprehensive
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

## Technology Stack

- **Python 3.11+** with native uv build backend for lightning-fast builds
- **RTL-SDR V4** professional RF hardware (500 kHz - 1.75 GHz)
- **Raspberry Pi Pico W** with RP2040 dual-core MCU and WiFi
- **Rich Terminal UI** for professional CLI dashboard experience
- **NumPy/SciPy** for real-time signal processing (<100ms latency)
- **pytest** comprehensive testing framework (109+ tests)

---

## Key Features

- **🔍 Advanced Threat Detection**: Replay attacks, jamming, brute force, signal injection with >90% accuracy
- **🎛️ Professional CLI Dashboard**: Real-time monitoring with Rich UI and technical evidence display
- **🔧 Hardware Auto-Management**: RTL-SDR/Pico W discovery, health monitoring, and failure recovery
- **📊 Comprehensive Testing**: 109+ tests with coverage reporting and performance validation

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
