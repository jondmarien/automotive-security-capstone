# Automotive Security Capstone Project (2025)

This repository contains the full proof-of-concept (POC) codebase for an automotive RF/NFC security monitoring system. The system uses an RTL-SDR V4 dongle, Python signal processing, and a Raspberry Pi Pico W to detect, classify, and alert on suspicious automotive wireless activity. A CLI dashboard provides real-time visualization for demos and development.

---

## Project Structure

```sh
├── backend/                  # Python backend: signal processing, event streaming, dashboard, Pico client
│   ├── cli_dashboard.py      # Rich-based CLI dashboard (supports --mock mode)
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
- **Event Streaming**: Detection events are broadcast over TCP to both the Pico W and the CLI dashboard.
- **CLI Dashboard**: Terminal UI (Rich) for live event display and demo/testing (`--mock` mode supported).
- **Pico W Client**: Receives events, triggers alerts (LEDs, NFC), connects via WiFi to the backend TCP server.
- **No FastAPI/MongoDB**: All event transport is via TCP; no web API or database is required for the MVP/POC.

---

## Quick Start

1. **See [`backend/README.md`](backend/README.md)** for backend setup, running the dashboard, and Pico/client instructions.
2. **See [`backend/docs/poc_migration_plan.md`](backend/docs/poc_migration_plan.md)** for full architecture, wiring, and implementation details.

---

## Tech Stack

- **Python 3.11+** (backend, signal processing, dashboard)
- **RTL-SDR V4** (RF hardware)
- **Raspberry Pi Pico W** (MicroPython TCP client)
- **Rich** (CLI dashboard)
- **NumPy/SciPy** (signal processing and advanced automotive signal analysis)
- **pytest** (comprehensive testing framework with 63 tests covering enhanced signal processing)

---

## References & Docs

- Backend implementation: [`backend/README.md`](backend/README.md)
- Architecture and hardware: [`backend/docs/poc_migration_plan.md`](backend/docs/poc_migration_plan.md)

For questions or demo support, see the project documentation or contact the maintainers.