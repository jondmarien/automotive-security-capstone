# Automotive Security Capstone Project

This repository contains the backend components for the Automotive Security Capstone system, designed to monitor, detect, and alert users about suspicious RF signals in vehicles using custom hardware and modern software stacks.

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
└── README.md                          # (this file)
```

---

## High-Level Plan

- **Backend:** Collects and analyzes RF signals, communicates with custom hardware, and exposes APIs for the frontend.

See [`backend/docs/plans/IMPLEMENTATION_PLAN.md`](backend/docs/plans/IMPLEMENTATION_PLAN.md)

---

## Tech Stack

- **Backend:**
  - Python 3.x
  - Flask or FastAPI (API server)
  - BLE/Wi-Fi communication (e.g., bless, pywifi)
  - Numpy, Scipy (signal processing)
  - Custom hardware interface
  - Unit testing: pytest

---

## Further Details

- For backend implementation, see [`backend/README.md`](backend/README.md)

- For project goals and architecture, see  [`backend/docs/poc_migration_plan.md`](backend/docs/poc_migration_plan.md)
