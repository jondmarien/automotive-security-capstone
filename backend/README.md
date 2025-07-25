# Automotive Security Capstone Backend (2025)

This backend powers the Automotive Security Capstone POC, enabling real-time automotive RF and NFC event detection, logging, and demo visualization via a CLI dashboard.

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

- `rtl_tcp_server.py`: Manages RTL-SDR, launches `rtl_tcp`, listens for Pico clients and dashboard on TCP (default: 8888)
- `signal_bridge.py`: Reads IQ samples from RTL-SDR, detects events, sends to TCP server
- `cli_dashboard.py`: Rich-powered CLI dashboard for real-time event display; supports `--mock` for demo/testing
- `pico/main.py`: MicroPython client for Pico W; connects to computer, receives events, triggers LEDs/NFC

## 🛠️ Setup & Usage

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
   python rtl_tcp_server.py
   python signal_bridge.py
   # Or: python startup_server.py
```

4. **Run the CLI dashboard (real events or mock mode)**

```sh
   # For live events (requires running TCP server with events):
   python cli_dashboard.py --source tcp --tcp-host localhost --tcp-port 8888
   # For demo/testing (no hardware required):
   python cli_dashboard.py --mock
```

### 2. Pico-Side (Raspberry Pi Pico W)

- Flash MicroPython firmware
- Upload `main.py` and required libraries (see [docs/poc_migration_plan.md](../docs/poc_migration_plan.md))
- Configure WiFi and server IP/port (default: 8888)
- Pico will connect to computer, receive detection events, and trigger alerts/NFC

## 🖥️ CLI Dashboard

- Real-time event table with threat levels, event type, source, and details
- Supports both live TCP and `--mock` demo mode
- Logs all events to `detection_events.log`
- Graceful error handling and Ctrl+C exit

## 🔄 Project Structure (simplified)

```
backend/
├── cli_dashboard.py         # CLI dashboard (Rich, --mock supported)
├── rtl_sdr/
│   ├── rtl_tcp_server.py    # Manages RTL-SDR, Pico TCP server
│   └── signal_bridge.py     # Signal processing, event detection
├── pico/
│   └── main.py              # Pico W MicroPython TCP client
├── requirements.txt         # Python dependencies
├── docs/
│   └── poc_migration_plan.md
└── ... (other scripts, logs, configs)
```

## ⚡ Troubleshooting

- **No events in dashboard?** Ensure `rtl_tcp_server.py` and `signal_bridge.py` are running, and Pico/dashboard are connecting to the correct port (default: 8888).
- **Testing without hardware?** Use `python cli_dashboard.py --mock` for demo mode.
- **RTL-SDR not detected?** Use `rtl_test` to verify driver installation.
- **Firewall issues?** Allow port 8888 for incoming TCP connections.

## 🗒️ Notes

- **No FastAPI or MongoDB**: This MVP/POC does not require a web API or database. All event streaming is via TCP.
- **For full hardware setup and wiring, see**: [`docs/poc_migration_plan.md`](../docs/poc_migration_plan.md)

## 📚 References
- [RTL-SDR Quick Start Guide](https://www.rtl-sdr.com/rtl-sdr-quick-start-guide/)
- [MicroPython for Pico W](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)

---

For questions or demo support, see the project documentation or contact the project maintainers.