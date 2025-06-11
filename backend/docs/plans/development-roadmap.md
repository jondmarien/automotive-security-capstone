# Automotive Security Capstone – Development Roadmap (Device-Agnostic Phase)

_This document converts all professor requirements and recent design agreements into a concrete, hardware-independent action plan.  Follow the checklist in order; each task is phrased so that it can be completed with nothing more than laptop-level tooling, your existing repositories, and free-tier cloud services._

## 0 Prerequisites

| Tool | Min Version | Purpose |
|------|-------------|---------|
| Python | 3.11 | Runs backend, unit tests, code-gen tools |
| Node.js | 20 LTS | Realm Flutter generator & web tooling |
| Flutter | 3.22 | Cross-platform mobile build |
| Docker | 25 | Local MongoDB + FastAPI containers |
| Git CLI | 2.43 | Branch & CI workflows |
| Poetry | 1.8 | Backend dependency/virtual-env manager |

Download and install everything before you begin Sprint 7.

---

## 1 Repository Hygiene

1. `git pull --all` to ensure local clones are current.
2. Add the following protected branches in GitHub: `main`, `dev`, `edge-dev`, `backend-dev`, `mobile-dev`.
3. Create a mono-repo **commit template** in `.gitmessage` that enforces _scope – subject – body – footer_.
4. Register pre-commit hooks:

   ```bash
   pre-commit install # runs ruff, black, and flutter format
   ```

---

## 2 Edge Folder (MicroPython – Device Stub Only)

> _Directory: `backend/hardware` will **not** touch physical I/O – we rely on pure Python stubs for now._

### 2.1  Create Packet & Metric Domain Classes

```python
# hardware/packet.py
class Packet:
    def __init__(self, ts: int, rssi: int, freq: float, payload: bytes):
        self.ts, self.rssi, self.freq, self.payload = ts, rssi, freq, payload
```

### 2.2  Implement `signal_filter.py`

1. Copy constants table (RSSI, band list, dupe window) into module-level variables.
2. Write `should_accept(pkt: Packet) -> bool` covering
   * RSSI ≥ `MIN_RSSI_DBM`
   * `FREQ_BANDS` containment
   * duplication placeholder `dupe_count(pkt) < MAX_DUPES`
3. Write unit tests in `tests/test_signal_filter.py`.

### 2.3  Implement `report_logic.py`

1. Add dummy helpers `is_replay`, `is_jam`.
2. `classify(pkt)` → returns `"benign" | "replay" | "jam" | "drop"` based on filter + helpers.
3. Test coverage ≥ 90 %.

### 2.4  Lightweight Persistence Layer (In-Memory)

1. `edge/dao.py` with dict-backed tables `packets`, `alerts`.
2. CRUD functions mirror the future SQLite schema but do **not** write to disk.

### 2.5  Logging Stub

`edge/log_utils.py` collects JSON objects into a list `LOG_BUFFER`; define `flush()` that prints to console (acting as JSONL rotation).

---

## 3 Backend Folder (FastAPI)

### 3.1  Poetry Setup

```bash
cd backend && poetry init --name automotive_security_backend
poetry add fastapi uvicorn[standard] motor pydantic-settings python-dotenv
poetry add --group dev pytest pytest-asyncio black ruff
```

### 3.2  Folder Conventions

```sh
backend/
 ├─ app_logging/        # existing structured-logging helpers
 ├─ api/
 │   ├─ dependencies.py # auth, db injection
 │   ├─ routers/
 │   │   ├─ alerts.py   # /v1/alerts
 │   │   └─ packets.py  # /v1/packets/bulk
 │   └─ __init__.py
 └─ dao/
     ├─ mongo.py        # Async DAO layer
     └─ __init__.py
```

### 3.3  DAO Implementation (`dao/mongo.py`)

```python
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from os import getenv

client = AsyncIOMotorClient(getenv("MONGODB_URI"))
db = client.auto_sec
signals = db.signals
alerts = db.alerts
rolling_codes = db.rolling_codes

async def insert_alert(doc: BaseModel):
    await alerts.insert_one(doc.model_dump())
```

### 3.4  Routers

