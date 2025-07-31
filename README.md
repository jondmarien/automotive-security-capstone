# Automotive Security Capstone Project (2025)

This repository contains the full proof-of-concept (POC) codebase for an automotive RF/NFC security monitoring system. The system uses an RTL-SDR V4 dongle, Python signal processing, and a Raspberry Pi Pico W to detect, classify, and alert on suspicious automotive wireless activity. Enhanced with multi-modal attack detection through NFC correlation, the system can identify coordinated physical and wireless attacks. An enhanced CLI dashboard provides real-time visualization with technical evidence presentation, signal analysis details, and event navigation for demos and development.

**NEW**: The system now includes comprehensive hardware management with automatic detection, failure recovery, synthetic event generation for validation, and organized logging infrastructure for production-ready deployment.

---

## Project Structure

```sh
├── backend/                  # Python backend: signal processing, event streaming, dashboard, Pico client
│   ├── cli_dashboard.py      # Rich-based CLI dashboard with signal analysis and technical evidence (supports --mock and --event modes)
│   ├── rtl_sdr/              # RTL-SDR server and signal processing modules
│   ├── pico/                 # MicroPython code for Pico W TCP client
│   ├── docs/                 # Documentation, migration plan, setup
│   ├── requirements.txt      # Python dependencies
│   └── README.md             # Backend-specific details and setup
│
└── README.md                 # (this file)
```

---

## System Overview

- **RF Detection**: RTL-SDR V4 captures raw IQ data; Python scripts process signals and detect automotive events.
- **Hardware Management**: Comprehensive hardware detection, configuration, and failure recovery with graceful fallback to mock mode.
- **Event Streaming**: Detection events are broadcast over TCP to both the Pico W and the CLI dashboard.
- **CLI Dashboard**: Terminal UI (Rich) for live event display with signal analysis visualization, technical evidence presentation, event navigation, and demo/testing (`--mock` and `--event` modes supported).
- **Pico W Client**: Receives events, triggers alerts (LEDs, NFC), connects via WiFi to the backend TCP server with automated deployment tools.
- **NFC Correlation System**: Enhanced security through multi-modal attack detection, correlating RF signals with physical NFC proximity events.
- **Enhanced Threat Detection**: Temporal analysis and pattern recognition for brute force attacks with escalating threat levels and detailed evidence collection.
- **Validation Framework**: Synthetic event generation and accuracy validation ensuring >90% detection accuracy requirement.
- **Logging Infrastructure**: Organized date-based logging with comprehensive system health monitoring and diagnostics.
- **No FastAPI/MongoDB**: All event transport is via TCP; no web API or database is required for the MVP/POC.

---

## Quick Start

### Quick Demo (RECOMMENDED)
```bash
cd backend

# Basic demo with realistic automotive security events
uv run python cli_dashboard.py --mock

# Advanced demo with synthetic signal generation
uv run python cli_dashboard.py --mock --synthetic
```

### Complete System Setup
```bash
# Automated system with real hardware detection
uv run python real_hardware_launcher.py

# Force demo mode for presentations (system-wide)
uv run python real_hardware_launcher.py --force-mock
```

### Manual Setup
1. **See [`backend/README.md`](backend/README.md)** for backend setup, running the dashboard, and Pico/client instructions.
2. **See [`backend/docs/deployment/real_hardware_setup.md`](backend/docs/deployment/real_hardware_setup.md)** for complete hardware setup guide.

### Validation & Testing
```bash
# Validate detection accuracy (>90% requirement)
uv run python utils/validate_detection_accuracy.py

# Run demonstration scenarios
uv run python demo_scenarios.py --scenario comprehensive
```

---

## Tech Stack

- **Python 3.11+** (backend, signal processing, dashboard)
- **RTL-SDR V4** (RF hardware)
- **Raspberry Pi Pico W** (MicroPython TCP client)
- **PN532 NFC Module** (NFC reader for proximity detection)
- **Rich** (CLI dashboard)
- **NumPy/SciPy** (signal processing and advanced automotive signal analysis)
- **MicroPython + asyncio** (correlation system for multi-modal attack detection)
- **pytest** (comprehensive testing framework with extensive coverage of signal processing and NFC correlation)

---

## References & Docs

### Core Documentation
- Backend implementation: [`backend/README.md`](backend/README.md)
- Real hardware setup: [`backend/docs/deployment/real_hardware_setup.md`](backend/docs/deployment/real_hardware_setup.md)
- System changelog: [`backend/docs/CHANGELOG.md`](backend/docs/CHANGELOG.md)

### API Documentation
- Hardware Management: [`backend/docs/api/hardware_management.md`](backend/docs/api/hardware_management.md)
- Validation Framework: [`backend/docs/api/validation_framework.md`](backend/docs/api/validation_framework.md)
- NFC Correlation System: [`backend/docs/api/nfc_correlation.md`](backend/docs/api/nfc_correlation.md)

### Implementation Guides
- NFC Implementation Plan: [`backend/docs/plans/nfc_correlation_implementation.md`](backend/docs/plans/nfc_correlation_implementation.md)

For questions or demo support, see the project documentation or contact the maintainers.