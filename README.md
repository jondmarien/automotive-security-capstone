# Automotive Security Capstone Project

This repository contains both the backend and frontend components for the Automotive Security Capstone system, designed to monitor, detect, and alert users about suspicious RF signals in vehicles using custom hardware and modern software stacks.

---

## Project Structure

```sh
├── backend/                           # Python backend for RF signal analysis, hardware comms, and API
│   ├── app_logging/                   # Logging utilities
│   ├── comms/                         # Communication (BLE/Wi-Fi, protocol)
│   ├── config/                        # Configuration files
│   ├── detection/                     # Signal detection & analysis logic
│   ├── hardware/                      # Hardware abstraction/interface
│   ├── main.py                        # Backend entrypoint
│   ├── requirements.txt               # Python dependencies
│   ├── tests/                         # Backend tests
│   ├── utils/                         # Utility functions
│   ├── README.md                      # Backend details
│   └── IMPLEMENTATION_PLAN.md         # High-level project and design plan
│
├── frontend/                          # Flutter mobile/web app for user interface and alerts
│   ├── android/                       # Android platform files
│   ├── ios/                           # iOS platform files
│   ├── linux/, macos/, windows/, web/ # Desktop/Web targets
│   ├── lib/                           # Dart source code (UI, providers, logic)
│   ├── assets/                        # Images, mockups, etc.
│   ├── pubspec.yaml                   # Flutter dependencies
│   ├── tests/                         # Frontend tests
│   ├── README.md                      # Frontend details
│   └── IMPLEMENTATION_PLAN.md         # High-level project and design plan
│
└── README.md                          # (this file)
```

---

## High-Level Plan

- **Backend:** Collects and analyzes RF signals, communicates with custom hardware, and exposes APIs for the frontend.
- **Frontend:** Cross-platform Flutter app for real-time alerts, dashboard, settings, and history, connecting to backend and hardware dongle via BLE/Wi-Fi.

See either `backend/IMPLEMENTATION_PLAN.md` or `frontend/IMPLEMENTATION_PLAN.md` for the full roadmap.

---

## Tech Stack

- **Backend:**
  - Python 3.x
  - Flask or FastAPI (API server)
  - BLE/Wi-Fi communication (e.g., bless, pywifi)
  - Numpy, Scipy (signal processing)
  - Custom hardware interface
  - Unit testing: pytest

- **Frontend:**
  - Flutter (Dart)
  - Provider (state management)
  - Platform channels for BLE/Wi-Fi
  - Material Design UI
  - Unit/widget/integration testing (Flutter test)

---

## Further Details

- For backend implementation, see [`backend/README.md`](backend/README.md)
- For frontend implementation, see [`frontend/README.md`](frontend/README.md)
- For project goals and architecture, see either [`backend/IMPLEMENTATION_PLAN.md`](backend/IMPLEMENTATION_PLAN.md) or [`frontend/IMPLEMENTATION_PLAN.md`](frontend/IMPLEMENTATION_PLAN.md)