* **`/v1/packets/bulk`** – validates JWT, inserts batch via `signals.insert_many`.
* **`/v1/alerts`** – returns last 100 alerts for a given `vehicle_id`.

### 3.5  Auth Middleware

1. Mutual-TLS postponed → implement JWT only (`pyjwt[crypto]`).
2. Dependency `get_current_device` decodes token, returns device claims.

### 3.6  Dockerfile & DO App Platform

* `Dockerfile`:

  ```dockerfile
  FROM python:3.11-slim
  ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
  WORKDIR /app
  COPY pyproject.toml poetry.lock /app/
  RUN pip install poetry && poetry install --no-root --only main
  COPY . /app
  CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8080"]
  ```

* Push to GitHub → DigitalOcean will build & deploy.

---

## 4 Mobile Folder (Flutter + Realm)

### 4.1  Add Dependencies

```bash
flutter pub add realm realm_flutter flutter_dotenv
```

### 4.2  Generate Realm Models

Run `dart run realm generate` after editing `realm_models.dart`.

### 4.3  Sync Service Prototype

```dart
class SyncService {
  late Realm realm;

  Future<void> init() async {
    final appConfig = AppConfiguration('<APP_ID>');
    final app = App(appConfig);
    realm = Realm(Configuration.flexibleSync(app, [Alert.schema]));
    await realm.subscriptions.update((mutable) {
      mutable.add(realm.all<Alert>());
    });
    await realm.syncSession.waitForDownload();
  }
}
```

### 4.4  Widget Test

Create `test/realm_open_test.dart` verifying `SyncService.init()` does not throw.

---

## 5 Cloud Database – Atlas Quick Start

1. Sign up → Create **Shared M0** cluster.
2. Region: same as DO app.
3. Add user `capstone_api` w/ readWrite on `auto_sec` DB.
4. Whitelist `0.0.0.0/0` for dev; later tighten.
5. In **Data Explorer** create collections.
6. Open **Web Shell**:

   ```js
   db.alerts.createIndex({ timestamp: 1 }, { expireAfterSeconds: 7776000 })
   db.signals.createIndex({ timestamp: 1 }, { expireAfterSeconds: 7776000 })
   ```

7. Copy SRV connection string → place in DO secrets & `.env.development`.

---

## 6 Continuous Integration Matrix

| Job | Runs On | Key Steps |
|-----|---------|-----------|
| `edge-tests` | ubuntu-latest | `pip install -r edge/requirements-dev.txt && pytest edge/tests` |
| `backend-tests` | ubuntu-latest | `poetry install && pytest` |
| `flutter-tests` | macos-latest | `flutter test` |
| `docker-build` | ubuntu-latest | `docker build -t backend . && docker push` |

---

## 7 Immediate Sprint Tasks

| ID | Task | Owner | Hours |
|----|------|-------|-------|
| S7-1 | Implement `should_accept` full logic | Alice | 4 |
| S7-2 | DAO layer + `/bulk` API | Bob | 6 |
| S7-3 | Realm sync POC | Carol | 5 |
| S7-4 | CI pipeline file | Dan | 3 |
| S7-5 | Update docs & diagrams | Eve | 2 |

Review pull-requests daily; merge freeze Wednesday @ 17:00.

---

## June 2025 POC Debugging & Tuning Sprint - 2025-06-11 - 3:40PM

### Key Fixes Implemented
- Dashboard now unpacks and flattens each detection in `signal_detection` events for proper display.
- Backend logs all burst analysis fields for tuning, suppresses log spam, and only processes/logs bursts if a Pico is connected.
- Burst pattern logic is ready for tuning to specific key fobs (e.g., BMW), using a new `FOB_SETTINGS` dict in `signal_bridge.py`.
- All logs are timestamped for easier correlation.

### Tuning Recommendations
- Use the dashboard and backend logs to observe burst characteristics when pressing your key fob.
- Adjust `min_peak_count`, `min_max_power_db`, and pattern logic in `signal_bridge.py` to match your fob's signature.
- Add new fob models to `FOB_SETTINGS` as you test more brands.

### Next Steps
- Capture and analyze real key fob bursts.
- Further tune detection logic for your specific vehicle.
- Expand dashboard columns as needed for new detection fields.
- Continue to update this guide as new lessons are learned.
