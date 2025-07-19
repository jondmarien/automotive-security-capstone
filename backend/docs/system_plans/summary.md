# Automotive Security POC: System Summary

## Overview
This document summarizes the architecture and flow of the Automotive Security Capstone Proof-of-Concept (POC) system. The POC demonstrates real-time detection and reporting of automotive RF/NFC security events using a combination of RTL-SDR hardware, a computer-based backend, Raspberry Pi Pico microcontrollers, and a CLI dashboard.

## System Components

- **RTL-SDR V4 Dongle**: Captures RF signals from automotive key fobs and other sources.
- **Computer Backend**:
    - **rtl_tcp_server.py**: Manages the RTL-SDR device and streams IQ data over TCP.
    - **signal_bridge.py**: Processes IQ samples, detects signal events (unlock, lock, jamming, replay, NFC), and generates detection events.
    - **CLI Dashboard (`cli_dashboard.py`)**: Displays real-time detection events in the terminal using Rich, supports mock/demo mode, and logs events to file.
    - **TCP Event Server**: Broadcasts detection events to connected Pico clients and dashboard.
- **Raspberry Pi Pico W**:
    - Connects over WiFi to the computer's TCP event server (port 8888).
    - Receives detection events and triggers alerting (e.g., buzzer, LED, NFC tag, etc.).
    - MicroPython code in `pico/main.py`.

## Event Flow

1. **Signal Capture**: RTL-SDR captures RF signals and streams IQ data via `rtl_tcp_server.py`.
2. **Signal Processing**: `signal_bridge.py` analyzes IQ data, detects events, and creates event messages.
3. **Event Distribution**:
    - Events are broadcast to:
        - CLI dashboard for real-time monitoring.
        - Pico clients for physical alerting.
4. **Dashboard**: `cli_dashboard.py` displays events in a color-coded table, supports mock/demo mode, and logs to file.
5. **Pico Alerting**: Pico receives events and can trigger hardware actions (e.g., sound buzzer, NFC tag, LED).

## Usage Modes
- **Live Mode**: Real signals processed from RTL-SDR; events sent to dashboard and Pico.
- **Mock Mode**: Dashboard simulates detection events for development/demo without hardware.

## Key Features
- Modular backend with clear separation of signal capture, processing, and UI.
- TCP event streaming for real-time updates to dashboard and Pico.
- Color-coded threat levels for rapid situational awareness.
- Student-friendly documentation and example usage in all code files.

## Demo Checklist
- [ ] RTL-SDR connected and recognized by computer
- [ ] Backend running (`rtl_tcp_server.py`, `signal_bridge.py`)
- [ ] Pico connected to WiFi and TCP server
- [ ] CLI dashboard running (live or mock mode)
- [ ] Events visible and color-coded in dashboard
- [ ] Pico responds to detection events

---

For detailed setup, troubleshooting, and architecture, see the project README files and the diagram below.
