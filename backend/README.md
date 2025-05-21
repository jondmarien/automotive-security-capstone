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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. Security Dongle Backend

This backend implements the core firmware, signal processing, and communication logic for a low-cost automotive security dongle. The system is designed to detect suspicious RF activity (315/433 MHz, e.g. relay attacks) and NFC events (13.56 MHz) in vehicles, alerting users via BLE or Wi-Fi to potential threats.

## Features

- **RF Signal Detection:** Uses RTL-SDR to monitor 315/433 MHz for suspicious transmissions (relay attacks, spoofing, etc.).
- **NFC Detection:** Monitors for unauthorized 13.56 MHz NFC activity using a PN532 module.
- **Anomaly Detection:** Combines RF and NFC data with pattern recognition and RSSI thresholds to minimize false positives.
- **Alert System:** Classifies threats, formats encrypted JSON alerts, and notifies users through BLE or Wi-Fi.
- **Power Management:** Designed for low power consumption and safe operation from a vehicle USB/lighter port.
- **Testing & Compliance:** Includes test plans for validation, power, and environmental compliance.

## Architecture

- **main.py:** Firmware main loop integrating hardware, detection, and alert modules.
- **hardware/**: RTL-SDR and PN532 hardware abstraction, power management, and circuit documentation.
- **detection/**: RF/NFC detection, anomaly detection, and alert classification.
- **comms/**: BLE, Wi-Fi, and encryption utilities for secure alert transmission.
- **logging/**: Logging and debug utilities.
- **utils/**: Helper functions and configuration loaders.
- **tests/**: Automated and manual test scripts, validation plans.

## Getting Started

1. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

2. Connect RTL-SDR and PN532 modules to your Raspberry Pi Pico (see `hardware/circuit.md`).
3. Run the backend firmware:

   ```sh
   python main.py
   ```

4. Use the mobile app to receive BLE/Wi-Fi alerts.

## Project Structure

```sh
backend/
├── main.py
├── requirements.txt
├── README.md
├── IMPLEMENTATION_PLAN.md
├── hardware/
├── detection/
├── comms/
├── logging/
├── utils/
├── config/
├── tests/
```

## Documentation

- See `IMPLEMENTATION_PLAN.md` for the full system design.
- See `hardware/circuit.md` for pinouts and integration details.
- See `tests/test_plan.md` for validation and compliance procedures.

## License

This project is for educational and research use. See LICENSE for details.
