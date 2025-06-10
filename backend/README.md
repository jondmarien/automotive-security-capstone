# Automotive Security Backend

This is the backend service for the Automotive Security Capstone project, built with FastAPI and MongoDB.

## 🚀 Features

- **FastAPI** for high-performance API endpoints
- **MongoDB** for data persistence
- **JWT Authentication** for secure API access
- **Structured Logging** for better debugging
- **CORS** enabled for frontend integration
- **Environment-based configuration**

## 🛠️ Prerequisites

- Python 3.11+
- MongoDB (local or remote)
- Poetry for dependency management

## 🏗️ Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Set up environment variables**
   Copy `.env.example` to `.env` and update the values:
   ```bash
   cp .env.example .env
   ```

4. **Run the application**
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

5. **Access the API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 📦 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       └── api.py
│   ├── core/
│   │   ├── config.py
│   │   └── logger.py
│   ├── db/
│   │   └── mongodb.py
│   ├── models/
│   │   └── base.py
│   └── main.py
├── tests/
├── .env.example
├── .gitignore
├── poetry.lock
├── pyproject.toml
└── README.md
```

## 🔧 Development

- **Format code**
  ```bash
  poetry run black .
  ```

- **Lint code**
  ```bash
  poetry run ruff check .
  ```

- **Run tests**
  ```bash
  poetry run pytest
  ```

## 🌐 API Endpoints

- `GET /health` - Health check endpoint
- `POST /auth/token` - Get access token
- `GET /api/v1/...` - Version 1 API endpoints

## 🔒 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_ENV` | Application environment | `development` |
| `SECRET_KEY` | Secret key for JWT | - |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `10080` (7 days) |
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGODB_DB_NAME` | Database name | `auto_sec` |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | `*` |

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# Automotive Security Capstone - POC Architecture (2025)

## Overview

This project implements a proof-of-concept (POC) automotive security system using an RTL-SDR V4 dongle, a computer (as intermediary), and a Raspberry Pi Pico W. The system detects and classifies automotive RF signals and NFC events, generating alerts for suspicious activity.

## System Architecture

```
RTL-SDR V4 → Computer (rtl_tcp server + Python signal server) → TCP/IP → Raspberry Pi Pico W → PN532 NFC
                                                        ↓
                                              Alert Processing & Logging
```

- **RTL-SDR V4** is connected to the computer (not the Pico).
- **Computer** runs `rtl_tcp` and a Python server (`rtl_tcp_server.py`, `signal_bridge.py`, `startup_server.py`) to process IQ samples and broadcast detection events over TCP.
- **Raspberry Pi Pico W** connects as a TCP client to the computer, receives detection events, and handles alerting and NFC monitoring.

## Running the POC

### 1. Computer-Side Setup

- Install dependencies:
  - Python 3.8+
  - `numpy`, `asyncio`
  - RTL-SDR drivers (use Zadig on Windows)
  - `rtl_tcp` utility (from the RTL-SDR package)
- Start the RTL-SDR TCP server and signal processing bridge:
  1. Run `rtl_tcp_server.py` to start the RTL-SDR process and Pico TCP server.
  2. Run `signal_bridge.py` to process IQ samples and broadcast detection events.
  3. Use `startup_server.py` to launch both together and monitor system health.

### 2. Pico-Side Setup

- Flash MicroPython firmware to the Pico W.
- Upload the Pico client code (see docs/poc_migration_plan.md for example).
- Configure the Pico to connect to the computer's IP and port (default: 8888).
- The Pico will receive detection events and handle alerting and NFC monitoring.

## Key Changes from Previous Architecture

- **No direct RTL-SDR access from the Pico.** All RF detection is performed on the computer and sent to the Pico over TCP.
- **Mock drivers** are retained for unit testing but are not used in the POC runtime.
- **Detection pipeline** in `main.py` and `detection/rf_detection.py` now expects detection events from the TCP server, not direct hardware.

## Example: Running the Server

```bash
# Start the server (from backend directory)
python startup_server.py
```

## Example: Pico Client

- See `docs/poc_migration_plan.md` for a full example of the Pico client code.
- The Pico should connect to the computer's IP and port 8888 to receive detection events.

## Troubleshooting

- Ensure the computer firewall allows incoming connections on port 8888.
- Use `rtl_test` to verify RTL-SDR is detected.
- Use `telnet <computer_ip> 8888` to test TCP connectivity from the Pico's network.

## Dependencies
- Python 3.8+
- numpy
- asyncio
- RTL-SDR tools (rtl_tcp)

## For More Details
See `docs/poc_migration_plan.md` for a full implementation guide and test plan.
